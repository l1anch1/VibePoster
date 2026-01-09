"""
KG 推理引擎 v2

实现语义化推理链：Industry/Vibe → Emotion → Visual Elements

推理流程：
1. 从 Industry/Vibe 关键词找到对应的 Emotions
2. 合并所有 Emotions 的视觉设计规则
3. 返回结构化的推理结果

Author: VibePoster Team
Date: 2025-01
"""

from typing import List, Dict, Any, Set, Optional

from .types import InferenceResult, NodeType
from .graph import DesignGraph
from ...core.logger import get_logger

logger = get_logger(__name__)


class InferenceEngine:
    """
    推理引擎 v2
    
    支持多层语义推理。
    """
    
    def __init__(self, graph: DesignGraph):
        """
        初始化推理引擎
        
        Args:
            graph: 设计知识图
        """
        self.graph = graph
    
    def infer(self, keywords: List[str]) -> InferenceResult:
        """
        基于关键词进行语义化推理
        
        推理链：Keywords → Emotions → Visual Elements
        
        Args:
            keywords: 关键词列表（如 ["Tech", "Minimalist"]）
        
        Returns:
            完整的推理结果
        """
        # Step 1: 收集所有相关的情绪
        all_emotions: Set[str] = set()
        all_design_principles: List[str] = []
        all_avoid: List[str] = []
        
        for keyword in keywords:
            if not self.graph.has_node(keyword):
                logger.debug(f"关键词 '{keyword}' 不在图谱中")
                continue
            
            # 获取该关键词体现的情绪
            emotions = self.graph.get_embodied_emotions(keyword)
            all_emotions.update(emotions)
            
            # 获取行业/风格的设计原则
            node_data = self.graph.get_node_data(keyword)
            if node_data:
                all_design_principles.extend(node_data.get("design_principles", []))
                all_avoid.extend(node_data.get("avoid", []))
        
        # Step 2: 从情绪推理视觉元素
        result = self._infer_from_emotions(list(all_emotions))
        
        # 添加设计原则
        result.design_principles = list(set(all_design_principles))
        result.avoid = list(set(all_avoid))
        
        logger.info(
            f"KG 推理完成: Keywords={keywords} → "
            f"Emotions={list(all_emotions)} → "
            f"Strategies={len(result.color_strategies)}, "
            f"Patterns={len(result.layout_patterns)}"
        )
        
        return result
    
    def _infer_from_emotions(self, emotions: List[str]) -> InferenceResult:
        """
        从情绪列表推理视觉元素
        
        Args:
            emotions: 情绪列表
        
        Returns:
            推理结果
        """
        # 收集器
        color_strategies: Set[str] = set()
        color_palettes: Dict[str, List[str]] = {}
        typography_styles: Set[str] = set()
        typography_weights: Set[str] = set()
        typography_characteristics: Set[str] = set()
        layout_strategies: Set[str] = set()
        layout_intents: Set[str] = set()
        layout_patterns: Set[str] = set()
        
        for emotion in emotions:
            emotion_def = self.graph.get_emotion_definition(emotion)
            if not emotion_def:
                continue
            
            # 配色
            color_strategies.update(emotion_def.get("color_strategies", []))
            
            palettes = emotion_def.get("color_palettes", {})
            for palette_type, colors in palettes.items():
                if palette_type not in color_palettes:
                    color_palettes[palette_type] = []
                color_palettes[palette_type].extend(colors)
            
            # 排版
            typography = emotion_def.get("typography", {})
            if typography:
                if "style" in typography:
                    typography_styles.add(typography["style"])
                if "weight" in typography:
                    typography_weights.add(typography["weight"])
                typography_characteristics.update(typography.get("characteristics", []))
            
            # 布局
            layout = emotion_def.get("layout", {})
            if layout:
                if "strategy" in layout:
                    layout_strategies.add(layout["strategy"])
                if "intent" in layout:
                    layout_intents.add(layout["intent"])
                layout_patterns.update(layout.get("patterns", []))
        
        # 去重配色
        for key in color_palettes:
            color_palettes[key] = list(set(color_palettes[key]))
        
        return InferenceResult(
            emotions=emotions,
            color_strategies=list(color_strategies),
            color_palettes=color_palettes,
            typography_styles=list(typography_styles),
            typography_weights=list(typography_weights),
            typography_characteristics=list(typography_characteristics),
            layout_strategies=list(layout_strategies),
            layout_intents=list(layout_intents),
            layout_patterns=list(layout_patterns)
        )
    
    def infer_single(self, keyword: str) -> InferenceResult:
        """对单个关键词进行推理"""
        return self.infer([keyword])
    
    def explain_inference(self, keywords: List[str]) -> Dict[str, Any]:
        """
        解释推理过程（用于调试和展示）
        
        Args:
            keywords: 关键词列表
        
        Returns:
            详细的推理过程说明
        """
        explanation = {
            "input_keywords": keywords,
            "inference_chain": [],
            "final_result": None
        }
        
        all_emotions = set()
        
        for keyword in keywords:
            keyword_chain = {
                "keyword": keyword,
                "found": self.graph.has_node(keyword),
                "node_type": None,
                "embodies_emotions": []
            }
            
            if keyword_chain["found"]:
                keyword_chain["node_type"] = self.graph.get_node_type(keyword)
                emotions = self.graph.get_embodied_emotions(keyword)
                keyword_chain["embodies_emotions"] = emotions
                all_emotions.update(emotions)
            
            explanation["inference_chain"].append(keyword_chain)
        
        # 添加最终结果
        result = self.infer(keywords)
        explanation["final_result"] = {
            "emotions": list(all_emotions),
            "color_strategies": result.color_strategies,
            "typography_styles": result.typography_styles,
            "layout_patterns": result.layout_patterns,
            "design_principles": result.design_principles,
            "avoid": result.avoid
        }
        
        return explanation
