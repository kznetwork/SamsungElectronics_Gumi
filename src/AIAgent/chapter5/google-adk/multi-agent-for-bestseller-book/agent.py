from google.adk.agents import Agent
import httpx
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class BookRecommendation(BaseModel):
    title: str = Field(description="책 제목")
    author: str = Field(description="저자")
    genre: str = Field(description="장르")
    reason: str = Field(description="추천 이유")
    rating: float = Field(description="평점 (1-5)")


class BookList(BaseModel):
    recommendations: List[BookRecommendation]
    total_count: int


# ① 최신 IT 도서 정보를 가져오는 함수 (도구)
def get_book_search(search_keyword: Optional[str] = None) -> Dict[str, Any]:
    """최신 IT 도서 정보를 가져옵니다. 키워드가 없으면 신간 도서 목록을 가져옵니다."""
    if search_keyword:
        result = httpx.get(f"https://api.itbook.store/1.0/search/{search_keyword}")
    else:
        result = httpx.get("https://api.itbook.store/1.0/new")
    return result.json()


# ② 도서 정보를 검색하는 에이전트
book_data_agent = Agent(
    name="book_data_finder",
    model="gemini-2.5-flash",
    description="최신 도서 정보를 조회하는 에이전트",
    instruction="""
    사용자의 관심사에 맞는 최신 도서 정보를 조회하세요.
    get_book_search 도구를 사용하여 현재 인기 있는 도서들을 조회하고,
    사용자의 선호도에 맞는 도서들을 선별하세요.
    """,
    tools=[get_book_search],  # 도구 추가
)


# ③ 구조화된 출력을 생성하는 에이전트
structured_output_agent = Agent(
    name="structured_output_generator",
    model="gemini-2.5-flash",
    description="도서 추천을 구조화된 형식으로 변환하는 에이전트",
    instruction="""
    받은 도서 정보를 BookList 스키마에 맞게 정리하세요.
    각 도서에 대해 추천 이유를 작성하고,
    전체 추천 도서 수를 total_count에 포함시키세요.
    """,
    output_schema=BookList,  # 출력 스키마 지정
)


# ④ 오케스트레이션을 담당하는 루트 에이전트
root_agent = Agent(
    name="book_recommendation_orchestrator",
    model="gemini-2.5-flash",
    description="도서 추천 프로세스를 조정하는 메인 에이전트",
    instruction="""
    사용자의 도서 추천 요청을 처리하는 오케스트레이터입니다.
    
    처리 순서:
    1. 먼저 book_data_finder 에이전트를 사용하여 사용자의 관심사에 맞는 
       최신 도서 정보를 조회합니다.
    2. 수집된 정보를 structured_output_generator 에이전트에게 전달하여
       BookList 형식으로 구조화된 추천 목록을 생성합니다.
    3. 최종 결과를 사용자에게 전달합니다.
    
    각 에이전트의 역할:
    - book_data_finder: IT도서 베스트 셀러 정보 조회 
    - structured_output_generator: 구조화된 BookList 형식으로 출력 생성
    """,
    sub_agents=[book_data_agent, structured_output_agent],  # 하위 에이전트들
)
