
import base64, pathlib, keyring, requests
from typing import Optional, Dict, Any
from app.core.config import settings

KR_SERVICE = "finabit-api"
KR_USERKEY = "finabit-user"

def _store_creds(username: str, password: str):
    keyring.set_password(KR_SERVICE, KR_USERKEY, username)
    keyring.set_password(KR_SERVICE, username, password)

def _get_creds() -> tuple[Optional[str], Optional[str]]:
    u = keyring.get_password(KR_SERVICE, KR_USERKEY)
    p = keyring.get_password(KR_SERVICE, u) if u else None
    return u, p

def _basic_header(username: str, password: str) -> Dict[str, str]:
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}

def auth_header(_: str) -> Dict[str, str]:
    """
    Return Authorization header using saved OS keyring credentials.
    Raise if missing (so caller can handle a re-login UI flow).
    """
    u, p = _get_creds()
    if not u or not p:
        raise RuntimeError("No saved credentials for Basic authentication.")
    return _basic_header(u, p)

class UserRepository:
    def __init__(self):
        self.base = settings.server_api_url.rstrip("/")

    def call_sp_get_login_user(
        self,
        username: str,
        password: str,
        webreports_id: str = "",
        windows_user: str = "MCP Server"
    ) -> dict | None:
        """
        First-time login with Basic:
          - save username/password to OS keychain
          - verify by calling /api/Account/userinfo with Basic
        """
        _store_creds(username, password)

        # verify credentials by calling a protected endpoint
        hdr = _basic_header(username, password)
        r = requests.get(f"{self.base}/api/Account/userinfo", headers=hdr, timeout=15)
        if not r.ok:
            # bad creds; don't keep them
            keyring.delete_password(KR_SERVICE, KR_USERKEY)
            try:
                keyring.delete_password(KR_SERVICE, username)
            except Exception:
                pass
            return None

        info = r.json()
        return {
            "UserID": info.get("userId") or info.get("UserID"),
            "Username": info.get("username") or username
        }

    def get_userinfo(self) -> Optional[Dict[str, Any]]:
        try:
            hdr = auth_header(self.base)
            r = requests.get(f"{self.base}/api/Account/userinfo", headers=hdr, timeout=15)
            if r.status_code == 401:
                # saved creds might be wrong/changed
                return None
            return r.json() if r.ok else None
        except Exception:
            return None