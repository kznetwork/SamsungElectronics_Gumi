import os
from langchain_openai import ChatOpenAI

from langchain_core.runnables import RunnableParallel, RunnableLambda
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

# ① 여러 분석을 동시에 수행
analysis_chain = RunnableParallel(
    synonyms=prompt | model | parser,  # ② 유사어 분석
    word_count=RunnableLambda(lambda x: len(x["word"])),  # ② 단어 수 계산
    uppercase=RunnableLambda(lambda x: x["word"].upper()),  # ② 대문자로 변환
)

result = analysis_chain.invoke({"word": "peaceful"})
print(result)
