import uvicorn
import time
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, records, extraction, qa, audit
from .config.settings import settings
from .services.auth_service import auth_service

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="HIPAA-compliant backend for MedicalRAG Assistant",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter Store (In-Memory)
# Maps user (IP or Username) to list of request timestamps
rate_limit_store = {}

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    # Determine identifier (username from authorization header or fallback to client IP)
    auth_header = request.headers.get("Authorization")
    identifier = request.client.host
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = auth_service.decode_token(token)
        if payload and "sub" in payload:
            identifier = payload["sub"]

    # Limit path exceptions (e.g. docs, health check)
    if request.url.path in ["/", "/docs", "/openapi.json"]:
        return await call_next(request)

    current_time = time.time()
    
    # Initialize request list
    if identifier not in rate_limit_store:
        rate_limit_store[identifier] = []
        
    # Filter timestamps older than 60 seconds
    rate_limit_store[identifier] = [t for t in rate_limit_store[identifier] if current_time - t < 60]
    
    # Check rate limit (10 requests per minute)
    if len(rate_limit_store[identifier]) >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 requests per minute per user allowed."
        )
        
    rate_limit_store[identifier].append(current_time)
    
    response = await call_next(request)
    return response

# Include Routers
app.include_router(auth.router)
app.include_router(records.router)
app.include_router(extraction.router)
app.include_router(qa.router)
app.include_router(audit.router)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "security": "PII AES-256 Encrypted",
        "api_docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
