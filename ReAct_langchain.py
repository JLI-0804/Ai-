from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
import datetime
from dotenv import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

# ─── 定义工具 ────────────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """获取指定城市的当前天气信息"""
    # 实际项目中替换为真实天气 API
    mock_data = {
        "北京": "晴天，气温 22°C，微风",
        "上海": "多云，气温 26°C，湿度 75%",
        "广州": "小雨，气温 30°C，建议带伞",
    }
    return mock_data.get(city, f"暂无 {city} 的天气数据")

@tool
def search_web(query: str) -> str:
    """在网络上搜索信息，返回相关内容摘要"""
    # 实际项目中接入 Tavily / Serper API
    return f"搜索 '{query}' 的结果：这是一个模拟的搜索结果..."

@tool
def calculate(expression: str) -> str:
    """计算数学表达式，例如 '2 + 3 * 4'"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误：{e}"

@tool
def get_date() -> str:
    """获取今天的日期"""
    return datetime.date.today().strftime("%Y年%m月%d日")

# ─── 创建 Agent ───────────────────────────────────────────────
tools = [get_weather, search_web, calculate, get_date]
llm = ChatOpenAI(model="MiniMax-M2.7-highspeed", api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, temperature=0)

agent = create_agent(model=llm,
    tools=tools,
    system_prompt="你是一个有用的助手，可以查天气、搜索信息、做数学计算和查日期。请一步步调用工具完成任务。")


# ─── 运行 ────────────────────────────────────────────────────
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "今天是几号？上海天气怎么样？如果出门步行 5km 消耗约 300 卡路里，"
                           "跑步同样距离消耗大约是步行的 1.6 倍，请计算跑步消耗的卡路里。",
            }
        ]
    },
    config={"recursion_limit": 25},   # ← 替代旧的 max_iterations，防止无限循环)
    )
print(result["messages"][-1].content)
