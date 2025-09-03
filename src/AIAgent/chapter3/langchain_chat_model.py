import random
import os
from langchain_openai import ChatOpenAI

# 환경변수 설정 (실제로는 .env 사용 권장)
os.environ["OPENAI_API_KEY"] = "-proj-DRnE5vys0joMbWlqJ4L9mO7ta67EFYLcvYiOMSB-4EqCazZ38lIDHzVROijGLy8cZuew6yEVhkT3BlbkFJwk1CwBOm_wXbxQZ7ePoA3UnHHqwWJ6UktyaAisceZYm1abuk77cI27E5cunrmsnndg30EELF4A"

# 모델 초기화
model = ChatOpenAI(model="gpt-5-mini")

if random.random() < 0.5:
    print("gpt-5-mini selected")
    model = ChatOpenAI(model="gpt-4o-mini")
else:
    print("claude-sonnet-4-20250514 selected")
result = model.invoke("RAG가 뭔가요?")
print(result.content)
