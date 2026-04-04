"""
分步生成路由 — 人机协作的可控生成流水线

Step 1: /api/step/plan     — 意图理解，返回设计简报供用户编辑
Step 2: /api/step/assets   — 素材搜索，返回多张候选背景图（及主体素材）供用户选择
Step 3: /api/step/layouts  — 版式生成 + 双路审核，仅返回通过审核的版式
Step 4: /api/step/finalize — 确认选择，直接返回（已审核通过）
"""

import asyncio
import json
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel, Field

from ...agents.planner import run_planner_agent
from ...agents.layout import run_layout_agent
from ...agents.critic import run_critic_agent
from ...models.design_brief import DesignBrief, AssetLayer, AssetList
from ...core.logger import get_logger

logger = get_logger(__name__)


def _quick_validate_layout(poster_data: Dict[str, Any]) -> Optional[str]:
    """
    快速结构校验（无 LLM，纯规则），返回 None 表示通过，否则返回问题描述。
    用于 Step 3 预过滤，在展示给用户之前剔除明显有问题的布局。
    """
    layers = poster_data.get("layers", [])
    canvas = poster_data.get("canvas", {})
    cw = canvas.get("width", 1080)
    ch = canvas.get("height", 1920)

    if not layers:
        return "无图层"

    has_text = False
    for layer in layers:
        w = layer.get("width", 0)
        h = layer.get("height", 0)
        if w <= 0 or h <= 0:
            return f"图层 {layer.get('id', '?')} 尺寸无效 ({w}x{h})"

        if layer.get("type") == "text":
            has_text = True
            x = layer.get("x", 0)
            y = layer.get("y", 0)
            if x + w > cw + 80 or y + h > ch + 80:
                return f"文字 '{layer.get('content', '')[:10]}' 严重溢出画布"
            if x < -40 or y < -40:
                return f"文字 '{layer.get('content', '')[:10]}' 位于画布外"

    if not has_text:
        return "缺少文字图层"

    return None

router = APIRouter(prefix="/api/step", tags=["step-by-step"])


# ============================================================================
# Step 1: 意图理解
# ============================================================================

class PlanRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    canvas_width: int = Field(default=1080, ge=100, le=10000)
    canvas_height: int = Field(default=1920, ge=100, le=10000)
    brand_name: Optional[str] = None


@router.post("/plan")
async def step_plan(req: PlanRequest):
    """
    Step 1: 运行 Planner Agent，返回设计简报供用户审阅/编辑。
    """
    logger.info(f"📋 [Step 1] 意图理解: {req.prompt[:60]}...")

    design_brief = run_planner_agent(
        user_prompt=req.prompt,
        brand_name=req.brand_name,
    )

    design_brief["user_prompt"] = req.prompt
    design_brief["canvas_width"] = req.canvas_width
    design_brief["canvas_height"] = req.canvas_height

    return {
        "step": "plan",
        "design_brief": design_brief,
    }


# ============================================================================
# Step 2: 素材选择
# ============================================================================

@router.post("/assets")
async def step_assets(
    design_brief_json: str = Form(..., description="设计简报 JSON 字符串"),
    canvas_width: int = Form(default=1080),
    canvas_height: int = Form(default=1920),
    count: int = Form(default=3),
    image_bg: Optional[UploadFile] = File(None),
    image_subject: Optional[UploadFile] = File(None),
):
    """
    Step 2: 根据设计简报搜索/生成多张候选背景图。

    三种模式：
    - Text Only:       无图 → 直接搜索/生成背景
    - Style Reference:  image_bg（无 image_subject）→ 分析风格后搜索/生成匹配的新背景
    - With Material:    image_subject（必选）+ image_bg（可选）→ 直接使用主体素材；
                        若有 image_bg 则直接作为背景，否则搜索/生成背景
    """
    from ...services.asset_service import AssetService

    design_brief = json.loads(design_brief_json)
    logger.info(f"🎨 [Step 2] 素材搜索，候选数: {count}")

    service = AssetService()
    has_subject = image_subject is not None
    has_bg = image_bg is not None

    if has_subject:
        subject_bytes = await image_subject.read()
        bg_bytes = (await image_bg.read()) if has_bg else None
        result = service.process_with_material(
            design_brief=design_brief,
            subject_bytes=subject_bytes,
            bg_bytes=bg_bytes,
            count=count,
            user_prompt=design_brief.get("user_prompt", ""),
        )
    elif has_bg:
        bg_bytes = await image_bg.read()
        result = service.process_style_reference(
            design_brief=design_brief,
            bg_bytes=bg_bytes,
            count=count,
        )
    else:
        result = service.process_text_only(
            design_brief=design_brief,
            count=count,
        )

    return {"step": "assets", **result.model_dump(exclude_none=True)}


