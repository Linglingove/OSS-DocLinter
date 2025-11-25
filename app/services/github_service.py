import httpx
import os
import re
from fastapi import HTTPException
import asyncio

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    @staticmethod
    def parse_github_url(url: str) -> tuple[str, str]:
        clean_url = url.removesuffix(".git")
        
        clean_url = clean_url.rstrip("/")
        
        pattern = r"github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, clean_url)
        
        if not match:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL format")
        
        return match.group(1), match.group(2)
    
    async def get_repo_metadata(self, owner: str, repo: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=self.headers
            )

            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Repository not found")
            elif resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="GitHub API error")
            
            return resp.json()
        
    async def _fetch_single_file(self, client: httpx.AsyncClient, owner: str, repo: str, path: str) -> dict | None:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        try:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                download_url = data.get("download_url")
                if download_url:
                    content_resp = await client.get(download_url)
                    return {"path": path, "content": content_resp.text}
        except Exception:
            return None
    
    async def fetch_repo_files(self, owner: str, repo: str) -> dict:
        targets = {
            "readme": ["README.md", "readme.md", "README.rst", "README.txt"],
            "contributing": ["CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"],
            "license": ["LICENSE", "LICENSE.txt", "COPYING"],
            "code_of_conduct": ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"],
            "security": ["SECURITY.md", ".github/SECURITY.md"],
            "changelog": ["CHANGELOG.md", "HISTORY.md", "RELEASES.md"]
        }

        results = {}

        async with httpx.AsyncClient() as client:
            tasks = []
            target_keys = []

            for key, paths in targets.items():
                for path in paths:
                    tasks.append(self._fetch_single_file(client, owner, repo, path))
                    target_keys.append((key, path))

            responses = await asyncio.gather(*tasks)

            found_files = {key: [] for key in targets}

            for i, resp in enumerate(responses):
                if resp:
                    key, _ = target_keys[i]
                    found_files[key].append(resp)

            for key, files in found_files.items():
                if files:
                    results[key] = files[0]
                else:
                    results[key] = None
            
        return results
    