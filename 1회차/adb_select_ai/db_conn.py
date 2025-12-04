import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 지갑 경로 설정 (압축 푼 폴더의 전체 경로)
WALLET_DIR = os.getenv("WALLET_DIR")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

# 필수 환경 변수 체크
if not WALLET_DIR:
    raise ValueError("WALLET_DIR environment variable is not set. Please create a .env file with required variables.")
if not DB_USER:
    raise ValueError("DB_USER environment variable is not set.")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is not set.")
if not DB_DSN:
    raise ValueError("DB_DSN environment variable is not set.")
if not WALLET_PASSWORD:
    raise ValueError("WALLET_PASSWORD environment variable is not set.")

# TNS_ADMIN 설정 (oracledb 모듈이 로드되기 전에 반드시 설정)
os.environ['TNS_ADMIN'] = WALLET_DIR

# 이제 select_ai를 import (TNS_ADMIN이 설정된 후)
import select_ai

# 연결 시도
select_ai.connect(
    user=DB_USER,
    password=DB_PASSWORD,  # 실제 비밀번호로 변경
    dsn=DB_DSN,  # tnsnames.ora 파일 안의 서비스 별칭
    wallet_location=WALLET_DIR,
    wallet_password=WALLET_PASSWORD  # 지갑 다운로드 시 설정한 비밀번호
)
print("Connected securely using Wallet")