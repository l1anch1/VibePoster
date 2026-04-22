"""
端到端成功率测试

通过完整流程（plan → assets → layouts → finalize）跑测试数据集，
统计成功率、耗时和审核结果分布。

运行命令：cd backend/engine && python -m pytest tests/test_e2e_benchmark.py -v -s -m slow
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

try:
    from app.agents.planner import run_planner_agent
    from app.agents.layout import run_layout_agent
    from app.agents.critic import run_critic_agent
    from app.utils.metrics import evaluate_poster
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

needs_env = pytest.mark.skipif(not _AVAILABLE, reason="应用模块不可用")

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"

# 行业 → 背景色映射（与 test_ablation.py 保持一致）
INDUSTRY_BG_COLORS = {
    "Tech":          "1A1A2E",
    "Food":          "F8E8D0",
    "Luxury":        "F5F0EB",
    "Healthcare":    "E8F5E9",
    "Education":     "87CEEB",
    "Entertainment": "FFD700",
}


def _get_placeholder_bg(industry: str) -> str:
    color = INDUSTRY_BG_COLORS.get(industry, "333333")
    return f"https://placehold.co/1080x1920/{color}/{color}"


def _load_prompts() -> List[Dict[str, Any]]:
    with open(DATA_DIR / "test_prompts.json", "r", encoding="utf-8") as f:
        return json.load(f)


@needs_env
@pytest.mark.slow
class TestE2EBenchmark:
    """端到端全流程测试（Full System 配置）"""

    def test_e2e_full_pipeline(self):
        """逐条跑完整流程，记录成功率和耗时"""
        prompts = _load_prompts()
        results = []

        for i, p in enumerate(prompts):
            print(f"\n[{i+1}/{len(prompts)}] {p['id']}: {p['prompt'][:50]}...")
            record = {"id": p["id"], "prompt": p["prompt"]}

            # ---- Plan ----
            t0 = time.time()
            try:
                brief = run_planner_agent(
                    user_prompt=p["prompt"],
                    brand_name=p.get("brand_name"),
                )
                record["plan_time"] = round(time.time() - t0, 2)
                record["plan_ok"] = bool(brief.get("title"))
            except Exception as e:
                record["plan_time"] = round(time.time() - t0, 2)
                record["plan_ok"] = False
                record["plan_error"] = str(e)
                brief = {
                    "title": "Fallback", "main_color": "#FFFFFF",
                    "background_color": "#333333", "style_keywords": [],
                    "intent": "promotion",
                }

            brief["canvas_width"] = 1080
            brief["canvas_height"] = 1920

            # ---- Assets (mock，按行业分配不同背景色) ----
            industry = p.get("expected_industry", "")
            assets = {
                "background_layer": {
                    "type": "image", "src": _get_placeholder_bg(industry),
                    "source_type": "placeholder",
                },
            }

            # ---- Layout ----
            t1 = time.time()
            try:
                poster = run_layout_agent(
                    design_brief=brief,
                    asset_list=assets,
                    canvas_width=1080,
                    canvas_height=1920,
                )
                record["layout_time"] = round(time.time() - t1, 2)
                record["layout_ok"] = bool(poster.get("layers"))
                record["layer_count"] = len(poster.get("layers", []))
            except Exception as e:
                record["layout_time"] = round(time.time() - t1, 2)
                record["layout_ok"] = False
                record["layout_error"] = str(e)
                poster = {"canvas": {"width": 1080, "height": 1920}, "layers": []}

            # ---- Critic ----
            t2 = time.time()
            try:
                review = run_critic_agent(poster, design_brief=brief)
                record["critic_time"] = round(time.time() - t2, 2)
                record["critic_status"] = review.get("status", "UNKNOWN")
            except Exception as e:
                record["critic_time"] = round(time.time() - t2, 2)
                record["critic_status"] = "ERROR"

            # ---- Retry (如果 REJECT) ----
            record["retry_count"] = 0
            if record["critic_status"] == "REJECT":
                t3 = time.time()
                try:
                    poster2 = run_layout_agent(
                        design_brief=brief,
                        asset_list=assets,
                        canvas_width=1080,
                        canvas_height=1920,
                        review_feedback=review,
                    )
                    review2 = run_critic_agent(poster2, design_brief=brief)
                    record["retry_count"] = 1
                    record["retry_status"] = review2.get("status", "UNKNOWN")
                    record["retry_time"] = round(time.time() - t3, 2)
                    if review2.get("status") == "PASS":
                        poster = poster2
                        record["critic_status"] = "PASS_AFTER_RETRY"
                except Exception:
                    record["retry_status"] = "ERROR"

            # ---- Metrics ----
            try:
                record["metrics"] = evaluate_poster(poster, brief)
            except Exception as e:
                record["metrics"] = {"error": str(e)}

            record["total_time"] = round(
                record.get("plan_time", 0)
                + record.get("layout_time", 0)
                + record.get("critic_time", 0)
                + record.get("retry_time", 0),
                2,
            )

            status_str = record["critic_status"]
            print(f"  → {status_str} | layers={record.get('layer_count', 0)} | {record['total_time']}s")
            results.append(record)

        # ---- 保存结果 ----
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out = RESULTS_DIR / "e2e_results.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # ---- 汇总 ----
        total = len(results)
        plan_ok = sum(1 for r in results if r.get("plan_ok"))
        layout_ok = sum(1 for r in results if r.get("layout_ok"))
        critic_pass = sum(1 for r in results if r.get("critic_status") in ("PASS", "PASS_AFTER_RETRY"))
        retried = sum(1 for r in results if r.get("retry_count", 0) > 0)
        avg_time = sum(r.get("total_time", 0) for r in results) / max(total, 1)

        print(f"\n{'='*50}")
        print(f"端到端测试汇总 (N={total})")
        print(f"{'='*50}")
        print(f"  Plan 成功率:   {plan_ok}/{total} ({plan_ok/total*100:.1f}%)")
        print(f"  Layout 成功率: {layout_ok}/{total} ({layout_ok/total*100:.1f}%)")
        print(f"  Critic 通过率: {critic_pass}/{total} ({critic_pass/total*100:.1f}%)")
        print(f"  触发重试:      {retried}/{total}")
        print(f"  平均耗时:      {avg_time:.1f}s")
        print(f"  结果文件:      {out}")

        assert plan_ok > 0, "Plan 全部失败"
        assert layout_ok > 0, "Layout 全部失败"
