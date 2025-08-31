import httpx
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain.chat_models import init_chat_model
import math
from geopy.geocoders import Nominatim


def calculator(expression: str) -> str:
    """수학 계산을 수행합니다."""
    print(f"계산 요청: {expression}")
    try:
        # 간단한 치환
        expression = expression.replace("sqrt", "math.sqrt")
        expression = expression.replace("sin", "math.sin")
        expression = expression.replace("cos", "math.cos")

        # 안전한 계산 실행
        result = eval(expression, {"__builtins__": {}, "math": math})
        return f"계산 결과: {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"


def get_weather(city_name: str) -> dict:  # ① 날씨 관련 도구 함수
    """도시 이름을 받아 해당 도시의 현재 날씨 정보를 반환합니다."""
    if city_name:
        latitude, longitude = get_coordinates(city_name)
    else:
        raise ValueError("City name must be provided to get weather information.")

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    response = httpx.get(url)
    response.raise_for_status()  # Raises an exception for HTTP errors
    return response.json()


def get_coordinates(city_name: str) -> tuple[float, float]:
    """도시 이름을 받아 위도와 경도를 반환합니다."""
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Could not find coordinates for {city_name}")


def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """통화 간 환율을 계산합니다."""
    print(f"{amount} {from_currency}를 {to_currency}로 변환합니다.")
    rates = {("USD", "KRW"): 1320.50, ("KRW", "USD"): 0.00076}
    rate_key = (from_currency.upper(), to_currency.upper())
    if rate_key in rates:
        rate = rates[rate_key]
        converted = amount * rate
        return f"{amount} {from_currency} = {converted:.2f} {to_currency}"
    return f"{amount} {from_currency} = {amount} {to_currency} (동일 통화)"


def should_continue(state: MessagesState):
    print("\n--- 분기 결정 ---")
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        print(f"결정: 도구 호출 필요 ({len(last_message.tool_calls)}개)")
        return "tools"
    else:
        print("결정: 최종 응답으로 종료")
        return END


def create_call_model_function(model_with_tools):
    """model_with_tools를 클로저로 캡처하는 call_model 함수 생성"""

    def call_model(state: MessagesState):
        """LLM을 호출하여 응답을 생성하는 노드 함수"""
        last_message = state["messages"][-1]
        # 도구 실행 결과를 받았는지, 아니면 사용자 질문을 받았는지에 따라 분기
        if isinstance(last_message, ToolMessage):
            print("\n--- 모델 호출 (도구 결과 기반) ---")
            # 도구 실행 결과가 길 수 있으므로 일부만 출력
            print(f"입력(도구 결과): {last_message.content[:300]}...")
        else:
            print("\n--- 모델 호출 (사용자 질문 기반) ---")
            print(f"입력(사용자 메시지): {last_message.content}")

        # 모델을 호출하여 다음 행동을 결정하게 함
        response = model_with_tools.invoke(state["messages"])

        # 모델의 결정에 따라 로그 출력
        if response.tool_calls:
            print(f"모델의 판단: 도구 호출 -> {response.tool_calls}")
        else:
            print(f"모델의 판단: 최종 답변 생성 -> {response.content}")

        return {"messages": [response]}

    return call_model


def create_graph(model_with_tools, tool_node):
    """LLM 워크플로우 그래프 생성"""
    workflow = StateGraph(MessagesState)

    call_model = create_call_model_function(model_with_tools)
    workflow.add_node("call_model", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "call_model")
    workflow.add_conditional_edges("call_model", should_continue, ["tools", END])
    workflow.add_edge("tools", "call_model")

    return workflow.compile()


def llm_tool_call(query: str):
    """하나의 질문에 대해 전체 LLM 워크플로우를 실행하고 로그를 출력합니다."""
    tools = [calculator, get_weather, currency_converter]
    tool_node = ToolNode(tools)
    model = init_chat_model("gpt-5-mini", model_provider="openai")
    model_with_tools = model.bind_tools(tools)

    print(f"질문: {query}")
    print("-" * 50)

    # LLM 기반 워크플로우 생성
    app = create_graph(model_with_tools, tool_node)

    # 워크플로우 실행
    app.invoke({"messages": [HumanMessage(content=query)]})

    # 최종 응답은 call_model 노드의 로그에서 출력됩니다.
    print("-" * 50)
    print("처리 완료")
    print("=" * 50 + "\n")


def main():
    print("=== LangGraph ToolNode 예제 (LLM 기반) ===\n")

    test_queries = [
        "2 + 3 * 4를 계산해줘",
        "서울 날씨 어때?",
        # "100달러를 원화로 바꿔줘",
        # "sqrt(16)을 계산해줘",
        # "도쿄 날씨가 궁금해",
        # "1000원을 달러로 환전해줘",
    ]

    print("\nLLM 기반 도구 호출 시작:")
    for query in test_queries:
        try:
            llm_tool_call(query)
        except Exception as e:
            print(f"'{query}' 처리 중 오류 발생: {e}")
            print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
