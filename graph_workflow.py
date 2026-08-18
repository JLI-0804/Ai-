from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.checkpoint.memory import InMemorySaver
import operator
import os
from dotenv import load_dotenv
from langchain_core.messages import AIMessageChunk


#获取信息
load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
api_base=os.getenv("OPENAI_BASE_URL")

#  定义状态结构（在节点件传递数据）
class ResearchState(TypedDict):
    topic: str   # 研究主题
    research_notes: str  #研究笔记
    draft: str   #草稿
    review_feedback: str   #审阅意见
    final_report: str   #最终报告
    revision_count: int  #修改次数（累加）

llm = ChatOpenAI(model="MiniMax-M2.7-highspeed", openai_api_key=api_key, openai_api_base=api_base, temperature=0.2, max_tokens=512)


#节点函数
def research_node(state):
    chunks = []
    for chunk in llm.stream(f"简要列出5个要点：{state['topic']}"):
        chunks.append(chunk.content)
    return {"research_notes": "".join(chunks)}

def write_node(state: ResearchState) -> dict:
    feedback = state.get("review_feedback") or ""
    prompt = f"""
    主题：{state['topic']}
    调研笔记： {state['research_notes']}
    {'上次审阅意见：' + feedback if feedback else ''}

    请根据以上内容撰写一份100字左右的分析报告草稿。
    """
    response = llm.invoke(prompt)
    new_rev = state["revision_count"] + 1
    return {"draft": response.content, "revision_count": new_rev}


def review_node(state: ResearchState) -> dict:
    response = llm.invoke(
        f"审阅以下报告，如果质量达标回复'APPROVED'，否则给出具体修改意见：\n\n{state['draft']}"
    )
    return {"review_feedback": response.content}

def finalize_node(state: ResearchState) -> dict:
    return {"final_report": state["draft"]}


# 路由函数
def should_revise(state: ResearchState) -> str:
    if "APPROVED" in state["review_feedback"]:
        return "finalize"
    elif state["revision_count"] >= 3:
        return "finalize"
    else:
        return "revise"

# 构建工作流图
workflow = StateGraph(ResearchState)

workflow.add_node("research", research_node)
workflow.add_node("write", write_node)
workflow.add_node("review", review_node)
workflow.add_node("finalize", finalize_node)


#新版用： start 常量代替 set_entry_point()
workflow.add_edge(START, "research")

workflow.add_edge("research", "write")
workflow.add_edge("write", "review")

workflow.add_conditional_edges(
    "review",
    should_revise,
    {
        "revise":"write",
        "finalize":"finalize"
    },
)

workflow.add_edge("finalize", END)


#  编译 （checkpoint + 中断点）
checkpointer = InMemorySaver()
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["finalize"],  # 在最终定稿前暂停，等待人工审核
    )

config = {"configurable": {"thread_id": "session-001"}}   # 会话ID，用于断点续跑

print("=" * 60)
print("▶ 第一阶段：流式执行到 finalize 前自动暂停")
print("=" * 60)

for chunk in app.stream(
    {"topic": "生成式 AI 对软件开发行业的影响", "revision_count": 0},
    config=config,
    stream_mode="updates"   #每个节点执行后增量更新状态
) :
    # chunk 可能是 {"节点名": 状态增量}，也可能是 (__interrupt__,) 这样的 tuple
    if isinstance(chunk, dict):
        for node_name, node_output in chunk.items():
            print(f"\n🔹 [{node_name}] 执行完毕")
            if isinstance(node_output, dict):
                for key, value in node_output.items():
                    print(f"   {key}: {str(value)[:200]}...")
            else:
                print(f"   {node_output}")
    else:
        print(f"\n⏸  中断/控制事件: {chunk}")

# 查看当前状态（断点处）
print("\n" + "=" * 60)
print("▶ 第二阶段：检查断点状态")
print("=" * 60)

state = app.get_state(config)
print(f"下一个待执行节点: {state.next}")           # 应输出 ('finalize',)
print(f"当前草稿预览: {state.values['draft'][:150]}...")

#人工审核逻辑
user_input = input(("是否确认定稿？(y/n): "))
if user_input != "y":
    new_rev = state.values.get("revision_count", 0) + 1
    app.update_state(config, {"review_feedback": user_input, "revision_count": new_rev})

# 恢复执行（传入 None 表示不注入新输入，沿用上次状态继续跑）
print("\n" + "=" * 60)
print("▶ 第三阶段：恢复执行，完成最终定稿")
print("=" * 60)


for chunk in app.stream(None, config=config, stream_mode="updates"):
    if isinstance(chunk, dict):
        for node_name, node_output in chunk.items():
            print(f"\n🔹 [{node_name}] 执行完毕")
            if isinstance(node_output, dict):
                for key, value in node_output.items():
                    print(f"   {key}: {str(value)[:200]}...")
            else:
                print(f"   {node_output}")
    else:
        print(f"\n⏸  中断/控制事件: {chunk}")


#获取最终结果
final_state = app.get_state(config)
print("\n" + "=" * 60)
print("📄 最终报告：")
print("=" * 60)
print(final_state.values["final_report"])