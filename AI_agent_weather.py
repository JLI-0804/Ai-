# 完整的一个miniAI Agent 示例

import random

#======================================工具定义=============================
def get_weather(city):
    """ 工具1： 模拟天气查询（实际可替换为真实的天气API）"""
    weather_options = ["晴","小雨","大风","多云"]
    temperature = random.randint(15,35)
    return f"{city}的天气是{random.choice(weather_options)}，温度是{temperature}摄氏度"

def simple_calculator(a, b, operator):
    """工具2：简单计算器"""
    if operator == '+':
        return f"{a}+{b}={a+b}"
    elif operator == '-':
        return f"{a}-{b}={a-b}"
    else:
        return "无效的运算符"

#============================短期记忆=========================
conversation_history = []

#============================Agent 主循环 ========================
def run_simple_agent():
    print("【简单AI Agent已启动】输入'退出'来结束对话。")
    print("提示：你可以问天气（如'北京今天天气'）或做计算（如'计算1+1'）\n")

    while True:
        #------感知阶段：获取用户输入-----
        user_input = input("请输入你的问题：")
        conversation_history.append(f"用户：{user_input}")

        #特殊指令：退出
        if user_input.lower() in ["退出","exit","quit"]:
            print("再见")
            break

        #----决策+ 行动阶段： 根据输入选择工具或对话---
        response = ""

        if "天气" in user_input:
            city = "上海"
            for c in ["北京","上海","广州","深圳"]:
                if c in user_input:
                    city = c
                    break
            #调用天气工具
            response = get_weather(city)
        
        elif "计算" in user_input or "+" in user_input or "-" in user_input:
            #简单的匹配模式，识别几个固定的计算表达方式
            if "1+1" in user_input:
                response = simple_calculator(1, 1, '+')
            elif "10-5" in user_input:
                response = simple_calculator(10, 5, '-')
            else:
                response = "无效的计算表达式"
            
        else:
            #没有匹配到工具，退化成为普通表达
            default_response = [
                 "我理解您的意思了。",
                "这是一个有趣的话题！",
                "我目前的技能有限，可以试试问我天气或做简单计算。",
                "嗯，请继续说。"
            ]
            response = random.choice(default_response)

        #----输出 + 记忆阶段： 打印回复，并存入历史-----
        print(f"AI:{response}")
        conversation_history.append(f"AI：{response}")

        #对话解释后，打印完整的对话历史（模拟短期记忆的内容）
        print ("\n=== 本次对话历史（短期记忆）===")
        for line in conversation_history:
            print(line)


# 启动 agent 
if __name__ == "__main__":
    run_simple_agent()
