from Crypto.Cipher import DES3
from Crypto.Hash import MD5
import base64

def encrypt_des_dotnet(password: str) -> str:
    # Key
    key_str = "1t2e3r4a5b6i7t8"
    md5 = MD5.new()
    md5.update(key_str.encode('ascii'))
    key_16 = md5.digest()
    key_24 = key_16 + key_16[:8]  # expand to 24 bytes

    # Pad password using PKCS7 (same as .NET for block ciphers)
    data = password.encode('ascii')
    pad_len = 8 - (len(data) % 8)
    pad_byte = bytes([pad_len])
    data_padded = data + pad_byte * pad_len

    cipher = DES3.new(key_24, DES3.MODE_ECB)
    encrypted = cipher.encrypt(data_padded)
    b64 = base64.b64encode(encrypted).decode('ascii')
    return b64

def decrypt_des_dotnet(enc: str) -> str:
    key_str = "1t2e3r4a5b6i7t8"
    md5 = MD5.new()
    md5.update(key_str.encode('ascii'))
    key_16 = md5.digest()
    key_24 = key_16 + key_16[:8]

    encrypted = base64.b64decode(enc)
    cipher = DES3.new(key_24, DES3.MODE_ECB)
    decrypted = cipher.decrypt(encrypted)
    # Remove PKCS7 padding
    pad_len = decrypted[-1]
    return decrypted[:-pad_len].decode('ascii')

# === TEST CASE ===

original = "servTera-24"
encrypted = encrypt_des_dotnet(original)
print("Encrypted:", encrypted)

decrypted = decrypt_des_dotnet(encrypted)
print("Decrypted:", decrypted)

# Try with your DB string:
db_encrypted = "qGJd10O1f6iubhDAXYF1kA=="
print("DB Decrypted:", decrypt_des_dotnet(db_encrypted))
