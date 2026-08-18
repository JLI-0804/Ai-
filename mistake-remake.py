# 重试和错误处理
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=5)
)

def claa_llm_with_retry(promt: str) -> str:
    try:
        response = llm.invoke(promt)
        return response.content
    except Exception as e:
        logging.error(f"LLM调用失败: {e}")
        raise

def safe_parse_json(text: str) ->dict:
    """安全解析 LLM 输出的JSON"""
    import json, re
    # 提取json 部分
    json_match = re.search(r'\{.*\}', text ,re.DOTALL)
    if json_mathc:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return {"error":"解析失败", "raw": text}  