from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI


# ① 채팅 모델 초기화
chat_model = ChatOpenAI(model="gpt-5-mini")
# ② 프롬프트 템플릿 정의
chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="당신은 까칠한 AI 도우미입니다. 사용자의 질문에 최대 3줄로 답하세요."
        ),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
)

# ③ 출력 파서 정의
string_output_parser = StrOutputParser()

# ④ 프롬프트 템플릿을 사용하여 모델을 실행
result: AIMessage = chat_model.invoke(
    chat_prompt_template.format_messages(
        question="파이썬에서 리스트를 정렬하는 방법은?"
    )
)

# ⑤ 결과를 str 형식으로 변환
parsed_result: str = string_output_parser.parse(result)
print(parsed_result.content)

print("----------------------------------------------------------------")

# ⑥ 체인 생성 (LCEL)
chain = chat_prompt_template | chat_model | string_output_parser
print(type(chain))

# ⑦ 체인 실행
result = chain.invoke({"question": "파이썬에서 딕셔너리를 정렬하는 방법은?"})
# 결과 출력
print(type(result))
print(result)
