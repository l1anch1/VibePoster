"""
知识模块路由

职责：
1. Knowledge Graph API - 设计规则推理（通过 DesignRuleSkill）
2. RAG API - 品牌知识库管理（通过 BrandContextSkill + KnowledgeBase）

Author: VibePoster Team
Date: 2025-01
"""

from fastapi import APIRouter, Form
from typing import Optional

from ...core.exceptions import ValidationException, ServiceException
from ...core.dependencies import (
    get_knowledge_graph,
    get_knowledge_base,
    get_design_rule_skill,
    get_brand_context_skill,
)
from ...core.logger import logger
from ...models.response import (
    APIResponse,
    KGInferResult,
    BrandSearchResult,
    BrandUploadResult,
    StatsResult,
)
from ...skills import DesignRuleSkill, DesignRuleInput, BrandContextSkill, BrandContextInput

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
        
        knowledge_base = get_knowledge_base()
        
        doc_id = f"{brand_name}_{category}_{hash(text) % 10000}"
        metadata = {
            "brand": brand_name,
            "category": category,
            "type": "user_upload"
        }
        
        knowledge_base.add_document(text, metadata, doc_id)
        
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
) -> APIResponse[BrandSearchResult]:
    """
    检索品牌知识库
    
    参数说明：
    - **query**: 查询文本（如：华为的配色、苹果的设计风格）
    - **brand_name**: 品牌名称过滤（可选）
    - **top_k**: 返回结果数量（默认 3）
    """
    try:
        knowledge_base = get_knowledge_base()
        
        filter_metadata = {"brand": brand_name} if brand_name else None
        results = knowledge_base.search(query, top_k, filter_metadata)
        
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
async def get_brand_knowledge_stats() -> APIResponse[StatsResult]:
    """获取品牌知识库的统计信息"""
    try:
        knowledge_base = get_knowledge_base()
        stats = knowledge_base.get_stats()
        
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
# Knowledge Graph API（通过 DesignRuleSkill）
# ============================================================================

@router.get("/kg/infer", summary="Knowledge Graph 设计规则推理")
async def infer_design_rules(
    keywords: str,
) -> APIResponse[KGInferResult]:
    """
    根据关键词推理设计规则（通过 DesignRuleSkill）
    
    参数说明：
    - **keywords**: 逗号分隔的关键词列表（如：Tech,Minimalist）
    
    支持的关键词：
    - 行业：Tech, Food, Education, Fashion, Real Estate, Healthcare, Finance
    - 风格：Minimalist, Energetic, Luxury, Friendly, Professional, Bold
    """
    try:
        keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        
        if not keyword_list:
            raise ValidationException(
                message="关键词为空",
                detail={"detail": "请提供至少一个关键词"}
            )
        
        skill = get_design_rule_skill()
        
        # 拆分行业和风格关键词
        industry = keyword_list[0] if keyword_list else None
        vibe = keyword_list[1] if len(keyword_list) > 1 else None
        additional = keyword_list[2:] if len(keyword_list) > 2 else []
        
        result = skill(DesignRuleInput(
            industry=industry,
            vibe=vibe,
            additional_keywords=additional
        ))
        
        rules = result.output.to_dict() if result.output else {}
        
        logger.info(f"🔮 KG 推理: {keyword_list} -> emotions={rules.get('emotions', [])}")
        
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
async def get_kg_stats() -> APIResponse[StatsResult]:
    """获取 Knowledge Graph 的统计信息"""
    try:
        knowledge_graph = get_knowledge_graph()
        stats = knowledge_graph.get_graph_stats()
        
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
