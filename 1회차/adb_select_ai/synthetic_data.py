import os

WALLET_DIR = os.getenv("WALLET_DIR", "/Users/joungminko/devkit/db_conn/Wallet_JTC0W11KMDNYYKBJ")

os.environ['TNS_ADMIN'] = WALLET_DIR
print(f"TNS_ADMIN: {WALLET_DIR}")

import select_ai
from select_ai import SyntheticDataAttributes, SyntheticDataParams

# 연결 (이미 연결되어 있다면 생략 가능)
if not select_ai.is_connected():
    select_ai.connect(
        user="NORTHWIND",
        password="Welcome12345#",  # 실제 비밀번호로 변경
        dsn="jtc0w11kmdnyykbj_low",  # tnsnames.ora 파일 안의 서비스 별칭
        wallet_location=WALLET_DIR,
        wallet_password="Dhfkzmf#12345"  # 지갑 다운로드 시 설정한 비밀번호
    )

profile = select_ai.Profile(profile_name="NORTHWIND_AI")

print("\n=== Synthetic Data 생성 테스트 ===\n")

# 가상 데이터 생성 파라미터 설정
syn_params = SyntheticDataParams(
    sample_rows=5,      # 기존 데이터 5건을 샘플링하여 패턴 학습
    priority="HIGH"     # 생성 우선순위
)

syn_attr = SyntheticDataAttributes(
    object_name="CUSTOMERS",
    owner_name="NORTHWIND",
    record_count=1,     # 3개의 가상 고객 생성
    user_prompt="Generate realistic customer data for a European food trading company. Include diverse countries and contact information.",
    params=syn_params
)

print("가상 데이터 생성 중...")
try:
    profile.generate_synthetic_data(synthetic_data_attributes=syn_attr)
    print("생성 완료!\n")
    
    # 결과 확인
    print("최근 추가된 고객 5명:")
    result = profile.run_sql(
        "SELECT CUSTOMER_ID, COMPANY_NAME, CONTACT_NAME, CITY, COUNTRY "
        "FROM CUSTOMERS "
        "ORDER BY CUSTOMER_ID DESC "
        "FETCH FIRST 5 ROWS ONLY"
    )
    print(result)
    
except Exception as e:
    print(f"✗ 실패: {e}")
    import traceback
    traceback.print_exc()