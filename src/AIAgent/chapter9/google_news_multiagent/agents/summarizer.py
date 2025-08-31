import asyncio
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

from state import NewsState
from config import Config


class NewsSummarizerAgent:
    """뉴스를 요약하는 에이전트"""

    def __init__(self, llm: ChatOpenAI):
        self.name = "News Summarizer"
        self.llm = llm
        # ① 튜플 형식의 메시지로 간결하게 프롬프트 템플릿 구성
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",  # ② 시스템 역할 메시지로 AI의 행동 지침 설정
                    """당신은 전문 뉴스 요약 전문가입니다. 
                    주어진 뉴스를 핵심만 간결하게 2-3문장으로 요약해주세요.
                    - 사실만을 전달하고 추측은 피하세요
                    - 중요한 숫자나 날짜는 포함하세요
                    - 명확하고 이해하기 쉽게 작성하세요""",
                ),
                (
                    "human",  # ③ 사용자 메시지 템플릿에 변수 플레이스홀더 포함
                    "제목: {title}\n내용: {content}\n\n위 뉴스를 2-3문장으로 요약해주세요:",
                ),
            ]
        )

    async def summarize_single_news(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """단일 뉴스 요약 (오류 발생 시 원본 내용 반환)"""
        content = news_item.get("content", "")
        try:
            # ④ 최소 콘텐츠 길이 검증으로 불필요한 API 호출 방지
            if not content or len(content) < 50:
                return {**news_item, "ai_summary": content}

            # ⑤ LCEL(LangChain Expression Language) 체인 구성
            chain = self.prompt | self.llm
            summary_response = await chain.ainvoke(
                {
                    "title": news_item["title"],
                    "content": content[:500],
                }
            )
            summary = summary_response.content.strip()
            # ⑥ 요약 결과 검증 및 폴백 처리
            return {**news_item, "ai_summary": summary or content}

        except Exception as e:
            # ⑦ 간결한 오류 로깅과 원본 반환으로 서비스 연속성 보장
            print(
                f"  [{self.name}] 요약 오류 (Title: {news_item['title']}): {str(e)[:50]}..."
            )
            return {**news_item, "ai_summary": content}  # 오류 시 원본 사용

    async def summarize_news(self, state: NewsState) -> NewsState:
        """모든 뉴스를 비동기로 요약"""
        print(f"\n[{self.name}] 뉴스 요약 시작...")

        batch_size = Config.BATCH_SIZE
        summarized_news = []
        raw_news = state.raw_news
        total_news = len(raw_news)

        # ⑧ 배치 단위 순차 처리로 API 부하 분산
        for i in range(0, total_news, batch_size):
            batch = raw_news[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_news + batch_size - 1) // batch_size

            print(f"  배치 {batch_num}/{total_batches} 처리 중...")

            tasks = [self.summarize_single_news(news) for news in batch]
            batch_results = await asyncio.gather(*tasks)
            summarized_news.extend(batch_results)

        # ⑨ LangGraph 워크플로우 상태 업데이트
        state.summarized_news = summarized_news
        state.messages.append(
            AIMessage(content=f"{len(summarized_news)}개의 뉴스 요약을 완료했습니다.")
        )

        print(f"[{self.name}] 요약 완료\n")
        return state
