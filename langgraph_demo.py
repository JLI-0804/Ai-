import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

api_base = os.getenv("OPENAI_API_BASE")
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="MiniMax-M2.7-highspeed",
    api_key=api_key,
    base_url=api_base,
    temperature=0.7,
    max_tokens=512,
)

#路由函数'
def classify_intent(state: MessagesState) -> str:
    """根据用户意图路由到不同的Agent"""
    last_message = state["messages"][-1]
    content = last_message.content.lower()

    if "天气" in content or "温度" in content:
        return "weather_agent"
    elif "代码" in content or "编程" in content:
        return "code_agent"
    elif "再见" in content or "退出" in content:
        return "farewell"
    else:
        return "general_agent"


# 定义节点
def router_node(state: MessagesState) -> dict:
    """路由节点不同：不做处理，只用触发路由判断"""
    return{}

def weather_node(state: MessagesState) -> dict:
    """天气Agent"""
    response = llm.invoke(
        [SystemMessage(content="你是一个天气助手，友好地回答天气相关问题。如果没有实时数据，可以给出一般性建议。"),
        *state["messages"]
    ])
    return {"messages": [response]}

def code_node(state: MessagesState) -> dict:
    """代码Agent"""
    response = llm.invoke([
        SystemMessage(content="你是一个编程助手，擅长解答代码问题并给出清晰的代码示例。"),
        *state["messages"]
    ])
    return {"messages": [response]}

def general_node(state: MessagesState) -> dict:
    """通用Agent"""
    response = llm.invoke([
        SystemMessage(content="你是一个友善的 AI 助手，可以回答各种问题。"),
        *state["messages"]
    ])
    return {"messages": [response]}

def farewell_node(state: MessagesState) -> dict:
    """告别节点：✅ 修正为标准 AIMessage 对象，替代原来的dict写法，适配新版add_messages reducer"""
    return{"messages": [AIMessage(content="再见！")]}


#构件图
builder = StateGraph(MessagesState)

#添加节点
builder.add_node("router", router_node)
builder.add_node("weather_agent", weather_node)
builder.add_node("code_agent", code_node)
builder.add_node("general_agent", general_node)
builder.add_node("farewell", farewell_node)

#添加边
builder.add_edge(START, "router")
builder.add_conditional_edges(
    "router",
    classify_intent,
    {
        "weather_agent": "weather_agent",
        "code_agent": "code_agent",
        "general_agent": "general_agent",
        "farewell": "farewell",
    }
)

#所有节点处理完后结束
for node in ["weather_agent", "code_agent", "general_agent", "farewell"]:
    builder.add_edge(node, END)

#编译图   （必须要）
graph = builder.compile()

#测试逻辑
if __name__ == "__main__":
    test_input = [
        "北京今天天气怎么样？",
        "帮我写一个 Python 快速排序",
        "你好，介绍一下你自己",
        "再见啦！"
    ]
    for user_input in test_input:
        print(f"\n用户: {user_input}")
        result = graph.invoke({"messages": [HumanMessage(content=user_input)]})
        print(f"助手: {result['messages'][-1].content[:100]}...")
        print("-" * 50)