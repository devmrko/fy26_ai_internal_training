import os

# 환경 설정
WALLET_DIR = os.getenv("WALLET_DIR", "/Users/joungminko/devkit/db_conn/Wallet_JTC0W11KMDNYYKBJ")
os.environ['TNS_ADMIN'] = WALLET_DIR

import select_ai
from select_ai import Conversation, ConversationAttributes

# 데이터베이스 연결
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

# 1. 대화 세션 메타데이터 정의
conv_attr = ConversationAttributes(
    title="재고 분석 세션",
    description="Northwind 제품 재고 현황 및 발주 필요성 분석"
)

# 2. 대화 객체 생성 및 등록
conversation = Conversation(attributes=conv_attr)
conv_id = conversation.create()
print(f"Conversation created - Session ID: {conv_id}\n")

# 3. 대화 시작 (문맥 유지)
print("=== 대화형 컨텍스트 테스트 ===\n")

with profile.chat_session(conversation=conversation) as session:
    # Q1: 첫 번째 질문 - 대상 확인
    print("User: 'Beverages' 카테고리에 어떤 제품들이 있어?")
    res1 = session.chat("List products in Beverages category")
    print(f"AI: {res1}\n")

    # Q2: 문맥 질문 ('그 중에서' -> 이전 답변의 Beverages 제품들을 기억)
    print(" User: 그 중에서 재고가 가장 적은 건 뭐야?")
    res2 = session.chat("Which one has the lowest stock?")
    print(f"AI: {res2}\n")
    
    # Q3: 추가 추론 질문 (이전 대화 내용 기반)
    print("User: 그걸 채우려면 얼마나 더 주문해야 할까?")
    res3 = session.chat("Considering units on order, do we need to order more?")
    print(f"AI: {res3}\n")

print("✓ Conversation completed")