import secrets
import logging
from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from app.services.users import UserService
from app.utils.templates import login_form_html
from app.auth.config import (
    INSTALL_KEY, generate_auth_code, logger, TOKEN_EXPIRY_HOURS, create_access_token, verify_code_challenge, ensure_claude_client
)
from app.core.db import get_db_connection
from app.auth.state import oauth_sessions, registered_clients

router = APIRouter()

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

    # Validate client
    if not ensure_claude_client(client_id):
        logger.error(f"Unknown client_id: {client_id}")
        raise HTTPException(status_code=400, detail="Invalid client_id")

    client_info = registered_clients[client_id]
    if redirect_uri not in client_info["redirect_uris"]:
        logger.error(f"Invalid redirect_uri: {redirect_uri} for client {client_id}")
        logger.info(f"Valid redirect_uris: {client_info['redirect_uris']}")
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")

    # Create auth session
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

    logger.info(f"Authorization request from client: {client_id} -> {redirect_uri}")

    # Show login form
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
    
    if username == "test" and password == "test":
        user_id = 9999
        auth_code = generate_auth_code()
        oauth_sessions[f"code_{auth_code}"] = {
            "user_id": user_id,
            "client_id": session["client_id"],
            "scope": session["scope"],
            "code_challenge": session["code_challenge"],
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        del oauth_sessions[auth_request_id]
        redirect_url = (
            f"{session['redirect_uri']}?"
            f"{urlencode({'code': auth_code, 'state': session['state']})}"
        )
        logger.info(f"Redirecting (test user) via GET: {redirect_url}")
        return RedirectResponse(url=redirect_url, status_code=302)

    # REAL user
    db = next(get_db_connection())
    try:
        service = UserService(db)
        user = service.authenticate_user(username, password)
        if not user:
            # Invalid credentials: re-show form with error message
            return HTMLResponse(
                login_form_html(auth_request_id, error_message="Invalid username or password."),
                status_code=200
            )

        auth_code = generate_auth_code()
        oauth_sessions[f"code_{auth_code}"] = {
            "user_id": user["UserID"],
            "client_id": session["client_id"],
            "scope": session["scope"],
            "code_challenge": session["code_challenge"],
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        del oauth_sessions[auth_request_id]
        redirect_url = (
            f"{session['redirect_uri']}?"
            f"{urlencode({'code': auth_code, 'state': session['state']})}"
        )
        logger.info(f"Redirecting (real user) via GET: {redirect_url}")
        return RedirectResponse(url=redirect_url, status_code=302)
    finally:
        db.close()

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

        logger.info(f"Token request data: {data}")
        grant_type = data.get("grant_type")
        auth_code = data.get("code")
        redirect_uri = data.get("redirect_uri")
        client_id = data.get("client_id")
        code_verifier = data.get("code_verifier")

        logger.info(f"Token request: grant_type={grant_type}, code={str(auth_code)[:10]}..., client_id={client_id}")

        if grant_type != "authorization_code":
            return JSONResponse(
                status_code=400,
                content={"error": "unsupported_grant_type", "error_description": f"Grant type '{grant_type}' not supported"}
            )

        if not auth_code:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "error_description": "Missing authorization code"}
            )

        code_key = f"code_{auth_code}"
        if code_key not in oauth_sessions:
            logger.error(f"Invalid authorization code: {auth_code}")
            logger.info(f"Available codes: {[k for k in oauth_sessions.keys() if k.startswith('code_')]}")
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_grant", "error_description": "Authorization code not found or expired"}
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
        expires_at = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)

        # TEST user
        if user_id == 9999:
            test_token_key = f"test_token_{access_token}"
            oauth_sessions[test_token_key] = {
                "user_id": 9999,
                "scope": code_data["scope"],
                "access_token": access_token
            }
            del oauth_sessions[code_key]
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": TOKEN_EXPIRY_HOURS * 3600 * 30 * 12,
                "scope": code_data["scope"]
            }

        # NORMAL user (no DB saving here but can be added)
        del oauth_sessions[code_key]
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in":  TOKEN_EXPIRY_HOURS * 3600 * 30 * 12,
            "scope": code_data["scope"]
        }
    except Exception as e:
        logger.error(f"Token endpoint error: {e}", exc_info=True)
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
        logger.info(f"Registered OAuth client: {client_id}")
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
        logger.error(f"Client registration error: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_client_metadata"}
        )