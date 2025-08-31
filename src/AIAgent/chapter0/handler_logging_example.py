import logging
import sys
from logging.handlers import TimedRotatingFileHandler

# ① 로거(Logger) 생성
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 로거 레벨 설정

# ② 로그 포맷 설정
log_format = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ③ 콘솔(표준 출력) 핸들러 설정
console_handler = logging.StreamHandler(sys.stdout) # ty: ignore
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.DEBUG)  # 콘솔에는 모든 레벨 출력
logger.addHandler(console_handler)

# ④ 시간 기반 파일 핸들러 설정
file_handler = TimedRotatingFileHandler(
    filename='test.log',
    when='midnight',     # 매일 자정에 로그 파일 교체
    interval=1,          # 1일 간격으로 교체
    backupCount=30,      # 최대 30개의 백업 파일 유지
    encoding='utf-8'     # 인코딩 설정
)
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.INFO)  # 파일에는 INFO 레벨 이상만 기록
logger.addHandler(file_handler)

# ⑤ 로깅 예시
if __name__ == "__main__":
    logger.debug("디버그 레벨 메시지입니다.")
    logger.info("정보 레벨 메시지입니다.")
    logger.warning("경고 레벨 메시지입니다.")
    logger.error("에러 레벨 메시지입니다.")
    logger.critical("치명적 에러 레벨 메시지입니다.")