from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-5-haiku-latest")


result = llm.invoke("아이와 함께 가면 좋은 경기도 여행지 3곳")
print(result.content)
