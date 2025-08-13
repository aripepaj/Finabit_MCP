from app.core.crypto import DESHelper
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, db):
        self.repo = UserRepository(db)

    def authenticate_user(self, username: str, password: str):
        """
        Encrypt the plain password, call the repository, 
        and return the user dict if credentials are valid.
        """
        encrypted = DESHelper.encrypt(password)
        return self.repo.call_sp_get_login_user(username, encrypted)

    def decrypt_user_password(self, encrypted_password: str) -> str:
        """
        Utility method: decrypt an encrypted password string using DESHelper.
        """
        return DESHelper.decrypt(encrypted_password)
