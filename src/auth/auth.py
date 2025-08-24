from passlib.context import CryptContext
from src.models import UserRegister
from src.db.db import MongoHandler
from src.exc.excs import (
    UserExists,
    UserDoesNotExists,
    RateLimitError,
)
from src.utils.limiter import is_rate_limited
from src.auth.jwt import JWT


class AuthUtilities:
    _instance = None
    _pwd_context = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if AuthUtilities._pwd_context is None:
            AuthUtilities._pwd_context = CryptContext(
                schemes=["bcrypt"], deprecated="auto"
            )

    def hash_password(self, password: str) -> str:
        """Hash a plain-text password using the configured hashing algorithm."""
        return self._pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify if a plain-text password matches a previously hashed password."""
        return self._pwd_context.verify(plain_password, hashed_password)


class Authentication:

    @staticmethod
    async def register(email: str, password: str) -> bool:
        rl = await is_rate_limited("register", email)
        if rl:
            raise RateLimitError("Ratelimit reached, try again later.")

        UserRegister(email=email, password=password)

        if await MongoHandler().query({"email": email}):
            raise UserExists("User already exists")

        hashed = AuthUtilities().hash_password(password)

        await MongoHandler().insert({"email": email, "password": hashed})
        return True

    @staticmethod
    async def login(email: str, password: str) -> bool:
        if await is_rate_limited("login", email):
            raise RateLimitError("Rate limit reached. Try again later.")

        user = await MongoHandler().query({"email": email})
        if not user:
            raise UserDoesNotExists("Email is not in records.")

        stored_hash = user.get("password")
        if not AuthUtilities().verify_password(password, stored_hash):
            return False

        JWT.encode_jwt(email)
        return True