# ============================================================================
# Step 3: 版式选择
# ============================================================================

class LayoutsRequest(BaseModel):
    design_brief: DesignBrief
    selected_asset_url: str = Field(..., description="用户选中的背景图 URL/base64")
    subject_asset_url: Optional[str] = Field(None, description="主体素材（透明 PNG）")
    subject_width: Optional[int] = Field(None, description="主体素材原始宽度")
    subject_height: Optional[int] = Field(None, description="主体素材原始高度")
    canvas_width: int = Field(default=1080)
    canvas_height: int = Field(default=1920)
    count: int = Field(default=6, ge=1, le=10)
    image_analyses: Optional[List[Dict[str, Any]]] = Field(None, description="图像分析结果")
    color_suggestions: Optional[Dict[str, Any]] = Field(None, description="配色建议")


_STYLE_HINTS = [
    "请尝试 A. 上文下图型 的思路，标题在上方，图在下方",
    "请尝试 B. 居中对称型 的思路，文字垂直居中，极简留白",
    "请尝试 C. 底部聚集型 的思路，标题和 CTA 在底部",
    "请尝试 D. 左对齐通栏型 的思路，杂志封面风格",
    "请尝试 E. 对角线型 的思路，标题左上 CTA 右下",
    "请尝试 F. 大标题铺满型 的思路，标题字号极大",
    "请尝试 G. 上下分割型 的思路，上半标题下半主体",
    "请自由创造一种全新的版式，不要参考 A-G",
    "请设计一种非对称、有冲击力的版式",
    "请设计一种文字与图片交错的版式",
]


