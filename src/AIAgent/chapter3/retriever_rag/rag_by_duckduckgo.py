from langchain_community.tools import DuckDuckGoSearchResults
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import time


# ① RealtimeWebRAG: 실시간 웹 검색을 활용한 RAG (Retrieval-Augmented Generation)
class RealtimeWebRAG:
    """실시간 웹 검색을 활용하는 RAG"""

    def __init__(self):
        self.search = DuckDuckGoSearchResults()
        self.llm = ChatOpenAI(temperature=0)

        message = """웹에서 검색한 최신 정보를 바탕으로 답변하세요.
검색 결과:
{search_results}

질문: {question}

중요: 검색 결과에 있는 정보만 사용하여 답변하세요.
답변:"""

        self.qa_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "human",
                    message,
                )
            ]
        )

    # ② 답변 생성 메서드
    def answer(self, question):
        """실시간 검색 후 답변 생성"""
        # 1. 웹 검색
        print(f"검색 중: {question}")
        search_results = self.search.run(question)
        time.sleep(10)  # 10초 대기로 rate limit 방지

        # 2. LLM으로 답변 생성
        qa_chain = self.qa_prompt | self.llm
        answer = qa_chain.invoke(
            {"search_results": search_results, "question": question}
        )

        return answer


# ③ 사용 예시
web_rag = RealtimeWebRAG()

# 최신 정보 질문
questions = ["오늘 주요 뉴스는?", "오늘 야구 순위는?", "최신 AI 기술 동향은?"]

for q in questions:
    print(f"\n질문: {q}")
    answer = web_rag.answer(q)
    print(f"답변: {answer.content}\n")
