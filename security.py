import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

# 1. Setup token signing variables from the environment
# Make sure to keep your fallback values safe
JWT_SECRET = os.getenv("JWT_SECRET", "super-duper-secret-dev-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


def hash_password(password: str) -> str:
    """Converts plain text password into a secure cryptographic hash using native bcrypt."""
    # Convert string text to raw bytes string payload
    password_bytes = password.encode("utf-8")

    # Generate a random cryptographic salt factor
    salt = bcrypt.gensalt()

    # Hash the password and decode back to database-storable string format
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a clear text password with the database hash using native bcrypt."""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    # Secure validation execution comparison loop
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict) -> str:
    """Generates a secure signed JWT token containing user identity claims."""

    # Create a copy of the data to avoid mutating the original dictionary
    to_encode = data.copy()
    # Set the expiration time for the token
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Add the expiration time to the payload(means the token will be invalid after this time)
    to_encode.update({"exp": expire})
    # Encode the payload into a JWT token using the secret and algorithm
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Optional[dict]:
    """Validates a JWT token string. Returns the decoded claims if valid, or None if invalid/expired."""
    try:
        # Decode and verify the signature + expiration time automatically
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except (jwt.PyJWTError, KeyError):
        # Catches expired tokens, malformed signatures, or tampering attempts safely
        return None
