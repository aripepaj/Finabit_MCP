from fastapi import APIRouter
from app.auth.config import AUTH_BASE_URL

router = APIRouter()

@router.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    return {
        "issuer": AUTH_BASE_URL,
        "authorization_endpoint": f"{AUTH_BASE_URL}/authorize",
        "token_endpoint": f"{AUTH_BASE_URL}/token",
        "registration_endpoint": f"{AUTH_BASE_URL}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["claudeai"],
        "logo_uri": f"{AUTH_BASE_URL}/static/icon.ico",
        "token_endpoint_auth_methods_supported": ["none", "client_secret_post"]
    }

@router.get("/.well-known/oauth-authorization-server/mcp")
async def oauth_metadata_mcp():
    return {
        "issuer": AUTH_BASE_URL,
        "authorization_endpoint": f"{AUTH_BASE_URL}/authorize",
        "token_endpoint": f"{AUTH_BASE_URL}/token",
        "registration_endpoint": f"{AUTH_BASE_URL}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["claudeai"],
        "token_endpoint_auth_methods_supported": ["none", "client_secret_post"]
    }

@router.get("/.well-known/oauth-protected-resource/mcp")
async def oauth_protected_resource_mcp():
    return {
        "resource": f"{AUTH_BASE_URL}/mcp",
        "authorization_servers": [AUTH_BASE_URL],
        "scopes_supported": ["claudeai"],
        "bearer_methods_supported": ["header"],
        "resource_documentation": f"{AUTH_BASE_URL}/docs"
    }