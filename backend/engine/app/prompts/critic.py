"""
Critic Agent Prompt - 海报质量审核
"""
import json
from typing import Dict, Any


SYSTEM_PROMPT = """
你是一个海报质量审核员。检查生成的海报数据是否符合要求。

【检查项】
1. 文字是否遮挡了前景图层（特别是人物）的面部区域？
2. 文字是否超出画布范围？
3. 文字对比度是否合格（文字是否与相邻图层对比度足够）？
4. 图层顺序是否正确（背景在下，前景在中，文字在上）？
5. 所有图层是否都有有效的 width 和 height？

【输出格式】
请输出 JSON：
{{
    "status": "PASS" | "REJECT",
    "feedback": "审核意见（如果通过则写'通过'，如果不通过则用自然语言详细描述问题）",
    "issues": ["问题1", "问题2"]  // 如果 status 是 REJECT，依次列出所有问题
}}

【注意】
1. 如遇到无法判断的情况，如因没有前景图层而无法判断文字是否遮挡前景图层等情况，请默认没有问题。
2. 无需非常严格，仅需确保海报质量基本合格即可。
"""


USER_PROMPT_TEMPLATE = """
【输入】
海报数据: {poster_data}

请检查并输出审核结果。
"""


def get_prompt(poster_data: Dict[str, Any]) -> Dict[str, str]:
    """
    获取 Critic Agent 的 prompt
    
    Args:
        poster_data: 海报数据
        
    Returns:
        包含 system 和 user prompt 的字典
    """
    return {
        "system": SYSTEM_PROMPT,
        "user": USER_PROMPT_TEMPLATE.format(
            poster_data=json.dumps(poster_data, ensure_ascii=False, indent=2)
        ),
    }

