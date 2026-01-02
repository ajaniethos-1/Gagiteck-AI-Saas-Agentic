"""Authentication API endpoints."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
import uuid

from api.config import settings

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Models ---

class UserCreate(BaseModel):
    """Request to create a new user."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")


class UserLogin(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class User(BaseModel):
    """User response model."""
    id: str
    email: str
    name: str
    role: str = "user"
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    email: str


class UserUpdate(BaseModel):
    """Update user request."""
    name: Optional[str] = None
    password: Optional[str] = None


class APIKeyCreate(BaseModel):
    """Create API key request."""
    name: str = Field(..., min_length=1, max_length=100)


class APIKey(BaseModel):
    """API key response."""
    id: str
    name: str
    key: str
    created_at: datetime


# --- In-memory storage (replace with database) ---
_users_db: dict[str, dict] = {}
_api_keys_db: dict[str, dict] = {}


# --- Helper functions ---

def _truncate_password(password: str) -> str:
    """Truncate password to 72 bytes for bcrypt compatibility."""
    encoded = password.encode('utf-8')[:72]
    return encoded.decode('utf-8', errors='ignore')


def hash_password(password: str) -> str:
    """Hash a password (truncated to 72 bytes for bcrypt)."""
    return pwd_context.hash(_truncate_password(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(_truncate_password(plain_password), hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=settings.JWT_EXPIRY_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenData:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None or email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials

    # Check if it's an API key
    if token.startswith(settings.API_KEY_PREFIX):
        api_key = next((k for k in _api_keys_db.values() if k["key"] == token), None)
        if api_key:
            user = _users_db.get(api_key["user_id"])
            if user:
                return User(**user)
        raise HTTPException(status_code=401, detail="Invalid API key")

    # JWT token
    token_data = decode_token(token)
    user = _users_db.get(token_data.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)


# --- Endpoints ---

@router.post(
    "/signup",
    response_model=User,
    status_code=201,
    summary="Create account",
    description="Create a new user account.",
)
async def signup(request: UserCreate):
    """Create a new user account."""
    # Check if email already exists
    if any(u["email"] == request.email for u in _users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"user_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    user = {
        "id": user_id,
        "email": request.email,
        "name": request.name,
        "password_hash": hash_password(request.password),
        "role": "user",
        "created_at": now,
        "updated_at": now,
    }

    _users_db[user_id] = user
    return User(**{k: v for k, v in user.items() if k != "password_hash"})


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate and receive a JWT token.",
)
async def login(request: UserLogin):
    """Authenticate user and return JWT token."""
    user = next((u for u in _users_db.values() if u["email"] == request.email), None)

    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]}
    )

    return Token(
        access_token=access_token,
        expires_in=settings.JWT_EXPIRY_HOURS * 3600,
    )


@router.get(
    "/me",
    response_model=User,
    summary="Get current user",
    description="Get the currently authenticated user's profile.",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.patch(
    "/me",
    response_model=User,
    summary="Update profile",
    description="Update the current user's profile.",
)
async def update_me(request: UserUpdate, current_user: User = Depends(get_current_user)):
    """Update current user profile."""
    user = _users_db.get(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if request.name:
        user["name"] = request.name
    if request.password:
        user["password_hash"] = hash_password(request.password)

    user["updated_at"] = datetime.utcnow()

    return User(**{k: v for k, v in user.items() if k != "password_hash"})


@router.post(
    "/api-keys",
    response_model=APIKey,
    status_code=201,
    summary="Create API key",
    description="Create a new API key for programmatic access.",
)
async def create_api_key(request: APIKeyCreate, current_user: User = Depends(get_current_user)):
    """Create a new API key."""
    key_id = f"key_{uuid.uuid4().hex[:12]}"
    api_key = f"{settings.API_KEY_PREFIX}{uuid.uuid4().hex}"
    now = datetime.utcnow()

    key_data = {
        "id": key_id,
        "name": request.name,
        "key": api_key,
        "user_id": current_user.id,
        "created_at": now,
    }

    _api_keys_db[key_id] = key_data
    return APIKey(**key_data)


@router.get(
    "/api-keys",
    response_model=list[APIKey],
    summary="List API keys",
    description="List all API keys for the current user.",
)
async def list_api_keys(current_user: User = Depends(get_current_user)):
    """List user's API keys."""
    keys = [
        APIKey(**{**k, "key": k["key"][:12] + "..."})
        for k in _api_keys_db.values()
        if k["user_id"] == current_user.id
    ]
    return keys


@router.delete(
    "/api-keys/{key_id}",
    status_code=204,
    summary="Delete API key",
    description="Revoke an API key.",
)
async def delete_api_key(key_id: str, current_user: User = Depends(get_current_user)):
    """Delete an API key."""
    key = _api_keys_db.get(key_id)
    if not key or key["user_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")
    del _api_keys_db[key_id]
