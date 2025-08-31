import os
from langchain.prompts import PromptTemplate

from langchain.prompts import load_prompt

template = PromptTemplate.from_template(
    "당신은 친절한 AI입니다.\n질문: {question}\n답변:"
)
print(template.format(question="랭체인이 뭐죠?"))

print("----------------------------------------------------------------")

template = PromptTemplate(
    input_variables=["article", "style"],
    template="다음 기사를 {style} 스타일로 요약하세요:\n\n{article}",
)
print(template.format(article="OpenAI가 GPT-5를 공개했다…", style="뉴스"))


print("----------------------------------------------------------------")
current_dir_path = os.path.dirname(os.path.abspath(__file__))
file_prompt = load_prompt(f"{current_dir_path}/template_example.yaml")
print(file_prompt.format(context="서울은 한국의 수도이다.", question="수도는?"))

print("----------------------------------------------------------------")
base_prompt = PromptTemplate.from_template("'{text}' 문장을 {lang}로 번역하세요.")
ko_prompt = base_prompt.partial(lang="Korean")  # lang 고정
en_prompt = base_prompt.partial(lang="English")  # 다른 버전

print(ko_prompt.format(text="Hello"))
print(en_prompt.format(text="안녕하세요"))
