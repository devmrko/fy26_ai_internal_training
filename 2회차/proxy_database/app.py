"""
Northwind Data Assistant - Oracle Select AI Chatbot (2회차: Sidecar & 이기종 DB)
Streamlit 기반 웹 UI로, 자연어 질문을 Oracle ADB에 보내고 결과를 확인하는 챗봇입니다.
1회차 app.py에서 확장: 다중 프로파일, Feedback, Comment 편집, 쿼리 이력 기능 포함.

실행 방법:
  uv run streamlit run app.py
"""

import os
import json
import re
from dotenv import load_dotenv

# ============================================================================
# 1단계: 환경 변수 로드 (.env 파일에서 DB 접속 정보를 읽어옵니다)
# ============================================================================
# ⚠️ 중요: TNS_ADMIN을 oracledb/select_ai 임포트 전에 설정해야 함!
load_dotenv()

WALLET_DIR = os.getenv("WALLET_DIR")             # Wallet 폴더 경로
DB_USER = os.getenv("DB_USER")                   # DB 사용자명 (예: NORTHWIND)
DB_PASSWORD = os.getenv("DB_PASSWORD")           # DB 비밀번호
DB_DSN = os.getenv("DB_DSN")                     # DB 접속 별칭 (예: mydb_low)
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")   # Wallet 비밀번호

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
# 3단계: 데이터베이스 연결 관리
# ============================================================================

# 연결 풀: 여러 요청이 DB 연결을 공유하여 성능 향상
db_pool = None


def init_db_pool():
    """DB 연결 풀을 초기화합니다. 최소 2개~최대 10개 연결을 유지합니다."""
    global db_pool
    try:
        if db_pool is None:
            db_pool = oracledb.create_pool(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN,
                config_dir=WALLET_DIR,
                wallet_location=WALLET_DIR,
                wallet_password=WALLET_PASSWORD,
                min=2,       # 최소 연결 수
                max=10,      # 최대 연결 수
                increment=1  # 부족 시 1개씩 추가
            )
        return True, None
    except Exception as e:
        return False, str(e)


def connect_to_database():
    """select_ai SDK용 연결을 생성합니다 (narrate, chat 등에 사용)."""
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


# ============================================================================
# 4단계: SQL 생성/실행 함수들
# ============================================================================

def get_sql_for_question(question, profile_name):
    """자연어 질문을 SQL로 변환합니다 (SELECT AI showsql 사용)."""
    try:
        with db_pool.acquire() as conn:
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

                # 자연어 → SQL 변환 (showsql: SQL만 반환, 실행하지 않음)
                cursor.execute(f"SELECT AI showsql '{safe_question}'")
                result = cursor.fetchone()

                return result[0] if result and result[0] else None
    except Exception as e:
        st.error(f"SQL 생성 실패: {e}")
        return None


def execute_sql(sql):
    """SQL을 실행하고 결과를 pandas DataFrame으로 반환합니다."""
    try:
        with db_pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                if rows and columns:
                    return pd.DataFrame(rows, columns=columns)
                return None
    except Exception as e:
        st.error(f"SQL 실행 실패: {e}")
        return None


