from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self):
        print(">>> Loaded UserService from", __file__)
        self.repo = UserRepository()

    def authenticate_user(self, username: str, password: str):
        return self.repo.call_sp_get_login_user(username, password)
