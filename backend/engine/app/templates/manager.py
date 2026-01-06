"""
模板管理器

负责模板的加载、选择和匹配
"""

from typing import Optional, List, Dict, Any
from .models import StyleTemplate
from .templates import STYLE_TEMPLATES, DEFAULT_TEMPLATE_ID
from ..core.logger import logger


class TemplateManager:
    """
    模板管理器
    
    提供模板的获取、智能选择和匹配功能
    """

    def __init__(self):
        self.templates = STYLE_TEMPLATES
        self.default_template_id = DEFAULT_TEMPLATE_ID

    def get_template(self, template_id: str) -> Optional[StyleTemplate]:
        """
        根据 ID 获取模板
        
        Args:
            template_id: 模板 ID
            
        Returns:
            StyleTemplate 或 None
        """
        template = self.templates.get(template_id)
        if not template:
            logger.warning(f"模板 {template_id} 不存在，返回 None")
        return template

    def get_default_template(self) -> StyleTemplate:
        """获取默认模板"""
        return self.templates[self.default_template_id]

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        列出所有可用模板
        
        Returns:
            模板摘要列表
        """
        return [
            {
                "id": template.id,
                "name": template.name,
                "display_name": template.display_name,
                "description": template.description,
                "use_cases": template.use_cases,
                "example_prompts": template.example_prompts,
            }
            for template in self.templates.values()
        ]

    def smart_match_template(
        self,
        user_prompt: str,
        intent: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> StyleTemplate:
        """
        智能匹配模板
        
        根据用户输入、意图和关键词智能选择最合适的模板
        
        Args:
            user_prompt: 用户输入的提示词
            intent: 意图类型（如果已识别）
            keywords: 关键词列表（如果已提取）
            
        Returns:
            最匹配的 StyleTemplate
        """
        prompt_lower = user_prompt.lower()
        matched_template_id = None
        max_score = 0

        # 为每个模板计算匹配分数
        for template_id, template in self.templates.items():
            score = 0

            # 1. 检查用户prompt中是否包含模板的关键词
            for keyword in template.style_preference.keywords:
                if keyword in user_prompt or keyword.lower() in prompt_lower:
                    score += 2

            # 2. 检查用户prompt中是否包含使用场景
            for use_case in template.use_cases:
                if use_case in user_prompt:
                    score += 3

            # 3. 检查示例提示词的相似度
            for example in template.example_prompts:
                if example in user_prompt:
                    score += 5

            # 4. 检查意图匹配（如果提供）
            if intent:
                # 商务风格：business, meeting, corporate, professional
                if template_id == "business" and intent in [
                    "business",
                    "corporate",
                    "meeting",
                    "training",
                ]:
                    score += 4

                # 校园风格：campus, student, school, club
                elif template_id == "campus" and intent in [
                    "campus",
                    "student",
                    "school",
                    "club",
                ]:
                    score += 4

                # 活动风格：event, concert, party, exhibition
                elif template_id == "event" and intent in [
                    "event",
                    "concert",
                    "party",
                    "exhibition",
                    "performance",
                ]:
                    score += 4

                # 产品风格：product, promotion, sale, shopping
                elif template_id == "product" and intent in [
                    "product",
                    "promotion",
                    "sale",
                    "shopping",
                    "ecommerce",
                ]:
                    score += 4

                # 节日风格：festival, holiday, celebration
                elif template_id == "festival" and intent in [
                    "festival",
                    "holiday",
                    "celebration",
                    "newyear",
                ]:
                    score += 4

            # 5. 检查关键词匹配（如果提供）
            if keywords:
                for kw in keywords:
                    if kw in template.style_preference.keywords:
                        score += 1

            # 更新最高分
            if score > max_score:
                max_score = score
                matched_template_id = template_id

        # 如果没有匹配到任何模板，返回默认模板
        if matched_template_id is None:
            logger.info(f"未找到匹配的模板，使用默认模板：{self.default_template_id}")
            return self.get_default_template()

        logger.info(
            f"智能匹配到模板：{matched_template_id}（得分：{max_score}）"
        )
        return self.templates[matched_template_id]

    def get_template_by_use_case(self, use_case: str) -> Optional[StyleTemplate]:
        """
        根据使用场景获取模板
        
        Args:
            use_case: 使用场景（如："企业宣传"、"社团招新"）
            
        Returns:
            匹配的 StyleTemplate 或 None
        """
        for template in self.templates.values():
            if use_case in template.use_cases:
                logger.info(f"根据使用场景 '{use_case}' 匹配到模板：{template.id}")
                return template

        logger.warning(f"未找到使用场景 '{use_case}' 对应的模板")
        return None


# 全局单例
template_manager = TemplateManager()

