# plan&Execute 架构的简化实现

class PlanExcuteAgent:
    """先规划，后执行的agent"""
    
    def plan(self, task: str) -> str:
        """阶段一：生成执行计划"""
        plan = self.model.generate(f"""
        请将以下任务拆解为可执行的步骤列表：
        任务：{task}
        返回 JSON 格式的步骤列表，每步包含：
        - step_id: 步骤编号
        - description: 步骤描述
        - tool: 需要调用的工具名
        """
        )
        return plan
   
    def excute(self, plan: list, dynamic:bool = False) -> str:
        """阶段二：逐步执行计划"""
        results = []
        remaining_plan = plan.copy()

        while remaining_plan:
            step = remaining_plan.pop(0)
            output = self.tools[step["tool"]][step["description"]]
            results.append({"step": step["step_id"], "output":output})

            if dynamic and remaining_plan:
                #动态调整：根据当前结果重新评估后续计划
                remaining_plan = self.replan(remaining_plan, results)

        return self.summarize(results)

#使用示例
agent = PlanExcuteAgent()
plan = agent.plan("为 runoob 项目添加用户认证功能")
# 人可以先审查plan 确认合理后再执行
result = agent.excute(plan, dynamic=True)