import httpx
import asyncio
import json

async def chat_streaming(prompt, temperature=0.7):
    """비동기 스트리밍 채팅"""
    url = "http://127.0.0.1:1234/v1/chat/completions"
    
    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "stream": True
    }
    
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=data) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    if line == "data: [DONE]":
                        break
                    
                    chunk = json.loads(line[6:])
                    if content := chunk["choices"][0]["delta"].get("content"):
                        print(content, end="", flush=True)
            print()

# 사용
async def main():
    await chat_streaming("짧은 이야기를 들려주세요.")

if __name__ == "__main__":
    asyncio.run(main())
