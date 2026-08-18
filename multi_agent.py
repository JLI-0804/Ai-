# 多agent 协作 简化实现

class Orchestrator:
    """编辑器：负责任务拆解、发布和结果汇总"""

    def __init__(self):
        self.subagents = {
            "code_review": Subagent(
                name="代码审查",
                tools=["read_file", "static_analysis"],
                system_prompt = "你是代码审核专家..."
            ),
            "security": Subagent(
                name="安全监测",
                tools=["scan_vulnerability", "check_deps"],
                system_prompt = "你是安全检测专家..."
            ),
            "performance": Subagent(
                name="性能分析",
                tools=["profile_code", "analyze_complexity"],
                system_prompt = "你是性能分析专家..."
          ),
        }

    def handle_task(self, task:str) -> dict:
        # 第一步：分析任务，决定用哪些subagent
        needed = self.plan(task)

        #第二步：并行分布（各 subagent 同时工作，独立上下文）
        results = []
        for agent_name in needed:
            sub_task = self.decompose(task, agent_name)
            results[agent_name] = self.subagents[agent_name].run(sub_task)

        #第三步：汇总各 subagent 的结果，综合输出
        return self.synthesize(task, results)


#使用示例：一次运行，三个维度并行分析
orch = Orchestrator()
report = orch.handle_task("审查 runoob 项目 PR #42")
