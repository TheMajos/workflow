import jwt
from datetime import datetime, timedelta, timezone
from src.utils.utils import save_jwt, grab_jwt
from config import JWT_ALGORITHM, SECRET_KEY


# could this just be a set of functions?
class JWT:

    @staticmethod
    def encode_jwt(email: str):

        payload = {
            "email": email,
            "exp": datetime.now(timezone.utc)
            + timedelta(seconds=3600),  # Token expires in 1 hour
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

        save_jwt(token.strip())

    @staticmethod
    def decode_jwt(token):
        try:
            decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return (True, decoded_payload)
        except jwt.exceptions.ExpiredSignatureError:
            return (False, "Token Expired")
        except jwt.exceptions.InvalidTokenError:
            return (False, "Invalid Token")


class JWTManager:
    def __init__(self):
        self.token = grab_jwt()
        self.email = self._grab_email_from_jwt()

    def refresher(self) -> bool:
        """Ensure the token is valid. Refresh if expired."""
        success, payload = JWT.decode_jwt(self.token)

        if success:
            return (True, self.email)

        if payload == "Invalid Token":
            return (False, None)

        if not self.email:
            return (False, None)

        self._refresh_token()
        return (True, self.email)

    def _refresh_token(self):
        new_token = JWT.encode_jwt(self.email)
        self.token = new_token

    # why not just return the whole payload, and let downstream
    # handle how they would like to handle it?
    def _grab_email_from_jwt(self) -> str | None:
        """
        Attempt to extract the email claim from the current JWT.
        Works even if the token is expired. Returns None if invalid.
        """
        try:
            payload = jwt.decode(
                self.token,
                SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
                options={"verify_exp": False},  # ignore expiry for extraction
            )
        except jwt.exceptions.InvalidTokenError:
            return None

        return payload.get("email")
