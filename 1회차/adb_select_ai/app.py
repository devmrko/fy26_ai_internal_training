"""
Northwind Data Assistant - Oracle Select AI Chatbot
Streamlit 기반 웹 UI로, 자연어 질문을 Oracle ADB에 보내고 결과를 확인하는 챗봇입니다.

실행 방법:
  uv run streamlit run app.py
"""

import os
from dotenv import load_dotenv

# ============================================================================
# 1단계: 환경 변수 로드 (.env 파일에서 DB 접속 정보를 읽어옵니다)
# ============================================================================
# ⚠️ 중요: TNS_ADMIN을 oracledb/select_ai 임포트 전에 설정해야 함!
load_dotenv()

WALLET_DIR = os.getenv("WALLET_DIR")         # Wallet 폴더 경로
DB_USER = os.getenv("DB_USER")               # DB 사용자명 (예: NORTHWIND)
DB_PASSWORD = os.getenv("DB_PASSWORD")       # DB 비밀번호
DB_DSN = os.getenv("DB_DSN")                 # DB 접속 별칭 (예: mydb_low)
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")  # Wallet 비밀번호

# 환경 변수가 하나라도 없으면 에러를 발생시킵니다
for var_name, var_val in [("WALLET_DIR", WALLET_DIR), ("DB_USER", DB_USER),
                          ("DB_PASSWORD", DB_PASSWORD), ("DB_DSN", DB_DSN),
                          ("WALLET_PASSWORD", WALLET_PASSWORD)]:
    if not var_val:
        raise ValueError(f"{var_name} 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")

# Oracle DB 접속에 필요한 TNS_ADMIN 경로 설정 (import 전에 반드시 실행)
os.environ['TNS_ADMIN'] = WALLET_DIR

# ============================================================================
# 2단계: 라이브러리 임포트 (TNS_ADMIN 설정 후에 import 해야 합니다)
# ============================================================================
import streamlit as st    # 웹 UI 프레임워크
import pandas as pd       # 데이터프레임 (표 형태로 결과 표시)
import oracledb           # Oracle DB 직접 연결 (SQL 실행용)
import select_ai          # Oracle Select AI Python SDK


# ============================================================================
# 3단계: 데이터베이스 연결 함수들
# ============================================================================

def connect_to_database():
    """Oracle ADB에 연결합니다. 이미 연결되어 있으면 재연결하지 않습니다."""
    try:
        if not select_ai.is_connected():
            select_ai.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN,
                wallet_location=WALLET_DIR,
                wallet_password=WALLET_PASSWORD
            )
        return True, None
    except Exception as e:
        return False, str(e)


@st.cache_resource
def get_ai_profile(profile_name):
    """AI 프로파일 객체를 가져옵니다. 캐시되어 재사용됩니다."""
    try:
        return select_ai.Profile(profile_name=profile_name)
    except Exception as e:
        st.error(f"프로파일 로드 실패: {e}")
        return None


def _get_connection():
    """Oracle ADB에 직접 연결을 생성합니다 (with문과 함께 사용)."""
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
        config_dir=WALLET_DIR,
        wallet_location=WALLET_DIR,
        wallet_password=WALLET_PASSWORD
    )


def get_sql_for_question(question, profile_name):
    """자연어 질문을 SQL로 변환합니다 (SELECT AI showsql 사용)."""
    try:
        # with문으로 연결 관리 (에러 발생 시에도 자동으로 연결 종료)
        with _get_connection() as conn:
            with conn.cursor() as cursor:
                # 사용할 AI 프로파일 활성화
                cursor.execute(f"""
                    BEGIN
                        DBMS_CLOUD_AI.SET_PROFILE(profile_name => '{profile_name}');
                    END;
                """)
                conn.commit()

                # 작은따옴표 이스케이프 (예: "What's" → "What''s")
                safe_question = question.replace("'", "''")

                # 자연어 -> SQL 변환 (showsql: SQL만 반환, 실행하지 않음)
                cursor.execute(f"SELECT AI showsql '{safe_question}'")
                result = cursor.fetchone()

                return result[0] if result and result[0] else None
    except Exception as e:
        st.error(f"SQL 생성 실패: {e}")
        return None


