from sqlalchemy import text

class UserRepository:
    def __init__(self, db):
        self.db = db

    def call_sp_get_login_user(self, username: str, password: str, webreports_id: str = "", windows_user: str = "MCP Server") -> dict | None:
        sql = text("""
                   EXEC spGetLoginUser @UserName=:UserName, @Password=:Password, @WebReportsID=:WebReportsID, @WindowsUser=:WindowsUser
                   """)
        result = self.db.execute(sql, {
            "UserName": username,
            "Password": password,
            "WebReportsID": webreports_id,
            "WindowsUser": windows_user
            })
        row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)

