"""
字体注册表 — 单一数据源

将 LLM/KG 输出的抽象 font_style 类别映射到具体的系统字体。

设计原则：
- LLM 只需输出 font_style 枚举（5 个值），不需要知道具体字体名
- 按 layer role（title / body）区分字体选择
- 每个条目包含 CSS family + PSD PostScript name，保证三端一致
"""

from typing import Dict, Any, Optional, List


# =============================================================================
# 字体注册表
# =============================================================================

FontEntry = Dict[str, str]  # {"family": ..., "weight": ..., "ps": ...}

FONT_REGISTRY: Dict[str, Dict[str, FontEntry]] = {
    "sans": {
        "title": {"family": "PingFang SC",  "weight": "600",    "ps": "PingFangSC-Semibold"},
        "body":  {"family": "PingFang SC",  "weight": "normal", "ps": "PingFangSC-Regular"},
    },
    "serif": {
        "title": {"family": "Songti SC",    "weight": "900",    "ps": "STSongti-SC-Black"},
        "body":  {"family": "Songti SC",    "weight": "normal", "ps": "STSongti-SC-Regular"},
    },
    "rounded": {
        "title": {"family": "Yuanti TC",    "weight": "bold",   "ps": "STYuanti-TC-Bold"},
        "body":  {"family": "Yuanti TC",    "weight": "normal", "ps": "STYuanti-TC-Regular"},
    },
    "handwriting": {
        "title": {"family": "Kaiti SC",     "weight": "bold",   "ps": "STKaitiSC-Bold"},
        "body":  {"family": "Kaiti SC",     "weight": "normal", "ps": "STKaitiSC-Regular"},
    },
    "display": {
        "title": {"family": "Baoli SC",     "weight": "normal", "ps": "STBaoliSC-Regular"},
        "body":  {"family": "PingFang SC",  "weight": "normal", "ps": "PingFangSC-Regular"},
    },
}

VALID_FONT_STYLES = list(FONT_REGISTRY.keys())
DEFAULT_FONT_STYLE = "sans"

# KG typography_styles → font_style 映射
_KG_STYLE_MAP: Dict[str, str] = {
    "sans-serif":   "sans",
    "serif":        "serif",
    "display":      "display",
    "rounded-sans": "rounded",
    "handwriting":  "handwriting",
    "script":       "handwriting",
}


# =============================================================================
# 解析函数
# =============================================================================

def resolve_font(
    font_style: Optional[str] = None,
    role: str = "body",
) -> FontEntry:
    """
    将 font_style + role 解析为具体的字体条目。

    Args:
        font_style: LLM 输出的枚举值（sans/serif/rounded/handwriting/display）
        role: 图层角色 — "title" 或 "body"

    Returns:
        {"family": "PingFang SC", "weight": "600", "ps": "PingFangSC-Semibold"}
    """
    style = (font_style or DEFAULT_FONT_STYLE).lower().strip()
    if style not in FONT_REGISTRY:
        style = DEFAULT_FONT_STYLE

    role_key = "title" if role in ("title", "heading", "cta") else "body"
    return FONT_REGISTRY[style][role_key]


def resolve_font_style_from_kg(typography_styles: List[str]) -> str:
    """
    从 KG 推理结果的 typography_styles 推导 font_style 枚举。

    Args:
        typography_styles: KG 输出，如 ["Sans-Serif", "Display"]

    Returns:
        font_style 枚举值（取第一个匹配的）
    """
    for ts in typography_styles:
        mapped = _KG_STYLE_MAP.get(ts.lower().strip())
        if mapped:
            return mapped
    return DEFAULT_FONT_STYLE


def build_ps_name_map() -> Dict[str, str]:
    """
    生成 CSS fontFamily → PostScript name 映射表。
    供 PSD 导出使用，替代硬编码的 FONT_NAME_MAP。
    """
    ps_map: Dict[str, str] = {}
    for style_entries in FONT_REGISTRY.values():
        for entry in style_entries.values():
            ps_map[entry["family"]] = entry["ps"]
    return ps_map
