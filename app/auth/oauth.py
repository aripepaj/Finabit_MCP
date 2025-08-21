import secrets
import logging
import os
import base64
import ctypes
import ctypes.wintypes as wt
from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from app.services.users import UserService
from app.utils.templates import login_form_html
from app.auth.config import (
    INSTALL_KEY, generate_auth_code, logger, TOKEN_EXPIRY_HOURS, create_access_token, verify_code_challenge, ensure_claude_client
)
from app.auth.state import oauth_sessions, registered_clients
from app.repositories.user_repository import _store_creds

router = APIRouter()

# DPAPI functions - inline to avoid import issues
class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wt.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
CryptUnprotectData.argtypes = [ctypes.POINTER(DATA_BLOB), ctypes.c_wchar_p,
                               ctypes.POINTER(DATA_BLOB), ctypes.c_void_p,
                               ctypes.c_void_p, wt.DWORD,
                               ctypes.POINTER(DATA_BLOB)]
CryptUnprotectData.restype = wt.BOOL

LocalFree = ctypes.windll.kernel32.LocalFree

def _to_blob(b: bytes) -> DATA_BLOB:
    buf = ctypes.create_string_buffer(b)
    return DATA_BLOB(len(b), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))

def dpapi_unprotect_b64(b64: str, entropy: bytes) -> str:
    raw = base64.b64decode(b64)
    in_blob = _to_blob(raw)
    ent_blob = _to_blob(entropy) if entropy else None
    out_blob = DATA_BLOB()
    ok = CryptUnprotectData(ctypes.byref(in_blob), None,
                            ctypes.byref(ent_blob) if ent_blob else None,
                            None, None, 0, ctypes.byref(out_blob))
    if not ok:
        raise OSError("CryptUnprotectData failed")
    try:
        data = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        return data.decode("utf-8")
    finally:
        LocalFree(out_blob.pbData)

def get_stdio_credentials():
    """Get credentials from environment when running in stdio mode"""
    if os.getenv("MCP_STDIO") != "1":
        return None
        
    try:
        user_encrypted = os.getenv("BASIC_AUTH_USER_DPAPI")
        pass_encrypted = os.getenv("BASIC_AUTH_PASS_DPAPI")
        
        if user_encrypted and pass_encrypted:
            entropy = b"FinabitMCP|v1"
            username = dpapi_unprotect_b64(user_encrypted, entropy)
            password = dpapi_unprotect_b64(pass_encrypted, entropy)
            return username, password
    except:
        pass
    return None

@router.get("/authorize")
async def authorize(
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(default="claudeai"),
    state: str = Query(default=""),
    code_challenge: str = Query(...),
    code_challenge_method: str = Query(default="S256")
):
    """OAuth 2.0 Authorization Endpoint"""
    
    if not ensure_claude_client(client_id):
        raise HTTPException(status_code=400, detail="Invalid client_id")

    client_info = registered_clients[client_id]
    if redirect_uri not in client_info["redirect_uris"]:
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")

    # Auto-login if we have stdio credentials
    creds = get_stdio_credentials()
    if creds:
        username, password = creds
        service = UserService()
        user = service.authenticate_user(username, password)
        
        if user:
            # ⬇️ seed the same OS keyring that the rest of your app uses
            try:
                _store_creds(username, password)
            except Exception as e:
                logger.warning(f"Failed to store creds in keyring during stdio auto-login: {e}")

            auth_code = generate_auth_code()
            oauth_sessions[f"code_{auth_code}"] = {
                "user_id": user["UserID"],
                "client_id": client_id,
                "scope": scope,
                "code_challenge": code_challenge,
                "expires_at": datetime.utcnow() + timedelta(minutes=10)
            }
            
            redirect_url = f"{redirect_uri}?{urlencode({'code': auth_code, 'state': state})}"
            return RedirectResponse(url=redirect_url, status_code=302)

    # Show login form if no auto-login
    auth_request_id = secrets.token_urlsafe(16)
    oauth_sessions[auth_request_id] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "created_at": datetime.utcnow()
    }

    return HTMLResponse(login_form_html(auth_request_id))

