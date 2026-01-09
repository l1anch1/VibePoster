"""
KG 数据加载器 v2

支持语义化设计知识图谱数据结构。

Author: VibePoster Team
Date: 2025-01
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from .types import (
    EmotionDefinition,
    IndustryDefinition,
    VibeDefinition,
    ColorPalette,
    Typography,
    LayoutStyle
)
from ...core.logger import get_logger

logger = get_logger(__name__)

# 默认数据文件路径
DEFAULT_DATA_DIR = Path(__file__).parent / "data"
DEFAULT_KG_RULES_FILE = DEFAULT_DATA_DIR / "kg_rules.json"


class RulesLoader:
    """规则数据加载器 v2"""
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        初始化加载器
        
        Args:
            rules_file: 规则文件路径（可选）
        """
        self.rules_file = self._resolve_rules_file(rules_file)
        self._cache: Optional[Dict[str, Any]] = None
        self._emotions_cache: Optional[Dict[str, EmotionDefinition]] = None
        self._industries_cache: Optional[Dict[str, IndustryDefinition]] = None
        self._vibes_cache: Optional[Dict[str, VibeDefinition]] = None
    
    def _resolve_rules_file(self, rules_file: Optional[str]) -> Path:
        """解析规则文件路径"""
        if rules_file:
            return Path(rules_file)
        
        try:
            from ...core.config import settings
            config_path = getattr(settings.kg, 'RULES_FILE', None)
            if config_path and Path(config_path).exists():
                return Path(config_path)
        except Exception:
            pass
        
        return DEFAULT_KG_RULES_FILE
    
    def load(self, force_reload: bool = False) -> Dict[str, Any]:
        """加载原始规则数据"""
        if self._cache is not None and not force_reload:
            return self._cache
        
        if not self.rules_file.exists():
            logger.warning(f"规则文件不存在: {self.rules_file}")
            self._cache = self._empty_rules()
            return self._cache
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)
            logger.info(f"成功加载 KG 规则 v{self._cache.get('$version', '1.0')}: {self.rules_file}")
            return self._cache
        except json.JSONDecodeError as e:
            logger.error(f"规则文件 JSON 解析失败: {e}")
            self._cache = self._empty_rules()
            return self._cache
        except Exception as e:
            logger.error(f"加载规则文件失败: {e}")
            self._cache = self._empty_rules()
            return self._cache
    
    def _empty_rules(self) -> Dict[str, Any]:
        """返回空规则结构"""
        return {
            "$version": "2.0.0",
            "emotions": {},
            "industries": {},
            "vibes": {},
            "design_strategies": {}
        }
    
    # ========================================================================
    # 情绪层
    # ========================================================================
    
    def get_emotions(self, force_reload: bool = False) -> Dict[str, EmotionDefinition]:
        """获取所有情绪定义"""
        if self._emotions_cache is not None and not force_reload:
            return self._emotions_cache
        
        data = self.load(force_reload)
        emotions_raw = data.get("emotions", {})
        
        self._emotions_cache = {}
        for name, config in emotions_raw.items():
            try:
                # 解析嵌套结构
                color_palettes = ColorPalette(**config.get("color_palettes", {}))
                typography = None
                if "typography" in config:
                    typography = Typography(**config["typography"])
                layout = None
                if "layout" in config:
                    layout = LayoutStyle(**config["layout"])
                
                self._emotions_cache[name] = EmotionDefinition(
                    description=config.get("description", ""),
                    color_strategies=config.get("color_strategies", []),
                    color_palettes=color_palettes,
                    typography=typography,
                    layout=layout
                )
            except Exception as e:
                logger.warning(f"解析情绪 '{name}' 失败: {e}")
        
        return self._emotions_cache
    
    def get_emotion(self, name: str) -> Optional[EmotionDefinition]:
        """获取单个情绪定义"""
        emotions = self.get_emotions()
        return emotions.get(name)
    
    # ========================================================================
    # 行业层
    # ========================================================================
    
    def get_industries(self, force_reload: bool = False) -> Dict[str, IndustryDefinition]:
        """获取所有行业定义"""
        if self._industries_cache is not None and not force_reload:
            return self._industries_cache
        
        data = self.load(force_reload)
        industries_raw = data.get("industries", {})
        
        self._industries_cache = {}
        for name, config in industries_raw.items():
            try:
                self._industries_cache[name] = IndustryDefinition(
                    description=config.get("description", ""),
                    embodies=config.get("embodies", []),
                    design_principles=config.get("design_principles", []),
                    avoid=config.get("avoid", [])
                )
            except Exception as e:
                logger.warning(f"解析行业 '{name}' 失败: {e}")
        
        return self._industries_cache
    
    def get_industry(self, name: str) -> Optional[IndustryDefinition]:
        """获取单个行业定义"""
        industries = self.get_industries()
        return industries.get(name)
    
    # ========================================================================
    # 风格层
    # ========================================================================
    
    def get_vibes(self, force_reload: bool = False) -> Dict[str, VibeDefinition]:
        """获取所有风格定义"""
        if self._vibes_cache is not None and not force_reload:
            return self._vibes_cache
        
        data = self.load(force_reload)
        vibes_raw = data.get("vibes", {})
        
        self._vibes_cache = {}
        for name, config in vibes_raw.items():
            try:
                self._vibes_cache[name] = VibeDefinition(
                    description=config.get("description", ""),
                    embodies=config.get("embodies", []),
                    modifiers=config.get("modifiers", {})
                )
            except Exception as e:
                logger.warning(f"解析风格 '{name}' 失败: {e}")
        
        return self._vibes_cache
    
    def get_vibe(self, name: str) -> Optional[VibeDefinition]:
        """获取单个风格定义"""
        vibes = self.get_vibes()
        return vibes.get(name)
    
    # ========================================================================
    # 辅助方法
    # ========================================================================
    
    def get_supported_keywords(self) -> Dict[str, List[str]]:
        """获取支持的关键词列表"""
        return {
            "industries": list(self.get_industries().keys()),
            "vibes": list(self.get_vibes().keys()),
            "emotions": list(self.get_emotions().keys())
        }
    
    def get_version(self) -> str:
        """获取数据版本"""
        data = self.load()
        return data.get("$version", "1.0.0")
    
    def clear_cache(self):
        """清除所有缓存"""
        self._cache = None
        self._emotions_cache = None
        self._industries_cache = None
        self._vibes_cache = None
