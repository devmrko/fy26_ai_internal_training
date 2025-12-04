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

from select_ai import SyntheticDataAttributes, SyntheticDataParams 

profile = select_ai.Profile(profile_name="NORTHWIND_AI")

print("\n=== 요약 및 번역 테스트 ===\n")

# 테스트용 긴 텍스트
long_text = """
Chai is a flavored tea beverage made by brewing black tea with a mixture of aromatic 
spices and herbs. Originating in India, the beverage has gained worldwide popularity, 
becoming a feature in many coffee and tea houses. Traditional chai is made with loose-leaf 
black tea, milk, water, and a combination of spices such as cardamom, ginger, cinnamon, 
cloves, and black pepper. The blend of spices varies by region and personal preference.
"""

# 1. 요약 (Summarize)
print("원문 요약 중...")
try:
    summary = profile.summarize(content=long_text)
    print(f"✓ 요약 완료:\n{summary}\n")
except Exception as e:
    print(f"✗ 요약 실패: {e}\n")
    summary = long_text  # 실패 시 원문 사용

# 2. 번역 (Translate) - chat 메서드 사용 (권장)
# 참고: Python SDK의 Action enum에는 TRANSLATE가 없습니다.
# 사용 가능한 Actions: RUNSQL, SHOWSQL, EXPLAINSQL, NARRATE, CHAT, SHOWPROMPT, FEEDBACK, SUMMARIZE
print("한국어로 번역 중...")
try:
    translation = profile.chat(
        f"다음 영문을 자연스러운 한국어로 번역해주세요:\n\n{summary}"
    )
    print(f"✓ 번역 완료:\n{translation}\n")
except Exception as e:
    print(f"✗ 번역 실패: {e}\n")