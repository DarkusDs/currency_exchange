from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from db.crud import get_user_by_username, verify_password

auth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Token(BaseModel):
    """
    Pydantic model representing a JWT access token returned after successful authentication
    """
    access_token: str
    token_type: str = 'bearer'

class TokenData(BaseModel):
    """
    Pydantic model used to store decoded token payload data
    """
    username: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a signed JWT access token containing the provided payload and expiration time

    :param data: Payload data to be embedded into the token (e.g. {"sub": username})
    :param expires_delta: Optional custom token lifetime. Defaults to application settings
    :return: Encoded JWT access token as a string
    """
    if not SECRET_KEY:
        raise HTTPException("SECRET_KEY не визначений")

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    """
    Validates and decodes a JWT access token, ensuring its integrity and expiration

    :param token: JWT access token received from the client
    :return: Decoded token payload if the token is valid
    """
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Час існування токену завершився")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не коректний")

def get_current_user(token: str = Depends(auth2_scheme)) -> str:
    """
    Extracts and returns the username from a valid JWT token for protected endpoints

    :param token: JWT access token provided via Authorization header
    :return: Username (subject) extracted from the token
    """
    payload = verify_access_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Інформація токену не дійсна")
    return username

def authenticate_user(username: str, password: str) -> bool:
    """
    Verifies user credentials by comparing the provided password with the stored hash

    :param username: Username provided by the client
    :param password: Plain-text password provided by the client
    :return: True if authentication succeeds, otherwise False
    """
    user = get_user_by_username(username)
    if not user:
        return False
    return verify_password(password, user["hashed_password"])

