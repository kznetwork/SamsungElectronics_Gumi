import json
import feedparser
import httpx
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from mcp.server.fastmcp import FastMCP
from geopy.geocoders import Nominatim

# ① MCP 서버 인스턴스 생성
mcp = FastMCP("Yozm-ai-agent")


# ② 웹페이지 스크래핑 도구
@mcp.tool()
def scrape_page_text(url: str) -> str:
    """웹페이지의 텍스트 콘텐츠를 스크랩합니다."""
    resp = httpx.get(url)

    if resp.status_code != 200:
        return f"Failed to fetch {url}"
    soup = BeautifulSoup(resp.text, "html.parser")
    # body 태그에서 텍스트를 추출하고 공백을 정리합니다.
    if soup.body:
        text = soup.body.get_text(separator=" ", strip=True)
        return " ".join(text.split())  # 연속된 공백 제거
    return ""


# ③ 도시명을 좌표로 변환하는 헬퍼 함수
def get_coordinates(city_name: str) -> tuple[float, float]:
    """도시 이름을 받아 위도와 경도를 반환합니다."""
    geolocator = Nominatim(user_agent="weather_app_langgraph")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    raise ValueError(f"좌표를 찾을 수 없습니다: {city_name}")


@mcp.tool()
def get_weather(city_name: str) -> str:
    """도시 이름을 받아 해당 도시의 현재 날씨 정보를 반환합니다."""
    print(f"날씨 조회: {city_name}")
    latitude, longitude = get_coordinates(city_name)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    response = httpx.get(url)
    result = response.json()
    print(result)
    return json.dumps(result)


# ④ 구글 뉴스 헤드라인 수집 도구
@mcp.tool()
def get_news_headlines() -> str:
    """구글 RSS피드에서 최신 뉴스와 URL을 반환합니다."""
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)

    if not feed.entries:
        return "뉴스를 가져올 수 없습니다."

    news_list = []
    for i, entry in enumerate(feed.entries, 1):
        # feedparser entry 객체에서 직접 속성 접근
        title = getattr(entry, "title", "제목 없음")
        link = getattr(entry, "link", "#")

        # 디버깅을 위한 로그 추가
        print(f"뉴스 {i}: {title} - {link}")

        # None 값이나 빈 문자열 처리
        if not title or title == "None":
            title = "제목 없음"
        if not link or link == "None":
            link = "#"

        # 마크다운 링크 형식으로 포맷팅
        news_item = f"{i}. [{title}]({link})"
        news_list.append(news_item)

    # 번호가 매겨진 리스트를 문자열로 반환
    return "\n".join(news_list)


# ⑤ KBO 프로야구 순위 조회 도구
@mcp.tool()
def get_kbo_rank() -> str:
    """한국 프로야구 구단의 랭킹을 가져옵니다"""
    result = httpx.get(
        "https://sports.daum.net/prx/hermes/api/team/rank.json?leagueCode=kbo&seasonKey=2025"
    )
    return result.text


# ⑥ 하드코딩된 일정 반환 도구
@mcp.tool()
def today_schedule() -> str:
    """임의의 스케줄을 반환합니다."""
    events = ["10:00 팀 미팅", "13:00 점심 약속", "15:00 프로젝트 회의", "19:00 헬스장"]
    return " | ".join(events)


# ⑦ LLM을 활용한 명언 생성 도구
@mcp.tool()
def daily_quote() -> str:
    """사용자에게 영감을 주는 명언을 출력합니다"""
    chat_model = ChatOpenAI(model="gpt-5-mini")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "당신은 오늘 하루의 명언을 알려주는 도우미입니다. 사용자의 명언 요청이 있을시 명언만 출력합니다.",
            ),
            ("human", "오늘의 명언을 출력해주세요. "),
        ]
    )
    chain = prompt | chat_model
    response = chain.invoke({})
    return response.content


# ⑧ 종합 브리핑 도구 (다른 도구들을 순차적으로 호출)
@mcp.tool()
def brief_today() -> str:
    """사용자의 하루 시작을 돕기 위해 날씨, 뉴스, 일정 등을 종합하여 전달합니다."""
    return """
다음을 순서대로 실행하고, 실행한 결과를 사용자에게 알려주세요. 
첫째로 사용자가 위치한 도시를 파악하세요. 위치를 모른다면, 사용자에게 질문하세요.
둘째로 사용자의 위치를 기반으로 get_weather 도구를 호출하여 날씨 정보를 찾아서 제공합니다. 
셋째로 get_news_headlines 도구를 사용하여 오늘의 주요 뉴스를 출력합니다. 
넷째로 get_kbo_rank 도구를 사용하여 현재 시간 프로야구 랭킹 및 전적을 리스트 형태로 출력합니다.  
다섯째로 today_schedule 도구를 사용하여 오늘 사용자의 일정을 알려줍니다. 
마지막으로 daily_quote 을 사용하여 명언을 출력하고, 따뜻한 말한마디를 덧붙입니다. 

출력은 다음과 같이 해주세요.
## 사용자님을 위한 맞춤 요약  
    
### 오늘의 날씨
[get_weather 의 결과]

### 오늘자 주요 뉴스
[get_news_headlines 의 결과] (링크를 함께 제공합니다)


### 야구단 랭킹 
[get_kbo_rank 의 결과]

### 오늘의 업무 일정
[today_schedule 의 결과]

### 영감을 주는 격언 한마디
[daily_quote 의 결과]
"""


# ⑨ 메인 실행 부분
if __name__ == "__main__":
    # MCP 서버 실행 (HTTP 스트리밍 모드, 포트 8000)
    mcp.run(transport="streamable-http")
