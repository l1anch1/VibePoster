"""
知识服务层 - 统一管理 KG 和 RAG

职责：
1. 统一管理知识图谱和品牌知识库的生命周期
2. 提供知识推理和检索的高层接口
3. 解耦 Agent 和知识模块的直接依赖

Author: VibePoster Team
Date: 2025-01
"""

from typing import Dict, Any, List, Optional
from ..core.interfaces import IKnowledgeGraph, IKnowledgeBase
from ..core.logger import get_logger

logger = get_logger(__name__)


class KnowledgeService:
    """
    知识服务类
    
    统一管理 Knowledge Graph 和 RAG 知识库，
    提供设计规则推理和品牌知识检索功能。
    """
    
    def __init__(
        self,
        knowledge_graph: Optional[IKnowledgeGraph] = None,
        knowledge_base: Optional[IKnowledgeBase] = None
    ):
        """
        初始化知识服务
        
        Args:
            knowledge_graph: 知识图谱实例（可选，延迟初始化）
            knowledge_base: 知识库实例（可选，延迟初始化）
        """
        self._knowledge_graph = knowledge_graph
        self._knowledge_base = knowledge_base
        self._kg_initialized = knowledge_graph is not None
        self._kb_initialized = knowledge_base is not None
    
    @property
    def knowledge_graph(self) -> IKnowledgeGraph:
        """延迟初始化知识图谱"""
        if not self._kg_initialized:
            from ..knowledge import DesignKnowledgeGraph
            logger.info("🔮 延迟初始化设计知识图谱 (Knowledge Graph)...")
            self._knowledge_graph = DesignKnowledgeGraph()
            self._kg_initialized = True
        return self._knowledge_graph
    
    @property
    def knowledge_base(self) -> IKnowledgeBase:
        """延迟初始化知识库"""
        if not self._kb_initialized:
            from ..knowledge import BrandKnowledgeBase
            logger.info("📚 延迟初始化品牌知识库 (RAG Engine)...")
            self._knowledge_base = BrandKnowledgeBase()
            self._kb_initialized = True
        return self._knowledge_base
    
    # ========================================================================
    # Knowledge Graph 相关方法
    # ========================================================================
    
    def infer_design_rules(self, keywords: List[str]) -> Dict[str, Any]:
        """
        根据关键词推理设计规则
        
        Args:
            keywords: 关键词列表（行业/氛围）
            
        Returns:
            推荐规则字典
        """
        if not keywords:
            return {
                "recommended_colors": [],
                "recommended_fonts": [],
                "recommended_layouts": []
            }
        
        logger.info(f"🔮 KG 推理关键词: {keywords}")
        rules = self.knowledge_graph.infer_rules(keywords)
        
        logger.info(f"🔮 KG 推荐颜色: {rules.get('recommended_colors', [])}")
        logger.info(f"🔮 KG 推荐字体: {rules.get('recommended_fonts', [])}")
        logger.info(f"🔮 KG 推荐布局: {rules.get('recommended_layouts', [])}")
        
        return rules
    
    def extract_keywords(self, user_prompt: str) -> List[str]:
        """
        从用户 prompt 中提取 KG 关键词
        
        Args:
            user_prompt: 用户输入的提示词
            
        Returns:
            关键词列表
        """
        # 支持的关键词映射（中英文）
        keyword_mapping = {
            # 行业
            "科技": "Tech", "tech": "Tech", "数码": "Tech", "互联网": "Tech", 
            "ai": "Tech", "人工智能": "Tech",
            "食品": "Food", "food": "Food", "美食": "Food", "餐饮": "Food", "餐厅": "Food",
            "教育": "Education", "education": "Education", "培训": "Education", 
            "学校": "Education", "课程": "Education",
            "时尚": "Fashion", "fashion": "Fashion", "服装": "Fashion", "穿搭": "Fashion",
            "房地产": "Real Estate", "地产": "Real Estate", "楼盘": "Real Estate", 
            "房产": "Real Estate",
            "医疗": "Healthcare", "healthcare": "Healthcare", "健康": "Healthcare", 
            "医院": "Healthcare",
            "金融": "Finance", "finance": "Finance", "银行": "Finance", 
            "理财": "Finance", "投资": "Finance",
            "旅游": "Travel", "travel": "Travel", "旅行": "Travel", "景点": "Travel",
            "音乐": "Music", "music": "Music", "演唱会": "Music", "音乐节": "Music",
            
            # 氛围
            "极简": "Minimalist", "minimalist": "Minimalist", "简约": "Minimalist", 
            "简洁": "Minimalist",
            "活力": "Energetic", "energetic": "Energetic", "动感": "Energetic", 
            "活泼": "Energetic",
            "奢华": "Luxury", "luxury": "Luxury", "高端": "Luxury", "豪华": "Luxury", 
            "尊贵": "Luxury",
            "友好": "Friendly", "friendly": "Friendly", "亲切": "Friendly", 
            "温馨": "Friendly",
            "专业": "Professional", "professional": "Professional", "商务": "Professional", 
            "正式": "Professional",
            "促销": "Promotion", "promotion": "Promotion", "打折": "Promotion", 
            "优惠": "Promotion", "活动": "Promotion",
            "复古": "Vintage", "vintage": "Vintage", "怀旧": "Vintage", "经典": "Vintage",
            "现代": "Modern", "modern": "Modern", "当代": "Modern",
            "自然": "Natural", "natural": "Natural", "环保": "Natural", "绿色": "Natural",
        }
        
        extracted = []
        prompt_lower = user_prompt.lower()
        
        for keyword, kg_keyword in keyword_mapping.items():
            if keyword.lower() in prompt_lower:
                if kg_keyword not in extracted:
                    extracted.append(kg_keyword)
        
        return extracted
    
    def get_kg_stats(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        return self.knowledge_graph.get_graph_stats()
    
    # ========================================================================
    # RAG 相关方法
    # ========================================================================
    
    def search_brand_knowledge(
        self,
        query: str,
        brand_name: Optional[str] = None,
        top_k: int = 2
    ) -> List[Dict[str, Any]]:
        """
        检索品牌知识
        
        Args:
            query: 查询文本
            brand_name: 品牌名称过滤（可选）
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        filter_metadata = {"brand": brand_name} if brand_name else None
        
        logger.info(f"📚 RAG 检索: '{query}' (品牌: {brand_name or '全部'})")
        results = self.knowledge_base.search(query, top_k, filter_metadata)
        logger.info(f"📚 找到 {len(results)} 条结果")
        
        return results
    
    def add_brand_document(
        self,
        text: str,
        brand_name: str,
        category: str,
        doc_id: Optional[str] = None
    ) -> str:
        """
        添加品牌文档到知识库
        
        Args:
            text: 文档内容
            brand_name: 品牌名称
            category: 文档类别
            doc_id: 文档 ID（可选）
            
        Returns:
            文档 ID
        """
        if doc_id is None:
            doc_id = f"{brand_name}_{category}_{hash(text) % 10000}"
        
        metadata = {
            "brand": brand_name,
            "category": category,
            "type": "user_upload"
        }
        
        self.knowledge_base.add_document(text, metadata, doc_id)
        logger.info(f"📚 添加品牌文档: {brand_name} - {category}")
        
        return doc_id
    
    def get_kb_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return self.knowledge_base.get_stats()
    
    # ========================================================================
    # 组合方法（用于 Planner Agent）
    # ========================================================================
    
    def get_design_context(
        self,
        user_prompt: str,
        brand_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取完整的设计上下文（KG + RAG）
        
        供 Planner Agent 使用的高层方法。
        
        Args:
            user_prompt: 用户输入的提示词
            brand_name: 品牌名称（可选）
            
        Returns:
            设计上下文字典
        """
        context = {
            "kg_keywords": [],
            "kg_rules": {},
            "brand_knowledge": []
        }
        
        # 1. KG 推理
        keywords = self.extract_keywords(user_prompt)
        if keywords:
            context["kg_keywords"] = keywords
            context["kg_rules"] = self.infer_design_rules(keywords)
        
        # 2. RAG 检索
        if brand_name:
            # 检索品牌配色
            color_results = self.search_brand_knowledge(
                f"{brand_name}的配色", brand_name, top_k=1
            )
            context["brand_knowledge"].extend(color_results)
            
            # 检索品牌风格
            style_results = self.search_brand_knowledge(
                f"{brand_name}设计风格", brand_name, top_k=1
            )
            context["brand_knowledge"].extend(style_results)
        
        return context
    
    def build_prompt_context(
        self,
        kg_rules: Dict[str, Any],
        brand_knowledge: List[Dict[str, Any]]
    ) -> str:
        """
        构建 LLM Prompt 上下文字符串
        
        Args:
            kg_rules: KG 推理结果
            brand_knowledge: RAG 检索结果
            
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        
        # KG 推荐规则
        if kg_rules and any(kg_rules.values()):
            context_parts.append("【知识图谱推荐】")
            if kg_rules.get("recommended_colors"):
                context_parts.append(f"- 推荐颜色: {', '.join(kg_rules['recommended_colors'])}")
            if kg_rules.get("recommended_fonts"):
                context_parts.append(f"- 推荐字体: {', '.join(kg_rules['recommended_fonts'])}")
            if kg_rules.get("recommended_layouts"):
                context_parts.append(f"- 推荐布局: {', '.join(kg_rules['recommended_layouts'])}")
            context_parts.append("")
        
        # 品牌知识
        if brand_knowledge:
            context_parts.append("【品牌知识库】")
            for doc in brand_knowledge:
                category = doc.get("metadata", {}).get("category", "通用")
                context_parts.append(f"- [{category}] {doc['text']}")
            context_parts.append("")
        
        # 设计指导
        context_parts.append("【设计指导】")
        context_parts.append("请根据上述知识图谱推荐和品牌知识来生成设计简报。")
        context_parts.append("如果没有具体推荐，请根据用户意图自主决策。")
        
        return "\n".join(context_parts)

