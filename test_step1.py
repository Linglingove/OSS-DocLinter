import asyncio
from app.services.github_service import GitHubService

async def main():
    service = GitHubService()
    
    url = "https://github.com/fastapi/fastapi"
    owner, repo = service.parse_github_url(url)
    print(f"解析结果: Owner={owner}, Repo={repo}")
    
    metadata = await service.get_repo_metadata(owner, repo)
    print(f"仓库默认分支: {metadata.get('default_branch')}")

    print(f"正在扫描 {owner}/{repo} 的文件...")
    files = await service.fetch_repo_files(owner, repo)
    
    for key, file_data in files.items():
        if file_data:
            print(f"[√] {key}: 找到 ({file_data['path']}) - 长度: {len(file_data['content'])}")
        else:
            print(f"[x] {key}: 未找到")

if __name__ == "__main__":
    asyncio.run(main())