# OSS-DOCLINTER API 详细设计

## 1. 核心分析模块

### 1.1 分析仓库文档

**Endpoint:**`POST /api/v1/analyze`

**描述:**应用主入口，后端并行获取文档、运行Linter和LLM分析，返回文档的原始内容给前端暂存。

**Request Body:**

```
{
    "url": "https://github.com/fastapi/fastapi"
}

```

**Response Body(200 OK):**

```
{
  "repo_info": {
    "owner": "fastapi",
    "repo": "fastapi",
    "default_branch": "master",
    "url": "https://github.com/fastapi/fastapi"
  },
  "files": {
    // 前端需保存此对象，用于后续 /fix/generate 请求的回传
    "README.md": "raw content string of readme...",
    "CONTRIBUTING.md": "raw content string..."
  },
  "report": {
    "overall_score": 85,
    "timestamp": "2023-10-27T10:00:00Z",
    "issues": [
      {
        "id": "missing_install", // 唯一标识，用于后续修复时指定问题类型
        "category": "completeness", // completeness 或 format
        "file": "README.md",
        "severity": "high",
        "description": "缺失安装指南",
        "suggestion": "建议添加 pip install 命令...",
        "score_deduction": 20
      },
      {
        "id": "md001",
        "category": "format",
        "file": "README.md",
        "severity": "low",
        "description": "标题层级错误",
        "suggestion": "H2 后直接使用了 H4",
        "line_number": 45,
        "score_deduction": 5
      }
    ]
  }
}
```

## 2. 用户认证模块

### 2.1 获取GitHub登录链接

**Endpoint:** `GET /api/v1/auth/login

**描述:** 前端点击登录时调用，后端生成GitHub OAuth跳转链接

**Response Body(200 OK):**

```
{
  "login_url": "https://github.com/login/oauth/authorize?client_id=...&scope=public_repo&redirect_uri=..."
}
```

### 2.2 OAuth回调与Token交换

**Endpoint:** `GET /api/v1/auth/callback`

**描述:** GitHub重定向回前端后，前端提取URL中的`code`参数调用此接口。后端交换GitHub Token，并生成应用自身的JWT返回

**Query Parameters:**

`code`: GitHub返回的授权码

**Response Body (200 OK):**

```
{
  "access_token": "eyJhbGciOiJIUzI1Ni...", // 应用侧 JWT
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 2.3 获取当前用户信息

**Endpoint:** `GET /api/v1/users/me`

**描述:** 用于前端展示当前登录用户，需要携带Bearer Token

**Headers:**

`Authorization`: `Bearer <access_token>`

**Response Body(200 OK):**

```
{
  "username": "octocat",
  "avatar_url": "https://avatars.githubusercontent.com/u/...",
  "github_profile": "https://github.com/octocat"
}
```

## 3. 修复与交付模块

### 3.1 生成修复内容

**Endpoint:** `POST /api/v1/fix/generate`

**描述:** 用户点击修复按钮时调用，后端利用LLM基于原文档和问题类型生成修复后的完整文档，后端无状态，通过前端传入`original_content`

**Headers:**

`Authorization`: `Bearer <access_token>`

**Request Body:**

```
{
  "repo_owner": "fastapi",
  "repo_name": "fastapi",
  "file_path": "README.md",
  "original_content": "raw content string of readme...", // 必填：来自 /analyze 的响应
  "issue_id": "missing_install", // 必填：来自 /analyze 的 issues.id
  "custom_instruction": "请使用 poetry 作为包管理器" // 可选：用户的高级指令
}
```

**Response Body(200 OK):**

```
{
  "file_path": "README.md",
  "fixed_content": "raw content string with fixes applied..." // 包含修复内容的完整文档
}
```

*前端拿到fixed_content后，结合本地的original_content使用vue-diff进行对比展示*

### 3.2 提交PR

**Endpoint:** `POST /api/v1/pr/create`

**描述:** 用户在Diff确认无误后调用。后端执行Fork->Branch->Commit->PR的全流程

**Headers:**

`Authorization`: `Bearer <access_token>`

**Request Body:**

```
{
  "target_owner": "fastapi", // 源仓库 Owner
  "target_repo": "fastapi",  // 源仓库 Name
  "file_path": "README.md",
  "final_content": "raw content string...", // 用户确认后的最终内容
  "commit_message": "docs: add installation guide via oss-doclinter", // 可选，后端可设默认值
  "pr_title": "Docs: Improve README completeness" // 可选
}
```

**Response Body(201 Created):**

```
{
  "pr_url": "https://github.com/fastapi/fastapi/pull/123",
  "status": "success",
  "message": "Pull Request created successfully"
}
```

## 4. 错误处理标准

所有接口发生错误的时候返回统一的错误结构:

**Response Body(4xx/5xx):**

```
{
  "detail": "GitHub API rate limit exceeded", // 错误描述
  "code": "RATE_LIMIT_ERROR" // 错误码，便于前端判断
}
```