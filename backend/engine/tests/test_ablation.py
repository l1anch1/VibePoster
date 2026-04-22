"""
消融实验运行器

五组配置 × 30 条 prompt，真实调用 LLM，输出结果到 tests/results/ablation_results.json。
运行命令：cd backend/engine && python -m pytest tests/test_ablation.py -v -s -m slow

需要 .env 中配好 API key。
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

# ============================================================================
# 环境检查
# ============================================================================

try:
    from app.agents.planner import run_planner_agent
    from app.agents.layout import run_layout_agent
    from app.agents.critic import run_critic_agent
    from app.utils.metrics import evaluate_poster
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

needs_env = pytest.mark.skipif(
    not _AVAILABLE,
    reason="应用模块不可用",
)

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"

# 行业 → 背景色映射（模拟真实场景中不同行业的典型背景色）
INDUSTRY_BG_COLORS = {
    "Tech":          "1A1A2E",  # 深蓝黑（科技感深色）
    "Food":          "F8E8D0",  # 暖米色（美食暖色调）
    "Luxury":        "F5F0EB",  # 米白（奢侈品浅色）
    "Healthcare":    "E8F5E9",  # 浅绿（医疗清新）
    "Education":     "87CEEB",  # 天蓝（教育明亮）
    "Entertainment": "FFD700",  # 金黄（娱乐活泼）
}


def _get_placeholder_bg(industry: str) -> str:
    """按行业返回对应颜色的占位图 URL"""
    color = INDUSTRY_BG_COLORS.get(industry, "333333")
    return f"https://placehold.co/1080x1920/{color}/{color}"

# ============================================================================
# 五种消融配置（递增式：每步只开一个开关）
# ============================================================================

ABLATION_CONFIGS = [
    {
        "name": "Baseline",
        "description": "纯 LLM 直接生成坐标（无 DSL、无 KG、无 RAG）",
        "skip_kg": True,
        "skip_rag": True,
        "use_dsl": False,
    },
    {
        "name": "+DSL",
        "description": "LLM + 语义 DSL + 布局引擎（无 KG、无 RAG）",
        "skip_kg": True,
        "skip_rag": True,
        "use_dsl": True,
    },
    {
        "name": "+DSL+KG",
        "description": "LLM + DSL + KG 知识图谱推理（无 RAG）",
        "skip_kg": False,
        "skip_rag": True,
        "use_dsl": True,
    },
    {
        "name": "+DSL+RAG",
        "description": "LLM + DSL + RAG 品牌知识（无 KG）",
        "skip_kg": True,
        "skip_rag": False,
        "use_dsl": True,
    },
    {
        "name": "Full",
        "description": "完整系统（DSL + KG + RAG）",
        "skip_kg": False,
        "skip_rag": False,
        "use_dsl": True,
    },
]


def _load_test_prompts() -> List[Dict[str, Any]]:
    """加载测试数据集"""
    path = DATA_DIR / "test_prompts.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _make_mock_assets(industry: str = "") -> Dict[str, Any]:
    """构造 mock 素材（不调真实图片服务），按行业分配不同背景色"""
    return {
        "background_layer": {
            "type": "image",
            "src": _get_placeholder_bg(industry),
            "source_type": "placeholder",
        },
    }


def _run_single(
    prompt_data: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """对单条 prompt 在单个配置下运行全流程"""
    prompt_text = prompt_data["prompt"]
    brand_name = prompt_data.get("brand_name")

    result = {
        "prompt_id": prompt_data["id"],
        "config": config["name"],
        "prompt": prompt_text,
    }

    # Step 1: Planner
    t0 = time.time()
    try:
        brief = run_planner_agent(
            user_prompt=prompt_text,
            brand_name=brand_name,
            skip_kg=config["skip_kg"],
            skip_rag=config["skip_rag"],
        )
        result["planner_time"] = round(time.time() - t0, 2)
        result["planner_ok"] = bool(brief.get("title"))
    except Exception as e:
        result["planner_time"] = round(time.time() - t0, 2)
        result["planner_ok"] = False
        result["planner_error"] = str(e)
        brief = {"title": "Fallback", "main_color": "#FFFFFF",
                 "background_color": "#333333", "style_keywords": [],
                 "intent": "promotion"}

    # 注入画布尺寸
    brief["canvas_width"] = 1080
    brief["canvas_height"] = 1920

    # Step 2: Mock 素材（按行业分配不同背景色）
    industry = prompt_data.get("expected_industry", "")
    assets = _make_mock_assets(industry)

    # Step 3: Layout
    t1 = time.time()
    try:
        poster = run_layout_agent(
            design_brief=brief,
            asset_list=assets,
            canvas_width=1080,
            canvas_height=1920,
            use_dsl=config["use_dsl"],
        )
        result["layout_time"] = round(time.time() - t1, 2)
        result["layout_ok"] = bool(poster.get("layers"))
    except Exception as e:
        result["layout_time"] = round(time.time() - t1, 2)
        result["layout_ok"] = False
        result["layout_error"] = str(e)
        poster = {"canvas": {"width": 1080, "height": 1920}, "layers": []}

    # Step 4: Critic
    t2 = time.time()
    try:
        review = run_critic_agent(poster, design_brief=brief)
        result["critic_time"] = round(time.time() - t2, 2)
        result["critic_status"] = review.get("status", "UNKNOWN")
        result["critic_feedback"] = review.get("feedback", "")
        result["critic_issues"] = review.get("issues", [])
    except Exception as e:
        result["critic_time"] = round(time.time() - t2, 2)
        result["critic_status"] = "ERROR"
        result["critic_error"] = str(e)

    # Step 5: 自动化指标
    try:
        metrics = evaluate_poster(poster, brief)
        result["metrics"] = metrics
    except Exception as e:
        result["metrics"] = {"error": str(e)}

    # 保存完整 poster JSON 和 design_brief 供后续分析
    result["poster"] = poster
    result["design_brief"] = brief

    result["total_time"] = round(
        result.get("planner_time", 0)
        + result.get("layout_time", 0)
        + result.get("critic_time", 0),
        2,
    )

    return result


# ============================================================================
# Pytest 入口
# ============================================================================

@needs_env
@pytest.mark.slow
class TestAblation:
    """消融实验：5 配置 × 30 prompt"""

    def test_run_ablation(self):
        """运行完整消融实验并保存结果"""
        prompts = _load_test_prompts()
        all_results = []

        for config in ABLATION_CONFIGS:
            print(f"\n{'='*60}")
            print(f"配置: {config['name']} — {config['description']}")
            print(f"{'='*60}")

            config_results = []
            for i, prompt_data in enumerate(prompts):
                print(f"  [{i+1}/{len(prompts)}] {prompt_data['id']}: {prompt_data['prompt'][:40]}...")
                try:
                    result = _run_single(prompt_data, config)
                    config_results.append(result)
                    status = result.get("critic_status", "?")
                    t = result.get("total_time", 0)
                    print(f"    → {status} ({t}s)")
                except Exception as e:
                    print(f"    → ERROR: {e}")
                    config_results.append({
                        "prompt_id": prompt_data["id"],
                        "config": config["name"],
                        "error": str(e),
                    })

            all_results.extend(config_results)

            # 打印配置汇总
            pass_count = sum(1 for r in config_results if r.get("critic_status") == "PASS")
            total = len(config_results)
            print(f"\n  汇总: {pass_count}/{total} PASS ({pass_count/total*100:.1f}%)")

        # 保存结果
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = RESULTS_DIR / "ablation_results.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 结果已保存到 {output_path}")

        # 打印总览表格
        print(f"\n{'='*60}")
        print("消融实验总览")
        print(f"{'='*60}")
        for config in ABLATION_CONFIGS:
            cr = [r for r in all_results if r.get("config") == config["name"]]
            pass_n = sum(1 for r in cr if r.get("critic_status") == "PASS")
            total_n = len(cr)
            avg_time = sum(r.get("total_time", 0) for r in cr) / max(total_n, 1)

            readabilities = [
                r["metrics"]["text_readability"]
                for r in cr
                if r.get("metrics", {}).get("text_readability", 0) > 0
            ]
            avg_read = sum(readabilities) / max(len(readabilities), 1)

            validities = [
                r["metrics"]["layout_validity"]["score"]
                for r in cr
                if "layout_validity" in r.get("metrics", {})
            ]
            avg_valid = sum(validities) / max(len(validities), 1)

            overlaps = [
                r["metrics"]["text_overlap_ratio"]
                for r in cr
                if "text_overlap_ratio" in r.get("metrics", {})
            ]
            avg_overlap = sum(overlaps) / max(len(overlaps), 1)

            gap_cvs = [
                r["metrics"]["gap_uniformity_cv"]
                for r in cr
                if "gap_uniformity_cv" in r.get("metrics", {})
            ]
            avg_gap_cv = sum(gap_cvs) / max(len(gap_cvs), 1)

            aligns = [
                r["metrics"]["alignment_lines"]
                for r in cr
                if "alignment_lines" in r.get("metrics", {})
            ]
            avg_align = sum(aligns) / max(len(aligns), 1)

            # 品牌色彩匹配度（仅对品牌 prompt 子集计算）
            brand_scores = [
                r["metrics"]["brand_color_adherence"]
                for r in cr
                if r.get("metrics", {}).get("brand_color_adherence", -1) >= 0
            ]
            avg_brand = sum(brand_scores) / max(len(brand_scores), 1) if brand_scores else -1

            brand_str = f"品牌色={avg_brand:.2f}({len(brand_scores)}条)" if brand_scores else "品牌色=N/A"

            print(
                f"  {config['name']:12s}  "
                f"PASS={pass_n}/{total_n} ({pass_n/max(total_n,1)*100:5.1f}%)  "
                f"可读性={avg_read:5.2f}  "
                f"布局={avg_valid:4.2f}  "
                f"重叠={avg_overlap:.4f}  "
                f"间距CV={avg_gap_cv:.4f}  "
                f"对齐线={avg_align:.1f}  "
                f"{brand_str}  "
                f"平均耗时={avg_time:5.1f}s"
            )

        assert len(all_results) > 0, "没有产出任何结果"
