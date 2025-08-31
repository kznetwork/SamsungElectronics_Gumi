import random
from langchain.chat_models import init_chat_model

if random.random() < 0.5:
    print("gpt-5-mini selected")
    model = init_chat_model("gpt-5-mini", model_provider="opanai")
else:
    print("claude-sonnet-4-20250514 selected")
    model = init_chat_model("claude-sonnet-4-20250514", model_provider="anthropic")
result = model.invoke("RAG가 뭔가요?")
print(result.content)
