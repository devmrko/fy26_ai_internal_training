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

# 2. 번역 (Translate) - chat 메서드 사용
print("한국어로 번역 중...")
try:
    translation = profile.chat(
        f"다음 영문을 자연스러운 한국어로 번역해주세요:\n\n{summary}"
    )
    print(f"✓ 번역 완료:\n{translation}\n")
except Exception as e:
    print(f"✗ 번역 실패: {e}\n")

# 3. 데이터베이스 내용 요약 예제
print("데이터베이스 쿼리 결과 요약...")
try:
    # 제품 정보를 조회하여 요약
    query_result = profile.chat(
        "Summarize the product catalog in 2-3 sentences, "
        "focusing on product categories and price ranges."
    )
    print(f"✓ 제품 카탈로그 요약:\n{query_result}")
except Exception as e:
    print(f"✗ 쿼리 요약 실패: {e}")