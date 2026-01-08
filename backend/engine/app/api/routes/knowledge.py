"""
知识模块路由

职责：
1. Knowledge Graph API - 设计规则推理
2. RAG API - 品牌知识库管理

Author: VibePoster Team
Date: 2025-01
"""

from fastapi import APIRouter, Form, Depends
from typing import Optional

from ...services.knowledge_service import KnowledgeService
from ...core.exceptions import ValidationException, ServiceException
from ...core.dependencies import get_knowledge_service
from ...core.logger import logger
from ...models.response import (
    APIResponse,
    KGInferResult,
    BrandSearchResult,
    BrandUploadResult,
    StatsResult,
)

# 创建路由实例
router = APIRouter(prefix="/api", tags=["knowledge"])


# ============================================================================
# 品牌知识库 API（RAG）
# ============================================================================

@router.post("/brand/upload", summary="上传企业品牌文档")
async def upload_brand_document(
    text: str = Form(..., description="品牌规范文本内容"),
    brand_name: str = Form(..., description="品牌名称"),
    category: str = Form(default="通用", description="文档类别"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> APIResponse[BrandUploadResult]:
    """
    上传企业品牌文档到 RAG 知识库
    
    参数说明：
    - **text**: 品牌规范文本内容
    - **brand_name**: 品牌名称（如：华为、小米、苹果）
    - **category**: 文档类别（配色方案/设计风格/字体规范/品牌口号）
    """
    try:
        if not text.strip():
            raise ValidationException(
                message="文档内容为空",
                detail={"detail": "请提供品牌规范内容"}
            )
        
        doc_id = knowledge_service.add_brand_document(
            text=text,
            brand_name=brand_name,
            category=category
        )
        
        logger.info(f"📚 品牌文档上传成功: {brand_name} - {category}")
        
        return APIResponse(
            success=True,
            data=BrandUploadResult(
                doc_id=doc_id,
                brand_name=brand_name,
                category=category,
                text_length=len(text)
            ),
            message=f"品牌文档上传成功"
        )
    
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"品牌文档上传失败: {e}", exc_info=True)
        raise ServiceException(
            message="品牌文档上传失败",
            detail={"detail": str(e)}
        )


@router.get("/brand/search", summary="检索品牌知识")
async def search_brand_knowledge(
    query: str,
    brand_name: Optional[str] = None,
    top_k: int = 3,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> APIResponse[BrandSearchResult]:
    """
    检索品牌知识库
    
    参数说明：
    - **query**: 查询文本（如：华为的配色、苹果的设计风格）
    - **brand_name**: 品牌名称过滤（可选）
    - **top_k**: 返回结果数量（默认 3）
    """
    try:
        results = knowledge_service.search_brand_knowledge(
            query=query,
            brand_name=brand_name,
            top_k=top_k
        )
        
        logger.info(f"📚 品牌知识检索: '{query}' -> 找到 {len(results)} 条结果")
        
        return APIResponse(
            success=True,
            data=BrandSearchResult(
                query=query,
                results=results,
                count=len(results)
            ),
            message=f"找到 {len(results)} 条相关知识"
        )
    
    except Exception as e:
        logger.error(f"品牌知识检索失败: {e}", exc_info=True)
        raise ServiceException(
            message="品牌知识检索失败",
            detail={"detail": str(e)}
        )


@router.get("/brand/stats", summary="获取品牌知识库统计信息")
async def get_brand_knowledge_stats(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> APIResponse[StatsResult]:
    """获取品牌知识库的统计信息"""
    try:
        stats = knowledge_service.get_kb_stats()
        
        return APIResponse(
            success=True,
            data=StatsResult(**stats),
            message="知识库统计信息获取成功"
        )
    
    except Exception as e:
        logger.error(f"获取知识库统计失败: {e}", exc_info=True)
        raise ServiceException(
            message="获取知识库统计失败",
            detail={"detail": str(e)}
        )


# ============================================================================
# Knowledge Graph API
# ============================================================================

@router.get("/kg/infer", summary="Knowledge Graph 设计规则推理")
async def infer_design_rules(
    keywords: str,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> APIResponse[KGInferResult]:
    """
    根据关键词推理设计规则
    
    参数说明：
    - **keywords**: 逗号分隔的关键词列表（如：Tech,Promotion）
    
    支持的关键词：
    - 行业：Tech, Food, Education, Fashion, Real Estate, Healthcare, Finance
    - 氛围：Minimalist, Energetic, Luxury, Friendly, Professional, Promotion
    """
    try:
        keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        
        if not keyword_list:
            raise ValidationException(
                message="关键词为空",
                detail={"detail": "请提供至少一个关键词"}
            )
        
        rules = knowledge_service.infer_design_rules(keyword_list)
        
        logger.info(f"🔮 KG 推理: {keyword_list} -> {rules}")
        
        return APIResponse(
            success=True,
            data=KGInferResult(
                keywords=keyword_list,
                rules=rules
            ),
            message="设计规则推理完成"
        )
    
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"KG 推理失败: {e}", exc_info=True)
        raise ServiceException(
            message="设计规则推理失败",
            detail={"detail": str(e)}
        )


@router.get("/kg/stats", summary="获取 Knowledge Graph 统计信息")
async def get_kg_stats(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> APIResponse[StatsResult]:
    """获取 Knowledge Graph 的统计信息"""
    try:
        stats = knowledge_service.get_kg_stats()
        
        return APIResponse(
            success=True,
            data=StatsResult(**stats),
            message="Knowledge Graph 统计信息获取成功"
        )
    
    except Exception as e:
        logger.error(f"获取 KG 统计失败: {e}", exc_info=True)
        raise ServiceException(
            message="获取 KG 统计失败",
            detail={"detail": str(e)}
        )

