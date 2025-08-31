import os
import logging
import asyncio
from datetime import datetime
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from workflow import create_news_workflow
from config import Config
from state import NewsState

# ① 로거 설정 - 시스템 실행 중 발생하는 이벤트와 오류를 추적
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Google News AI 멀티에이전트 시스템의 메인 실행 함수"""
    print(
        """
Google News AI 멀티에이전트 시스템
RSS 수집 → AI 요약 → 카테고리 분류 → 리포트 생성
"""
    )
    try:
        # ② 설정 유효성 검사 - API 키 존재 여부 확인
        if not Config.validate():
            raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")

        print("\n" + "=" * 60)
        print("뉴스 처리 시작")
        print("=" * 60)

        # ③ LLM 및 워크플로우 초기화 - AI 모델과 처리 파이프라인 생성
        llm = ChatOpenAI(
            model=Config.MODEL_NAME,
            max_tokens=Config.MAX_TOKENS,
            api_key=Config.OPENAI_API_KEY,
        )
        app = create_news_workflow(llm)

        # ④ 워크플로우 실행 - 초기 상태 설정 후 비동기로 전체 파이프라인 실행
        initial_state = NewsState(
            messages=[HumanMessage(content="Google News RSS 처리를 시작합니다.")]
        )
        final_state = await app.ainvoke(initial_state)

        # ⑤ 최종 보고서 저장 및 출력 - 처리 결과를 파일로 저장하고 요약 정보 표시
        if not final_state.get("final_report"):
            print("\n생성된 보고서가 없습니다.")
            return

        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(Config.OUTPUT_DIR, f"news_report_{timestamp}.md")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_state["final_report"])

        print("\n" + "=" * 60)
        print("처리 완료")
        print("=" * 60)
        print(f"\n보고서가 저장되었습니다: {filename}")
        print(f"처리된 뉴스: {len(final_state.get('summarized_news', []))}건")
        print("\n보고서 미리보기:")
        print("-" * 60)
        print(final_state["final_report"][:500] + "...")

    # ⑥ 예외 처리 - 사용자 중단과 일반 오류를 구분하여 처리
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.exception("실행 중 오류 발생")
        print(f"\n오류 발생: {e}")


# ⑦ 프로그램 진입점 - 비동기 메인 함수를 실행
if __name__ == "__main__":
    asyncio.run(main())