def get_last_sql_id():
    """가장 최근 실행된 SELECT AI 쿼리의 SQL ID를 조회합니다 (Feedback용)."""
    try:
        with db_pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT sql_id, sql_text,
                           TO_CHAR(translation_timestamp, 'YYYY-MM-DD HH24:MI:SS') as ts,
                           MAPPED_SQL_FULLTEXT
                    FROM v$mapped_sql
                    WHERE sql_text LIKE '%SELECT AI%'
                    ORDER BY translation_timestamp DESC
                    FETCH FIRST 1 ROW ONLY
                """)
                result = cursor.fetchone()

                if result:
                    # LOB(대형 객체) 타입이면 문자열로 변환
                    nl_query_raw = result[3]
                    if nl_query_raw is not None and hasattr(nl_query_raw, 'read'):
                        nl_query_raw = nl_query_raw.read()
                    nl_query = _extract_nl_query(nl_query_raw)
                    return {
                        'sql_id': result[0],
                        'sql_text': result[1],
                        'timestamp': result[2],
                        'nl_query': nl_query
                    }
                return None
    except Exception as e:
        print(f"⚠️ SQL ID 조회 실패: {e}")
        return None


def get_recent_sql_queries(limit=10):
    """최근 실행된 SELECT AI 쿼리 이력을 조회합니다."""
    try:
        with db_pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT sql_id, sql_text,
                           TO_CHAR(translation_timestamp, 'YYYY-MM-DD HH24:MI:SS') as ts,
                           MAPPED_SQL_FULLTEXT
                    FROM v$mapped_sql
                    WHERE sql_text LIKE '%SELECT AI%'
                    ORDER BY translation_timestamp DESC
                    FETCH FIRST {limit} ROWS ONLY
                """)
                results = cursor.fetchall()

                # LOB 객체를 문자열로 변환 (Streamlit 표시 호환)
                processed = []
                for row in results:
                    row = list(row)
                    if len(row) > 3 and row[3] is not None and hasattr(row[3], 'read'):
                        row[3] = row[3].read()
                    processed.append(tuple(row))
                return processed
    except Exception as e:
        print(f"⚠️ 쿼리 이력 조회 실패: {e}")
        return []


def _extract_nl_query(full_text):
    """SELECT AI 구문에서 자연어 질문 부분만 추출합니다."""
    if not full_text:
        return ""
    if "SELECT AI" in full_text.upper():
        match = re.search(r"SELECT\s+AI.*?'([^']+)'", full_text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    return full_text


# ============================================================================
# 5단계: Feedback & Comment 관리 함수들
# ============================================================================

def submit_feedback(profile_name, sql_id, feedback_type, correct_sql, feedback_content):
    """AI가 생성한 SQL에 대한 피드백을 등록합니다 (DBMS_CLOUD_AI.FEEDBACK)."""
    try:
        with db_pool.acquire() as conn:
            with conn.cursor() as cursor:
                # SQL에서 작은따옴표 이스케이프
                clean_sql = correct_sql.strip()
                if clean_sql.startswith("'") and clean_sql.endswith("'"):
                    clean_sql = clean_sql[1:-1]
                safe_sql = clean_sql.replace("'", "''")
                safe_content = feedback_content.replace("'", "''")

                plsql = f"""
                BEGIN
                    DBMS_CLOUD_AI.FEEDBACK(
                        profile_name     => '{profile_name}',
                        sql_id           => '{sql_id}',
                        feedback_type    => '{feedback_type}',
                        response         => '{safe_sql}',
                        feedback_content => '{safe_content}',
                        operation        => 'add'
                    );
                END;
                """
                cursor.execute(plsql)
                conn.commit()
                return True
    except Exception as e:
        error_msg = str(e)
        if "ORA-20000" in error_msg and "not supported" in error_msg:
            raise Exception("DBMS_CLOUD_AI.FEEDBACK가 이 DB 버전에서 지원되지 않습니다.")
        raise e


def get_profile_list_from_db():
    """DB에 생성된 AI 프로파일 목록을 조회합니다."""
    with db_pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT profile_name, status,
                       TO_CHAR(created, 'YYYY-MM-DD HH24:MI:SS') as created
                FROM user_cloud_ai_profiles
                ORDER BY created DESC
            """)
            return cursor.fetchall()


def get_profile_attributes(profile_name):
    """특정 프로파일의 속성 (model, provider 등)을 조회합니다."""
    with db_pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT attribute_name, attribute_value
                FROM user_cloud_ai_profile_attributes
                WHERE profile_name = :profile_name
                ORDER BY attribute_name
            """, {'profile_name': profile_name})
            return cursor.fetchall()


