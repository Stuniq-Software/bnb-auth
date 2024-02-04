import jwt
from datetime import datetime, timedelta
from typing import Tuple


class JWTHandler:
    secret: bytes
    algorithm: str
    at_expiration: int
    rt_expiration: int
    issuer: str

    def __init__(self, secret: str, algorithm: str = "HS256", at_expiration: int = 3600, rt_expiration: int = 86400,
                 issuer: str = "auth.bnbclone.local"):
        self.secret = secret.encode()
        self.algorithm = algorithm
        self.at_expiration = at_expiration
        self.rt_expiration = rt_expiration
        self.issuer = issuer

    @staticmethod
    def get_expiration_time(expiration: int):
        expire_date = datetime.now() + timedelta(seconds=expiration)
        return int(round(expire_date.timestamp()))

    def create_tokens(self, payload: dict) -> Tuple[str, str]:
        access_token_jwt_payload = {
            **payload,
            "exp": self.get_expiration_time(self.at_expiration),
            "iss": self.issuer,
            "iat": int(round(datetime.now().timestamp())),
            "nbf": int(round(datetime.now().timestamp()) - 1),
        }

        refresh_token_jwt_payload = {
            **payload,
            "exp": self.get_expiration_time(self.rt_expiration),
            "iss": self.issuer,
            "iat": int(round(datetime.now().timestamp())),
            "nbf": int(round(datetime.now().timestamp()) - 1),
        }

        access_token = jwt.encode(access_token_jwt_payload, self.secret, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_token_jwt_payload, self.secret, algorithm=self.algorithm)

        return access_token, refresh_token

    def verify_token(self, token: str, for_refresh: bool = False):
        try:
            return jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                options={
                    'verify_exp': not for_refresh,
                    'verify_iss': True,
                    'verify_iat': True,
                    'verify_nbf': True,
                    'verify_signature': True,
                }
            ), None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"

    def refresh_token(self, access_token: str, refresh_token: str):
        rt_payload, error = self.verify_token(refresh_token)
        at_payload, error = self.verify_token(access_token, for_refresh=True)
        if error:
            return None, error
        if at_payload["id"] != rt_payload["id"]:
            return None, "Invalid token"
        return self.create_tokens(at_payload)
