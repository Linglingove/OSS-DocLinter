from datetime import datetime, timezone
from app.schemas import (
    AnalyzeResponse, RepoInfo, FileContent, HealthCheck, Report, Issue,
    Severity, IssueCategory
)
from app.services.github_service import GitHubService
from app.services.llm_service import LLMService

class AnalysisService:
    def __init__(self):
        self.github_service = GitHubService()
        self.llm_service = LLMService()

    async def analyze_repo(self, url: str) -> AnalyzeResponse:
        # 1. 解析 URL
        owner, repo = self.github_service.parse_github_url(url)
        
        # 2. 获取仓库元数据
        repo_meta = await self.github_service.get_repo_metadata(owner, repo)
        
        # 3. 获取文档文件
        files_data = await self.github_service.fetch_repo_files(owner, repo)
        
        # 4. 构建 RepoInfo
        repo_info = RepoInfo(
            owner=repo_meta["owner"]["login"],
            repo=repo_meta["name"],
            default_branch=repo_meta["default_branch"],
            url=repo_meta["html_url"]
        )
        
        # 5. 构建 Files 响应 (供前端暂存，用于后续修复回传)
        files_response = {}
        for key, data in files_data.items():
            if data:
                files_response[key] = FileContent(path=data["path"], content=data["content"])
            else:
                files_response[key] = FileContent(path=f"{key.upper()}.md", content=None)

        # 6. 执行 Health Check (存在性检查)
        health_check = HealthCheck(
            has_readme=files_data.get("readme") is not None,
            has_contributing=files_data.get("contributing") is not None,
            has_license=files_data.get("license") is not None,
            has_code_of_conduct=files_data.get("code_of_conduct") is not None,
            has_security_policy=files_data.get("security") is not None,
            has_changelog=files_data.get("changelog") is not None
        )

        # 7. 调用 LLM 进行文档完整性分析
        llm_report = await self.llm_service.analyze_documentation_completeness(files_data)
        
        # 8. 转换 issues 格式
        issues = self._convert_issues(llm_report.get("issues", []))
        
        # 9. 补充存在性检查的 issues (LLM 可能已经包含，这里做兜底)
        issues = self._add_health_check_issues(issues, health_check)

        # 10. 组装最终响应
        return AnalyzeResponse(
            repo_info=repo_info,
            files=files_response,
            health_check=health_check,
            report=Report(
                overall_score=max(0, min(100, llm_report.get("overall_score", 0))),
                timestamp=datetime.now(timezone.utc).isoformat(),
                issues=issues
            )
        )

    def _convert_issues(self, raw_issues: list) -> list[Issue]:
        """
        将 LLM 返回的 issues 转换为 Schema 定义的 Issue 对象
        """
        issues = []
        for raw in raw_issues:
            # 映射 severity
            severity_map = {
                "high": Severity.HIGH,
                "medium": Severity.MEDIUM,
                "low": Severity.LOW,
                "critical": Severity.CRITICAL
            }
            severity = severity_map.get(raw.get("severity", "medium"), Severity.MEDIUM)
            
            issues.append(Issue(
                id=raw.get("id", "unknown_issue"),
                category=IssueCategory.COMPLETENESS,
                file=raw.get("file", "README.md"),
                severity=severity,
                description=raw.get("description", ""),
                suggestion=raw.get("suggestion", ""),
                line_number=raw.get("line_number"),
                score_deduction=raw.get("score_deduction", 0)
            ))
        
        return issues

    def _add_health_check_issues(self, issues: list[Issue], health_check: HealthCheck) -> list[Issue]:
        """
        根据 health_check 结果补充缺失文件的 issues
        避免重复添加 (检查是否已存在相同 id)
        """
        existing_ids = {issue.id for issue in issues}
        
        # 定义缺失文件的 issue 模板
        missing_file_issues = [
            {
                "check": not health_check.has_security_policy,
                "id": "missing_security",
                "file": "SECURITY.md",
                "severity": Severity.MEDIUM,
                "description": "缺失安全策略文件",
                "suggestion": "建议添加 SECURITY.md 说明漏洞上报流程",
                "score_deduction": 5
            },
            {
                "check": not health_check.has_changelog,
                "id": "missing_changelog",
                "file": "CHANGELOG.md",
                "severity": Severity.LOW,
                "description": "缺失变更日志文件",
                "suggestion": "建议添加 CHANGELOG.md 记录版本变更历史",
                "score_deduction": 5
            }
        ]
        
        for item in missing_file_issues:
            if item["check"] and item["id"] not in existing_ids:
                issues.append(Issue(
                    id=item["id"],
                    category=IssueCategory.COMPLETENESS,
                    file=item["file"],
                    severity=item["severity"],
                    description=item["description"],
                    suggestion=item["suggestion"],
                    score_deduction=item["score_deduction"]
                ))
        
        return issues