@router.post("/authorize")
async def process_authorization(
    request: Request,
    auth_request_id: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    install_key: str = Form(...) 
):
    if auth_request_id not in oauth_sessions:
        raise HTTPException(status_code=400, detail="Invalid authorization request")
    
    session = oauth_sessions[auth_request_id]

    if install_key != INSTALL_KEY:
        return HTMLResponse(
            login_form_html(auth_request_id, error_message="Invalid installation key."),
            status_code=200
        )
    
    # Test user
    if username == "test" and password == "test":
        user_id = 9999
    else:
        service = UserService()
        user = service.authenticate_user(username, password)
        if not user:
            return HTMLResponse(
                login_form_html(auth_request_id, error_message="Invalid username or password."),
                status_code=200
            )
        user_id = user["UserID"]

        try:
            _store_creds(username, password)
        except Exception as e:
            logger.warning(f"Failed to store creds in keyring during form login: {e}")

    auth_code = generate_auth_code()
    oauth_sessions[f"code_{auth_code}"] = {
        "user_id": user_id,
        "client_id": session["client_id"],
        "scope": session["scope"],
        "code_challenge": session["code_challenge"],
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }
    
    del oauth_sessions[auth_request_id]
    redirect_url = f"{session['redirect_uri']}?{urlencode({'code': auth_code, 'state': session['state']})}"
    return RedirectResponse(url=redirect_url, status_code=302)

@router.post("/token")
async def token_endpoint(request: Request):
    """OAuth 2.0 Token Endpoint"""
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            data = await request.json()
        else:
            form_data = await request.form()
            data = dict(form_data)

        grant_type = data.get("grant_type")
        auth_code = data.get("code")
        code_verifier = data.get("code_verifier")

        if grant_type != "authorization_code":
            return JSONResponse(
                status_code=400,
                content={"error": "unsupported_grant_type"}
            )

        if not auth_code:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "error_description": "Missing authorization code"}
            )

        code_key = f"code_{auth_code}"
        if code_key not in oauth_sessions:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_grant", "error_description": "Authorization code not found"}
            )

        code_data = oauth_sessions[code_key]
        if datetime.utcnow() > code_data["expires_at"]:
            del oauth_sessions[code_key]
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_grant", "error_description": "Authorization code expired"}
            )

        if code_verifier and not verify_code_challenge(code_verifier, code_data["code_challenge"]):
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_grant", "error_description": "PKCE verification failed"}
            )

        user_id = code_data["user_id"]
        scope = code_data["scope"].split() if isinstance(code_data["scope"], str) else ["claudeai"]
        access_token = create_access_token(user_id, expires_delta=TOKEN_EXPIRY_HOURS * 3600 * 30 * 12, scopes=scope)

        del oauth_sessions[code_key]
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": TOKEN_EXPIRY_HOURS * 3600 * 30 * 12,
            "scope": code_data["scope"]
        }
    except Exception as e:
        logger.error(f"Token endpoint error: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request", "error_description": str(e)}
        )

@router.post("/register")
async def register_client(request: Request):
    """OAuth 2.0 Dynamic Client Registration"""
    try:
        body = await request.json()
        client_id = f"claude_client_{secrets.token_urlsafe(16)}"
        registered_clients[client_id] = {
            "client_id": client_id,
            "redirect_uris": body.get("redirect_uris", []),
            "created_at": datetime.utcnow()
        }
        return {
            "client_id": client_id,
            "client_id_issued_at": int(datetime.utcnow().timestamp()),
            "redirect_uris": body.get("redirect_uris", []),
            "token_endpoint_auth_method": "none",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "claudeai"
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_client_metadata"}
        )