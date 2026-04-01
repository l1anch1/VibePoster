"""
Skills 模块测试

测试所有 Skill 的功能和集成流程。

Author: VibePoster Team
Date: 2025-01
"""

import pytest
from app.skills import (
    IntentParseSkill,
    DesignRuleSkill,
    BrandContextSkill,
    DesignBriefSkill,
    SkillOrchestrator,
    IntentParseInput,
    IntentParseOutput,
    DesignRuleInput,
    DesignRuleOutput,
    BrandContextInput,
    BrandContextOutput,
    DesignBriefInput,
    DesignBriefOutput,
    SkillResult,
    SkillStatus,
)


# ============================================================================
# IntentParseSkill 测试
# ============================================================================

class TestIntentParseSkill:
    """IntentParseSkill 测试类"""
    
    @pytest.fixture
    def skill(self):
        return IntentParseSkill()
    
    def test_skill_name(self, skill):
        assert skill.name == "intent_parse"
    
    def test_parse_tech_industry(self, skill):
        result = skill(IntentParseInput(user_prompt="帮我做一个科技风格的海报"))
        assert result.is_success()
        assert result.output.industry == "Tech"
        assert "Tech" in result.output.extracted_keywords
    
    def test_parse_food_industry(self, skill):
        result = skill(IntentParseInput(user_prompt="设计一个美食餐厅的宣传海报"))
        assert result.is_success()
        assert result.output.industry == "Food"
    
    def test_parse_minimalist_vibe(self, skill):
        result = skill(IntentParseInput(user_prompt="我想要一个简约风格的海报"))
        assert result.is_success()
        assert result.output.vibe == "Minimalist"
        assert "Minimalist" in result.output.extracted_keywords
    
    def test_parse_promotion_type(self, skill):
        result = skill(IntentParseInput(user_prompt="双十一打折促销海报"))
        assert result.is_success()
        assert result.output.poster_type == "promotion"
    
    def test_parse_event_type(self, skill):
        result = skill(IntentParseInput(user_prompt="新品发布会邀请函"))
        assert result.is_success()
        assert result.output.poster_type in ["event", "invitation"]
    
    def test_parse_brand_apple(self, skill):
        result = skill(IntentParseInput(user_prompt="苹果新品发布会海报"))
        assert result.is_success()
        assert result.output.brand_name in ["苹果", "Apple"]
    
    def test_parse_brand_huawei(self, skill):
        result = skill(IntentParseInput(user_prompt="华为手机宣传海报"))
        assert result.is_success()
        assert result.output.brand_name in ["华为", "Huawei"]
    
    def test_parse_multiple_keywords(self, skill):
        result = skill(IntentParseInput(
            user_prompt="帮我做一个科技风格极简设计的海报"
        ))
        assert result.is_success()
        assert result.output.industry == "Tech"
        assert result.output.vibe == "Minimalist"
        assert len(result.output.extracted_keywords) >= 2
    
    def test_parse_key_elements(self, skill):
        result = skill(IntentParseInput(
            user_prompt="2025年双十一5折促销活动海报"
        ))
        assert result.is_success()
        assert len(result.output.key_elements) > 0
        elements_str = " ".join(result.output.key_elements)
        assert "2025年" in elements_str or "5折" in elements_str
    
    def test_parse_empty_prompt(self, skill):
        result = skill(IntentParseInput(user_prompt="海报"))
        assert result.is_success()
        assert result.output.poster_type == "promotion"
    
    def test_confidence_full_vs_vague(self, skill):
        result_full = skill(IntentParseInput(
            user_prompt="苹果科技公司极简风格新品发布会海报"
        ))
        result_vague = skill(IntentParseInput(user_prompt="做个海报"))
        assert result_full.output.confidence > result_vague.output.confidence


# ============================================================================
# DesignRuleSkill 测试
# ============================================================================

class TestDesignRuleSkill:
    """DesignRuleSkill 测试类"""
    
    @pytest.fixture
    def skill(self):
        return DesignRuleSkill()
    
    def test_skill_name(self, skill):
        assert skill.name == "design_rule"
    
    def test_infer_tech_rules(self, skill):
        result = skill(DesignRuleInput(industry="Tech"))
        assert result.output is not None
        if result.output.emotions:
            assert any(e in result.output.emotions for e in ["Trust", "Innovation"])
    
    def test_infer_minimalist_rules(self, skill):
        result = skill(DesignRuleInput(vibe="Minimalist"))
        assert result.output is not None
        if result.output.emotions:
            assert any(e in result.output.emotions for e in ["Premium", "Trust"])
    
    def test_infer_combined_rules(self, skill):
        result = skill(DesignRuleInput(industry="Tech", vibe="Minimalist"))
        assert result.output is not None
        if result.output.emotions:
            assert len(result.output.emotions) >= 2
    
    def test_infer_returns_colors(self, skill):
        result = skill(DesignRuleInput(industry="Tech"))
        assert result.output is not None
        if not result.output.is_empty():
            assert len(result.output.color_palettes) > 0
    
    def test_infer_empty_input(self, skill):
        result = skill(DesignRuleInput())
        assert result.is_success()
        assert result.output.is_empty()
    
    def test_source_keywords_tracking(self, skill):
        result = skill(DesignRuleInput(industry="Tech", vibe="Minimalist"))
        assert result.output is not None
        assert "Tech" in result.output.source_keywords
        assert "Minimalist" in result.output.source_keywords
    
    def test_get_supported_keywords(self, skill):
        keywords = skill.get_supported_keywords()
        assert "industries" in keywords
        assert "vibes" in keywords
        assert "Tech" in keywords["industries"]


