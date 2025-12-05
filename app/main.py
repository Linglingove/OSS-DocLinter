from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analysis, auth, remediation

app = FastAPI(
    title="OSS-DOCLINTER API",
    description="API for analyzing and improving open source documentation",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(remediation.router, prefix="/api/v1", tags=["Remediation"])

@app.get("/")
async def root():
    return {"message": "OSS-DOCLINTER API is running"}