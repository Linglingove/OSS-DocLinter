from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas import LoginUrlResponse, TokenResponse, UserProfile
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter()
security = HTTPBearer()

@router.get("/auth/login", response_model=LoginUrlResponse)
async def get_login_url():
    """
    获取 GitHub OAuth 登录链接
    """
    service = AuthService()
    return LoginUrlResponse(login_url=service.get_login_url())

@router.get("/auth/callback", response_model=TokenResponse)
async def auth_callback(code: str = Query(..., description="GitHub 返回的授权码")):
    """
    处理 GitHub OAuth 回调，交换 Token
    """
    service = AuthService()
    
    # 1. 用 code 换 GitHub Token
    token_data = await service.exchange_code_for_token(code)
    github_token = token_data["access_token"]
    
    # 2. 获取用户信息
    user_info = await service.get_github_user(github_token)
    username = user_info["login"]
    
    # 3. 生成应用侧 JWT
    app_token = service.create_jwt(github_token, username)
    
    return TokenResponse(
        access_token=app_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_HOURS * 3600
    )

@router.get("/users/me", response_model=UserProfile)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    获取当前登录用户信息
    """
    service = AuthService()
    
    # 1. 解码 JWT
    payload = service.decode_jwt(credentials.credentials)
    github_token = payload.get("github_token")
    
    if not github_token:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # 2. 用 GitHub Token 获取最新用户信息
    user_info = await service.get_github_user(github_token)
    
    return UserProfile(
        username=user_info["login"],
        avatar_url=user_info["avatar_url"],
        github_profile=user_info["html_url"]
    )