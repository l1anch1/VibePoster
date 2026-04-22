"""
消融实验结果分析脚本

读取 ablation_results.json，输出论文表格和统计检验结果。
运行: cd backend/engine && python tests/analyze_ablation.py
"""

import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any

try:
    from scipy.stats import mannwhitneyu, fisher_exact
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

RESULTS_PATH = Path(__file__).parent / "results" / "ablation_results.json"
CONFIGS = ["Baseline", "+DSL", "+DSL+KG", "+DSL+RAG", "Full"]

BRAND_PROMPTS = {
    "tech_min_1", "tech_pro_3", "tech_bol_5",
    "food_min_6", "food_ene_7", "food_fri_9",
    "lux_bol_15", "health_ene_17", "ent_bol_30",
}


def load_data() -> Dict[str, List[Dict[str, Any]]]:
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    by_config = defaultdict(list)
    for r in data:
        by_config[r["config"]].append(r)
    return by_config


def extract_metric(results: List[Dict], key: str, nested_key: str = None) -> List[float]:
    vals = []
    for r in results:
        m = r.get("metrics", {})
        if nested_key:
            v = m.get(key, {}).get(nested_key)
        else:
            v = m.get(key)
        if v is not None and v > 0:
            vals.append(v)
    return vals


def safe_avg(vals: List[float]) -> float:
    return sum(vals) / max(len(vals), 1)


def safe_std(vals: List[float]) -> float:
    if len(vals) < 2:
        return 0.0
    return statistics.stdev(vals)


def print_main_table(by_config):
    """论文主表：版式结构质量"""
    print()
    print("=" * 120)
    print("表 5-1：消融实验——版式结构质量")
    print("=" * 120)
    header = (
        f"{'配置':12s} | {'间距异常↓':>8s} | {'装饰层数':>8s} | {'遮罩覆盖':>8s} | "
        f"{'字号比':>8s} | {'间距CV↓':>8s} | {'对齐线↓':>8s} | {'重叠率↓':>8s}"
    )
    print(header)
    print("-" * 120)

    for config in CONFIGS:
        results = by_config[config]

        gap_defects = [r["metrics"]["gap_defects"] for r in results
                       if "gap_defects" in r.get("metrics", {})]
        posters_with_defects = sum(1 for v in gap_defects if v > 0)

        deco = [r["metrics"]["decoration_layers"]["count"] for r in results
                if "decoration_layers" in r.get("metrics", {})]
        overlay = sum(1 for r in results
                      if r.get("metrics", {}).get("decoration_layers", {}).get("has_overlay"))

        font_ratios = [r["metrics"]["font_size_ratio"] for r in results
                       if r.get("metrics", {}).get("font_size_ratio", 0) > 0]

        gaps = [r["metrics"]["gap_uniformity_cv"]
                for r in results if "gap_uniformity_cv" in r.get("metrics", {})]
        aligns = [r["metrics"]["alignment_lines"]
                  for r in results if "alignment_lines" in r.get("metrics", {})]
        overlaps = [r["metrics"]["text_overlap_ratio"]
                    for r in results if "text_overlap_ratio" in r.get("metrics", {})]

        print(
            f"{config:12s} | {posters_with_defects:>5d}/30 | {safe_avg(deco):8.2f} | "
            f"{overlay:>5d}/30 | {safe_avg(font_ratios):8.2f} | "
            f"{safe_avg(gaps):8.2f} | {safe_avg(aligns):8.2f} | "
            f"{safe_avg(overlaps):8.4f}"
        )

    print()
    print("↓ = 越低越好。间距异常 = gap≤0 的海报数。字号比 = 最大字号/最小字号（2-4 为合理）。")


