import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated

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

# LangGraph 的 state 类型，messages 用 add_messages reducer 自动追加
class State(TypedDict):
    messages: Annotated[list, add_messages]

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的助手"),
    MessagesPlaceholder(variable_name="messages"),
])

# 定义节点：调用 LLM
def call_llm(state: State):
    return {"messages": [llm.invoke(prompt.invoke(state))]}

# 构建图
workflow = StateGraph(State)
workflow.add_node("llm", call_llm)
workflow.add_edge(START, "llm")
workflow.add_edge("llm", END)

# MemorySaver 自动保存每个 thread_id 的对话历史
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    print("--- 已进入 MiniMax-M2.7-highspeed 聊天模式 (输入 'exit' 或 退出 退出) | LangGraph ---")
    config = {"configurable": {"thread_id": "user_001"}}

    while True:
        user_input = input("你：")
        if user_input.lower() in ["exit", "quit", "退出"]:
            print("助手：再见！")
            break

        result = app.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )
        print(f"AI：{result['messages'][-1].content}\n")