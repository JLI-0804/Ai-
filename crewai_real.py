from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

# 配置LLM
llm = LLM(
    model="openai/MiniMax-M2.7-highspeed",   ###关键，必须含有服务商，然后再写模型
    api_key=api_key,
    api_base=api_base,
    temperature=0.4
)


#Agents 各种agent 配置
researcher = Agent(
    role="技术研究员",
    goal="寻找最新，准确，可验证的技术资料，并给出代码证明",
    backstory="擅长系统性分析技术问题，注重事实和可复现性",
    llm=llm,
    verbose=True,
    allow_delegation=True
)

writer = Agent(
    role="技术博客作家",
    goal="将研究成果整理成适合初学者阅读的技术文章。",
    backstory="擅长将复杂概念拆解为清晰步骤，并提供完整示例。",
    llm=llm,
    verbose=True,
    allow_delegation=True
)

# Tasks 配置
reseracher_task = Task(
    description=(
        "深入研究：使用 Python 进行自动化数据清洗。\n"
        "重点包括：pandas、numpy、缺失值、重复值、格式不一致问题。\n"
        "必须提供完整、可运行的代码示例。"
    ),
    agent = researcher,
    expected_output=("一份研究报告，包含问题分类、解决方案代码和完整清洗流程。"),
)

writer_task = Task(
    description=(
        "基于研究报告，撰写入门级技术博客。\n"
        "标题：《Python 数据清洗入门：用 pandas 告别脏数据》。"
    ),
    agent = writer,
    context=[reseracher_task],
    expected_output=("一份大约200字的技术博客文章，包含数据清洗的基本概念、步骤和示例代码。"),
)

#crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[reseracher_task, writer_task],
    process=Process.sequential,
    verbose=True,
    max_tokens=1024,
    max_retries=3,
)

# Run
if __name__ == '__main__':
    result = crew.kickoff()

    output = result.raw

    with open("python_data_cleaning_blog.md", "w", encoding="utf-8") as f:
        f.write(output)
