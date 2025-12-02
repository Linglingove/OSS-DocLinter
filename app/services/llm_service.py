import os
import httpx
from typing import Dict, List, Optional
from fastapi import HTTPException
import json

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"  # 或使用 deepseek-coder 针对代码文档
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_documentation_completeness(
        self, 
        files: Dict[str, Optional[Dict]]
    ) -> Dict:
        """
        分析文档完整性并打分
        
        Args:
            files: 从 GitHubService.fetch_repo_files() 获取的文件字典
        
        Returns:
            包含总分和详细问题的报告
        """
        # 准备文档内容
        readme_content = files.get("readme", {}).get("content", "") if files.get("readme") else ""
        contributing_content = files.get("contributing", {}).get("content", "") if files.get("contributing") else ""
        code_of_conduct_content = files.get("code_of_conduct", {}).get("content", "") if files.get("code_of_conduct") else ""
        license_content = files.get("license", {}).get("content", "") if files.get("license") else ""
        
        # 构建评测prompt
        prompt = self._build_completeness_prompt(
            readme_content,
            contributing_content,
            code_of_conduct_content,
            license_content
        )
        
        # 调用DeepSeek API
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是一个专业的开源项目文档评审专家，精通开源社区最佳实践。"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,  # 降低随机性，提高一致性
                        "response_format": {"type": "json_object"}
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"DeepSeek API error: {response.text}"
                    )
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 解析JSON响应
                analysis = json.loads(content)
                
                # 转换为标准报告格式
                return self._format_report(analysis, files)
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="LLM request timeout")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse LLM response: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")
    
    def _build_completeness_prompt(
        self,
        readme: str,
        contributing: str,
        code_of_conduct: str,
        license_info: str
    ) -> str:
        """构建完整性评测的Prompt"""
        
        return f"""请对以下开源项目文档进行完整性评测，总分70分，分为5个维度：
                **评分标准：**

                1. **安装与依赖指南 (20分)**
                - 是否清晰说明了安装方式（pip/npm/cargo等）？
                - 是否列出了系统依赖和前置条件？
                - 是否提供了多种安装方式（如源码安装、包管理器）？
                - 是否有版本兼容性说明？

                2. **快速上手/使用示例 (20分)**
                - 是否提供了最小可运行示例？
                - 示例代码是否完整可执行？
                - 是否涵盖了核心功能的演示？
                - 是否有进阶使用指南的链接？

                3. **贡献指南 (20分)**
                - 是否存在CONTRIBUTING.md文件？
                - 是否说明了如何提交Issue和PR？
                - 是否有开发环境搭建指南？
                - 是否有代码规范和测试要求？

                4. **行为准则 (5分)**
                - 是否存在CODE_OF_CONDUCT.md？
                - 内容是否明确社区行为规范？

                5. **许可证信息 (5分)**
                - 是否存在LICENSE文件？
                - 许可证类型是否清晰？

                ---

                **待评测文档：**

                ### README.md

                {readme if readme else "[文件不存在]"}

                ### CONTRIBUTING.md

                {contributing if contributing else "[文件不存在]"}

                ### CODE_OF_CONDUCT.md

                {code_of_conduct if code_of_conduct else "[文件不存在]"}

                ### LICENSE

                {license_info if license_info else "[文件不存在]"}

                ---


                ---

                **输出要求：**
                请以JSON格式返回评测结果，结构如下：

                ```json
                {{
                "overall_score": 65,
                "dimensions": [
                    {{
                    "name": "installation_guide",
                    "score": 15,
                    "max_score": 20,
                    "issues": [
                        {{
                        "id": "missing_install_command",
                        "severity": "high",
                        "description": "未提供具体的安装命令",
                        "suggestion": "建议添加 `pip install package-name` 等安装指令",
                        "file": "README.md"
                        }}
                    ]
                    }},
                    {{
                    "name": "quick_start",
                    "score": 18,
                    "max_score": 20,
                    "issues": [
                        {{
                        "id": "example_not_runnable",
                        "severity": "medium",
                        "description": "示例代码缺少import语句",
                        "suggestion": "建议补充完整的import声明",
                        "file": "README.md"
                        }}
                    ]
                    }},
                    {{
                    "name": "contributing_guide",
                    "score": 0,
                    "max_score": 20,
                    "issues": [
                        {{
                        "id": "missing_contributing",
                        "severity": "high",
                        "description": "缺失CONTRIBUTING.md文件",
                        "suggestion": "建议创建贡献指南，说明PR流程和开发规范",
                        "file": "CONTRIBUTING.md"
                        }}
                    ]
                    }},
                    {{
                    "name": "code_of_conduct",
                    "score": 5,
                    "max_score": 5,
                    "issues": []
                    }},
                    {{
                    "name": "license",
                    "score": 5,
                    "max_score": 5,
                    "issues": []
                    }}
                ]
                }}

                注意：

                - 每个维度必须给出具体扣分理由

                - issue的id使用snake_case命名

                - severity只能是：high/medium/low

                - 如果某个文件不存在，这是最高优先级的问题

                - 评分要客观严格，参考顶级开源项目标准
                """
    
    def _format_report(self, analysis: Dict, files: Dict) -> Dict: 
        issues = [] 
        overall_score = analysis.get("overall_score", 0)
        for dimension in analysis.get("dimensions", []): 
            for issue in dimension.get("issues", []): 
                issues.append({ "id": issue.get("id"),
                                "category": "completeness", 
                                "file": issue.get("file"), 
                                "severity": issue.get("severity"), 
                                "description": issue.get("description"), 
                                "suggestion": issue.get("suggestion"), 
                                "score_deduction": dimension.get("max_score", 0) - dimension.get("score", 0) })
        return { "overall_score": overall_score, "issues": issues, "raw_analysis": analysis }
    
