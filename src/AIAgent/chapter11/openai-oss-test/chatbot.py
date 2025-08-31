import httpx
import json

class GPTOSSChat:
    def __init__(self, base_url="http://127.0.0.1:1234", timeout=30.0):
        self.base_url = base_url
        self.model = "openai/gpt-oss-20b"
        self.messages = []
        self.timeout = timeout
        # 재사용 가능한 클라이언트 생성
        self.client = httpx.Client(timeout=timeout)
    
    def add_message(self, role, content):
        """메시지를 대화 히스토리에 추가"""
        self.messages.append({"role": role, "content": content})
    
    def chat(self, user_input, temperature=0.7, max_tokens=1000):
        """사용자 입력을 받아 응답 생성"""
        self.add_message("user", user_input)
        
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        
        data = {
            "model": self.model,
            "messages": self.messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # 어시스턴트 응답을 히스토리에 추가
            self.add_message("assistant", assistant_message)
            
            return assistant_message
            
        except httpx.HTTPStatusError as e:
            print(f"HTTP 오류: {e}")
            return None
        except httpx.RequestError as e:
            print(f"요청 오류: {e}")
            return None
    
    def reset_conversation(self):
        """대화 히스토리 초기화"""
        self.messages = []
    
    def set_system_prompt(self, prompt):
        """시스템 프롬프트 설정"""
        self.messages = [{"role": "system", "content": prompt}]
    
    def close(self):
        """클라이언트 연결 종료"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# 대화형 사용 예시
if __name__ == "__main__":
    # context manager 사용
    with GPTOSSChat() as chatbot:
        chatbot.set_system_prompt("You are a helpful and friendly assistant.")
        
        print("GPT-OSS 챗봇 (종료하려면 'quit' 입력)")
        print("-" * 50)
        
        while True:
            user_input = input("\n사용자: ")
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("챗봇을 종료합니다.")
                break
            
            response = chatbot.chat(user_input)
            
            if response:
                print(f"\nGPT-OSS: {response}")
            else:
                print("응답을 받지 못했습니다.")
