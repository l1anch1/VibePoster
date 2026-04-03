"""
本体数据加载器 v3

加载 ontology.json 的节点表和关系表，返回类型化的 Pydantic 模型。
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from .types import (
    EmotionDefinition,
    IndustryDefinition,
    VibeDefinition,
    ColorStrategyDefinition,
    TypographyStyleDefinition,
    LayoutPatternDefinition,
    DecorationThemeDefinition,
    Relation,
)
from ...core.logger import get_logger

logger = get_logger(__name__)

DEFAULT_DATA_DIR = Path(__file__).parent / "data"
DEFAULT_ONTOLOGY_FILE = DEFAULT_DATA_DIR / "ontology.json"


class OntologyLoader:
    """本体数据加载器 v3"""

    def __init__(self, ontology_file: Optional[str] = None):
        self.ontology_file = self._resolve_file(ontology_file)
        self._raw: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # 文件解析
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_file(ontology_file: Optional[str]) -> Path:
        if ontology_file:
            return Path(ontology_file)
        try:
            from ...core.config import settings
            cfg_path = getattr(settings.kg, "RULES_FILE", None)
            if cfg_path and Path(cfg_path).exists():
                return Path(cfg_path)
        except Exception:
            pass
        return DEFAULT_ONTOLOGY_FILE

    def load(self, force_reload: bool = False) -> Dict[str, Any]:
        if self._raw is not None and not force_reload:
            return self._raw
        if not self.ontology_file.exists():
            logger.warning(f"本体文件不存在: {self.ontology_file}")
            self._raw = self._empty()
            return self._raw
        try:
            with open(self.ontology_file, "r", encoding="utf-8") as f:
                self._raw = json.load(f)
            logger.info(
                f"本体 v{self._raw.get('$version', '?')} 加载完成: {self.ontology_file}"
            )
            return self._raw
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"本体文件加载失败: {e}")
            self._raw = self._empty()
            return self._raw

    @staticmethod
    def _empty() -> Dict[str, Any]:
        return {
            "$version": "3.0.0",
            "nodes": {
                "emotions": {},
                "industries": {},
                "vibes": {},
                "color_strategies": {},
                "typography_styles": {},
                "layout_patterns": {},
                "decoration_themes": {},
            },
            "relations": [],
        }

    # ------------------------------------------------------------------
    # 节点访问
    # ------------------------------------------------------------------

    def _nodes(self) -> Dict[str, Any]:
        return self.load().get("nodes", {})

    def get_emotions(self) -> Dict[str, EmotionDefinition]:
        raw = self._nodes().get("emotions", {})
        result: Dict[str, EmotionDefinition] = {}
        for name, cfg in raw.items():
            try:
                result[name] = EmotionDefinition(**cfg)
            except Exception as e:
                logger.warning(f"解析 Emotion '{name}' 失败: {e}")
        return result

    def get_industries(self) -> Dict[str, IndustryDefinition]:
        raw = self._nodes().get("industries", {})
        result: Dict[str, IndustryDefinition] = {}
        for name, cfg in raw.items():
            try:
                result[name] = IndustryDefinition(**cfg)
            except Exception as e:
                logger.warning(f"解析 Industry '{name}' 失败: {e}")
        return result

    def get_vibes(self) -> Dict[str, VibeDefinition]:
        raw = self._nodes().get("vibes", {})
        result: Dict[str, VibeDefinition] = {}
        for name, cfg in raw.items():
            try:
                result[name] = VibeDefinition(**cfg)
            except Exception as e:
                logger.warning(f"解析 Vibe '{name}' 失败: {e}")
        return result

    def get_color_strategies(self) -> Dict[str, ColorStrategyDefinition]:
        raw = self._nodes().get("color_strategies", {})
        result: Dict[str, ColorStrategyDefinition] = {}
        for name, cfg in raw.items():
            try:
                result[name] = ColorStrategyDefinition(**cfg)
            except Exception as e:
                logger.warning(f"解析 ColorStrategy '{name}' 失败: {e}")
        return result

    def get_typography_styles(self) -> Dict[str, TypographyStyleDefinition]:
        raw = self._nodes().get("typography_styles", {})
        result: Dict[str, TypographyStyleDefinition] = {}
        for name, cfg in raw.items():
            try:
                result[name] = TypographyStyleDefinition(**cfg)
            except Exception as e:
                logger.warning(f"解析 TypographyStyle '{name}' 失败: {e}")
        return result

    def get_layout_patterns(self) -> Dict[str, LayoutPatternDefinition]:
        raw = self._nodes().get("layout_patterns", {})
        result: Dict[str, LayoutPatternDefinition] = {}
        for name, cfg in raw.items():
            try:
                result[name] = LayoutPatternDefinition(**cfg)
            except Exception as e:
                logger.warning(f"解析 LayoutPattern '{name}' 失败: {e}")
        return result

    def get_decoration_themes(self) -> Dict[str, DecorationThemeDefinition]:
        raw = self._nodes().get("decoration_themes", {})
        result: Dict[str, DecorationThemeDefinition] = {}
        for name, cfg in raw.items():
            try:
                result[name] = DecorationThemeDefinition(**cfg)
            except Exception as e:
                logger.warning(f"解析 DecorationTheme '{name}' 失败: {e}")
        return result

    # ------------------------------------------------------------------
    # 关系访问
    # ------------------------------------------------------------------

    def get_relations(self) -> List[Relation]:
        raw_list = self.load().get("relations", [])
        relations: List[Relation] = []
        for item in raw_list:
            if "_comment" in item:
                continue
            try:
                relations.append(Relation(**item))
            except Exception as e:
                logger.warning(f"解析关系失败 {item}: {e}")
        return relations

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------

    def get_supported_keywords(self) -> Dict[str, List[str]]:
        return {
            "industries": list(self.get_industries().keys()),
            "vibes": list(self.get_vibes().keys()),
            "emotions": list(self.get_emotions().keys()),
        }

    def get_version(self) -> str:
        return self.load().get("$version", "3.0.0")

    def clear_cache(self) -> None:
        self._raw = None


# backward-compat alias
RulesLoader = OntologyLoader
