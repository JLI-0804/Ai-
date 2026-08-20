import os
import ast
import operator
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent



load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

llm = ChatOpenAI(
    model="MiniMax-M2.7-highspeed",
    api_key=api_key,
    base_url=api_base,
    temperature=0,
    max_tokens=512,
)

#定义工具
@tool
def get_current_weather(city: str) -> str:
    """获取指定城市的当前天气信息。当用户询问天气时使用此工具。
    Args:
        city：需要查询天气的城市名称。
    """

    #模拟天气接口
    weather_data = {
        "北京": "晴天，气温 28°C，湿度 45%",
        "上海": "多云，气温 25°C，湿度 70%",
        "深圳": "雷阵雨，气温 30°C，湿度 85%",
    }
    return weather_data.get(city, f"抱歉，暂无{city}的天气数据")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。当用户需要进行数学计算时使用此工具。
    支持基本的四则运算，幂运算，如 '2 + 3 * 4'、'2**10'。
    Args:
        expression: 待计算的数学表达式字符串。
    """
    #ast 安全解析，拒绝eval()直接执行，防止代码注入
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def safe_eval(node):
        if isinstance(node, ast.Expression):
            return safe_eval(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = safe_eval(node.left)
            right = safe_eval(node.right)
            return ops[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = safe_eval(node.operand)
            return ops[type(node.op)](operand)
        else:
            raise ValueError(f"不支持的表达类型: {type(node)}")

    try:
        tree = ast.parse(expression, mode='eval')
        result = safe_eval(tree)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

@tool
def search_knowledge(query: str) -> str:
    """搜索知识库获取相关信息。当用户询问事实性问题时使用此工具。
    Args:
        query: 用户的查询关键词
    """
    #模拟知识库
    knowledge = {
        "LangChain": "LangChain 是一个用于构建 LLM 应用的开源框架，支持链式调用、记忆管理和工具集成。",
        "Python": "Python 是一种高级编程语言，以简洁易读著称，广泛用于 AI、数据科学等领域。",
    }
    for key, value in knowledge.items():
        if key.lower() in query.lower():
            return value
    return f"未找到和{query}相关的信息"

#组装工具列表给agent
tools = [get_current_weather, calculate, search_knowledge]

# 使用 langgraph 的 create_react_agent 创建 agent（langchain 1.x 推荐方式）
agent_executor = create_react_agent(
    llm,
    tools,
    prompt="你是一个功能强大的 AI 助手，可以使用工具来帮助用户。根据用户的问题，判断是否需要使用工具，选择最合适的工具来获取信息。",
)

if __name__ == "__main__":
    # 测试1：天气查询
    print("=" * 60)
    resp1 = agent_executor.invoke({"messages": [HumanMessage(content="北京今天天气怎么样？")]})
    print(f"\n【最终回答】{resp1['messages'][-1].content}")

    # 测试2：数学计算
    print("\n" + "=" * 60)
    resp2 = agent_executor.invoke({"messages": [HumanMessage(content="帮我算一下 (15 * 37 + 228) / 3 等于多少")]})
    print(f"\n【最终回答】{resp2['messages'][-1].content}")

    # 测试3：综合问题，agent自动调用多个不同工具
    print("\n" + "=" * 60)
    resp3 = agent_executor.invoke({"messages": [HumanMessage(content="LangChain 是什么？另外帮我算下 2 的 10 次方")]})
    print(f"\n【最终回答】{resp3['messages'][-1].content}")