from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from telebot.types import User

from settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from db.crud import get_user_by_username, verify_password

auth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenData(BaseModel):
    username: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if not SECRET_KEY:
        raise HTTPException("SECRET_KEY не визначений")

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Час існування токену завершився")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не коректний")

def get_current_user(token: str = Depends(auth2_scheme)) -> str:
    payload = verify_access_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Інформація токену не дійсна")
    return username

def authenticate_user(username: str, password: str) -> bool:
    user = get_user_by_username(username)
    if not user:
        return False
    return verify_password(password, user["hashed_password"])


# import os
# from typing import Optional
#
# import jwt
# from datetime import datetime, timedelta
# from settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
# from fastapi import HTTPException, Security
# from fastapi.security import OAuth2PasswordBearer
# from datetime import datetime, timedelta
# import jwt
# from pydantic import BaseModel
#
# from fastapi.security import HTTPBearer
#
# oauth2_scheme = HTTPBearer()
#
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
# class User(BaseModel):
#     username: str
#     password: str
#
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
# def verify_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=403, detail="Invalid token")
