from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field


# Pydantic을 사용한 State 정의
class AgentState(BaseModel):
    user_message: str = Field(default="", description="사용자 입력 작업")
    task_details: str = Field(default="", description="작업 상세 정보")
    response: str = Field(default="", description="응답 결과")


# ① 노드 함수 정의
def get_llm_response_node(state: AgentState, llm):
    """LLM과 상호작용하여 응답을 생성하거나, 추가 정보를 요청하는 노드"""
    details = state.task_details

    if details:
        print(f"\n상세 정보를 바탕으로 작업 실행: '{details}'")
        prompt = f"다음 요청에 따라 보고서를 작성해주세요: {details}"
    else:
        task = state.user_message
        print(f"\n작업 실행: '{task}' 작업을 수행합니다...")
        # ② LLM에게 상세 정보를 묻는 질문을 하도록 유도하고, 반드시 '?'로 끝내도록 지시
        prompt = f"'{task}' 작업을 수행하려고 합니다. 어떤 종류의 보고서가 필요한지, 구체적인 주제는 무엇인지 질문해주세요. 추가 정보가 필요하면, 반드시 응답의 마지막을 물음표('?')로 끝내주세요."

    response = llm.invoke(prompt).content

    print("--- LLM 응답 ---")
    print(response)
    print("--------------------")

    return {"response": response, "task_details": ""}


# ③ 사람의 입력을 받는 노드
def get_task_details_node(state: AgentState) -> AgentState:
    """LLM의 질문에 대한 사용자 답변을 입력받는 노드"""
    print("\nLLM의 질문에 답변해주세요.")
    user_input = input("답변: ")
    return {"task_details": user_input}


# ④ 조건부 분기 노드
def check_llm_response(state: AgentState) -> Literal["get_details", "end"]:
    """LLM의 응답이 질문인지 확인하여 다음 단계를 결정합니다."""
    print("LLM 응답 분석 중...")
    if state.response.strip().endswith("?"):
        print("LLM이 추가 정보를 요청했습니다. 사용자 입력을 받습니다.")
        return "get_details"
    print("최종 보고서가 생성되었습니다. 워크플로우를 종료합니다.")
    return "end"


# ⑤ 그래프 생성
def create_graph():
    """Human-in-the-loop 워크플로우 그래프를 생성합니다."""
    # 그래프 전체에서 사용할 LLM 모델을 초기화합니다.
    llm = init_chat_model("gpt-5-mini", model_provider="openai")

    def get_llm_response_with_llm(state):
        return get_llm_response_node(state, llm)

    workflow = StateGraph(AgentState)
    workflow.add_node("get_llm_response", get_llm_response_with_llm)
    workflow.add_node("get_details", get_task_details_node)

    workflow.add_edge(START, "get_llm_response")
    workflow.add_conditional_edges(
        "get_llm_response",
        check_llm_response,
        {
            "get_details": "get_details",
            "end": END,
        },
    )
    workflow.add_edge("get_details", "get_llm_response")
    return workflow.compile()


def main():
    print("=== LangGraph Human-in-the-loop 간소화 예제 ===\n")
    app = create_graph()

    # mermaid_png = app.get_graph().draw_mermaid_png()
    # with open("human_in_the_loop_graph.png", "wb") as f:
    #     f.write(mermaid_png)

    final_state = app.invoke(AgentState(user_message="블로그 글 작성"))
    print("\n--- 워크플로우 종료 ---")
    print("최종 응답:")
    print(final_state["response"])


if __name__ == "__main__":
    main()
