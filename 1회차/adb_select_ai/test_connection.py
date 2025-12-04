import os

# 환경 변수 설정 (실제 값으로 교체 필요)
WALLET_DIR = os.getenv("WALLET_DIR", "/Users/joungminko/devkit/db_conn/Wallet_JTC0W11KMDNYYKBJ")
DB_USER = os.getenv("DB_USER", "NORTHWIND")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Welcome12345#")
DB_DSN = os.getenv("DB_DSN", "jtc0w11kmdnyykbj_low")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD", "Dhfkzmf#12345")

# TNS_ADMIN 설정 (oracledb 로드 전에 필수) - MUST be set BEFORE importing select_ai
os.environ['TNS_ADMIN'] = WALLET_DIR
print(f"TNS_ADMIN: {WALLET_DIR}")

# Now import select_ai AFTER TNS_ADMIN is set
import select_ai

# 데이터베이스 연결
# select_ai.connect(
#     user=DB_USER,
#     password=DB_PASSWORD,
#     dsn=DB_DSN,
#     wallet_location=WALLET_DIR,
#     wallet_password=WALLET_PASSWORD
# )
select_ai.connect(
    user="NORTHWIND",
    password="Welcome12345#",  # 실제 비밀번호로 변경
    dsn="jtc0w11kmdnyykbj_low",  # tnsnames.ora 파일 안의 서비스 별칭
    wallet_location=WALLET_DIR,
    wallet_password="Dhfkzmf#12345"  # 지갑 다운로드 시 설정한 비밀번호
)
print("Connected to database")

# 프로파일 로드
profile = select_ai.Profile(profile_name="NORTHWIND_AI")
print("✓ Profile loaded")

# 자연어 질의 테스트
question = "What is the product with the most stock?"
print(f"\nQuestion: {question}")

# 방법 1: narrate() - 결과와 설명을 자연어로 반환
response = profile.narrate(question)
print(f"Answer: {response}")

# 방법 2: generate() - SQL만 생성
sql = profile.generate(f"showsql {question}")
print(f"\nGenerated SQL:\n{sql}")

# 방법 3: chat() - 일반 대화
info = profile.chat("Tell me about the Northwind database structure")
print(f"\nDatabase Info: {info}")