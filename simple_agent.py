# 单agent循环的简化实现
class SimpleAgent:
    """单agent 循环的基本结构"""

    def __init__(self, model, tools ,max_turns=5):
        self.model = model  # 大语言模型
        self.tools = tools  # 可用工具列表
        self.max_turns = max_turns   #最大循环轮次，防止无限循环

    def run(self, task: str) -> str:
        """ 执行任务的主循环"""
        context = f"用户任务：{task}"

        for turn in range(self.max_turns):
            # 1.思考—— 让模型决定下一步
            response = self.model.think(context)

            # 如果模型认定为任务完成，则返回答案
            if response.is_final():
                return response.content

            #第二步：行动- 调用模型选择工具
            tool_name = response.tool_choice
            tool_args = response.tool_args
            tool_result = self.tools[tool_name](**tool_args)


            #第三部：将工具结果反馈给大模型，进入下一轮
            context += f"\n工具{tool_name}返回：{tool_result}"

        return "达到最大次数，未有完成任务"

# 使用示例
agent = SimpleAgent(model=llm, tools={
    "read_file":read_file,
    "search_code":search_code,
    "run_test": run_test
})
result = agent.run("修复 runoob 项目中的 user.py 的类型错误")