import httpx
from typing import Optional
from fastapi import HTTPException
from app.services.llm_service import LLMService

class RemediationService:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.llm_service = LLMService()
        self.headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def generate_fix(
        self,
        original_content: str,
        issue_id: str,
        custom_instruction: Optional[str] = None
    ) -> str:
        """
        生成修复后的文档
        """
        # issue_id 到描述的映射 (简化版，后续可以从数据库获取)
        issue_descriptions = {
            "missing_readme": "文档缺失 README 文件",
            "missing_install": "缺失安装指南",
            "missing_usage": "缺失使用说明",
            "missing_contributing": "缺失贡献指南",
            "missing_license": "缺失许可证信息",
            "missing_security": "缺失安全策略",
            "missing_changelog": "缺失变更日志",
        }
        
        description = issue_descriptions.get(issue_id, f"文档问题: {issue_id}")
        
        return await self.llm_service.generate_fix(
            original_content=original_content,
            issue_id=issue_id,
            issue_description=description,
            custom_instruction=custom_instruction
        )
    
    async def create_pull_request(
        self,
        target_owner: str,
        target_repo: str,
        file_path: str,
        final_content: str,
        commit_message: str,
        pr_title: str
    ) -> dict:
        """
        执行 Fork -> Branch -> Commit -> PR 流程
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. 获取当前用户信息
            user_resp = await client.get(
                "https://api.github.com/user",
                headers=self.headers
            )
            if user_resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid GitHub token")
            
            current_user = user_resp.json()["login"]
            
            # 2. Fork 仓库 (如果已 fork 会返回已有的 fork)
            fork_resp = await client.post(
                f"https://api.github.com/repos/{target_owner}/{target_repo}/forks",
                headers=self.headers
            )
            
            if fork_resp.status_code not in [200, 202]:
                raise HTTPException(status_code=400, detail="Failed to fork repository")
            
            # 等待 fork 完成 (GitHub fork 是异步的)
            import asyncio
            await asyncio.sleep(2)
            
            # 3. 获取目标仓库的默认分支
            repo_resp = await client.get(
                f"https://api.github.com/repos/{target_owner}/{target_repo}",
                headers=self.headers
            )
            default_branch = repo_resp.json()["default_branch"]
            
            # 4. 获取默认分支的最新 commit SHA
            ref_resp = await client.get(
                f"https://api.github.com/repos/{current_user}/{target_repo}/git/refs/heads/{default_branch}",
                headers=self.headers
            )

            if ref_resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get branch reference")
            
            base_sha = ref_resp.json()["object"]["sha"]
            
            # 5. 创建新分支
            import time
            branch_name = f"docs/fix-{int(time.time())}"
            
            create_branch_resp = await client.post(
                f"https://api.github.com/repos/{current_user}/{target_repo}/git/refs",
                headers=self.headers,
                json={
                    "ref": f"refs/heads/{branch_name}",
                    "sha": base_sha
                }
            )
            
            if create_branch_resp.status_code != 201:
                raise HTTPException(status_code=400, detail="Failed to create branch")
            
            # 6. 获取文件当前 SHA (如果存在)
            file_sha = None
            file_resp = await client.get(
                f"https://api.github.com/repos/{current_user}/{target_repo}/contents/{file_path}?ref={branch_name}",
                headers=self.headers
            )
            if file_resp.status_code == 200:
                file_sha = file_resp.json()["sha"]
            
            # 7. 创建或更新文件
            import base64
            content_base64 = base64.b64encode(final_content.encode()).decode()
            
            update_payload = {
                "message": commit_message,
                "content": content_base64,
                "branch": branch_name
            }
            if file_sha:
                update_payload["sha"] = file_sha
            
            update_resp = await client.put(
                f"https://api.github.com/repos/{current_user}/{target_repo}/contents/{file_path}",
                headers=self.headers,
                json=update_payload
            )
            
            if update_resp.status_code not in [200, 201]:
                raise HTTPException(status_code=400, detail="Failed to update file")
            
            # 8. 创建 Pull Request
            pr_resp = await client.post(
                f"https://api.github.com/repos/{target_owner}/{target_repo}/pulls",
                headers=self.headers,
                json={
                    "title": pr_title,
                    "head": f"{current_user}:{branch_name}",
                    "base": default_branch,
                    "body": "This PR was automatically generated by OSS-DocLinter to improve documentation quality."
                }
            )
            
            if pr_resp.status_code != 201:
                raise HTTPException(status_code=400, detail="Failed to create pull request")
            
            pr_data = pr_resp.json()
            
            return {
                "pr_url": pr_data["html_url"],
                "status": "success",
                "message": "Pull Request created successfully"
            }