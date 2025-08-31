import httpx

def chat(prompt, temperature=0.7, max_tokens=1000):
    """동기 방식 간단한 채팅 함수"""
    with httpx.Client() as client:
        response = client.post(
            "http://127.0.0.1:1234/v1/chat/completions",
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        return response.json()["choices"][0]["message"]["content"]

# 사용
print(chat("안녕하세요!"))