@router.post("/layouts")
async def step_layouts(req: LayoutsRequest):
    """
    Step 3: 生成 → 快速校验 → 双路 Critic 审核 → 仅返回通过的版式。

    流程：
    1. 并行生成 N 个版式
    2. 快速规则校验，剔除结构异常的
    3. 对通过的版式并行运行双路 Critic（JSON + 视觉）
    4. REJECT 的自动带反馈重试一次
    5. 只返回最终 PASS 的版式供用户选择
    """
    logger.info(f"📐 [Step 3] 版式生成 + 审核，方案数: {req.count}")

    asset_list = _build_asset_list(req)
    brief_dict = req.design_brief.model_dump()

    # ---- Phase 1: 并行生成 ----
    async def _gen(idx: int) -> Dict[str, Any]:
        hint = _STYLE_HINTS[idx % len(_STYLE_HINTS)]
        logger.info(f"  📐 生成版式 {idx + 1}/{req.count} ({hint[:15]}...)")
        return await asyncio.to_thread(
            run_layout_agent,
            design_brief=brief_dict,
            asset_list=asset_list,
            canvas_width=req.canvas_width,
            canvas_height=req.canvas_height,
            style_hint=hint,
        )

    gen_results = await asyncio.gather(
        *[_gen(i) for i in range(req.count)],
        return_exceptions=True,
    )

    # ---- Phase 2: 快速规则校验 ----
    candidates: List[Dict[str, Any]] = []
    for i, r in enumerate(gen_results):
        if isinstance(r, Exception):
            logger.error(f"  ❌ 版式 {i + 1} 生成失败: {r}")
            continue
        issue = _quick_validate_layout(r)
        if issue:
            logger.warning(f"  ⚠️ 版式 {i + 1} 规则校验不通过: {issue}")
        else:
            candidates.append(r)

    logger.info(f"📋 规则校验后剩余 {len(candidates)}/{req.count} 个版式，进入双路审核...")

    # ---- Phase 3: 并行双路 Critic 审核 ----
    async def _review(poster: Dict[str, Any]) -> Dict[str, Any]:
        review = await asyncio.to_thread(
            run_critic_agent, poster, design_brief=brief_dict
        )
        return {"poster": poster, "review": review}

    review_results = await asyncio.gather(
        *[_review(c) for c in candidates],
        return_exceptions=True,
    )

    passed: List[Dict[str, Any]] = []
    to_retry: List[Dict[str, Any]] = []

    for i, r in enumerate(review_results):
        if isinstance(r, Exception):
            logger.error(f"  ❌ 审核版式 {i + 1} 出错: {r}")
            continue
        if r["review"].get("status") == "PASS":
            logger.info(f"  ✅ 版式 {i + 1} 审核通过")
            poster = r["poster"]
            poster["_review"] = r["review"]
            passed.append(poster)
        else:
            fb = r["review"].get("feedback", "")
            logger.warning(f"  ❌ 版式 {i + 1} 审核不通过: {fb}")
            to_retry.append(r["review"])

    # ---- Phase 4: 对 REJECT 的重试一次（带反馈重新生成 + 审核） ----
    if to_retry:
        logger.info(f"🔄 {len(to_retry)} 个版式被 REJECT，带反馈重试...")

        async def _retry(review_feedback: Dict[str, Any], idx: int) -> Optional[Dict[str, Any]]:
            hint = _STYLE_HINTS[(req.count + idx) % len(_STYLE_HINTS)]
            poster = await asyncio.to_thread(
                run_layout_agent,
                design_brief=brief_dict,
                asset_list=asset_list,
                canvas_width=req.canvas_width,
                canvas_height=req.canvas_height,
                review_feedback=review_feedback,
                style_hint=hint,
            )
            issue = _quick_validate_layout(poster)
            if issue:
                return None
            review = await asyncio.to_thread(
                run_critic_agent, poster, design_brief=brief_dict
            )
            if review.get("status") == "PASS":
                poster["_review"] = review
                return poster
            return None

        retry_results = await asyncio.gather(
            *[_retry(fb, i) for i, fb in enumerate(to_retry)],
            return_exceptions=True,
        )
        for r in retry_results:
            if isinstance(r, Exception):
                continue
            if r is not None:
                passed.append(r)

    logger.info(f"✅ [Step 3] 最终通过审核的版式: {len(passed)} 个")

    return {
        "step": "layouts",
        "layouts": passed,
    }


def _build_asset_list(req: LayoutsRequest) -> Dict[str, Any]:
    """从 LayoutsRequest 构建 asset_list"""
    asset_list = AssetList(
        background_layer=AssetLayer(
            type="image",
            src=req.selected_asset_url,
            source_type="selected",
        ),
        subject_layer=AssetLayer(
            type="image",
            src=req.subject_asset_url,
            source_type="user_upload",
            width=req.subject_width,
            height=req.subject_height,
        ) if req.subject_asset_url else None,
        image_analyses=req.image_analyses,
        color_suggestions=req.color_suggestions,
    )
    return asset_list.model_dump(exclude_none=True)


# ============================================================================
# Step 4: 确认选择（版式已在 Step 3 通过双路审核）
# ============================================================================

class FinalizeRequest(BaseModel):
    poster_data: Dict[str, Any] = Field(..., description="用户选中的版式 JSON（已审核通过）")


@router.post("/finalize")
async def step_finalize(req: FinalizeRequest):
    """
    Step 4: 确认用户选择，直接返回。

    版式已在 Step 3 通过双路 Critic 审核（JSON 结构 + 视觉），
    此步骤仅作为流程终点，不再重复审核。
    """
    logger.info("✅ [Step 4] 确认选择（版式已通过审核）")

    return {
        "step": "finalize",
        "poster": req.poster_data,
        "review": {"status": "PASS", "feedback": "版式已在 Step 3 通过双路审核"},
    }
