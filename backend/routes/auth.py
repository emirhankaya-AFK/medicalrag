from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, Any
from ..services.storage_service import storage_service
from ..services.auth_service import auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    username: str
    password: str
    role: str # doctor, nurse, patient, admin

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

@router.post("/register")
def register(user: UserRegister):
    existing = storage_service.get_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    if user.role not in ["doctor", "nurse", "patient", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'doctor', 'nurse', 'patient', or 'admin'.")
        
    hashed_pwd = auth_service.hash_password(user.password)
    storage_service.add_user(
        username=user.username,
        password_hash=hashed_pwd,
        role=user.role
    )
    return {"message": "User registered successfully"}

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = storage_service.get_user_by_username(form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = auth_service.create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"]
    }

@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
