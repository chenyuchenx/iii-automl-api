from datetime import datetime, timedelta
from typing import Union
from fastapi import Depends, APIRouter, HTTPException, status, Query, Response, Request, security, Form
from jose import JWTError, jwt
from passlib.context import CryptContext
import passlib.handlers.bcrypt, app.routers.schemas as sc, bcrypt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = APIRouter()
oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "admin": {
        "username": "admin",
        "name": "Admin",
        "email": "admin@gmail.com",
        "hashed_password": "$2b$12$JGMcEjmJ63AsOr8P8HKx/.fLLXaDATE1vpvnPJT3yT3Xc2puTtsJ6",
        "disabled": False,
    },
    "lisa6222lisa@gmail.com": {
        "username": "lisa6222lisa@gmail.com",
        "name": "Lisa",
        "email": "lisa6222lisa@gmail.com",
        "hashed_password": "$2b$12$T.4HYwL./yfIp1a7iqA8c.Ew5gv3YkTLHGoUTRkAeEE0ZBB4MlkmC",
        "disabled": False,
    },
    "cj827iii@gmail.com": {
        "username": "cj827iii@gmail.com",
        "name": "Mork",
        "email": "cj827iii@gmail.com",
        "hashed_password": "$2b$12$a3FOyyIW3w9W2o27mqheQuCV1SZMW1oBmqdzbXYzYXJtV5RNVJQYm",
        "disabled": False,
    },
    "kenny.chen@iii.org.tw": {
        "username": "kenny.chen@iii.org.tw",
        "name": "Kenny",
        "email": "kenny.chen@iii.org.tw",
        "hashed_password": "$2b$12$IsFVfAdVMDtPoRzhK7NDe.QxTNqQUaDsBMzwwL0gX2Jgq5r9FVULW",
        "disabled": True,
    }
}

def hash_password(password: str):
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return sc.UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str = None):
    user = get_user(fake_db, username)
    if not user:
        return False
    if password is not None:
        if not verify_password(password, user.hashed_password):
            return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# JWT authentication function
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = authenticate_user(fake_users_db, username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@app.post("/login", response_model=sc.Token)
async def login_for_access_token(*, username: str = Form(...), password: str = Form(...), response: Response):
    user = authenticate_user(fake_users_db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.headers["Authorization"] = f"Bearer {access_token}"
    response.set_cookie(key="IIIUser", value=username)
    response.set_cookie(key="IIIToken", value=access_token)
    response.set_cookie(key="IIITenant", value="VGVuYW50.ZEuHp_yvwNmosMF9")
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_user_me(*, request: Request):

    access_token = request.cookies.get("IIIToken")
    try:
        user = await get_current_user(access_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    return {"name": user.name, "username": user.username, "email": user.email}

@app.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie("IIIUser")
    response.delete_cookie("IIIToken")
    response.delete_cookie("IIITenant")
    return {'message': 'Logged out successfully'}


