from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from state import NewsState
from agents.collector import RSSCollectorAgent
from agents.summarizer import NewsSummarizerAgent
from agents.organizer import NewsOrganizerAgent
from agents.reporter import ReportGeneratorAgent


def create_news_workflow(llm: ChatOpenAI = None) -> StateGraph:
    """뉴스 처리 워크플로우 생성 - RSS 수집 → AI 요약 → 카테고리 분류 → 보고서 생성"""

    # ① 각 작업을 담당할 4개의 전문 에이전트 인스턴스 생성
    collector = RSSCollectorAgent()  # RSS 피드 수집 전담
    summarizer = NewsSummarizerAgent(llm)  # AI 요약 생성 전담
    organizer = NewsOrganizerAgent(llm)  # 카테고리 분류 전담
    reporter = ReportGeneratorAgent()  # 보고서 작성 전담

    # ② NewsState를 state객체로 사용하는 워크플로우 그래프 생성
    workflow = StateGraph(NewsState)

    # ③ 각 에이전트의 메서드를 워크플로우 노드로 등록
    workflow.add_node("collect", collector.collect_rss)
    workflow.add_node("summarize", summarizer.summarize_news)
    workflow.add_node("organize", organizer.organize_news)
    workflow.add_node("report", reporter.generate_report)

    # ④ 워크플로우 실행 순서 정의 (순차적 파이프라인)
    workflow.set_entry_point("collect")  # 시작점 설정
    workflow.add_edge("collect", "summarize")  # 수집 → 요약
    workflow.add_edge("summarize", "organize")  # 요약 → 분류
    workflow.add_edge("organize", "report")  # 분류 → 보고서
    workflow.add_edge("report", END)  # 보고서 → 종료

    # ⑤ 실행 가능한 워크플로우 객체로 컴파일하여 반환
    return workflow.compile()
