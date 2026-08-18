#成本控制
# 根据任务重要性选择模型
def get_llm(task_type: str):
    if task_type == "classification":  #分类任务，轻量模型足够
        return ChatOpenAI(model="MiniMax-M2.1-highspeed")
    elif task_type == "generation":  #生成任务，用中等模型
        return ChatOpenAI(model="MiniMax-M2.7-highspeed")
    elif task_type == "reasoning":  #复杂任务，用高等模型
        return ChatOpenAI(model="MiniMax-M3")


# 缓存重复请求
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
set_llm_cache(InMemoryCache()) # 想通输入直接返回缓存，不用重复计费

#
