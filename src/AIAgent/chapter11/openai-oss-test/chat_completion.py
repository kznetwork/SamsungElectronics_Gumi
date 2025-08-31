import httpx

def quick_chat(prompt, temperature=0.7):
    """빠른 테스트를 위한 간단한 함수"""
    with httpx.Client() as client:
        response = client.post(
            "http://127.0.0.1:1234/v1/chat/completions",
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
        )
        return response.json()["choices"][0]["message"]["content"]

# 사용
print(quick_chat("안녕하세요!"))
