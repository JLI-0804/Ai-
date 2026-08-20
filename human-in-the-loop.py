import os 
from dotenv import load_dotenv

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

def request_node(state: MessagesState) -> dict:
    """请求用户输入"""
    return {"messages": state["messages"]}

def approval_node(state: MessagesState) -> dict:
    """用户审批：暂停等待用户审批"""
    last_msg = state["messages"][-1].content

    # 暂停执行，等待人工处理
    human_decision = interrupt({
        "question": "是否批准以下操作？",
        "action": last_msg
    })
    if human_decision == "approve":
        return {"messages": [AIMessage(content=f"操作已批准：{last_msg}")]}
    else:
        return {"messages": [AIMessage(content=f"操作已拒绝：{last_msg}")]}

def execute_node(state: MessagesState) -> dict:
    """执行操作"""
    return {"messages": [AIMessage(content=f"任务执行完成！")]}

#构件图
builder = StateGraph(MessagesState)
builder.add_node("request", request_node)
builder.add_node("approval", approval_node)
builder.add_node("execute", execute_node)

builder.add_edge(START, "request")
builder.add_edge("request", "approval")
builder.add_edge("approval", "execute")
builder.add_edge("execute", END)


#使用checkpoint 编译图
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


#每次对话使用唯一的session_id
config = {"configurable": {"thread_id": "approval-seesion-001"}}

if __name__ == "__main__":
    # Step 1: 启动图，会在 interrupt 处暂停
    print("=== Step 1: 提交请求 ===")
    result = graph.invoke(
        {"messages": [HumanMessage(content="请删除数据库中的所有测试数据")]},
        config=config
    )
    print("图已暂停，等待审批...")

    # Step 2: 人工审批后，用 Command 恢复执行
    print("\n=== Step 2: 人工审批 ===")
    # 批准操作
    result = graph.invoke(
        Command(resume="approve"),
        config=config
    )
    print(f"最终结果: {result['messages'][-1].content}")

    # 如果要拒绝，使用：
    # result = graph.invoke(Command(resume="reject"), config=config)
    # print(f"最终结果: {result['messages'][-1].content}")