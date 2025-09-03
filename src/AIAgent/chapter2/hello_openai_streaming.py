from openai import OpenAI
import os
import rich

os.environ["OPENAI_API_KEY"] = "-proj-DRnE5vys0joMbWlqJ4L9mO7ta67EFYLcvYiOMSB-4EqCazZ38lIDHzVROijGLy8cZuew6yEVhkT3BlbkFJwk1CwBOm_wXbxQZ7ePoA3UnHHqwWJ6UktyaAisceZYm1abuk77cI27E5cunrmsnndg30EELF4A"


# ② OpenAI API 키 가져오기
api_key = os.environ.get("OPENAI_API_KEY")
# ③ OpenAI 클라이언트 초기화
#  client = OpenAI() # 이렇게 해도 문제 없음
client = OpenAI(api_key=api_key) # OpenAI 클라이언트 초기화

default_model = "gpt-5-mini"


def stream_chat_completion(prompt, model):
    # ① chat.completions API를 사용한 스트리밍 응답 함수
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,  # ② 스트리밍 모드 활성화
    )
    for chunk in stream:  # ③ 응답 청크(조각)를 하나씩 처리
        content = chunk.choices[0].delta.content
        if content is not None:
            print(content, end="")


def stream_response(prompt, model):
    # ④ 새로운 responses API를 사용한 스트리밍 함수( 컨텍스트 매니저로 스트림 관리)
    with client.responses.stream(model=model, input=prompt) as stream:
        for event in stream:  # ⑤ 스트림에서 발생하는 각 이벤트 처리
            if "output_text" in event.type:  # ⑥ 텍스트 출력 이벤트인 경우
                rich.print(event)
    rich.print(stream.get_final_response())  # 최종 응답 출력


if __name__ == "__main__":
    # stream_chat_completion("스트리밍이 뭔가요?", default_model)
    stream_response("점심 메뉴 추천 해주세요.", default_model)
