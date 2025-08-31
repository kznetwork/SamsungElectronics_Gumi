from langchain.chat_models import init_chat_model

model = init_chat_model("claude-sonnet-4-20250514", model_provider="anthropic")
result = model.invoke("랭체인이 뭔가요?")
print(result.content)
