import httpx
from geopy.geocoders import Nominatim
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain.chat_models import init_chat_model
from typing import Literal
import json


def get_coordinates(city_name: str) -> tuple[float, float]:
    """도시 이름을 받아 위도와 경도를 반환합니다."""
    geolocator = Nominatim(user_agent="weather_app_langgraph")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    raise ValueError(f"좌표를 찾을 수 없습니다: {city_name}")


def get_weather(city_name: str) -> str:
    """도시 이름을 받아 해당 도시의 현재 날씨 정보를 반환합니다."""
    print(f"날씨 조회: {city_name}")
    latitude, longitude = get_coordinates(city_name)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    response = httpx.get(url)
    response.raise_for_status()
    return json.dumps(response.json())


# ① 기상 전문가 서브그래프 생성
def create_weather_agent():
    """날씨 관련 질문을 처리하는 전문가 서브그래프를 생성합니다."""
    model = init_chat_model("gpt-5-mini", model_provider="openai").bind_tools(
        [get_weather]
    )
    tool_node = ToolNode([get_weather])

    def call_model(state: MessagesState):
        return {"messages": [model.invoke(state["messages"])]}

    graph = StateGraph(MessagesState)
    graph.add_node("call_model", call_model)
    graph.add_node("tool_node", tool_node)

    graph.add_edge(START, "call_model")
    graph.add_conditional_edges(
        "call_model",
        lambda s: "tool_node" if s["messages"][-1].tool_calls else END,
        {"tool_node": "tool_node", END: END},
    )
    graph.add_edge("tool_node", "call_model")
    return graph.compile()


def router(state: MessagesState) -> Literal["weather_expert", "general_agent"]:
    query = state["messages"][-1].content.lower()
    if "날씨" in query or "기온" in query:
        print("라우팅 결정: 기상 전문가에게 위임")
        return "weather_expert"
    print("라우팅 결정: 일반 에이전트가 처리")
    return "general_agent"


# ② 메인 그래프 생성
def create_main_agent(weather_subgraph):
    """질문을 라우팅하고 처리하는 메인 에이전트 그래프를 생성합니다."""
    main_model = init_chat_model("gpt-5-mini", model_provider="openai")

    workflow = StateGraph(MessagesState)
    workflow.add_node(
        "general_agent", lambda s: {"messages": [main_model.invoke(s["messages"])]}
    )
    workflow.add_node("weather_expert", weather_subgraph)
    workflow.add_conditional_edges(
        START,
        router,
        {
            "weather_expert": "weather_expert",
            "general_agent": "general_agent",
        },
    )
    workflow.add_edge("general_agent", END)
    workflow.add_edge("weather_expert", END)
    return workflow.compile()


def main():
    print("=== LangGraph 서브그래프 예제 (기상 전문가) ===\n")
    weather_agent = create_weather_agent()
    main_agent = create_main_agent(weather_agent)

    main_graph_image = main_agent.get_graph(xray=True).draw_mermaid_png()
    with open("main_agent_graph.png", "wb") as f:
        f.write(main_graph_image)

    queries = ["성남 날씨 어때?", "잠은 몇시간 자는게 좋을까?"]
    for query in queries:
        print(f"\n--- 질문: {query} ---")
        result = main_agent.invoke({"messages": [HumanMessage(content=query)]})
        print(f"최종 답변: {result['messages'][-1].content}")
        print("-" * 20)


if __name__ == "__main__":
    main()
