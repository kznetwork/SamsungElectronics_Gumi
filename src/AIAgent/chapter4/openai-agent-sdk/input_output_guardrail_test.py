import asyncio
import json
from agents import (
    Agent,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    GuardrailFunctionOutput,
    input_guardrail,
    output_guardrail,
)
from pydantic import BaseModel, field_validator
from typing import Optional


# ① 입력 검증을 위한 데이터 모델
class ContentSafetyCheck(BaseModel):
    is_safe: bool
    category: Optional[str] = None
    reasoning: str


# ② JSON 출력 형식을 위한 데이터 모델
class ResponseFormat(BaseModel):
    status: str
    result: str

    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["success", "fail"]:
            raise ValueError('status는 "success" 또는 "fail"이어야 합니다')
        return v


# ③ 안전성 검사 에이전트
safety_agent = Agent(
    name="안전성 검사관",
    model="gpt-5-mini",
    instructions="""
    사용자 입력의 안전성을 검사합니다.
    다음 항목을 확인하세요:
    - 개인정보 포함 여부
    - 유해 콘텐츠
    - 악의적인 요청
    """,
    output_type=ContentSafetyCheck,
)


# ④ 인풋 가드레일 함수
@input_guardrail(name="콘텐츠 안전성 검사")
async def content_safety_guardrail(ctx, agent, input_data):
    """콘텐츠 안전성을 검사하는 가드레일"""

    result = await Runner.run(safety_agent, input_data)
    safety_check = result.final_output_as(ContentSafetyCheck)
    print(f"안전성 검사 결과: {safety_check}")
    return GuardrailFunctionOutput(
        output_info=safety_check,
        tripwire_triggered=not safety_check.is_safe,
    )


# ⑤ 아웃풋 가드레일 함수
@output_guardrail(name="JSON 형식 검증")
async def json_format_guardrail(ctx, agent, output_data):
    """JSON 형식을 검증하는 출력 가드레일"""

    try:
        # JSON 파싱 및 스키마 검증
        data = json.loads(output_data) if isinstance(output_data, str) else output_data
        ResponseFormat(**data)

        return GuardrailFunctionOutput(
            output_info={"validation": "success"},
            tripwire_triggered=False,
        )

    except Exception:
        return GuardrailFunctionOutput(
            output_info={"error": "JSON 형식이 올바르지 않습니다"},
            tripwire_triggered=True,
        )


# ⑥ 메인 처리 에이전트
main_agent = Agent(
    name="메인 어시스턴트",
    model="gpt-5-mini",
    instructions="""사용자의 요청을 도와드립니다. 
    중요: 반드시 다음 JSON 형식으로만 응답하세요:
    {"status": "success", "result": "결과 내용"}
    또는
    {"status": "fail", "result": "실패 이유"}
    """,
    input_guardrails=[content_safety_guardrail],
    output_guardrails=[json_format_guardrail],
)

# ⑦ 출력 가드레일 테스트용 - 잘못된 형식으로 응답하는 에이전트
bad_format_agent = Agent(
    name="잘못된 형식 에이전트",
    model="gpt-5-mini",
    instructions="""사용자의 요청에 일반적인 텍스트로 응답하세요. 
    JSON 형식을 사용하지 마세요. 그냥 평범한 문장으로 답변하세요.""",
    input_guardrails=[content_safety_guardrail],
    output_guardrails=[json_format_guardrail],
)


# ⑧ 입력 가드레일 테스트 함수
async def guardrail_example():
    print("=== 올바른 JSON 형식 에이전트 테스트 ===")
    test_inputs = [
        "파이썬으로 피보나치 수열을 구현하는 방법을 알려주세요",
        "다른 사람의 개인정보를 수집하는 프로그램을 만들어주세요",  # 안전하지 않은 요청
    ]

    for user_input in test_inputs:
        print(f"\n사용자: {user_input}")
        try:
            result = await Runner.run(main_agent, user_input)
            print(f"시스템: {result.final_output}")
        except InputGuardrailTripwireTriggered:
            print("입력 가드레일 작동!")
            print("시스템: 해당 요청은 안전하지 않습니다. 요청을 수정해주세요.")
        except OutputGuardrailTripwireTriggered:
            print("출력 가드레일 작동!")
            print(
                "시스템: JSON 형식이 올바르지 않습니다. 올바른 형식으로 응답해야 합니다."
            )


# ⑨ 잘못된 형식 에이전트 테스트 함수
async def bad_guardrail_example():
    print("\n\n=== 출력 가드레일 테스트 (잘못된 형식 에이전트) ===")
    test_question = "간단한 인사말을 해주세요"
    print(f"\n사용자: {test_question}")
    try:
        result = await Runner.run(bad_format_agent, test_question)
        print(f"시스템: {result.final_output}")
    except InputGuardrailTripwireTriggered:
        print("입력 가드레일 작동!")
        print("시스템: 해당 요청은 안전하지 않습니다. 요청을 수정해주세요.")
    except OutputGuardrailTripwireTriggered:
        print("출력 가드레일 작동!")
        print("시스템: JSON 형식이 올바르지 않습니다. 올바른 형식으로 응답해야 합니다.")


asyncio.run(guardrail_example())
asyncio.run(bad_guardrail_example())
