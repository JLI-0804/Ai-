import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
#独立扩展包
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
#核心组建
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

llm = ChatOpenAI(
    model="MiniMax-M2.7-highspeed",
    api_key=api_key,
    base_url=api_base,
    temperature=0,
    max_tokens=512,
)

#本地embedding
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

documents = [
    Document(page_content="LangChain 是一个用于构建大语言模型应用的开源框架，由 Harrison Chase 于 2022 年创建。"),
    Document(page_content="LangChain 的核心组件包括：模型接口、提示词模板、链、记忆、检索和代理。"),
    Document(page_content="LCEL（LangChain Expression Language）是 LangChain 的新一代链构建语法，使用管道符 | 连接各组件。"),
    Document(page_content="RAG（检索增强生成）通过在生成前检索相关文档，让 LLM 能回答训练数据之外的问题。"),
    Document(page_content="LangGraph 是 LangChain 团队推出的新框架，专门用于构建复杂的多步骤 AI 代理工作流。"),
    Document(page_content="LangSmith 是 LangChain 的可观测性平台，用于调试、测试和监控 LLM 应用。"),
]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 100,
    chunk_overlap = 30
)

text = text_splitter.split_documents(documents)

#构建Faiss 向量库
vectorstore = FAISS.from_documents(text, embedding)
retriever = vectorstore.as_retriever(search_kwargs={"k":2})

#RAG prompt
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个知识助手。根据以下检索到的上下文来回答问题。如果上下文中没有答案，就说你不知道。\n\n上下文：{context}"),
    ("human", "{question}"),
])


def format_docs(docs):
    return "\n".join([doc.page_content for doc in docs])


#LCEL RAG链 
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

if __name__ == "__main__":
    question = "LlamaIndex是什么？"
    print(f"问题：{question}")
    print(f"回答：{rag_chain.invoke(question)}") 
