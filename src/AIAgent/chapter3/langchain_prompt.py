from langchain.prompts import PromptTemplate, ChatPromptTemplate

string_prompt = PromptTemplate.from_template("tell me a joke about {subject}")

chat_prompt = ChatPromptTemplate.from_template("tell me a joke about {subject}")

string_prompt_value = string_prompt.format_prompt(subject="walruses")

chat_prompt_value = chat_prompt.format_prompt(subject="walruses")

print(f'{string_prompt_value.to_string()}')
print(f'{chat_prompt_value.to_string()}')

print(f'{string_prompt_value.to_messages()}')
print(f'{chat_prompt_value.to_messages()}')