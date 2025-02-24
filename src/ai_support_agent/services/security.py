from datetime import datetime, timedelta
from jose import jwt
from argon2 import PasswordHasher
from typing import Optional
from ..core.config import settings

# Initialize the Argon2 hasher
ph = PasswordHasher()

# JWT settings
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        # Note: ph.verify expects (hash, password) order
        return ph.verify(hashed_password, plain_password)
    except Exception as e:
        return False


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return ph.hash(password)


def create_access_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=8)
        
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM) 