def get_profile_object_list(profile_name):
    """프로파일에 등록된 테이블/뷰 목록 (object_list)을 조회합니다."""
    with db_pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT attribute_value
                FROM user_cloud_ai_profile_attributes
                WHERE profile_name = :profile_name
                AND attribute_name = 'object_list'
            """, {'profile_name': profile_name})
            result = cursor.fetchone()
            return result[0] if result else None


def check_object_accessible(table_name):
    """테이블/뷰에 접근 가능한지 확인합니다 (DB Link 끊김 감지)."""
    try:
        with db_pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name.upper()} WHERE ROWNUM = 1")
                cursor.fetchone()
                return True
    except Exception as e:
        error_msg = str(e)
        # DB Link 관련 오류이면 접근 불가
        if 'ORA-28509' in error_msg or 'ORA-28511' in error_msg or 'RDS_LINK' in error_msg:
            return False
        return True  # 다른 오류(빈 테이블 등)는 접근 가능으로 처리


def get_table_details(table_name):
    """테이블/뷰의 Comment와 컬럼 정보를 조회합니다."""
    with db_pool.acquire() as conn:
        with conn.cursor() as cursor:
            # 객체 유형 확인 (TABLE or VIEW)
            cursor.execute("""
                SELECT object_type FROM user_objects
                WHERE object_name = :table_name
            """, {'table_name': table_name.upper()})
            obj_type_row = cursor.fetchone()
            obj_type = obj_type_row[0] if obj_type_row else 'TABLE'

            # 테이블 Comment 조회
            cursor.execute("""
                SELECT comments FROM user_tab_comments
                WHERE table_name = :table_name
            """, {'table_name': table_name.upper()})
            comment_row = cursor.fetchone()
            table_comment = comment_row[0] if comment_row else None

            # 컬럼 정보 + Comment 조회
            cursor.execute("""
                SELECT c.column_name, c.data_type, c.data_length,
                       c.nullable, cm.comments
                FROM user_tab_columns c
                LEFT JOIN user_col_comments cm
                    ON c.table_name = cm.table_name AND c.column_name = cm.column_name
                WHERE c.table_name = :table_name
                ORDER BY c.column_id
            """, {'table_name': table_name.upper()})
            columns = cursor.fetchall()

            return table_comment, columns, obj_type


def update_table_comment(table_name, comment):
    """테이블/뷰의 COMMENT를 변경합니다."""
    try:
        with db_pool.acquire() as conn:
            with conn.cursor() as cursor:
                safe_comment = comment.replace("'", "''")
                cursor.execute(f"COMMENT ON TABLE {table_name.upper()} IS '{safe_comment}'")
                conn.commit()
                return True
    except Exception as e:
        raise e


def update_column_comment(table_name, column_name, comment, obj_type='TABLE'):
    """컬럼의 COMMENT를 변경합니다. 소문자 컬럼은 큰따옴표로 감쌉니다."""
    try:
        with db_pool.acquire() as conn:
            with conn.cursor() as cursor:
                # 실제 저장된 컬럼 이름 조회
                cursor.execute("""
                    SELECT column_name FROM user_tab_columns
                    WHERE table_name = :table_name
                    AND UPPER(column_name) = UPPER(:column_name)
                """, {'table_name': table_name.upper(), 'column_name': column_name})
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"컬럼 {column_name}이(가) {table_name}에 없습니다")

                actual_col_name = result[0]
                safe_comment = comment.replace("'", "''")

                # 소문자나 특수문자가 있으면 큰따옴표로 감싸기
                if actual_col_name != actual_col_name.upper() or not actual_col_name.replace('_', '').isalnum():
                    col_identifier = f'"{actual_col_name}"'
                else:
                    col_identifier = actual_col_name

                cursor.execute(
                    f"COMMENT ON COLUMN {table_name.upper()}.{col_identifier} IS '{safe_comment}'"
                )
                conn.commit()
                return True
    except Exception as e:
        raise e


# ============================================================================
# 6단계: AI 응답 모드별 처리 함수
# ============================================================================

def chat_mode(profile, question):
    """Chat 모드: DB 데이터 없이 AI와 자유 대화 (스키마 질문 등)"""
    response = profile.chat(question)
    st.markdown(response)
    return {"content": response}


def narrate_mode(profile, question, profile_name, show_sql):
    """Narrate 모드: DB에서 데이터를 조회하고 자연어로 설명 (가장 권장)"""
    sql = None
    if show_sql:
        with st.spinner("SQL 생성 중..."):
            sql = get_sql_for_question(question, profile_name)
            if sql:
                st.code(sql, language="sql")

    try:
        with st.spinner("결과 조회 및 설명 생성 중..."):
            response = profile.narrate(question)
            st.markdown(response)
        return {"content": response, "sql": sql}
    except Exception as e:
        error_msg = str(e)
        # DB Link 오류 시 친절한 안내
        if 'ORA-28509' in error_msg or 'ORA-28511' in error_msg or 'RDS_LINK' in error_msg:
            st.error("❌ Database Link 오류: 외부 DB에 연결할 수 없습니다")
            st.warning("⚠️ AI 프로파일에 포함된 외부 DB 테이블에 접근할 수 없습니다.")
            st.info("💡 해결 방법: 프로파일의 object_list에서 DB Link 객체를 제거하거나, 외부 DB 연결을 확인하세요.")
            return {"content": "Database Link 오류", "sql": sql}
        else:
            st.error(f"❌ 오류: {e}")
            return {"content": f"오류: {e}", "sql": sql}


def sql_only_mode(question, profile_name):
    """SQL Only 모드: SQL만 생성하고 표시 (실행 버튼으로 직접 실행 가능)"""
    with st.spinner("SQL 생성 중..."):
        sql = get_sql_for_question(question, profile_name)

        if sql:
            st.markdown("**생성된 SQL:**")
            st.code(sql, language="sql")

            # Feedback용 SQL ID 조회
            sql_info = get_last_sql_id()

            col1, col2, col3 = st.columns([2, 2, 2])

            with col1:
                if st.button("🚀 SQL 실행", use_container_width=True):
                    with st.spinner("실행 중..."):
                        df = execute_sql(sql)
                        if df is not None:
                            st.success(f"✅ {len(df)}건 조회됨")
                            st.dataframe(df, use_container_width=True)

            with col2:
                if st.button("📝 피드백", use_container_width=True):
                    st.session_state.show_feedback = True
                    st.session_state.feedback_sql_id = sql_info['sql_id'] if sql_info else 'unknown'
                    st.session_state.feedback_original_sql = sql
                    st.session_state.feedback_question = question
                    st.rerun()

            with col3:
                if sql_info:
                    st.caption(f"✓ SQL ID: {sql_info['sql_id'][:8]}...")
                else:
                    st.caption("⚠️ SQL ID 없음")

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

        sql_info = get_last_sql_id()

        if show_sql:
            st.code(sql, language="sql")

        df = execute_sql(sql)

        if df is not None:
            st.markdown(f"**결과: {len(df)}건**")

            if show_table:
                st.dataframe(df, use_container_width=True)
            else:
                st.write(df)

            # 피드백 버튼
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("📝 피드백", use_container_width=True):
                    st.session_state.show_feedback = True
                    st.session_state.feedback_sql_id = sql_info['sql_id'] if sql_info else 'unknown'
                    st.session_state.feedback_original_sql = sql
                    st.session_state.feedback_question = question
                    st.rerun()
            with col2:
                if sql_info:
                    st.caption(f"✓ 피드백 등록 가능")
                else:
                    st.caption("⚠️ SQL ID를 찾을 수 없습니다")

            return {"content": f"**결과: {len(df)}건**", "sql": sql, "dataframe": df}
        else:
            st.info("조회 결과가 없습니다")
            return {"content": "결과 없음", "sql": sql}


def show_feedback_form(profile_name):
    """피드백 입력 폼을 표시합니다. AI가 잘못 생성한 SQL을 교정할 수 있습니다."""
    st.divider()
    st.subheader("📝 AI 개선을 위한 피드백")

    sql_id = st.session_state.get('feedback_sql_id', '')
    original_sql = st.session_state.get('feedback_original_sql', '')
    question = st.session_state.get('feedback_question', '')

    st.info(f"**원본 질문:** {question}")
    st.code(original_sql, language="sql")

    with st.form(key="feedback_form"):
        feedback_type = st.radio(
            "피드백 유형",
            ["negative", "positive"],
            help="negative: SQL이 틀림, positive: SQL이 맞음"
        )
        correct_sql = st.text_area(
            "수정된 SQL (negative인 경우)",
            value=original_sql, height=150,
            help="올바른 SQL을 입력하세요"
        )
        feedback_content = st.text_input(
            "설명",
            placeholder="왜 이 SQL이 더 나은지 설명하세요",
            help="AI가 학습할 수 있도록 이유를 설명해주세요"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("✅ 제출")
        with col2:
            cancel = st.form_submit_button("❌ 취소")

        if submitted:
            if not feedback_content:
                st.error("설명을 입력해주세요")
            else:
                try:
                    submit_feedback(profile_name, sql_id, feedback_type, correct_sql, feedback_content)
                    st.success("✅ 피드백이 등록되었습니다! AI가 이를 학습합니다.")
                    st.balloons()
                    st.session_state.show_feedback = False
                    import time
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"피드백 제출 실패: {e}")

        if cancel:
            st.session_state.show_feedback = False
            st.rerun()


# ============================================================================
# 7단계: UI 구성 (페이지 설정, 사이드바, 채팅 이력)
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
    st.markdown("*자연어로 데이터베이스에 질문하세요 (이기종 DB 포함)*")


def setup_sidebar():
    """사이드바 설정: DB 연결, 프로파일 선택, 모드 설정, 피드백 탭"""
    with st.sidebar:
        st.title("🤖 Northwind Data Assistant")

        # 사이드바를 설정/피드백 두 탭으로 구분
        tabs = st.tabs(["⚙️ 설정", "📝 피드백"])

        # ─── 설정 탭 ───
        with tabs[0]:
            # --- DB 연결 ---
            st.subheader("🎯 AI 프로파일")

            pool_success, pool_error = init_db_pool()
            if not pool_success:
                st.error(f"❌ 연결 풀 생성 실패: {pool_error}")
                st.stop()

            success, error = connect_to_database()
            if success:
                st.success("✅ 연결됨 (Pool Active)")
            else:
                st.error(f"❌ 연결 실패: {error}")
                st.stop()

            # --- 프로파일 선택 ---
            try:
                profile_list = get_profile_list_from_db()
                # 시스템 프로파일 제외
                available_profiles = [
                    row[0] for row in profile_list
                    if not row[0].startswith(('AGENT$', 'SYS$', 'SYSTEM$'))
                ]

                if not available_profiles:
                    st.error("❌ 프로파일이 없습니다. DBMS_CLOUD_AI.CREATE_PROFILE로 먼저 생성하세요.")
                    st.stop()

                profile = st.selectbox(
                    "프로파일 선택", available_profiles,
                    help="DB에 생성된 AI 프로파일을 선택하세요"
                )

                # 프로파일 상세 정보
                with st.expander("📋 프로파일 상세"):
                    profile_attrs = get_profile_attributes(profile)
                    if profile_attrs:
                        for attr_name, attr_value in profile_attrs:
                            if attr_name == 'object_list':
                                continue  # 아래에서 별도 표시
                            display_value = str(attr_value)[:100]
                            st.text(f"{attr_name}: {display_value}")

                # 프로파일에 등록된 테이블 목록 + Comment 편집
                with st.expander("📊 등록된 테이블 (Comment 편집 가능)"):
                    _render_object_list_editor(profile)

            except Exception as e:
                st.error(f"❌ 프로파일 조회 오류: {e}")
                st.stop()

            # --- 쿼리 모드 ---
            st.subheader("💬 모드")
            mode = st.radio(
                "쿼리 모드",
                ["Chat", "Narrate", "SQL Only", "RunSQL"],
                index=1,
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

            # --- 대화 초기화 ---
            st.divider()
            if st.button("🔄 대화 초기화", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

        # ─── 피드백 탭 ───
        with tabs[1]:
            _render_feedback_tab(profile)

        return profile, mode, show_sql, show_table


def _render_object_list_editor(profile_name):
    """프로파일의 object_list에 등록된 테이블들과 Comment 편집 UI를 표시합니다."""
    object_list = get_profile_object_list(profile_name)
    if not object_list:
        st.info("object_list가 정의되지 않았습니다")
        return

    try:
        objects = json.loads(str(object_list))
    except json.JSONDecodeError as e:
        st.error(f"object_list JSON 파싱 오류: {e}")
        return

    for obj in objects:
        table_name = obj.get('name', '')
        owner = obj.get('owner', '')
        if not table_name:
            continue

        st.markdown(f"### 🗂️ {table_name}")
        if owner:
            st.markdown(f"**Owner:** {owner}")

        # DB Link 접근 가능 여부 확인
        if not check_object_accessible(table_name):
            st.warning(f"⚠️ {table_name}: DB Link 연결 불가")
            st.divider()
            continue

        try:
            table_comment, columns, obj_type = get_table_details(table_name)
            st.caption(f"Type: {obj_type} ✅ 접근 가능")

            # 테이블 Comment 편집
            st.markdown("**테이블 Comment:**")
            with st.form(key=f"form_table_{table_name}"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    new_comment = st.text_input(
                        "Comment", value=table_comment or "",
                        key=f"tc_{table_name}", label_visibility="collapsed"
                    )
                with col2:
                    if st.form_submit_button("💾"):
                        try:
                            update_table_comment(table_name, new_comment)
                            st.success("✅ 저장됨!")
                            import time
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {e}")

            # 컬럼 Comment 편집
            if columns:
                st.markdown("**컬럼:**")
                for col_name, data_type, data_length, nullable, col_comment in columns:
                    null_str = "NULL" if nullable == 'Y' else "NOT NULL"
                    type_str = f"{data_type}({data_length})" if data_length else data_type

                    with st.form(key=f"form_col_{table_name}_{col_name}"):
                        ca, cb, cc = st.columns([2, 2, 1])
                        with ca:
                            st.markdown(f"**{col_name}**")
                            st.caption(f"{type_str} • {null_str}")
                        with cb:
                            new_col_comment = st.text_input(
                                "Comment", value=col_comment or "",
                                key=f"cc_{table_name}_{col_name}",
                                label_visibility="collapsed", placeholder="Comment 추가..."
                            )
                        with cc:
                            if st.form_submit_button("💾"):
                                try:
                                    update_column_comment(table_name, col_name, new_col_comment, obj_type)
                                    st.success("✅")
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ {e}")

        except Exception as e:
            st.warning(f"{table_name} 상세 조회 실패: {e}")

        st.divider()


def _render_feedback_tab(profile_name):
    """사이드바 피드백 탭: 최근 쿼리 목록에서 선택하여 피드백을 등록합니다."""
    st.subheader("📝 피드백 등록")
    st.markdown("최근 SELECT AI 쿼리를 선택하고 피드백을 등록하세요.")

    recent_queries = get_recent_sql_queries(20)

    if not recent_queries:
        st.info("최근 SELECT AI 쿼리가 없습니다. 먼저 질문을 해보세요!")
        return

    # 최근 쿼리 목록 표시
    df_queries = pd.DataFrame(
        recent_queries,
        columns=['SQL ID', 'SQL Text', 'Timestamp', 'Original Query']
    )
    st.markdown("**최근 쿼리:**")
    st.dataframe(df_queries, use_container_width=True, hide_index=True)

    # 쿼리 선택
    st.markdown("**피드백할 쿼리 선택:**")
    query_options = [f"{row[2]} - {row[0][:8]}..." for row in recent_queries]
    selected_idx = st.selectbox(
        "쿼리 선택", range(len(query_options)),
        format_func=lambda i: query_options[i],
        label_visibility="collapsed"
    )

    if selected_idx is not None:
        selected = recent_queries[selected_idx]
        sql_id = selected[0]
        sql_text = selected[1]
        timestamp = selected[2]
        nl_query_raw = selected[3] if len(selected) > 3 else ""
        nl_query = _extract_nl_query(nl_query_raw)

        st.info(f"**원본 질문:** {nl_query}")
        st.code(sql_text, language="sql")
        st.caption(f"SQL ID: {sql_id} | 실행: {timestamp}")

        # 피드백 입력 폼
        with st.form(key="feedback_tab_form"):
            st.markdown("### 피드백 상세")

            feedback_type = st.radio(
                "피드백 유형", ["negative", "positive"],
                help="negative: SQL이 틀림, positive: SQL이 맞음"
            )
            corrected_sql = st.text_area(
                "수정된 SQL", value=sql_text, height=150,
                help="negative: 올바른 SQL로 수정, positive: 그대로 유지"
            )
            feedback_content = st.text_area(
                "설명 (필수)", placeholder="왜 이 SQL이 더 나은지 설명하세요",
                height=100
            )

            if st.form_submit_button("✅ 피드백 제출", use_container_width=True):
                if not feedback_content.strip():
                    st.error("❌ 설명을 입력해주세요")
                else:
                    try:
                        submit_feedback(profile_name, sql_id, feedback_type, corrected_sql, feedback_content)
                        st.success("✅ 피드백이 등록되었습니다!")
                        st.balloons()
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 피드백 제출 실패: {e}")


def display_chat_history(show_sql, show_table):
    """이전 대화 이력을 화면에 표시합니다."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                if show_sql and msg.get("sql"):
                    st.code(msg["sql"], language="sql")
                if show_table and "dataframe" in msg:
                    df = msg.get("dataframe")
                    if df is not None and isinstance(df, pd.DataFrame):
                        st.dataframe(df, use_container_width=True)
                if msg.get("content"):
                    st.markdown(msg["content"])


