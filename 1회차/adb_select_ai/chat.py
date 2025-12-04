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

from select_ai import Conversation, ConversationAttributes

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
print(f"대화 생성 완료 - 세션 ID: {conv_id}\n")

# 3. 대화 시작 (narrate로 데이터 조회 → chat으로 의견 교환)
print("=== 시나리오: narrate()로 DB 조회, chat()으로 LLM 의견 수렴 ===\n")

with profile.chat_session(conversation=conversation) as session:
    
    # ==========================================
    # 단계 1: narrate()로 실제 데이터 조회
    # ==========================================
    print("=" * 60)
    print("단계 1: narrate()로 DB에서 실제 데이터 조회")
    print("=" * 60)
    
    print("\n[DB 쿼리] Beverages 카테고리 제품 재고 조회 중...")
    db_query = "List all products in the Beverages category with their unit price, units in stock, and units on order"
    beverages_data = profile.narrate(db_query)
    print(f"\n📊 데이터베이스 조회 결과:\n{beverages_data}\n")
    
    # ==========================================
    # 단계 2: chat()으로 LLM 분석 및 의견 받기
    # ==========================================
    print("=" * 60)
    print("단계 2: chat()으로 LLM에게 데이터 분석 요청")
    print("=" * 60)
    
    print("\n[사용자] 재고 데이터 분석 요청...")
    analysis_request = f"""다음 Beverages 재고 데이터를 간단히 분석해주세요:

{beverages_data}

가장 우려되는 제품과 이유, 그리고 개선 방안을 3-4문장으로 요약해주세요."""
    
    analysis = session.chat(analysis_request)
    print(f"\n🤖 LLM 분석:\n{analysis}\n")
    
    # ==========================================
    # 단계 3: 추가 질문 (대화 맥락 유지)
    # ==========================================
    print("=" * 60)
    print("단계 3: 대화 맥락을 유지하며 추가 질문")
    print("=" * 60)
    
    print("\n[사용자] 우선순위 질문...")
    priority_question = session.chat("가장 먼저 재주문해야 할 제품을 1-2개만 간단히 추천해주세요.")
    print(f"\n🤖 LLM 답변:\n{priority_question}\n")

print("=" * 60)
print("✓ 대화 완료")
print("=" * 60)
print("\n💡 요약:")
print("  1. narrate() → DB에서 실제 재고 데이터 조회")
print("  2. chat() → LLM에게 데이터 분석 및 의견 요청")
print("  3. chat() → 대화 맥락 유지하며 추가 질문")
print("\n✨ narrate()는 팩트(데이터), chat()은 인사이트(분석)를 제공합니다!")