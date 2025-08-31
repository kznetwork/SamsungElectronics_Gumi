import os


class Config:
    """프로젝트 설정 관리 클래스"""

    # OpenAI 설정
    # ① 환경변수에서 API 키를 가져오되, 없으면 빈 문자열을 기본값으로 사용
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = "gpt-5-mini"
    MAX_TOKENS: int = 150

    # ② 현재 파일의 위치를 기준으로 프로젝트 루트 디렉토리를 설정
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))

    # RSS 설정
    RSS_URL: str = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    MAX_NEWS_COUNT: int = 60

    # ③ API 호출을 효율적으로 하기 위한 배치 크기를 설정
    BATCH_SIZE: int = 10

    # ④ 뉴스를 분류할 카테고리 목록을 정의
    NEWS_CATEGORIES: list[str] = [
        "정치",
        "경제",
        "사회",
        "문화/연예",
        "IT/과학",
        "스포츠",
        "국제",
        "생활/건강",
        "기타",
    ]

    NEWS_PER_CATEGORY: int = 30  # 카테고리별 표시할 뉴스 수

    # ⑤ 출력 파일들을 저장할 디렉토리 설정
    OUTPUT_DIR: str = f"{ROOT_DIR}/outputs"

    # ⑥ 설정의 유효성을 검사하는 클래스 메서드
    @classmethod
    def validate(cls) -> bool:
        """설정 유효성 검사"""
        if not cls.OPENAI_API_KEY:
            print("OpenAI API 키가 설정되지 않았습니다.")
            print("환경변수 OPENAI_API_KEY를 설정하거나 실행 시 입력하세요.")
            return False
        return True
