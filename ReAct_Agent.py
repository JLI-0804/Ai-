import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import ast 
import operator

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

@tool
def search_web(query: str) -> str:
    """搜索网络最新信息"""
    return f"关于{query}的搜索结果：这是模拟的搜索结果..."

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
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
        raise ValueError(f"不支持的节点类型: {type(node)}")

    try: 
        tree = ast.parse(expression, mode="eval")
        result = safe_eval(tree.body)
        return f"计算结果： {expression} = {result}"
    except (SyntaxError, ValueError) as e:
        return f"表达式解析错误: {e}"   

@tool
def get_weather(city: str) -> str:
    """获取指定城市的当前天气信息"""
    return f"当前{city}的天气是晴天，气温 28°C，湿度 45%"

tools = [search_web, calculate, get_weather]

llm = ChatOpenAI(
    model="MiniMax-M2.7-highspeed",
    api_key=api_key,
    base_url=api_base,
    temperature=0,
    max_tokens=512,
)

llm_with_tools = llm.bind_tools(tools)

def agent_node(state: MessagesState) -> dict:
    """agent 推理节点： 调用LLM决定下一步"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": response}


#react graph 构建
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        END:END
    }
)
builder.add_edge("tools", "agent")

graph = builder.compile()

#运行测试
if __name__ == "__main__":
    result = graph.invoke({
        "messages": [HumanMessage(content="北京天气怎么样？另外再帮我计算1111*2222")]})

    for message in result["messages"]:
        if message.content:
            show_text = message.content[200:]
        else:
            show_text = "(工具调用，无文本内容)"
    print(f"[{message.type}]: {show_text}")