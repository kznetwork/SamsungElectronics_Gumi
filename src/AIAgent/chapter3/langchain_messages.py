from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import random
import os
from langchain_openai import ChatOpenAI

# 환경변수 설정 (실제로는 .env 사용 권장)
os.environ["OPENAI_API_KEY"] = "-proj-DRnE5vys0joMbWlqJ4L9mO7ta67EFYLcvYiOMSB-4EqCazZ38lIDHzVROijGLy8cZuew6yEVhkT3BlbkFJwk1CwBOm_wXbxQZ7ePoA3UnHHqwWJ6UktyaAisceZYm1abuk77cI27E5cunrmsnndg30EELF4A"

# 모델 초기화
chat_model = ChatOpenAI(model="gpt-5-mini")

messages = [
    SystemMessage(
        content="당신은 사용자의 질문에 간결하고 명확하게 답변하는 AI도우미 입니다."
    ),
    HumanMessage(content="LangChain에 대해 설명해주세요."),
    AIMessage(
        content="LangChain은 대규모 언어 모델(LLM)을 활용하여 애플리케이션을 구축하기 위한 프레임워크입니다."
    ),  # 이전 대화 예시
    HumanMessage(content="주요 기능 세 가지만 알려주세요."),  # 사용자의 질문
]

result = chat_model.invoke(messages)
print("AI의 응답 : ", result.content)
