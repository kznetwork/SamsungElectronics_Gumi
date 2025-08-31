from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5-mini", model_provider="openai")
result = model.invoke("랭체인이 뭔가요?")
print(type(result))
print(result.content)
