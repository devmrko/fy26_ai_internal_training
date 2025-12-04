import os

# 지갑 경로 설정 (압축 푼 폴더의 전체 경로)
wallet_dir = "/Users/joungminko/devkit/db_conn/Wallet_JTC0W11KMDNYYKBJ" 

# TNS_ADMIN 설정 (oracledb 모듈이 로드되기 전에 반드시 설정)
os.environ['TNS_ADMIN'] = wallet_dir

# 이제 select_ai를 import (TNS_ADMIN이 설정된 후)
import select_ai

# 연결 시도
select_ai.connect(
    user="NORTHWIND",
    password="Welcome12345#",  # 실제 비밀번호로 변경
    dsn="jtc0w11kmdnyykbj_low",  # tnsnames.ora 파일 안의 서비스 별칭
    wallet_location=wallet_dir,
    wallet_password="Dhfkzmf#12345"  # 지갑 다운로드 시 설정한 비밀번호
)
print("✓ Connected securely using Wallet")