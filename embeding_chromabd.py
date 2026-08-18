# 构建一个文档语义搜索系统
import chromadb
from chromadb.utils import embedding_functions
import os 
from dotenv import load_dotenv

load_dotenv(dotenv_path="d:/cainiao_learn/.env")
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

# 1. 初始化客户端
#持久化到本地
client = chromadb.PersistentClient(path="./my_vector_db")
  
             
#使用sentence transformer嵌入模型
st_ef=embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
#2.创建集合
collection = client.get_or_create_collection(
    name="my_collection_st",
    embedding_function=st_ef,
    metadata={"hnsw:space":"cosine"}   
)

#3.添加文档
documents = [
    "Python 是一种面向对象的解释型编程语言，广泛用于数据科学和 AI 开发",
    "机器学习是人工智能的子领域，让计算机从数据中学习规律",
    "深度学习使用多层神经网络，在图像识别和 NLP 任务中表现优异",
    "向量数据库专门存储高维向量，支持语义相似度搜索",
    "PostgreSQL 是功能强大的开源关系型数据库",
    "Redis 是基于内存的高性能键值数据库，常用于缓存",
    "Docker 容器化技术让应用可以在任何环境中一致运行",
    "Git 是分布式版本控制系统，是现代软件开发的基础工具",
]

ids = [f"doc{i}" for i in range(len(documents))]


#批量插入(chroma自动调用嵌入模型转为向量后存储)
collection.add(
    documents=documents,
    ids=ids,
    metadatas=[{"source":"tutorial", "index":i} for i in range(len(documents))]
)

print(f"成功添加 {len(documents)} 条文档到集合 my_collection")

#4. 语义检索
query="如何用 python 做人工智能"

results = collection.query(
    query_texts=[query],
    n_results=3,   #返回最相似的3条
    include=["documents", "metadatas", "distances"]
)
print(f"\n查询：{query}")
print("-" * 50)
for i, (doc, dist) in enumerate(zip(
    results["documents"][0],
    results["distances"][0]
)):
    similarity = 1 - dist   # 余弦相似度
    print(f"第 {i+1} 名 （相似度{similarity:.4f}) : ")
    print(f" {doc}")
    print()


# 5. 带过滤条件的搜索（元数据过滤）
results_filtered = collection.query(
    query_texts=[query],
    n_results=2,
    where={"source":"tutorial"},   #只在 source=tutorial 的文档中搜索
    include=["documents", "distances"]
)

# 6. 更新文档
collection.upsert(
    ids=["doc0"],
    documents=["Python 是目前最流行的编程语言，在 AI、数据分析、Web 开发中均有广泛应用"],
    metadatas =[{"source":"tutorial", "index":0, "updated":True}]
)


#7. 删除文档
collection.delete(
    ids=["doc_7"]    #删除git 相关文档
)

#8.查看集合统计
print(f"当前集合中文档数：{collection.count()}")


"""
# 关于数据库的性能优化
# 推荐：批量插入
collection.add(documents=doc_list, ids=ids_list)



#向量归一化：使用余弦相似度前，提前归一化向量可加速计算
import numpy as np
def normalize(v):
    #对向量做 L2 归一化， 是模长为1
    return v / np.linalg.norm(v)


# 只在“技术文档”分类中搜索，缩小范围
collection.query(
    query_texts=["python 异常处理"],
    where={"category":"tech_doc"}
    n_reuslts=5
)"""