def process_user_input(prompt, profile_name, mode, show_sql, show_table):
    """사용자 입력을 처리하고 AI 응답을 생성합니다."""
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        profile = get_ai_profile(profile_name)
        if not profile:
            return

        try:
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

            response_data["role"] = "assistant"
            st.session_state.messages.append(response_data)

        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.exception(e)


# ============================================================================
# 8단계: 메인 함수 - 앱 실행 진입점
# ============================================================================

def main():
    """앱 실행: 페이지 설정 → 사이드바 → 대화 이력 → 사용자 입력 처리"""
    setup_page()
    profile_name, mode, show_sql, show_table = setup_sidebar()

    # 채팅 이력 초기화 (첫 실행 시)
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "👋 안녕하세요! 데이터베이스에 대해 자유롭게 질문하세요. (이기종 DB 포함)"
        }]

    display_chat_history(show_sql, show_table)

    if prompt := st.chat_input("질문을 입력하세요 (예: 가장 비싼 제품 5개는?)"):
        process_user_input(prompt, profile_name, mode, show_sql, show_table)

    # 인라인 피드백 폼 (SQL Only/RunSQL에서 피드백 버튼 클릭 시)
    if st.session_state.get('show_feedback', False):
        show_feedback_form(profile_name)

    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "<small>Powered by Oracle Select AI - Sidecar Edition</small>"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
