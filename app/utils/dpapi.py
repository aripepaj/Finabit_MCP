import os
import base64
import ctypes
import ctypes.wintypes as wt
from typing import Dict

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

def get_basic_header_or_raise() -> Dict[str, str]:
    """Get Basic Auth header from available credentials"""
    
    # Try DPAPI first (for Claude Desktop)
    user_dpapi = os.getenv("BASIC_AUTH_USER_DPAPI")
    pass_dpapi = os.getenv("BASIC_AUTH_PASS_DPAPI")
    if user_dpapi and pass_dpapi:
        try:
            entropy = b"FinabitMCP|v1"
            username = dpapi_unprotect_b64(user_dpapi, entropy)
            password = dpapi_unprotect_b64(pass_dpapi, entropy)
            token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
            return {"Authorization": f"Basic {token}"}
        except:
            pass

    # Try keyring
    try:
        import keyring
        username = keyring.get_password("finabit-api", "finabit-user")
        if username:
            password = keyring.get_password("finabit-api", username)
            if password:
                token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
                return {"Authorization": f"Basic {token}"}
    except:
        pass

    # Try plain environment
    username = os.getenv("BASIC_AUTH_USER")
    password = os.getenv("BASIC_AUTH_PASS")
    if username and password:
        token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {token}"}

    raise RuntimeError("No Basic credentials available")