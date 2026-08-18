# 重排序流程伪代码
from sentence_transformers import CrossEncoder

reanker = CrossEncoder("BAAI/bge-reranker-v2-m3")

#1.粗排：向量检索急速召回top50
candidates = vector_store.similarity_search(query, k=50)

#2.精排：构建[问题，文档]对进行精确打分
pairs = ([query, doc.page_count] for doc in candidates)
scores = reanker.predict(pairs)

#3.筛选最终传入LLM的 top-5
ranked_docs = sorted(zip(scores, candidates), reverse=True)
final_docs = [doc for _, doc in ranked_docs[:5]]
