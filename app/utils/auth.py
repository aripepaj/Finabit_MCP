# app/util/auth.py
import os, base64
from typing import Dict

from app.utils.dpapi import dpapi_unprotect_b64

_ENTROPY = b"FinabitMCP|v1"  
try:
    import keyring
except Exception:
    keyring = None

def _from_dpapi_env():
    u_b64 = os.getenv("BASIC_AUTH_USER_DPAPI")
    p_b64 = os.getenv("BASIC_AUTH_PASS_DPAPI")
    if u_b64 and p_b64:
        user = dpapi_unprotect_b64(u_b64, _ENTROPY)
        pwd  = dpapi_unprotect_b64(p_b64, _ENTROPY)
        return user, pwd
    return None

def _from_keyring():
    if not keyring:
        return None
    KR_SERVICE, KR_USERKEY = "finabit-api", "finabit-user"
    u = keyring.get_password(KR_SERVICE, KR_USERKEY)
    if not u:
        return None
    p = keyring.get_password(KR_SERVICE, u)
    if not p:
        return None
    return u, p

def _from_plain_env():
    u = os.getenv("BASIC_AUTH_USER")
    p = os.getenv("BASIC_AUTH_PASS")
    if u and p:
        return u, p
    return None

def get_basic_header_or_raise() -> Dict[str, str]:
    for source in (_from_dpapi_env, _from_keyring, _from_plain_env):
        up = source()
        if up:
            user, pwd = up
            token = base64.b64encode(f"{user}:{pwd}".encode("utf-8")).decode("ascii")
            return {"Authorization": f"Basic {token}"}
    raise RuntimeError("No Basic credentials available (DPAPI env / keyring / plain env).")