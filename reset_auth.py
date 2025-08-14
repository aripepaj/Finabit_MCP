# reset_auth.py
import pathlib, keyring
KR_SERVICE = "finabit-api"
KR_USERKEY = "finabit-user"

# delete token cache
p = pathlib.Path.home() / ".finabit" / "token.json"
if p.exists():
    p.unlink()
    print("Deleted token cache:", p)

# delete keychain creds (best-effort)
u = keyring.get_password(KR_SERVICE, KR_USERKEY)
if u:
    keyring.delete_password(KR_SERVICE, KR_USERKEY)
    try:
        keyring.delete_password(KR_SERVICE, u)
    except keyring.errors.PasswordDeleteError:
        pass
    print("Cleared keychain entries.")
else:
    print("No keychain entries to clear.")
