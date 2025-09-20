from mcp.server.fastmcp import FastMCP

# ① FastMCP 인스턴스를 생성
mcp = FastMCP("Simple MCP Server")


@mcp.tool()  # ② 도구를 정의합니다.
def hello(name: str = "World") -> str:
    """간단한 인사말을 반환하는 도구"""
    return f"안녕하세요, {name}님!"


@mcp.tool()
def get_prompt(prompt_type: str = "general") -> str:
    """사전 정의된 프롬프트를 반환하는 도구"""
    prompts = {
        "general": "당신은 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 정확하고 친절하게 답변해주세요.",
        "code_review": "다음 코드를 검토하고 개선점을 제안해주세요. 코드의 가독성, 성능, 보안 측면을 고려해주세요.",
        "translate": "다음 텍스트를 자연스러운 한국어로 번역해주세요.",
        "summarize": "다음 내용을 핵심 포인트 중심으로 간결하게 요약해주세요.",
    }
    return prompts.get(prompt_type, prompts["general"])


@mcp.resource("simple://info")  # ③ 리소스를 정의합니다.
def get_server_info() -> str:
    """서버 정보를 제공하는 리소스"""
    return """
    Simple MCP Server 정보
    =====================
    
    이 서버는 MCP(Model Context Protocol)의 기본 기능을 시연하는 간단한 예제입니다.
    
    제공하는 도구:
    - hello: 인사말 생성
    - get_prompt: 프롬프트 템플릿 제공
    
    제공하는 리소스:
    - simple://info: 서버 정보
    """


if __name__ == "__main__":
    """서버를 실행합니다."""
    # ④ 서버를 실행합니다.
    mcp.run(transport="streamable-http")
