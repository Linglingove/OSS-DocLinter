from fastapi import APIRouter, HTTPException
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repository(request: AnalyzeRequest):
    """
    分析 GitHub 仓库的文档质量
    
    - 获取仓库的关键文档文件 (README, CONTRIBUTING, LICENSE 等)
    - 执行存在性检查
    - 生成质量报告和改进建议
    """
    service = AnalysisService()
    try:
        return await service.analyze_repo(str(request.url))
    except HTTPException:
        # 已知的 HTTP 异常直接抛出
        raise
    except Exception as e:
        # 未知异常包装为 500 错误
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")