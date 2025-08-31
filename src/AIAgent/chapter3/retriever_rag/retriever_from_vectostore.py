from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


# 임베딩 모델과 텍스트 분할기 준비
embeddings = OpenAIEmbeddings()
text_splitter = CharacterTextSplitter(separator=".", chunk_size=50, chunk_overlap=20)

# 샘플 문서들 준비
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

# 문서 분할
split_docs = text_splitter.split_documents(documents)

# ① 리트리버 생성
retriever = FAISS.from_documents(split_docs, embeddings).as_retriever(
    search_type="similarity",
    search_kwargs={"k": 1},
)

# ② 리트리버를 사용한 검색
results = retriever.get_relevant_documents("초보자가 배우기 좋은 프로그래밍 언어는?")
for i, doc in enumerate(results, 1):
    print(
        f"{i}. {doc.page_content[:30]}... | 출처: {doc.metadata['source']} | 주제: {doc.metadata['topic']}"
    )


# ③ 리트리버를 사용한 LLM 호출
llm = ChatOpenAI(model_name="gpt-5-mini")
message = """
질문에 대한 답변을 작성할 때, 리트리버에서 가져온 문서를 참고하여 답변을 작성하세요.

질문: 
{question}

참고: 
{context}
"""

prompt = ChatPromptTemplate.from_messages([("human", message)])

chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm


response = chain.invoke("초보자가 배우기 좋은 프로그래밍 언어는?")
print("\nLLM 응답:")
print(response.content)
