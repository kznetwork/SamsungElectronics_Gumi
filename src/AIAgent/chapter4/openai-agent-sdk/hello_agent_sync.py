import os
from langchain_openai import ChatOpenAI

from agents import Agent, Runner

# 환경변수 설정 (실제로는 .env 사용 권장)
os.environ["OPENAI_API_KEY"] = "-proj-DRnE5vys0joMbWlqJ4L9mO7ta67EFYLcvYiOMSB-4EqCazZ38lIDHzVROijGLy8cZuew6yEVhkT3BlbkFJwk1CwBOm_wXbxQZ7ePoA3UnHHqwWJ6UktyaAisceZYm1abuk77cI27E5cunrmsnndg30EELF4A"


# ① 에이전트 생성
hello_agent = Agent(
    name="HelloAgent",
    instructions="당신은 HelloAgent입니다. 당신의 임무는 '안녕하세요'라고 인사하는 것입니다.",
)

# ② 에이전트 실행
result = Runner.run_sync(hello_agent, "프랑스어로만 인사해주세요.")
# ③ 결과 출력
print(result.final_output)
