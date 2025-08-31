from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import uvicorn


def create_prompt_template() -> ChatPromptTemplate:
    """에이전트를 위한 프롬프트 템플릿을 생성합니다."""
    system_prompt = """당신은 친절하고 도움이 되는 AI 어시스턴트 "금토깽"입니다. 

다음과 같은 도구들을 활용하여 사용자를 도와드릴 수 있습니다:
- 웹페이지의 텍스트 콘텐츠를 스크랩하여 정보를 가져올 수 있습니다
- 도시 이름을 받아 해당 도시의 현재 날씨 정보를 제공할 수 있습니다
- 구글 RSS 피드에서 최신 뉴스와 URL을 가져올 수 있습니다
- 한국 프로야구 구단의 랭킹 정보를 제공할 수 있습니다
- 일정과 스케줄 정보를 확인할 수 있습니다
- 사용자에게 영감을 주는 명언을 제공할 수 있습니다
- 사용자의 하루 일정 준비를 도와주는 브리핑 기능이 있습니다. 
  사용자가 위치한 곳을 안다면 바로 brief_today() 도구의 지침을 따르면 됩니다. 아니라면, 위치를 물어보고나서 도구의 지침을 따릅니다. 

사용자와의 대화에서 다음 원칙을 지켜주세요:
1. 항상 친절하고 정중한 태도로 응답해주세요
2. 사용자의 질문을 정확히 이해하고 관련된 도구를 적절히 활용해주세요
3. 최신 뉴스를 요청받으면, 도구의 출력을 그대로 출력하면 됩니다.
4. 응답은 명확하고 이해하기 쉽게 구성해주세요
5. 필요시 추가 정보나 설명을 제공하여 사용자에게 더 나은 도움을 주세요
6. 링크가 포함된 정보를 제공할 때는 [제목](URL) 형태의 마크다운 링크로 제공해주세요
"""
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )


def create_agent(tools):
    """주어진 도구를 사용하여 에이전트를 생성합니다."""
    memory = InMemorySaver()
    prompt = create_prompt_template()
    llm = ChatOpenAI(model="gpt-5-mini")
    return create_react_agent(llm, tools, checkpointer=memory, prompt=prompt)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 애플리케이션의 생명주기 동안 MCP 연결 및 에이전트 설정을 관리합니다."""
    print("애플리케이션 시작: MCP 서버에 연결하고 에이전트를 설정합니다...")

    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            app.state.agent_executor = create_agent(tools)
            print("에이전트 설정 완료. 애플리케이션이 준비되었습니다.")
            yield

    print("애플리케이션 종료.")
    app.state.agent_executor = None


# lifespan 관리자를 사용하여 FastAPI 앱 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# 정적 파일 마운트
static_path = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# chat_agent.py 파일의 위치를 기준으로 templates 디렉토리의 절대 경로를 계산
templates_path = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=templates_path)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """메인 채팅 페이지를 렌더링"""
    return templates.TemplateResponse("index.html", {"request": request})


async def stream_agent_response(agent_executor, message: str, session_id: str):
    """에이전트의 응답을 스트리밍하는 비동기 제너레이터"""
    if agent_executor is None:
        yield "에이전트가 아직 준비되지 않았습니다. 잠시 후 다시 시도해주세요."
        return

    try:
        config = {"configurable": {"thread_id": session_id}}
        input_message = HumanMessage(content=message)

        # astream_events를 사용하여 응답 스트리밍
        async for event in agent_executor.astream_events(
            {"messages": [input_message]},
            config=config,
            version="v1",
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    # 스트리밍된 콘텐츠를 클라이언트로 전송
                    yield content
            elif kind == "on_tool_start":
                # TODO: 도구 사용 시작을 클라이언트에 알릴 수 있습니다.
                print(f"Tool start: {event['name']}")
            elif kind == "on_tool_end":
                # TODO: 도구 사용 완료를 클라이언트에 알릴 수 있습니다.
                print(f"Tool end: {event['name']}")
            else:
                print(event)

    except Exception as e:
        print(f"스트리밍 중 오류 발생: {e}")
        yield f"오류가 발생했습니다: {e}"


@app.post("/chat")
async def chat(request: Request, message: str = Form(...), session_id: str = Form(...)):
    """사용자 메시지를 받아 에이전트의 응답을 스트리밍합니다."""
    agent_executor = request.app.state.agent_executor
    return StreamingResponse(
        stream_agent_response(agent_executor, message, session_id),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