def execute_sql(sql):
    """SQL을 실행하고 결과를 pandas DataFrame으로 반환합니다."""
    try:
        with _get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)

                rows = cursor.fetchall()
                # 컬럼 이름 추출
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                if rows and columns:
                    return pd.DataFrame(rows, columns=columns)
                return None
    except Exception as e:
        st.error(f"SQL 실행 실패: {e}")
        return None


# ============================================================================
# 4단계: AI 응답 모드별 처리 함수
# ============================================================================

def chat_mode(profile, question):
    """Chat 모드: DB 데이터 없이 AI와 자유 대화 (스키마 질문 등)"""
    response = profile.chat(question)
    st.markdown(response)
    return {"content": response}


def narrate_mode(profile, question, profile_name, show_sql):
    """Narrate 모드: DB에서 데이터를 조회하고 자연어로 설명 (가장 권장)"""
    sql = None
    # SQL 보기 옵션이 켜져 있으면 생성된 SQL을 먼저 표시
    if show_sql:
        with st.spinner("SQL 생성 중..."):
            sql = get_sql_for_question(question, profile_name)
            if sql:
                st.code(sql, language="sql")

    # 자연어로 결과 설명
    with st.spinner("결과 조회 및 설명 생성 중..."):
        response = profile.narrate(question)
        st.markdown(response)

    return {"content": response, "sql": sql}


def sql_only_mode(question, profile_name):
    """SQL Only 모드: SQL만 생성하고 표시 (실행 버튼으로 직접 실행 가능)"""
    with st.spinner("SQL 생성 중..."):
        sql = get_sql_for_question(question, profile_name)

        if sql:
            st.markdown("**생성된 SQL:**")
            st.code(sql, language="sql")

            # 실행 버튼 - 클릭하면 SQL을 실제로 DB에서 실행
            if st.button("🚀 SQL 실행"):
                with st.spinner("실행 중..."):
                    df = execute_sql(sql)
                    if df is not None:
                        st.success(f"✅ {len(df)}건 조회됨")
                        st.dataframe(df, use_container_width=True)

            return {"content": "**생성된 SQL:**", "sql": sql}
        else:
            st.error("SQL 생성에 실패했습니다")
            return {"content": "SQL 생성 실패"}


def runsql_mode(question, profile_name, show_sql, show_table):
    """RunSQL 모드: SQL을 생성하고 자동으로 실행하여 결과를 표로 표시"""
    with st.spinner("SQL 생성 및 실행 중..."):
        sql = get_sql_for_question(question, profile_name)

        if not sql:
            st.error("SQL 생성에 실패했습니다")
            return {"content": "SQL 생성 실패"}

        # SQL 보기 옵션이 켜져 있으면 SQL 표시
        if show_sql:
            st.code(sql, language="sql")

        # SQL 실행
        df = execute_sql(sql)

        if df is not None:
            st.markdown(f"**결과: {len(df)}건**")

            if show_table:
                st.dataframe(df, use_container_width=True)
            else:
                st.write(df)

            return {
                "content": f"**결과: {len(df)}건**",
                "sql": sql,
                "dataframe": df
            }
        else:
            st.info("조회 결과가 없습니다")
            return {"content": "결과 없음", "sql": sql}


# ============================================================================
# 5단계: UI 구성 (페이지 설정, 사이드바, 채팅 이력)
# ============================================================================

def setup_page():
    """페이지 기본 설정 (제목, 레이아웃 등)"""
    st.set_page_config(
        page_title="Northwind Data Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🤖 Northwind Data Assistant")
    st.markdown("*자연어로 데이터베이스에 질문하세요*")


