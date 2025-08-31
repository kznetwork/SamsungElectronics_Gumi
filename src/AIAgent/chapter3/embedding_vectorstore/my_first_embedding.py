from langchain_openai import OpenAIEmbeddings
import numpy as np

# ① 임베딩 모델 초기화
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# ② 단어들을 임베딩으로 변환
words = ["강아지", "고양이", "자동차", "비행기"]
word_embeddings = embeddings.embed_documents(words)

# ③ 쿼리 임베딩 생성
query = "동물"
query_embedding = embeddings.embed_query(query)


# ④ 코사인 유사도 계산 함수
def cosine_similarity(vec1, vec2):
    """두 벡터 간의 코사인 유사도를 계산합니다."""
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2 + 1e-9)  # 작은 값 추가로 0 나누기 방지


# ⑤ 각 단어와 쿼리의 유사도 계산
print(f"'{query}'에 대한 유사도:")
for word, embedding in zip(words, word_embeddings):
    similarity = cosine_similarity(query_embedding, embedding)
    print(f"  {word}: {similarity:.3f}")
