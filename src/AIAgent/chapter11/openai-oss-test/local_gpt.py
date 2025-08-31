import httpx
import asyncio
import json

async def chat_with_local_gpt_async(messages, temperature=0.7, max_tokens=1000):
    """
    로컬 GPT-OSS 서버와 대화하는 함수 (비동기 방식)
    
    Args:
        messages: 대화 메시지 리스트
        temperature: 생성 온도
        max_tokens: 최대 토큰 수
    
    Returns:
        응답 텍스트
    """
    url = "http://127.0.0.1:1234/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "openai/gpt-oss-20b",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]

# 비동기 사용 예시
async def main():
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "파이썬의 장점을 3가지 알려주세요."}
    ]
    
    response = await chat_with_local_gpt_async(messages)
    print(f"GPT-OSS 응답: {response}")

if __name__ == "__main__":
    asyncio.run(main())