def setup_sidebar():
    """사이드바 설정: DB 연결 상태, AI 프로파일 선택, 쿼리 모드 등"""
    with st.sidebar:
        st.header("⚙️ 설정")

        # --- DB 연결 상태 표시 ---
        st.subheader("🔌 데이터베이스")
        success, error = connect_to_database()
        if success:
            st.success("✅ 연결됨")
        else:
            st.error("❌ 연결 실패")
            if error:
                st.error(error)
            st.stop()  # 연결 실패 시 앱 중단

        # --- AI 프로파일 선택 ---
        st.subheader("🎯 AI 프로파일")
        try:
            # DB에서 사용 가능한 프로파일 목록 조회
            profile_objects = select_ai.Profile.list()
            if profile_objects:
                available_profiles = [p.profile_name for p in profile_objects]
            else:
                st.warning("⚠️ 프로파일이 없습니다")
                available_profiles = ["NORTHWIND_AI"]

            profile = st.selectbox(
                "프로파일 선택",
                available_profiles,
                help="DB에 생성된 AI 프로파일을 선택하세요"
            )
        except Exception as e:
            st.warning(f"⚠️ 프로파일 조회 실패: {e}")
            profile = st.selectbox("프로파일 선택", ["NORTHWIND_AI"])

        # --- 쿼리 모드 선택 ---
        st.subheader("💬 모드")
        mode = st.radio(
            "쿼리 모드",
            ["Chat", "Narrate", "SQL Only", "RunSQL"],
            index=1,  # 기본값: Narrate
            help="Narrate 모드가 대부분의 질의에 적합합니다"
        )

        # --- 표시 옵션 ---
        st.subheader("🔧 표시 옵션")
        show_sql = st.checkbox("SQL 보기", value=True)
        show_table = st.checkbox("표 형태로 보기", value=True)

        # --- 예시 질문 ---
        st.subheader("💡 질문 예시")
        st.markdown("""
        - 가장 비싼 제품 5개는?
        - 재고가 10개 미만인 제품은?
        - 고객별 주문 횟수는?
        - Beverages 카테고리 총 매출은?
        """)

        # --- 대화 이력 초기화 ---
        st.divider()
        if st.button("🔄 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        return profile, mode, show_sql, show_table


def display_chat_history(show_sql, show_table):
    """이전 대화 이력을 화면에 표시합니다."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                # SQL이 있으면 코드 블록으로 표시
                if show_sql and msg.get("sql"):
                    st.code(msg["sql"], language="sql")

                # DataFrame이 있으면 표로 표시
                if show_table and "dataframe" in msg:
                    df = msg.get("dataframe")
                    if df is not None and isinstance(df, pd.DataFrame):
                        st.dataframe(df, use_container_width=True)

                # 텍스트 응답 표시
                if msg.get("content"):
                    st.markdown(msg["content"])


def process_user_input(prompt, profile_name, mode, show_sql, show_table):
    """사용자 입력을 처리하고 AI 응답을 생성합니다."""
    # 사용자 메시지를 이력에 추가
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        profile = get_ai_profile(profile_name)
        if not profile:
            return

        try:
            # 선택된 모드에 따라 적절한 함수 호출
            if mode == "Chat":
                response_data = chat_mode(profile, prompt)
            elif mode == "Narrate":
                response_data = narrate_mode(profile, prompt, profile_name, show_sql)
            elif mode == "SQL Only":
                response_data = sql_only_mode(prompt, profile_name)
            elif mode == "RunSQL":
                response_data = runsql_mode(prompt, profile_name, show_sql, show_table)
            else:
                response_data = {"content": "알 수 없는 모드"}

            # 응답을 이력에 저장
            response_data["role"] = "assistant"
            st.session_state.messages.append(response_data)

        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.exception(e)


# ============================================================================
# 6단계: 메인 함수 - 앱 실행 진입점
# ============================================================================

def main():
    """앱 실행: 페이지 설정 → 사이드바 → 대화 이력 → 사용자 입력 처리"""
    setup_page()
    profile_name, mode, show_sql, show_table = setup_sidebar()

    # 채팅 이력 초기화 (첫 실행 시)
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 안녕하세요! Northwind 데이터베이스에 대해 자유롭게 질문하세요."
        })

    # 이전 대화 표시
    display_chat_history(show_sql, show_table)

    # 사용자 입력 처리
    if prompt := st.chat_input("질문을 입력하세요 (예: 가장 비싼 제품 5개는?)"):
        process_user_input(prompt, profile_name, mode, show_sql, show_table)

    # 하단 푸터
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "<small>Powered by Oracle Select AI</small>"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
