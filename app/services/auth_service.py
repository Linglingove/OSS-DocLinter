import httpx
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.config import settings

class AuthService:
    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_API = "https://api.github.com/user"

    def get_login_url(self) -> str:
        """
        生成 GitHub OAuth 登录链接
        """
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": "public_repo read:user", # 需要的权限
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.GITHUB_AUTH_URL}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """
        用 GitHub 返回的 code 换取 access_token
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.GITHUB_TOKEN_URL,
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.GITHUB_REDIRECT_URI,
                },
                headers={"Accept": "application/json"}
            )
            
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            data = resp.json()
            if "error" in data:
                raise HTTPException(status_code=400, detail=data.get("error_description", "OAuth error"))
            
            return data # 包含 access_token, token_type, scope

    async def get_github_user(self, github_token: str) -> dict:
        """
        使用 GitHub Token 获取用户信息
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self.GITHUB_USER_API,
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid GitHub token")
            
            return resp.json()

    def create_jwt(self, github_token: str, username: str) -> str:
        """
        创建应用侧的 JWT，内嵌 GitHub Token
        """
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
        payload = {
            "sub": username, # subject: 用户标识
            "github_token": github_token, # 存储 GitHub Token 以便后续调用 GitHub API
            "exp": expire
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_jwt(self, token: str) -> dict:
        """
        解码并验证 JWT
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")