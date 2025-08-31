from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import random


# ① 그래프 상태 정의 - 워크플로우 전체에서 공유되는 데이터 구조
class EmotionBotState(BaseModel):
    user_message: str = Field(default="", description="사용자 입력 메시지")
    emotion: str = Field(default="", description="분석된 감정")
    response: str = Field(default="", description="최종 응답 메시지")


# ② LangChain LLM 초기화 - 감정 분석에 사용할 AI 모델 설정
llm = ChatOpenAI(model="gpt-5-mini", max_tokens=10)


# ③ LLM 기반 감정 분석 노드 - 첫 번째 처리 단계
def analyze_emotion(state: EmotionBotState) -> Dict[str, Any]:
    message = state.user_message
    print(f"LLM 감정 분석 중: '{message}'")

    messages = [
        SystemMessage(
            content="당신은 감정 분석 전문가입니다. 사용자의 메시지를 분석하여 'positive', 'negative', 'neutral' 중 하나로 감정을 분류해주세요. 답변은 반드시 하나의 단어만 출력하세요."
        ),
        HumanMessage(content=f"다음 메시지의 감정을 분석해주세요: '{message}'"),
    ]

    response = llm.invoke(messages)
    emotion = response.content.strip().lower()

    # 유효성 검사
    if emotion not in ["positive", "negative", "neutral"]:
        emotion = "neutral"

    print(f"LLM 감정 분석 결과: {emotion}")
    return {"emotion": emotion}


# 긍정적 응답 생성
def generate_positive_response(state: EmotionBotState) -> Dict[str, Any]:
    responses = ["정말 좋은 소식이네요!", "기분이 좋으시군요!", "멋지네요!"]
    return {"response": random.choice(responses)}


# 부정적 응답 생성
def generate_negative_response(state: EmotionBotState) -> Dict[str, Any]:
    responses = [
        "힘든 시간이시군요. 괜찮아요.",
        "마음이 아프시겠어요.",
        "더 좋은 날이 올 거예요.",
    ]
    return {"response": random.choice(responses)}


# 중립적 응답 생성
def generate_neutral_response(state: EmotionBotState) -> Dict[str, Any]:
    responses = [
        "감사해요! 더 자세히 말씀해주세요.",
        "이해했어요. 다른 도움이 필요하시면 말씀하세요!",
        "흥미로운 주제네요!",
    ]
    return {"response": random.choice(responses)}


# ④ 조건부 라우팅 함수 - 감정 분석 결과에 따라 다음 노드 결정
def route_by_emotion(
    state: EmotionBotState,
) -> Literal["positive_response", "negative_response", "neutral_response"]:
    emotion = state.emotion
    print(f"라우팅: {emotion}")

    if emotion == "positive":
        return "positive_response"
    elif emotion == "negative":
        return "negative_response"
    else:
        return "neutral_response"


# ⑤ 그래프 생성 함수 - 전체 워크플로우 구성
def create_emotion_bot_graph():
    workflow = StateGraph(EmotionBotState)

    # ⑥ 노드 추가 - 각 처리 단계를 그래프에 등록
    workflow.add_node("analyze_emotion", analyze_emotion)
    workflow.add_node("positive_response", generate_positive_response)
    workflow.add_node("negative_response", generate_negative_response)
    workflow.add_node("neutral_response", generate_neutral_response)

    # ⑦ 시작 엣지 설정 - 워크플로우의 진입점 정의
    workflow.add_edge(START, "analyze_emotion")

    # ⑧ 조건부 엣지 설정 - 동적 라우팅 구현
    workflow.add_conditional_edges(
        "analyze_emotion",
        route_by_emotion,
        {
            "positive_response": "positive_response",
            "negative_response": "negative_response",
            "neutral_response": "neutral_response",
        },
    )

    # ⑨ 종료 엣지 설정 - 각 응답 노드에서 워크플로우 종료
    workflow.add_edge("positive_response", END)
    workflow.add_edge("negative_response", END)
    workflow.add_edge("neutral_response", END)

    return workflow.compile()


def main():
    print("=== 감정 분석 챗봇 테스트 ===\n")
    app = create_emotion_bot_graph()

    test_cases = [
        "오늘 정말 기분이 좋아요!",
        "너무 슬프고 힘들어요...",
        "날씨가 어떤가요?",
    ]

    for i, message in enumerate(test_cases, 1):
        print(f"테스트 {i}: '{message}'")
        state = EmotionBotState(user_message=message)
        result = app.invoke(state)
        print(f"응답: {result['response']}\n")

    # 그래프 시각화
    mermaid_png = app.get_graph().draw_mermaid_png()
    with open("./02_conditional_routing.png", "wb") as f:
        f.write(mermaid_png)


if __name__ == "__main__":
    main()
