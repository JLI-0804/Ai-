# 反思架构的简化实现

class ReflectiveAgent:
    """带自我反思能力的AGENT"""

    def __init__(self, model, tools, max_relection=3):
        self.model = model
        self.tools = tools
        self.max_relection = max_relection  #修正次数，防止死循环

    def run(self, task:str) -> str:
        """第一步： 正常执行，产生初始输出"""
        output = self.model.generate(task)

        for i in range(self.max_relection):
            #第二步：反思-评估输出质量
            critique = self.model.generate(f"""
            请严格评估以下输出：
            原始任务：{task}
            当前输出：{output}
            检查：事实错误？逻辑漏洞？遗漏信息？格式问题？
            如果输出完美无缺，请回复 "PASS"。
            """)
            if "PASS" in critique:
                break # 输出通过审查

            #第三步：修正-根据批评意见改进
            output = self.model.generate(f"""
            原始任务：{task}
            上次输出：{output}
            问题反馈：{critique}
            请根据反馈修正输出。
            """)


        return output

#使用示例
agent = ReflectiveAgent(model=model, tools={})
code = agent.run("编写一个 python 函数， 实现 runoob 字符串的 aes 加密")

# Agent 生成代码后自我检查加密实现、密钥处理，
# 发现漏洞后自动修正，确保输出安全可靠
