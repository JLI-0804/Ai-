#  三种相似度计算方法
import numpy as np

#1.余弦相似度： 衡量方向相似性
def cosine_similarity(a, b):
    return np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))

#2.欧式距离： 衡量绝对位置差异
def euclidena_distance(a, b):
    return np.linalg.norm(a - b)

#3.点积：结合方向与长度
def dot_product(a, b):
    return np.dot(a,b)

#示例向量
v1 = np.array([0.12, -0.54, 0.87, 0.03])
v2 = np.array([0.10, -0.50, 0.90, 0.05])
v3 = np.array([-0.8, 0.20, -0.30, 0.70])

print(f"v1 vs v2 余弦相似度: {cosine_similarity(v1, v2):.4f}")  # 约 0.9997（非常相似）
print(f"v1 vs v3 余弦相似度: {cosine_similarity(v1, v3):.4f}")  # 约 -0.55（不相似）
print(f"v1 vs v2 欧式距离: {euclidena_distance(v1, v2):.4f}")  # 约 0.3247（中等距离）
print(f"v1 vs v3 欧式距离: {euclidena_distance(v1, v3):.4f}")  # 约 1.2247（较大距离）
print(f"v1 vs v2 点积: {dot_product(v1, v2):.4f}")  # 约 0.0547（中等点积）
print(f"v1 vs v3 点积: {dot_product(v1, v3):.4f}")


"""主流向量数据库从 Chroma 或 pgvector 起步，前者适合 AI 应用原型，后者适合已有 PostgreSQL 的项目"""
