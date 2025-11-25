from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict
from enum import Enum

# --- 通用枚举 ---
class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IssueCategory(str, Enum):
    COMPLETENESS = "completeness"
    FORMAT = "format"

# --- 1. Analyze 模块模型 ---

class AnalyzeRequest(BaseModel):
    url: HttpUrl = Field(..., description="开源项目的 GitHub URL")

class RepoInfo(BaseModel):
    owner: str
    repo: str
    default_branch: str
    url: HttpUrl

class FileContent(BaseModel):
    path: str
    content: Optional[str] = None # 如果文件不存在则为 None

class HealthCheck(BaseModel):
    has_readme: bool
    has_contributing: bool
    has_license: bool
    has_code_of_conduct: bool
    has_security_policy: bool
    has_changelog: bool

class Issue(BaseModel):
    id: str
    category: IssueCategory
    file: str
    severity: Severity
    description: str
    suggestion: str
    line_number: Optional[int] = None
    score_deduction: int

class Report(BaseModel):
    overall_score: int
    timestamp: str
    issues: List[Issue]

class AnalyzeResponse(BaseModel):
    repo_info: RepoInfo
    # key 是文件标识 (如 'readme', 'security')，value 是文件详情
    files: Dict[str, FileContent] 
    health_check: HealthCheck
    report: Report

# --- 2. Auth 模块模型 ---

class LoginUrlResponse(BaseModel):
    login_url: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserProfile(BaseModel):
    username: str
    avatar_url: HttpUrl
    github_profile: HttpUrl

# --- 3. Remediation (修复) 模块模型 ---

class FixRequest(BaseModel):
    repo_owner: str
    repo_name: str
    file_path: str
    original_content: str = Field(..., description="前端回传的原始文件内容")
    issue_id: str
    custom_instruction: Optional[str] = None

class FixResponse(BaseModel):
    file_path: str
    fixed_content: str

# --- 4. PR 提交模块模型 ---

class PRRequest(BaseModel):
    target_owner: str
    target_repo: str
    file_path: str
    final_content: str = Field(..., description="用户确认后的最终内容")
    commit_message: Optional[str] = "docs: improve documentation via oss-doclinter"
    pr_title: Optional[str] = "Docs: Improve documentation completeness"

class PRResponse(BaseModel):
    pr_url: HttpUrl
    status: str
    message: str