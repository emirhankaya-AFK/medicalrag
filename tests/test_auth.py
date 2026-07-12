import pytest
from backend.services.auth_service import auth_service

def test_password_handling():
    pwd = "securepassword123"
    hashed = auth_service.hash_password(pwd)
    
    assert auth_service.verify_password(pwd, hashed) is True
    assert auth_service.verify_password("wrong", hashed) is False

def test_token_lifecycle():
    user_payload = {"sub": "testdoc", "role": "doctor"}
    token = auth_service.create_access_token(user_payload)
    
    decoded = auth_service.decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "testdoc"
    assert decoded["role"] == "doctor"
