# 本示例展示如何使用 crewai 库来创建一个简单的市场调研系统


from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
api_base=os.getenv("OPENAI_BASE_URL")

llm = ChatOpenAI(model="MiniMax-M2.7-highspeed", openai_api_key=api_key, openai_api_base=api_base, max_tokens=512, temperature=0.3)


# 定义 agent (角色)
researcher = Agent(
    role="市场研究员",
    goal="收集并整理关于目标主题的全面、准确的市场信息",
    backstory="你是一位经验丰富的市场分析师，擅长从海量信息中提炼关键洞察",
    llm="MiniMax-M2.7-highspeed",
    verbose=False
)

analyst = Agent(
    role="数据分析师",
    goal="基于研究员提供的信息，进行深度分析并得出有价值的结论",
    backstory="你擅长用数据说话，能发现隐藏在信息背后的趋势和机会",
    llm="MiniMax-M2.7-highspeed",
    verbose=False
)

writer = Agent(
    role="报告撰写专家",
    goal="将分析结论撰写成清晰、专业、有说服力的报告",
    backstory="你有丰富的商业写作经验，能让复杂的分析变得易于理解",
    llm="MiniMax-M2.7-highspeed",
    verbose=False
)

# 定义task (任务)
research_task = Task(
    description="调研中国新能源汽车市场的现状，包括主要品牌、市场份额、增长趋势",
    expected_output="一份包含 5 个关键数据点的市场调研报告，含数字和具体事实,每个要点都在50个字以内",
    agent=researcher
)

analysis_task = Task(
    description="基于调研报告，分析未来 3 年的机会与风险，给出投资评级建议",
    expected_output="SWOT 分析表格 + 投资评级（强烈推荐/推荐/中性/谨慎）+ 理由，总共要在100字以内",
    agent=analyst,
    context=[research_task]
)

write_task = Task(
    description="将调研和分析整合成一份 500 字的专业投资简报，格式清晰",
    expected_output="包含执行摘要、市场现状、机会风险、投资建议四个部分的简报，每个部分在50字以内",
    agent=writer,
    context=[research_task, analysis_task]
)


#组建团队并执行
crew = Crew(
    agents = [researcher, analyst, writer],
    tasks = [research_task, analysis_task, write_task],
    process = Process.sequential,
    verbose=False,
    tracing=False
)

result = crew.kickoff()
print(result)