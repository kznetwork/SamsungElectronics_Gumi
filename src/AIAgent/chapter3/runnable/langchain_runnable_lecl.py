import os
from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 환경변수 설정 (실제로는 .env 사용 권장)
os.environ["OPENAI_API_KEY"] = "-proj-DRnE5vys0joMbWlqJ4L9mO7ta67EFYLcvYiOMSB-4EqCazZ38lIDHzVROijGLy8cZuew6yEVhkT3BlbkFJwk1CwBOm_wXbxQZ7ePoA3UnHHqwWJ6UktyaAisceZYm1abuk77cI27E5cunrmsnndg30EELF4A"

prompt = ChatPromptTemplate.from_template(
    "주어지는 문구에 대하여 50자 이내의 짧은 시를 작성해주세요 : {word}"
)
# 모델 초기화
model = ChatOpenAI(model="gpt-5-mini")
parser = StrOutputParser()

# ① LCEL로 체인 구성
chain = prompt | model | parser

# 실행
result = chain.invoke({"word": "평범한 일상"})
print(result)
