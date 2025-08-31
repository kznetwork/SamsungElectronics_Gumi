from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

# ① 임베딩 모델과 텍스트 분할기 준비
embeddings = OpenAIEmbeddings()
text_splitter = CharacterTextSplitter(separator=".", chunk_size=50, chunk_overlap=20)

# ② 샘플 문서들 준비
documents = [
    Document(
        page_content="파이썬은 읽기 쉽고 배우기 쉬운 프로그래밍 언어입니다. "
        "다양한 분야에서 활용되며, 특히 데이터 과학과 AI 개발에 인기가 높습니다.",
        metadata={"source": "python_intro.txt", "topic": "programming"},
    ),
    Document(
        page_content="자바스크립트는 웹 브라우저에서 실행되는 프로그래밍 언어로 시작했지만, "
        "현재는 서버 사이드 개발에도 널리 사용됩니다. Node.js가 대표적입니다.",
        metadata={"source": "js_guide.txt", "topic": "programming"},
    ),
    Document(
        page_content="머신러닝은 데이터에서 패턴을 학습하는 AI의 한 분야입니다. "
        "지도학습, 비지도학습, 강화학습 등 다양한 방법론이 있습니다.",
        metadata={"source": "ml_basics.txt", "topic": "ai"},
    ),
]

# ③ 문서 분할
split_docs = text_splitter.split_documents(documents)

for doc in split_docs:
    print(
        f"문서: {doc.page_content[:20]}... | 출처: {doc.metadata['source']} | 주제: {doc.metadata['topic']}"
    )

# FAISS 벡터 스토어 생성
vectorstore = FAISS.from_documents(split_docs, embeddings)

# ④ 유사도 검색 수행
query = "초보자가 배우기 좋은 프로그래밍 언어는?"
results = vectorstore.similarity_search(query, k=2)

print(f"질문: {query}\n")
print("검색 결과:")
for i, doc in enumerate(results, 1):
    print(f"\n{i}. {doc.page_content[:100]}...")
    print(f"   출처: {doc.metadata['source']}")
    print(f"   주제: {doc.metadata['topic']}")

# ⑤ 유사도 점수와 함께 검색
results_with_scores = vectorstore.similarity_search_with_score(query, k=2)
print("\n\n유사도 점수:")
for doc, score in results_with_scores:
    print(f"- {doc.metadata['source']}: {score:.3f}")
