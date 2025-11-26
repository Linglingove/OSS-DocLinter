================================================================================
OSS-DocLinter - 开源项目文档质量分析工具
================================================================================

[项目简介]
OSS-DocLinter 是一个旨在自动化评估开源项目文档质量的工具。
它通过扫描项目的 README、CONTRIBUTING 等核心文档，从“完整性”和“规范性”两个维度进行评分，
并利用大语言模型 (LLM) 提供具体的改进建议，甚至支持一键生成修复后的文档内容并提交 Pull Request。

[项目结构]
/OSS-DocLinter
  |-- frontend/          # 前端项目 (React + TypeScript + Vite)
  |-- backend/           # 后端项目 (Python + FastAPI) - *需根据设计文档实现*
  |-- requirements.txt   # 后端 Python 依赖列表
  |-- README.txt         # 本文件
  |-- README.md          # Markdown 格式的项目说明
  |-- ... (其他设计文档)

[快速开始]

1. 前端环境 (Frontend)
--------------------------------------------------------------------------------
前端位于 `frontend` 目录下。

依赖要求:
- Node.js (推荐 v16+)
- npm 或 yarn

安装与运行:
$ cd frontend
$ npm install          # 安装依赖
$ npm run dev          # 启动开发服务器

访问地址: http://localhost:5173 (默认)

2. 后端环境 (Backend)
--------------------------------------------------------------------------------
后端建议使用 Python 3.9+ 开发。

依赖安装:
$ pip install -r requirements.txt

运行方式 (假设后端入口为 main.py):
$ uvicorn main:app --reload

注意: 
- 后端服务默认应运行在 http://localhost:8000 以配合前端的代理配置。
- 您需要配置相应的环境变量 (如 OPENAI_API_KEY, GITHUB_TOKEN 等) 才能正常使用分析和 PR 功能。

[功能特性]
- 自动化文档扫描
- 完整性与规范性双重评估
- 基于 LLM 的智能改进建议
- 修复内容预览 (Diff View)
- 自动化 Pull Request 提交

[联系方式]
如有问题，请参考项目设计文档或联系开发者。
