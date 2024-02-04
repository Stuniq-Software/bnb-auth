from util import JWTHandler, Database, PasswordHasher, RedisSession
from typing import Optional


class AuthRepository:
    jwt_handler: JWTHandler
    db_session: Database
    redis_session: RedisSession

    def __init__(self, jwt_handler: JWTHandler, db_session: Database, redis_session: RedisSession):
        self.jwt_handler = jwt_handler
        self.db_session = db_session
        self.redis_session = redis_session

    async def create_user(
            self,
            email: str,
            password: str,
            first_name: str,
            last_name: str,
            phone: str,
            line1: str,
            line2: str,
            city: str,
            state: str,
            country: str,
            postal_code: str,
            account_type: str
    ) -> tuple[bool, Optional[str]]:
        address_query = ("INSERT INTO address (line1, line2, city, state, country, postal_code) VALUES (%s, %s, %s, "
                         "%s, %s, %s) RETURNING id")
        addr_query, error = self.db_session.execute_query(
            address_query,
            (line1, line2, city, state, country, postal_code)
        )
        if error:
            return False, error
        address_id = self.db_session.get_cursor().fetchone()[0]
        hashed_password = PasswordHasher.hash_password(password)
        query = ("INSERT INTO users (email, password, first_name, last_name, phone, address_id, account_type) VALUES ("
                 "%s, %s, %s, %s, %s, %s, %s)")
        success, error = self.db_session.execute_query(
            query,
            (email, hashed_password, first_name, last_name, phone, address_id, account_type)
        )
        if not success:
            return False, error
        self.db_session.commit()
        return True, None

    async def get_user(self, email: str) -> tuple[Optional[dict], Optional[str]]:
        query = ("SELECT u.*, a.line1, a.line2, a.city, a.state, a.country, a.postal_code FROM users u "
                 "INNER JOIN address a ON u.address_id = a.id WHERE email = %s")
        success, error = self.db_session.execute_query(query, (email,))
        if not success:
            return None, error
        return self.db_session.get_cursor().fetchone(), None

    async def login_user(self, email: str, password: str) -> tuple[Optional[dict], Optional[str]]:
        user, error = await self.get_user(email)
        if error:
            return None, error
        if user is None:
            return None, "User not found"
        if PasswordHasher.verify_password(user[2], password) is False:
            return None, "Invalid password"
        access_token, refresh_token = self.jwt_handler.create_tokens({"id": user[0], "email": user[1], "type": user[7]})
        return {"access_token": access_token, 'refresh_token': refresh_token}, None

    async def verify_user(self, jwt_token: str):
        expired_access_tokens = self.redis_session.get("expired_access_tokens")
        if expired_access_tokens:
            if jwt_token in expired_access_tokens.decode().split(';'):
                return None, "Access token has expired"
        return self.jwt_handler.verify_token(jwt_token)

    async def refresh_token(self, access_token: str, refresh_token: str):
        expired_refresh_tokens = self.redis_session.get("expired_refresh_tokens")
        if expired_refresh_tokens:
            if refresh_token in expired_refresh_tokens.decode().split(';'):
                return None, "Refresh token has expired"
            else:
                expired_refresh_tokens = expired_refresh_tokens.decode().split(';')
                expired_refresh_tokens.append(refresh_token)
                self.redis_session.set("expired_tokens", ';'.join(expired_refresh_tokens), 60 * 60 * 24 * 7)
        else:
            self.redis_session.set("expired_refresh_tokens", ';'.join([refresh_token]), 60 * 60 * 24 * 7)

        at, rt = self.jwt_handler.refresh_token(access_token, refresh_token)

        expired_access_tokens = self.redis_session.get("expired_access_tokens")
        if expired_access_tokens:
            expired_access_tokens = expired_access_tokens.decode().split(';')
            expired_access_tokens.append(access_token)
            self.redis_session.set("expired_access_tokens", ';'.join(expired_access_tokens), 60 * 60)
        else:
            self.redis_session.set("expired_access_tokens", ';'.join([access_token]), 60 * 60)

        return at, rt
