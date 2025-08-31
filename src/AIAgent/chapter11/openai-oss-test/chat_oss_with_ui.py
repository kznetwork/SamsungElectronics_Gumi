from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
import asyncio
from typing import List, Dict, Optional
import uuid

app = FastAPI()

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 설정
GPT_OSS_URL = "http://127.0.0.1:1234"
MODEL_NAME = "openai/gpt-oss-20b"

# 요청 모델
class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7
    max_tokens: int = 1000
    conversation_id: Optional[str] = None
    
# 대화 저장소 (실제 환경에서는 Redis나 DB 사용 권장)
conversations: Dict[str, List[Dict]] = {}

# GPT-OSS 통신 함수
async def generate_sse_response(messages: List[Dict], temperature: float = 0.7):
    """GPT-OSS로부터 스트리밍 응답을 받아 SSE 형식으로 전송"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{GPT_OSS_URL}/v1/chat/completions",
                json={
                    "model": MODEL_NAME,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": True
                }
            ) as response:
                full_response = ""
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            yield f"data: {json.dumps({'type': 'done', 'content': full_response})}\n\n"
                            break
                        try:
                            chunk = json.loads(line[6:])
                            if content := chunk["choices"][0]["delta"].get("content"):
                                full_response += content
                                yield f"data: {json.dumps({'type': 'stream', 'content': content})}\n\n"
                        except json.JSONDecodeError:
                            continue
                            
    except httpx.ConnectError:
        yield f"data: {json.dumps({'type': 'error', 'content': 'GPT-OSS 서버에 연결할 수 없습니다.'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

# 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 스트리밍 채팅 엔드포인트
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE를 사용한 스트리밍 채팅"""
    
    if not request.conversation_id:
        request.conversation_id = str(uuid.uuid4())
    
    if request.conversation_id not in conversations:
        conversations[request.conversation_id] = []
    
    messages = conversations[request.conversation_id]
    messages.append({"role": "user", "content": request.message})
    
    async def event_generator():
        assistant_message = ""
        async for event in generate_sse_response(messages, request.temperature):
            yield event
            try:
                data = json.loads(event.split("data: ")[1])
                if data["type"] == "stream":
                    assistant_message += data["content"]
                elif data["type"] == "done":
                    messages.append({"role": "assistant", "content": assistant_message})
            except:
                pass
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

# 일반 채팅 엔드포인트
@app.post("/chat")
async def chat(request: ChatRequest):
    """일반 채팅 (스트리밍 없음)"""
    
    if not request.conversation_id:
        request.conversation_id = str(uuid.uuid4())
    
    if request.conversation_id not in conversations:
        conversations[request.conversation_id] = []
    
    messages = conversations[request.conversation_id]
    messages.append({"role": "user", "content": request.message})
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{GPT_OSS_URL}/v1/chat/completions",
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": False
            }
        )
        result = response.json()
        assistant_message = result["choices"][0]["message"]["content"]
        
        messages.append({"role": "assistant", "content": assistant_message})
        
        return {
            "response": assistant_message,
            "conversation_id": request.conversation_id
        }

# 대화 초기화
@app.post("/chat/reset/{conversation_id}")
async def reset_chat(conversation_id: str):
    """대화 초기화"""
    if conversation_id in conversations:
        del conversations[conversation_id]
    return {"status": "reset", "conversation_id": conversation_id}

# 대화 히스토리 조회
@app.get("/chat/history/{conversation_id}")
async def get_history(conversation_id: str):
    """대화 히스토리 조회"""
    return {
        "conversation_id": conversation_id,
        "messages": conversations.get(conversation_id, [])
    }

# 서버 상태 확인
@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GPT_OSS_URL}/")
            gpt_oss_status = "connected" if response.status_code == 200 else "error"
    except:
        gpt_oss_status = "disconnected"
    
    return {
        "status": "healthy",
        "gpt_oss_status": gpt_oss_status,
        "active_conversations": len(conversations)
    }

if __name__ == "__main__":
    import uvicorn
    # reload=True를 제거
    uvicorn.run(app, host="0.0.0.0", port=18000)