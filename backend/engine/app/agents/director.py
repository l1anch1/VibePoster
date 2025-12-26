import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 里的 API Key
load_dotenv()

# 初始化 DeepSeek 客户端 (兼容 OpenAI 协议)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
)


def run_director_agent(user_prompt: str):
    print(f"🕵️ Director Agent 正在思考: {user_prompt}...")

    system_prompt = """
    你是一个专业的海报设计总监。你的任务是将用户的模糊需求转化为结构化的设计简报。
    
    请严格按照以下 JSON 格式输出，不要包含 Markdown 格式（如 ```json ... ```）：
    {
        "title": "海报主标题 (简短有力)",
        "subtitle": "副标题 (补充说明)",
        "main_color": "主色调Hex值 (如 #FF0000)",
        "background_color": "背景色Hex值",
        "style_keywords": ["风格关键词1", "关键词2"]
    }
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # 或者 deepseek-reasoner
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},  # 强制让模型吐出 JSON
        )

        content = response.choices[0].message.content
        print(f"✅ Director 思考完毕: {content}")

        # 将字符串转为 Python 字典
        return json.loads(content)

    except Exception as e:
        print(f"❌ Director 出错: {e}")
        # 出错时的兜底方案
        return {
            "title": "生成失败",
            "subtitle": "请检查 API Key",
            "main_color": "#000000",
            "background_color": "#FFFFFF",
        }
