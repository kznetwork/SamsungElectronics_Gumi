from tkinter import Image
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field


# ① 워크플로우 단계 정의
class WorkflowStep:
    GREETING = "GREETING"
    PROCESSING = "PROCESSING"


# ② 그래프 상태 정의
class GraphState(BaseModel):
    name: str = Field(default="", description="사용자 이름")
    greeting: str = Field(default="", description="생성된 인사말")
    processed_message: str = Field(default="", description="처리된 최종 메시지")


# ③ 첫번째 노드 함수
def generate_greeting(state: GraphState) -> Dict[str, Any]:
    name = state.name or "아무개"
    greeting = f"안녕하세요, {name}님!"
    print(f"[generate_greeting] 인사말 생성: {greeting}")
    return {"greeting": greeting}


# ④두 번째 노드: 인사말을 처리하고 최종 메시지 생성
def process_message(state: GraphState) -> Dict[str, Any]:
    greeting = state.greeting
    processed_message = f"{greeting} LangGraph에 오신 것을 환영합니다!"

    print(f"[process_message] 최종 메시지: {processed_message}")

    return {"processed_message": processed_message}


# ⑤ 그래프 생성
def create_hello_graph():
    workflow = StateGraph(GraphState)

    # 노드 추가
    workflow.add_node(WorkflowStep.GREETING, generate_greeting)
    workflow.add_node(WorkflowStep.PROCESSING, process_message)

    # 시작점 설정
    workflow.add_edge(START, WorkflowStep.GREETING)

    # 엣지 추가 (노드 간 연결)
    workflow.add_edge(WorkflowStep.GREETING, WorkflowStep.PROCESSING)
    workflow.add_edge(WorkflowStep.PROCESSING, END)

    # 그래프 컴파일
    app = workflow.compile()

    return app


def main():
    print("=== Hello 랭그래프 ===\n")
    app = create_hello_graph()

    initial_state = GraphState(name="승귤", greeting="", processed_message="")
    print("초기 상태:", initial_state.model_dump())
    print("\n--- 그래프 실행 시작 ---")

    # 그래프 실행
    final_state = app.invoke(initial_state)

    print("--- 그래프 실행 종료 ---\n")
    print("최종 상태:", final_state)
    print(f"\n결과 메시지: {final_state['processed_message']}")
    # ⑥ ASCII로 그래프 출력
    result = app.get_graph().draw_ascii()
    print(result)

    # ⑦ Mermaid로 그래프 이미지 생성
    result = app.get_graph().draw_mermaid_png()

    with open("./hello_langgraph.png", "wb") as f:
        f.write(result)


if __name__ == "__main__":
    main()
