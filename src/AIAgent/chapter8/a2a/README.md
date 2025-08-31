# Google A2A (Agent-to-Agent) Examples

이 디렉토리는 Google A2A 프로토콜을 사용한 에이전트 구현 예제들을 포함합니다.

## 프로젝트 구조

```
chapter5/a2a/
└── basic_agent/                 # 기본 Hello World 에이전트
     ├── main.py                 # 서버 실행
     ├── agent_executor.py       # 기본 에이전트 로직
     └── test_client.py          # 테스트 클라이언트
```

## 설치 및 설정

### 1. 의존성 설치

```bash
# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 사용법

### Basic Agent (기본 예제)

간단한 Hello World 에이전트로 A2A 기본 개념을 학습할 수 있습니다.

```bash
# 서버 실행
cd basic_agent
python main.py

# 새 터미널에서 클라이언트 테스트
python test_client.py
```


## 주요 기능

### Basic Agent
- A2A 프로토콜 기본 구현
- 비스트리밍/스트리밍 메시지 처리
- 간단한 에이전트 카드 및 스킬 정의


## 참고 자료

- [Google A2A 공식 문서](https://google-a2a.github.io/A2A/)
- [A2A Python SDK](https://github.com/google-a2a/a2a-samples)
- [A2A 프로토콜 명세](https://google-a2a.github.io/A2A/specification/)
