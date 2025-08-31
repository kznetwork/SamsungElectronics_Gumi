from langchain_core.runnables import RunnableLambda


def add_exclamation(text: str) -> str:
    """텍스트 끝에 느낌표를 추가하는 함수"""
    return f"{text}!"


# RunnableLambda로 감싸서 Runnable로 만들기
exclamation_runnable = RunnableLambda(add_exclamation)

# 다양한 방식으로 실행 가능
result = exclamation_runnable.invoke("안녕하세요")
print(result)

# 배치 처리도 자동으로 지원
results = exclamation_runnable.batch(["안녕", "반가워", "좋은 아침"])
print(results)