# ============================================================================
# BrandContextSkill 测试
# ============================================================================

class TestBrandContextSkill:
    """BrandContextSkill 测试类"""
    
    @pytest.fixture
    def skill(self):
        return BrandContextSkill()
    
    def test_skill_name(self, skill):
        assert skill.name == "brand_context"
    
    def test_search_known_brand(self, skill):
        """测试已知品牌检索"""
        result = skill(BrandContextInput(brand_name="华为"))
        # 无论是否检索到，都不应该失败
        assert result.output is not None
        assert result.output.brand_name == "华为"
    
    def test_search_unknown_brand(self, skill):
        """测试未知品牌检索"""
        result = skill(BrandContextInput(brand_name="不存在的品牌"))
        assert result.output is not None
        assert result.output.brand_name == "不存在的品牌"
    
    def test_custom_aspects(self, skill):
        """测试自定义检索方面"""
        result = skill(BrandContextInput(
            brand_name="苹果",
            aspects=["color"]
        ))
        assert result.output is not None
    
    def test_output_structure(self, skill):
        """测试输出结构完整性"""
        result = skill(BrandContextInput(brand_name="测试品牌"))
        output = result.output
        assert hasattr(output, "brand_name")
        assert hasattr(output, "brand_colors")
        assert hasattr(output, "brand_style")
        assert hasattr(output, "guidelines")
        assert hasattr(output, "source_documents")


# ============================================================================
# Skills 集成测试
# ============================================================================

class TestSkillsIntegration:
    """Skills 集成测试"""
    
    def test_intent_to_design_rule_flow(self):
        """测试 意图解析 → 设计规则推理 流程"""
        intent_skill = IntentParseSkill()
        intent_result = intent_skill(IntentParseInput(
            user_prompt="帮我做一个科技公司的极简风格宣传海报"
        ))
        
        assert intent_result.is_success()
        intent_output = intent_result.output
        
        rule_skill = DesignRuleSkill()
        rule_result = rule_skill(DesignRuleInput(
            industry=intent_output.industry,
            vibe=intent_output.vibe
        ))
        
        assert rule_result.output is not None
        assert intent_output.industry == "Tech"
        assert intent_output.vibe == "Minimalist"
    
    def test_intent_to_brand_context_flow(self):
        """测试 意图解析 → 品牌上下文 流程"""
        intent_skill = IntentParseSkill()
        intent_result = intent_skill(IntentParseInput(
            user_prompt="华为手机发布会海报"
        ))
        
        assert intent_result.is_success()
        assert intent_result.output.brand_name in ["华为", "Huawei"]
        
        brand_skill = BrandContextSkill()
        brand_result = brand_skill(BrandContextInput(
            brand_name=intent_result.output.brand_name
        ))
        
        assert brand_result.output is not None


# ============================================================================
# 依赖注入测试
# ============================================================================

class TestSkillDependencies:
    """Skill 依赖注入测试"""
    
    def test_get_intent_parse_skill(self):
        from app.core.dependencies import get_intent_parse_skill, reset_skill_cache
        reset_skill_cache()

        skill1 = get_intent_parse_skill()
        skill2 = get_intent_parse_skill()
        assert skill1 is skill2
        assert skill1.name == "intent_parse"

    def test_get_design_rule_skill(self):
        from app.core.dependencies import get_design_rule_skill, reset_skill_cache
        reset_skill_cache()

        skill1 = get_design_rule_skill()
        skill2 = get_design_rule_skill()
        assert skill1 is skill2
        assert skill1.name == "design_rule"

    def test_get_brand_context_skill(self):
        from app.core.dependencies import get_brand_context_skill, reset_skill_cache
        reset_skill_cache()

        skill1 = get_brand_context_skill()
        skill2 = get_brand_context_skill()
        assert skill1 is skill2
        assert skill1.name == "brand_context"

    def test_get_design_brief_skill(self):
        from app.core.dependencies import get_design_brief_skill, reset_skill_cache
        reset_skill_cache()

        skill1 = get_design_brief_skill()
        skill2 = get_design_brief_skill()
        assert skill1 is skill2
        assert skill1.name == "design_brief"
