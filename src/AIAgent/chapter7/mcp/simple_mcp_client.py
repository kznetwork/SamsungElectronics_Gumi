import asyncio
from fastmcp import Client

async def main():
    """MCP 클라이언트를 사용하여 서버와 통신합니다."""

    client = Client("http://localhost:8000/mcp")
    print("MCP 클라이언트를 생성하고 서버에 연결합니다.\n")

    try:
        # ① async with 블록을 사용하여 클라이언트 세션을 관리합니다.
        async with client:
            print("--- 사용 가능한 도구 목록 ---")
            tools = await client.list_tools()
            print([tool.name for tool in tools])
            print("")

            # ② 'hello' 도구 테스트
            print("--- 'hello' 도구 테스트 ---")
            response_default = await client.call_tool("hello")
            # call_tool은 콘텐츠 객체의 리스트를 반환합니다.
            print(f"기본 호출: {response_default[0].text}")

            response_custom = await client.call_tool("hello", {"name": "승귤"})
            print(f"이름 지정 호출: {response_custom[0].text}\n")

            # ③ 'get_prompt' 도구 테스트
            print("--- 'get_prompt' 도구 테스트 ---")
            prompt_code = await client.call_tool(
                "get_prompt", {"prompt_type": "code_review"}
            )
            print(f"'code_review' 프롬프트:\n{prompt_code[0].text}\n")

            # ④ 'simple://info' 리소스 테스트
            print("--- 'simple://info' 리소스 테스트 ---")
            resource_content = await client.read_resource("simple://info")
            # read_resource도 콘텐츠 객체의 리스트를 반환합니다.
            print(f"리소스 내용:\n{resource_content[0].text}")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")


if __name__ == "__main__":
    asyncio.run(main())
