import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = "SECRET_KEY_GOES_HERE_CHANGE_THIS_IN_PROD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Password Hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class User(BaseModel):
    username: str

class UserCreate(User):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Utils
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return User(username=username)

# DB Operations (Supabase REST API)
def create_user(user: UserCreate):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False, "Server misconfiguration: Missing Supabase credentials"
        
    try:
        hashed_pw = get_password_hash(user.password)
        
        url = f"{SUPABASE_URL}/rest/v1/users"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        payload = {
            "username": user.username,
            "hashed_password": hashed_pw
        }
        
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                return True, "User created"
            elif response.status_code == 409:
                return False, "Username already exists"
            else:
                print(f"Supabase Error: {response.status_code} - {response.text}")
                return False, f"Registration failed: {response.status_code}"
                
    except Exception as e:
        print(f"Connection Error: {e}")
        return False, f"Connection error: {str(e)}"

def get_user(username: str):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
        
    try:
        url = f"{SUPABASE_URL}/rest/v1/users"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }
        params = {
            "username": f"eq.{username}",
            "select": "*"
        }
        
        with httpx.Client() as client:
            response = client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    return data[0]
            else:
                print(f"Supabase Error: {response.status_code} - {response.text}")
                
        return None
    except Exception as e:
        print(f"Connection Error: {e}")
        return None
