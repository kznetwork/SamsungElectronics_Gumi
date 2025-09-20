import os
from langchain_openai import ChatOpenAI

import asyncio
from agents import Agent, Runner

# 환경변수 설정 (실제로는 .env 사용 권장)
os.environ["OPENAI_API_KEY"] = "-proj-DRnE5vys0joMbWlqJ4L9mO7ta67EFYLcvYiOMSB-4EqCazZ38lIDHzVROijGLy8cZuew6yEVhkT3BlbkFJwk1CwBOm_wXbxQZ7ePoA3UnHHqwWJ6UktyaAisceZYm1abuk77cI27E5cunrmsnndg30EELF4A"


async def simple_handoff_example():
    print("Agent 병원 안내 시스템\n")
    print("=" * 50)

    # ① 정형외과 전문의 에이전트
    정형외과의사 = Agent(
        name="정형외과 전문의",
        instructions="근골격계 문제(허리 통증, 관절염, 골절 등)를 진료합니다.",
    )

    # ② 내과 전문의 에이전트
    내과의사 = Agent(
        name="내과 전문의",
        instructions="내과 질환(감기, 소화불량, 두통 등)을 진료합니다. 근골격계 문제는 정형외과 의사에게 연결합니다.",
        handoffs=[정형외과의사],
    )

    # ③ 병원 안내 에이전트
    안내데스크 = Agent(
        name="병원 안내",
        instructions="""
        환자의 증상을 듣고 적절한 전문의에게 연결합니다:
        - 감기, 소화불량, 두통 → 내과 전문의
        - 허리, 관절, 골절 → 정형외과 전문의
        """,
        handoffs=[내과의사, 정형외과의사],
    )

    # ④ 핸드오프 테스트
    response_id = None
    current_agent = 안내데스크

    conversations = [
        "안녕하세요, 며칠 전부터 머리가 아파요",
        "커피를 마시면 아파요. 허리도 아파요.",
        "운동을 하면 좋아 질까요?",
    ]

    for msg in conversations:
        print(f"\n환자: {msg}")

        # 이전 대화가 있으면 response_id 전달
        if response_id:
            result = await Runner.run(
                current_agent, msg, previous_response_id=response_id
            )
        else:
            result = await Runner.run(current_agent, msg)

        response_id = result.last_response_id
        # handoff가 발생한 경우. 에이전트를 변경
        if current_agent != result.last_agent:
            print(
                f"<핸드오프 발생> {current_agent.name}에서 {result.last_agent.name}로 핸드오프"
            )
            current_agent = result.last_agent

        print(f"<Agent 병원> {current_agent.name}: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(simple_handoff_example())
