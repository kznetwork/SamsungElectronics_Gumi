from langchain_core.runnables import RunnableBranch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


model = ChatOpenAI(model="gpt-5-mini")
parser = StrOutputParser()


# ① 입력된 텍스트가 영어인지 확인하는 함수
# 모든 문자가 ASCII 범위(128 미만)에 있으면 영어로 간주합니다.
def is_english(x: dict) -> bool:
    """입력 딕셔너리의 'word' 키에 해당하는 값이 영어인지 확인합니다."""
    return all(ord(char) < 128 for char in x["word"])


# ② 영어 단어에 대한 프롬프트 템플릿입니다.
english_prompt = ChatPromptTemplate.from_template(
    "Give me 3 synonyms for {word}. Only list the words."
)

# ③ 한국어 단어에 대한 프롬프트 템플릿입니다.
korean_prompt = ChatPromptTemplate.from_template(
    "주어진 '{word}'와 유사한 단어 3가지를 나열해주세요. 단어만 나열합니다."
)

# ④ 조건부 분기를 정의합니다.
# is_english 함수가 True를 반환하면 english_prompt를, 그렇지 않으면 korean_prompt를 사용합니다.
language_aware_chain = RunnableBranch(
    (is_english, english_prompt | model | parser),  # 조건이 참일 때 실행될 체인
    korean_prompt | model | parser,  # 기본값 (조건이 거짓일 때 실행될 체인)
)

# 영어 단어 예시
english_word = {"word": "happy"}
english_result = language_aware_chain.invoke(english_word)
print(f"Synonyms for '{english_word['word']}':\n{english_result}\n")

# 한국어 단어 예시
korean_word = {"word": "행복"}
korean_result = language_aware_chain.invoke(korean_word)
print(f"'{korean_word['word']}'의 동의어:\n{korean_result}\n")