def print_kg_rag_table(by_config):
    """KG/RAG 专属指标子表"""
    print()
    print("=" * 80)
    print("表 5-2：知识增强专属指标")
    print("=" * 80)

    # KG: style_consistency（仅 +DSL+KG 和 Full 有值）
    print("\n(a) KG 风格一致性（海报主色调 vs KG 推荐色的匹配度）")
    print(f"{'配置':12s} | {'风格一致性':>10s} | {'有效样本':>8s}")
    print("-" * 40)
    for config in CONFIGS:
        results = by_config[config]
        styles = [r["metrics"]["style_consistency"]
                  for r in results
                  if r.get("metrics", {}).get("style_consistency", -1) >= 0]
        if styles:
            print(f"{config:12s} | {safe_avg(styles):10.3f} | {len(styles):>5d}/30")
        else:
            print(f"{config:12s} | {'N/A':>10s} | {'0':>5s}/30")

    # RAG: brand_color_adherence（仅品牌子集 + 有 RAG 的组）
    print(f"\n(b) RAG 品牌色彩匹配度（品牌子集，共 {len(BRAND_PROMPTS)} 条 prompt）")
    print(f"{'配置':12s} | {'品牌匹配度':>10s} | {'有效样本':>8s}")
    print("-" * 40)
    for config in CONFIGS:
        results = by_config[config]
        brand_results = [r for r in results if r["prompt_id"] in BRAND_PROMPTS]
        adherences = [r["metrics"]["brand_color_adherence"]
                      for r in brand_results
                      if r.get("metrics", {}).get("brand_color_adherence", -1) >= 0]
        if adherences:
            print(f"{config:12s} | {safe_avg(adherences):10.3f} | {len(adherences):>5d}/{len(brand_results)}")
        else:
            print(f"{config:12s} | {'N/A':>10s} | {'0':>5s}/{len(brand_results)}")


def print_composite_score(by_config):
    """综合质量评分"""
    print()
    print("=" * 60)
    print("综合质量评分（加权归一化，满分 1.0）")
    print("=" * 60)
    print("权重: 可读性 30%, 布局 20%, 无重叠 15%, 间距均匀 20%, 对齐 15%")
    print()

    for config in CONFIGS:
        results = by_config[config]
        scores = []
        for r in results:
            m = r.get("metrics", {})
            # 可读性: 二元评分（>=3.0 AA 标准即为 1.0，否则 0.0）
            # 超过 3.0 后更高不意味着更好（对比度非越大越好）
            read = 1.0 if m.get("text_readability", 1.0) >= 3.0 else 0.0
            # 布局完整性
            valid = m.get("layout_validity", {}).get("score", 0)
            # 无重叠 (0 = 完美)
            overlap = 1.0 - min(m.get("text_overlap_ratio", 0) * 10, 1.0)
            # 间距均匀 (0 = 完美)
            gap = 1.0 / (1.0 + m.get("gap_uniformity_cv", 5.0))
            # 对齐 (1 线 = 完美)
            align_val = max(m.get("alignment_lines", 1), 1)
            align = 1.0 / align_val

            composite = (read * 0.25 + valid * 0.20 + overlap * 0.15
                         + gap * 0.25 + align * 0.15)
            scores.append(composite)

        avg = safe_avg(scores)
        std = safe_std(scores)
        print(f"  {config:12s}: {avg:.4f} ± {std:.4f}")


def print_stat_tests(by_config):
    """统计显著性检验"""
    if not HAS_SCIPY:
        print("\n⚠️ scipy 未安装，跳过统计检验")
        return

    print()
    print("=" * 90)
    print("统计显著性检验")
    print("=" * 90)

    bl = by_config["Baseline"]

    # 1. 可读性 Mann-Whitney
    print("\n── 文字可读性 Mann-Whitney U（单侧: Baseline < 其他组） ──")
    bl_reads = extract_metric(bl, "text_readability")
    for c in CONFIGS[1:]:
        other_reads = extract_metric(by_config[c], "text_readability")
        u, p = mannwhitneyu(bl_reads, other_reads, alternative="less")
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
        print(f"  Baseline vs {c:10s}: U={u:6.1f}, p={p:.6f} {sig}")

    # 2. WCAG AA 通过率 Fisher
    print("\n── WCAG AA 通过率 (>=3.0) Fisher 精确检验 ──")
    bl_pass = sum(1 for v in bl_reads if v >= 3.0)
    bl_fail = len(bl_reads) - bl_pass
    for c in CONFIGS[1:]:
        other_reads = extract_metric(by_config[c], "text_readability")
        o_pass = sum(1 for v in other_reads if v >= 3.0)
        o_fail = len(other_reads) - o_pass
        if bl_fail == 0 and o_fail == 0:
            print(f"  Baseline vs {c:10s}: 两组均 100% 通过")
            continue
        odds, p = fisher_exact([[bl_pass, bl_fail], [o_pass, o_fail]])
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
        print(f"  Baseline({bl_pass}/30) vs {c}({o_pass}/30): "
              f"odds={odds:.3f}, p={p:.6f} {sig}")

    # 3. 间距 CV Mann-Whitney
    print("\n── 间距均匀性 CV Mann-Whitney U（单侧: Baseline > 其他组） ──")
    bl_gaps = [r["metrics"]["gap_uniformity_cv"]
               for r in bl if "gap_uniformity_cv" in r.get("metrics", {})]
    for c in CONFIGS[1:]:
        other_gaps = [r["metrics"]["gap_uniformity_cv"]
                      for r in by_config[c]
                      if "gap_uniformity_cv" in r.get("metrics", {})]
        u, p = mannwhitneyu(bl_gaps, other_gaps, alternative="greater")
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
        print(f"  Baseline vs {c:10s}: U={u:6.1f}, p={p:.6f} {sig}")


