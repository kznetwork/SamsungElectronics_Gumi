from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter

# 의존성 패키지 설치 필요
# pip install unstructured 

# 임베딩 모델과 텍스트 분할기 준비
embeddings = OpenAIEmbeddings()
text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)

# 샘플 문서들 준비
# 현재 스크립트 파일의 디렉토리 찾기
current_dir = Path(__file__).parent
documents_path = current_dir / "documents"

loader = DirectoryLoader(
    str(documents_path),  # 스크립트와 같은 디렉토리의 documents 폴더
    glob="**/*.txt",
    show_progress=True
)
documents = loader.load()

# 문서 분할
split_docs = text_splitter.split_documents(documents)

# FAISS 벡터 스토어 생성
vectorstore = FAISS.from_documents(split_docs, embeddings)

# 유사도 검색 수행
query = "초보자가 배우기 좋은 프로그래밍 언어는?"
results = vectorstore.similarity_search(query, k=2)

print(f"질문: {query}\n")
print("검색 결과:")
for i, doc in enumerate(results, 1):
    print(f"\n{i}. {doc.page_content[:100]}...")
    print(f"   출처: {doc.metadata['source']}")

# 유사도 점수와 함께 검색
results_with_scores = vectorstore.similarity_search_with_score(query, k=2)
print("\n\n유사도 점수:")
for doc, score in results_with_scores:
    print(f"- {doc.metadata['source']}: {score:.3f}")