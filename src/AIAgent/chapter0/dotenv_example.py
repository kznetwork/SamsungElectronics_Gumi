from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 사용
mongodb_url = os.environ.get('MONGO_DB_URL')
phase = os.environ.get('PHASE')

print(mongodb_url)
print(phase)