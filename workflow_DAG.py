#DAG 工作流的简化定义（类似LangGraph风格）

from langgraph import StateGraph


#定义工作流 - 节点间传递的数据对象
class PipelineState:
    raw_data: str = "" # 原始输入数据
    cleaned_data: str = "" #清洗后的数据
    analysis_result: str = "" #分析结果
    final_report: str = ""  # 最终报告


#定义 DAG 节点 - 每个节点是独立的处理单元
def extract_data(state: PipelineState) -> PipelineState:
    """节点1：从 runoob 数据库中提取原始数据"""
    state.raw_data = query_database( "SELECT * FROM logs")
    return state

def clean_data(state: PipelineState) -> PipelineState:
    """节点2：清洗原始数据(去重，标准化格式)"""
    state.cleaned_data = preprocess(state.raw_data)
    return state

def analyze_data(state: PipelineState) -> PipelineState:
    """节点3： 统计分析"""
    state.analysis_result = statistical_analysis(state.cleaned_data)
    return state

def generate_report(state: PipelineState) -> PipelineState:
    """节点4：生成最终报告"""
    state.final_report = llm.generate(
        f"基于一下分析结果生成报告：{state.analysis_result}"
    )
    return state


#构建 DAG：定义节点和变（数据流向）
workflow = StateGraph(PipelineState)
workflow.add_node("extract", extract_data)
workflow.add_node("clean", clean_data)
workflow.add_node("analyze", analyze_data)
workflow.add_node("report", generate_report)

#定义边：extract -> clean -> analyze -> report
workflow.add_edge("extract", "clean")
workflow.add_edge("clean", "analyze")
workflow.add_edge("analyze", "report")
workflow.set_entry_point("extract")
workflow.set_finish_point("report")

#编译并运行
app = workflow.compile()
result = app.invoke(PipelineState())
print(result.final_report)
