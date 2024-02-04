import bcrypt
import os
from typing import Optional


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(hashed_password: str, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
