#  OpenAI API를 사용하여 AI 응답을 받아오는 코드
import asyncio
import os
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "-proj-DRnE5vys0joMbWlqJ4L9mO7ta67EFYLcvYiOMSB-4EqCazZ38lIDHzVROijGLy8cZuew6yEVhkT3BlbkFJwk1CwBOm_wXbxQZ7ePoA3UnHHqwWJ6UktyaAisceZYm1abuk77cI27E5cunrmsnndg30EELF4A"

os.environ["ANTHROPIC_API_KEY"] = "-ant-api03-uF4-a-kR3DQhVaEWIFmrVhwJ3h-b9p8_qyJg_L5XSyirHfhGUtNUiDbxp-dQMfmDGwWqo-6PMm4htclG9fKycA-vT4knQAA"

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic


openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
claude_client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


async def call_async_openai(prompt: str, model: str = "gpt-5-mini") -> str:
    response = await openai_client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


async def call_async_claude(prompt: str, model: str = "claude-3-5-haiku-latest") -> str:
    response = await claude_client.messages.create(
        model=model, max_tokens=1000, messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


async def main():
    print("동시에 API 호출하기")
    prompt = "비동기 프로그래밍에 대해 2-3문장으로 설명해주세요."
    openai_task = call_async_openai(prompt)
    claude_task = call_async_claude(prompt)
    openai_response, claude_response = await asyncio.gather(openai_task, claude_task)
    print(f"OpenAI 응답: {openai_response}")
    print(f"Claude 응답: {claude_response}")


if __name__ == "__main__":
    asyncio.run(main())
