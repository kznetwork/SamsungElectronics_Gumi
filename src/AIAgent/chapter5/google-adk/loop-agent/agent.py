from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

# ① 랜덤한 메시지를 생성하는 에이전트
random_generator = LlmAgent(
    name="RandomGenerator",
    model="gemini-2.5-flash",
    description="랜덤한 메시지를 생성하는 에이전트입니다. 스팸메시지와 정상적인 메시지를 60:40 비율로 생성합니다.",
    output_key="random_message",
    instruction="스팸메시지와 정상적인 메시지를 60:40 확률로 생성합니다. 스팸 메시지는 '[웹발신]'을 앞에 넣고, 정상적인 메시지는 따로 표시 안해도됩니다. 반드시 하나의 메시지만 출력해야합니다.",
)

# ② 스팸 메시지를 확인하는 에이전트
spam_checker = LlmAgent(
    name="SpamChecker",
    model="gemini-2.5-flash",
    instruction="{random_message}이 스팸인지 확인하세요. 스팸이면 'fail', 아니면 'pass'를 반환하세요.",
    output_key="spam_status",
)


# ③ 상태를 확인하고, 정상 메시지일 경우 루프를 중단하도록 요청하는 하는 커스텀 에이전트
class CheckStatusAndEscalate(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("spam_status", "fail")
        should_stop = status == "pass"  # pass 상태면 루프를 중지
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))


# ④ 루프 에이전트
root_agent = LoopAgent(
    name="SpamCheckLoop",
    max_iterations=10,
    sub_agents=[
        random_generator,
        spam_checker,
        CheckStatusAndEscalate(name="StopChecker"),
    ],
)
