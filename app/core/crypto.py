from Crypto.Cipher import DES3
from Crypto.Hash import MD5
import base64

class DESHelper:
    SECRET = "1t2e3r4a5b6i7t8"

    @classmethod
    def encrypt(cls, password: str) -> str:
        md5 = MD5.new()
        md5.update(cls.SECRET.encode('ascii'))
        key_24 = md5.digest() + md5.digest()[:8]

        data = password.encode('ascii')
        pad_len = 8 - (len(data) % 8)
        data_padded = data + bytes([pad_len] * pad_len)

        cipher = DES3.new(key_24, DES3.MODE_ECB)
        encrypted = cipher.encrypt(data_padded)
        b64 = base64.b64encode(encrypted).decode('ascii')
        return b64

    @classmethod
    def decrypt(cls, encrypted: str) -> str:
        md5 = MD5.new()
        md5.update(cls.SECRET.encode('ascii'))
        key_24 = md5.digest() + md5.digest()[:8]

        cipher = DES3.new(key_24, DES3.MODE_ECB)
        data = base64.b64decode(encrypted)
        decrypted = cipher.decrypt(data)
        pad_len = decrypted[-1]
        return decrypted[:-pad_len].decode('ascii')

