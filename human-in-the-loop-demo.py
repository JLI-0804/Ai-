# LangGraph 支持在关键步骤暂停，等待人工确认后再继续执行
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict
from langgraph.types import interrupt

class EmailState(TypedDict):
    recipient: str
    content: str | None
    approved: bool

def draft_email(state: EmailState) -> EmailState:
    """起草邮件， 完成后触发人工中断审核"""
    content = f"尊敬的{state['recipient']}，\n\n 这是AI起草的邮件内容...\n\n此致"

    # ✅关键点：先返回把content写入state，再interrupt。
    # 机制：return 的字典会先合并到state，然后才执行interrupt暂停
    # interrupt的payload仅用于携带提示信息，不写入state

    interrupt(
        {
            "task": "邮件审核",
            "recipient": state["recipient"],
            "content": content
        }
    )
    return {"content": content}

def send_email(state: EmailState) -> EmailState:
    """发送邮件（高风险操作，需要人工审核后才执行"""
    print(f"邮件已发送给{state['recipient']}")
    return {}


#路由： 根据人工审核结果决定是否发送
def check_approval(state: EmailState) -> str:
    return "send" if state.get("approved") else END

workflow = StateGraph(EmailState)

workflow.add_node("draft", draft_email)
workflow.add_node("send", send_email)

workflow.add_edge(START, "draft")
workflow.add_conditional_edges(
    source="draft",
    path=check_approval,
    path_map={"send": "send", END: END}
)

workflow.add_edge("send",END)

memory = MemorySaver()

app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id":"email-001"}}

#第一次运行，执行到draft内部interrupt会自动暂停
app.invoke({"recipient": "客户A", "approved": False}, config)
snapshot = app.get_state(config)
current_state = snapshot.values

#兼容：优先从state拿content，如果为空，从interrupt携带的载荷拿
interrupt_payload = snapshot.tasks[0].interrupts[0].value if snapshot.tasks else None
content = current_state.get("content") or (interrupt_payload.get("content") if interrupt_payload else None)

print("草稿已生成，等待审核：")
print(content)


#模拟人工审核
user_input = input("是否确认发送邮件？(y/n): ")
if user_input.lower() == "y":
    app.update_state(config, {"approved": True})
    app.invoke(None, config)
    print("邮件已发送")
else:
    print("邮件发送已取消")
