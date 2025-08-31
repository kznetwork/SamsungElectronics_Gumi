"""Test client for Basic Hello World A2A Agent."""

import asyncio
from uuid import uuid4
from typing import Any, Optional

import httpx

from a2a.client import A2ACardResolver
from a2a.client.client_factory import ClientFactory
from a2a.client.client import ClientConfig
from a2a.types import Message
from a2a.utils import get_message_text


def create_user_message(text: str, message_id: Optional[str] = None) -> Message:
    """A2A 사용자 메시지 생성 함수."""
    return Message(
        role="user",
        parts=[{"kind": "text", "text": text}],
        messageId=message_id or uuid4().hex,
    )


async def test_basic_agent():
    """헬로 월드 A2A 에이전트 테스트 함수."""
    base_url = "http://localhost:9999"

    print("Basic Hello World A2A Agent 테스트 시작...")
    print(f"서버 URL: {base_url}")
    print("-" * 50)

    async with httpx.AsyncClient() as httpx_client:
        try:
            # ① A2A 카드 리졸버 생성
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=base_url,
            )

            # ② 에이전트 카드 가져오기
            print("에이전트 카드를 가져오는 중...")
            agent_card = await resolver.get_agent_card()
            print(f"에이전트 이름: {agent_card.name}")
            print(f"에이전트 설명: {agent_card.description}")
            print(f"지원 스킬: {[skill.name for skill in agent_card.skills]}")
            print()

            # ③ A2A 클라이언트 생성
            streaming_config = ClientConfig(httpx_client=httpx_client, streaming=True)
            streaming_factory = ClientFactory(streaming_config)
            streaming_client = streaming_factory.create(agent_card)

            non_streaming_config = ClientConfig(
                httpx_client=httpx_client, streaming=False
            )
            non_streaming_factory = ClientFactory(non_streaming_config)
            non_streaming_client = non_streaming_factory.create(agent_card)

            # ④ 테스트 메시지 목록
            test_messages = [
                "안녕하세요",
                "날씨가 어때요?",
                "고마워요",
                "이름이 뭔가요?",
                "오늘 기분이 어때요?",
            ]

            # ⑤ 비스트리밍 메시지 테스트 (streaming=False)
            print("=== 비스트리밍 메시지 테스트 ===")

            for i, message_text in enumerate(test_messages, 1):
                print(f"\n{i}. 사용자: {message_text}")

                # ⑥ 사용자 메시지 생성
                user_message = create_user_message(message_text)

                # ⑦ 비스트리밍 메시지 전송
                async for event in non_streaming_client.send_message(user_message):
                    if isinstance(event, Message):
                        response_text = get_message_text(event)
                        print(response_text)
                        break  # 첫 번째 Message 응답만 처리

            print("\n" + "=" * 50)

            # ⑧ 스트리밍 메시지 테스트 (streaming=True)
            print("=== 스트리밍 메시지 테스트 ===")

            for i, message_text in enumerate(
                test_messages[:3], 1
            ):  # 3개의 메시지만 스트리밍 테스트
                print(f"\n{i}. 사용자: {message_text}")

                # ⑨ 사용자 메시지 생성
                user_message = create_user_message(message_text)

                # ⑩ 스트리밍 메시지 전송
                print("   에이전트 (스트리밍): ", end="", flush=True)
                async for event in streaming_client.send_message(user_message):
                    if isinstance(event, Message):
                        response_text = get_message_text(event)
                        print(response_text, end="", flush=True)
                print()

            print("\n테스트 완료!")

        except Exception as e:
            print(f"테스트 중 오류 발생: {e}")
            print("서버가 실행 중인지 확인해주세요.")
            print("서버 실행: python basic_agent/__main__.py")


async def main():
    """Main function to run the test."""
    await test_basic_agent()


if __name__ == "__main__":
    asyncio.run(main())
