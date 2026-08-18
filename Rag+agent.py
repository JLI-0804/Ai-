# RAG + Agent 架构的简化实现

class RAGAgent:
    """带有动态检索能力的 Agent"""

    def __init__(self, model, vector_db, max_retrievals=5):
        self.model=model
        self.vector_db=vector_db
        self.max_retrievals=max_retrievals

    
    def should_retrieve(self, context: str, question: str) -> bool:
        """判断是否需要检索更多信息"""
        decision = self.model.generate(f"""
        当前已知信息：{context}
        当前问题：{question}
        现有信息是否足以回答问题？回答 YES 或 NO。
        """)
        return "NO" in decision

    def run(self, task: str)  -> str:
        context = ""
        retrieval_count = 0

        while retrieval_count < self.max_retrievals:
            # Agent 自主判断是否需要检索
            if not self.should_retrieve(context, task):
                break

            #Agent 自主决定检索什么
            search_query = self.model.generate(f"""
            任务：{task}
            已有信息：{context}
            为了完成任务，下一步应该检索什么信息?
            """)


            #执行检索，结果追上下文
            docs = self.vector_db.search(search_query)
            context += "\n".join(docs)
            retrieval_count += 1


        #综合所有信息生成最终答案
        return self.model.generate(f"任务：{task}\n参考资料：{context}")

#使用示例
agent = RAGAgent(model=llm, vector_db=runoob_doc_db)
answer = agent.run("RUNOOB 架构中如何配置数据库连接池？")

# Agent 先检索"连接池配置"，发现提到"最大连接数"
# 如果不理解，会再次检索"最大连接数最佳实践"
# 最终综合多轮检索结果给出完整回答
