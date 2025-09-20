import os
from langchain_openai import ChatOpenAI

from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 환경변수 설정 (실제로는 .env 사용 권장)
os.environ["OPENAI_API_KEY"] = "-proj-DRnE5vys0joMbWlqJ4L9mO7ta67EFYLcvYiOMSB-4EqCazZ38lIDHzVROijGLy8cZuew6yEVhkT3BlbkFJwk1CwBOm_wXbxQZ7ePoA3UnHHqwWJ6UktyaAisceZYm1abuk77cI27E5cunrmsnndg30EELF4A"

prompt = ChatPromptTemplate.from_template(
    "주어진 '{word}'와 유사한 단어 3가지를 나열해주세요. 단어만 나열합니다."
)
# 모델 초기화
model = ChatOpenAI(model="gpt-5-mini")
parser = StrOutputParser()

# ① 병렬처리 체인 구성
chain = RunnableParallel(
    {
        "original": RunnablePassthrough(),  # ② 원본 데이터 보존
        "processed": prompt | model | parser,  # ③ 처리된 데이터
    }
)

result = chain.invoke({"word": "행복"})
print(result)
