from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas import FixRequest, FixResponse, PRRequest, PRResponse
from app.services.remediation_service import RemediationService
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()

def get_github_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    从 JWT 中提取 GitHub Token
    """
    auth_service = AuthService()
    payload = auth_service.decode_jwt(credentials.credentials)
    github_token = payload.get("github_token")
    
    if not github_token:
        raise HTTPException(status_code=401, detail="Invalid token: missing GitHub token")
    
    return github_token

@router.post("/fix/generate", response_model=FixResponse)
async def generate_fix(
    request: FixRequest,
    github_token: str = Depends(get_github_token)
):
    """
    使用 LLM 生成修复后的文档
    """
    service = RemediationService(github_token)
    
    fixed_content = await service.generate_fix(
        original_content=request.original_content,
        issue_id=request.issue_id,
        custom_instruction=request.custom_instruction
    )
    
    return FixResponse(
        file_path=request.file_path,
        fixed_content=fixed_content
    )

@router.post("/pr/create", response_model=PRResponse)
async def create_pull_request(
    request: PRRequest,
    github_token: str = Depends(get_github_token)
):
    """
    自动创建 Pull Request
    """
    service = RemediationService(github_token)
    
    result = await service.create_pull_request(
        target_owner=request.target_owner,
        target_repo=request.target_repo,
        file_path=request.file_path,
        final_content=request.final_content,
        commit_message=request.commit_message or "docs: improve documentation via oss-doclinter",
        pr_title=request.pr_title or "Docs: Improve documentation completeness"
    )
    
    return PRResponse(
        pr_url=result["pr_url"],
        status=result["status"],
        message=result["message"]
    )