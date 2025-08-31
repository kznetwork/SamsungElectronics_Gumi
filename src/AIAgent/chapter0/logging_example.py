import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='test.log',
    filemode='a' # w: 새로 쓰기, a: 이어서 쓰기 
)

# ② 로거(Logger) 생성
logger = logging.getLogger(__name__)

# ③ 로깅 예시
if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.debug("디버그 레벨 메시지입니다.")
    logger.info("정보 레벨 메시지입니다.")
    logger.warning("경고 레벨 메시지입니다.")
    logger.error("에러 레벨 메시지입니다.")
    logger.critical("치명적 에러 레벨 메시지입니다.")