def print_timing(by_config):
    """耗时统计"""
    print()
    print("=" * 60)
    print("平均耗时（秒）")
    print("=" * 60)
    print(f"{'配置':12s} | {'Planner':>8s} | {'Layout':>8s} | {'Critic':>8s} | {'Total':>8s}")
    print("-" * 60)
    for config in CONFIGS:
        results = by_config[config]
        pt = safe_avg([r.get("planner_time", 0) for r in results])
        lt = safe_avg([r.get("layout_time", 0) for r in results])
        ct = safe_avg([r.get("critic_time", 0) for r in results])
        tt = safe_avg([r.get("total_time", 0) for r in results])
        print(f"{config:12s} | {pt:8.1f} | {lt:8.1f} | {ct:8.1f} | {tt:8.1f}")


def print_per_industry(by_config):
    """按行业分析"""
    print()
    print("=" * 80)
    print("按行业分析：Full 配置下的可读性和间距均匀性")
    print("=" * 80)

    full_results = by_config["Full"]
    industries = defaultdict(list)
    for r in full_results:
        brief = r.get("design_brief", {})
        # 从 prompt_id 推断行业
        pid = r["prompt_id"]
        if pid.startswith("tech_"):
            ind = "Tech"
        elif pid.startswith("food_"):
            ind = "Food"
        elif pid.startswith("lux_"):
            ind = "Luxury"
        elif pid.startswith("health_"):
            ind = "Healthcare"
        elif pid.startswith("edu_"):
            ind = "Education"
        elif pid.startswith("ent_"):
            ind = "Entertainment"
        else:
            ind = "Unknown"
        industries[ind].append(r)

    print(f"{'行业':12s} | {'n':>3s} | {'可读性':>7s} | {'AA通过':>7s} | {'间距CV':>7s} | {'对齐线':>7s}")
    print("-" * 60)
    for ind in ["Tech", "Food", "Luxury", "Healthcare", "Education", "Entertainment"]:
        results = industries[ind]
        reads = extract_metric(results, "text_readability")
        read_pass = sum(1 for v in reads if v >= 3.0)
        gaps = [r["metrics"]["gap_uniformity_cv"]
                for r in results if "gap_uniformity_cv" in r.get("metrics", {})]
        aligns = [r["metrics"]["alignment_lines"]
                  for r in results if "alignment_lines" in r.get("metrics", {})]
        print(f"{ind:12s} | {len(results):>3d} | {safe_avg(reads):7.2f} | "
              f"{read_pass:>3d}/{len(reads)}  | {safe_avg(gaps):7.4f} | {safe_avg(aligns):7.2f}")


def main():
    by_config = load_data()

    total = sum(len(v) for v in by_config.values())
    print(f"\n共加载 {total} 条结果（{len(by_config)} 个配置）")

    print_main_table(by_config)
    print_kg_rag_table(by_config)
    print_composite_score(by_config)
    print_stat_tests(by_config)
    print_timing(by_config)
    print_per_industry(by_config)


if __name__ == "__main__":
    main()
