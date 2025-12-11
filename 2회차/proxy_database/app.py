"""
Northwind Data Assistant - Oracle Select AI Chatbot
Simple, modular, and easy to read
"""

import os
from dotenv import load_dotenv

# ⚠️ 중요: TNS_ADMIN을 oracledb/select_ai 임포트 전에 설정해야 함!

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
print(f"✓ TNS_ADMIN 설정됨: {WALLET_DIR}")
print(f"✓ DB_DSN: {DB_DSN}")

# 이제 다른 모듈들을 import (TNS_ADMIN이 설정된 후)
import streamlit as st
import pandas as pd
import oracledb
import select_ai
import json
import re

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

# Global connection pool
db_pool = None

def init_db_pool():
    """Initialize database connection pool"""
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
                min=2,
                max=10,
                increment=1
            )
            print("✓ 데이터베이스 연결 풀 생성 성공!")
        return True, None
    except Exception as e:
        print(f"❌ 연결 풀 생성 실패: {e}")
        return False, str(e)

def connect_to_database():
    """Connect to Oracle database (for select_ai)"""
    try:
        if not select_ai.is_connected():
            select_ai.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN,
                wallet_location=WALLET_DIR,
                wallet_password=WALLET_PASSWORD
            )
            print("✓ 데이터베이스 연결 성공!")
        return True, None
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False, str(e)


@st.cache_resource
def get_ai_profile(profile_name):
    """Get AI profile object (cached)"""
    try:
        return select_ai.Profile(profile_name=profile_name)
    except Exception as e:
        st.error(f"Failed to load profile: {e}")
        return None


def get_sql_for_question(question, profile_name):
    """Generate SQL from natural language question"""
    try:
        conn = db_pool.acquire()
        cursor = conn.cursor()
        
        # Set AI profile
        cursor.execute(f"""
            BEGIN
                DBMS_CLOUD_AI.SET_PROFILE(profile_name => '{profile_name}');
            END;
        """)
        conn.commit()
        
        # Get SQL
        cursor.execute(f"SELECT AI showsql {question}")
        result = cursor.fetchone()
        
        cursor.close()
        db_pool.release(conn)
        
        return result[0] if result and result[0] else None
    except Exception as e:
        st.error(f"SQL generation failed: {e}")
        return None


def execute_sql(sql):
    """Execute SQL and return results as DataFrame"""
    try:
        conn = db_pool.acquire()
        cursor = conn.cursor()
        cursor.execute(sql)
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        cursor.close()
        db_pool.release(conn)
        
        if rows and columns:
            return pd.DataFrame(rows, columns=columns)
        return None
    except Exception as e:
        st.error(f"SQL execution failed: {e}")
        return None

def get_last_sql_id():
    """Get the SQL ID of the last executed SELECT AI query"""
    try:
        conn = db_pool.acquire()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sql_id, sql_text, TO_CHAR(translation_timestamp, 'YYYY-MM-DD HH24:MI:SS') as ts, MAPPED_SQL_FULLTEXT
            FROM v$mapped_sql
            WHERE sql_text LIKE '%SELECT AI%'
            ORDER BY translation_timestamp DESC
            FETCH FIRST 1 ROW ONLY
        """)
        
        result = cursor.fetchone()
        cursor.close()
        db_pool.release(conn)
        
        if result:
            # Convert LOB to string if needed
            nl_query_raw = result[3]
            if nl_query_raw is not None and hasattr(nl_query_raw, 'read'):
                nl_query_raw = nl_query_raw.read()
            # Extract just the NL query part from SELECT AI statement
            nl_query = extract_nl_query_from_select_ai(nl_query_raw)
            return {'sql_id': result[0], 'sql_text': result[1], 'timestamp': result[2], 'nl_query': nl_query}
        return None
    except Exception as e:
        print(f"⚠️ Could not get SQL ID: {e}")
        return None

def get_recent_sql_queries(limit=10):
    """Get recent SELECT AI queries from v$mapped_sql"""
    try:
        conn = db_pool.acquire()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT sql_id, sql_text, TO_CHAR(translation_timestamp, 'YYYY-MM-DD HH24:MI:SS') as ts, MAPPED_SQL_FULLTEXT
            FROM v$mapped_sql
            WHERE sql_text LIKE '%SELECT AI%'
            ORDER BY translation_timestamp DESC
            FETCH FIRST {limit} ROWS ONLY
        """)
        
        results = cursor.fetchall()
        cursor.close()
        db_pool.release(conn)
        
        # Convert LOB objects to strings for Streamlit compatibility
        processed_results = []
        for row in results:
            processed_row = list(row)
            # Convert MAPPED_SQL_FULLTEXT (4th column) LOB to string
            if len(processed_row) > 3 and processed_row[3] is not None:
                if hasattr(processed_row[3], 'read'):
                    processed_row[3] = processed_row[3].read()
            processed_results.append(tuple(processed_row))
        
        return processed_results
    except Exception as e:
        print(f"⚠️ Could not get SQL queries: {e}")
        return []

def extract_nl_query_from_select_ai(full_text):
    """Extract the natural language query from SELECT AI statement"""
    if not full_text:
        return ""
    
    # If it's already a SELECT AI statement, extract the NL query
    if "SELECT AI" in full_text.upper():
        # Pattern: SELECT AI ... 'natural language query' ...
        # Match content between first set of quotes after SELECT AI
        match = re.search(r"SELECT\s+AI.*?'([^']+)'", full_text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    
    # Otherwise return as-is (user may have edited it)
    return full_text

def submit_feedback(profile_name, sql_id, feedback_type, correct_sql, feedback_content):
    """Submit feedback for Select AI query using DBMS_CLOUD_AI.FEEDBACK"""
    conn = db_pool.acquire()
    cursor = conn.cursor()
    
    try:
        # Clean and escape the SQL - strip any surrounding quotes first
        clean_sql = correct_sql.strip()
        if clean_sql.startswith("'") and clean_sql.endswith("'"):
            clean_sql = clean_sql[1:-1]
        
        # Escape single quotes for PL/SQL
        safe_sql = clean_sql.replace("'", "''")
        safe_content = feedback_content.replace("'", "''")
        
        plsql = f"""
        BEGIN
            DBMS_OUTPUT.ENABLE(buffer_size => NULL);
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
        
        print(f"Executing feedback: {plsql}")
        cursor.execute(plsql)
        conn.commit()
        
        print(f"✓ Feedback submitted for SQL ID: {sql_id}")
        
        cursor.close()
        db_pool.release(conn)
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error submitting feedback: {error_msg}")
        conn.rollback()
        cursor.close()
        db_pool.release(conn)
        
        # Check if it's the "not supported" error
        if "ORA-20000" in error_msg and "not supported" in error_msg:
            raise Exception("DBMS_CLOUD_AI.FEEDBACK is not supported in this database version. "
                          "Please check your Oracle database version and ensure Select AI feedback is enabled.")
        raise e

@st.cache_data(ttl=300)
def get_prompts_from_db():
    """Fetch real prompts from database"""
    try:
        conn = db_pool.acquire()
        cursor = conn.cursor()
        
        # Try to fetch from prompts table if it exists
        cursor.execute("""
            SELECT prompt_text 
            FROM user_prompts 
            WHERE is_active = 1 
            ORDER BY display_order
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        db_pool.release(conn)
        
        if rows:
            return [row[0] for row in rows]
        else:
            # Fallback to default prompts
            return [
                "가장 비싼 제품 5개는?",
                "재고가 10개 미만인 제품은?",
                "1997년 총 매출은?",
                "고객별 주문 횟수는?"
            ]
    except Exception as e:
        print(f"⚠️ Could not fetch prompts from DB: {e}")
        # Return default prompts as fallback
        return [
            "가장 비싼 제품 5개는?",
            "재고가 10개 미만인 제품은?",
            "1997년 총 매출은?",
            "고객별 주문 횟수는?"
        ]

def get_profile_list_from_db():
    """Fetch AI profile list from database"""
    conn = db_pool.acquire()
    cursor = conn.cursor()
    
    # Convert timestamp to string to avoid thin mode timezone issues
    cursor.execute("""
        SELECT profile_name, status, TO_CHAR(created, 'YYYY-MM-DD HH24:MI:SS') as created
        FROM user_cloud_ai_profiles
        ORDER BY created DESC
    """)
    
    rows = cursor.fetchall()
    cursor.close()
    db_pool.release(conn)
    
    return rows

def get_profile_attributes(profile_name):
    """Fetch profile attributes from database"""
    conn = db_pool.acquire()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT attribute_name, attribute_value
        FROM user_cloud_ai_profile_attributes
        WHERE profile_name = :profile_name
        ORDER BY attribute_name
    """, {'profile_name': profile_name})
    
    rows = cursor.fetchall()
    cursor.close()
    db_pool.release(conn)
    
    return rows

def get_profile_object_list(profile_name):
    """Get object_list from profile attributes"""
    conn = db_pool.acquire()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT attribute_value
        FROM user_cloud_ai_profile_attributes
        WHERE profile_name = :profile_name
        AND attribute_name = 'object_list'
    """, {'profile_name': profile_name})
    
    result = cursor.fetchone()
    cursor.close()
    db_pool.release(conn)
    
    return result[0] if result else None

def check_object_accessible(table_name):
    """Check if object is accessible (not using broken DB link)"""
    try:
        conn = db_pool.acquire()
        cursor = conn.cursor()
        
        # Try a simple query to see if we can access it
        cursor.execute(f"SELECT * FROM {table_name.upper()} WHERE ROWNUM = 1")
        cursor.fetchone()
        
        cursor.close()
        db_pool.release(conn)
        return True
    except Exception as e:
        error_msg = str(e)
        if 'ORA-28509' in error_msg or 'ORA-28511' in error_msg or 'RDS_LINK' in error_msg:
            # Database link issue
            return False
        # Other errors might be ok (empty table, etc)
        return True

def get_table_details(table_name):
    """Get table comment and column details"""
    conn = db_pool.acquire()
    cursor = conn.cursor()
    
    # Check if it's a table or view
    cursor.execute("""
        SELECT object_type
        FROM user_objects
        WHERE object_name = :table_name
    """, {'table_name': table_name.upper()})
    
    obj_type_row = cursor.fetchone()
    obj_type = obj_type_row[0] if obj_type_row else 'TABLE'
    
    # Get table/view comment
    cursor.execute("""
        SELECT comments
        FROM user_tab_comments
        WHERE table_name = :table_name
    """, {'table_name': table_name.upper()})
    
    table_comment_row = cursor.fetchone()
    table_comment = table_comment_row[0] if table_comment_row else None
    
    # Get columns with comments
    cursor.execute("""
        SELECT 
            c.column_name,
            c.data_type,
            c.data_length,
            c.nullable,
            cm.comments
        FROM user_tab_columns c
        LEFT JOIN user_col_comments cm 
            ON c.table_name = cm.table_name 
            AND c.column_name = cm.column_name
        WHERE c.table_name = :table_name
        ORDER BY c.column_id
    """, {'table_name': table_name.upper()})
    
    columns = cursor.fetchall()
    cursor.close()
    db_pool.release(conn)
    
    return table_comment, columns, obj_type

def update_table_comment(table_name, comment):
    """Update table comment"""
    conn = db_pool.acquire()
    cursor = conn.cursor()
    
    try:
        # Escape single quotes in comment
        safe_comment = comment.replace("'", "''")
        
        sql = f"COMMENT ON TABLE {table_name.upper()} IS '{safe_comment}'"
        print(f"Executing: {sql}")
        
        cursor.execute(sql)
        conn.commit()
        
        print(f"✓ Table comment updated for {table_name}")
        
        cursor.close()
        db_pool.release(conn)
        return True
    except Exception as e:
        print(f"❌ Error updating table comment: {e}")
        conn.rollback()
        cursor.close()
        db_pool.release(conn)
        raise e

def update_column_comment(table_name, column_name, comment, obj_type='TABLE'):
    """Update column comment"""
    conn = db_pool.acquire()
    cursor = conn.cursor()
    
    try:
        # Get the actual column name as stored in the database
        cursor.execute("""
            SELECT column_name
            FROM user_tab_columns
            WHERE table_name = :table_name
            AND UPPER(column_name) = UPPER(:column_name)
        """, {'table_name': table_name.upper(), 'column_name': column_name})
        
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Column {column_name} not found in {table_name}")
        
        actual_col_name = result[0]
        
        # Escape single quotes in comment
        safe_comment = comment.replace("'", "''")
        
        # Check if column name needs quotes (has lowercase or special chars)
        if actual_col_name != actual_col_name.upper() or not actual_col_name.isalnum():
            col_identifier = f'"{actual_col_name}"'
        else:
            col_identifier = actual_col_name
        
        sql = f"COMMENT ON COLUMN {table_name.upper()}.{col_identifier} IS '{safe_comment}'"
        print(f"Executing: {sql} (Object Type: {obj_type})")
        
        cursor.execute(sql)
        conn.commit()
        
        print(f"✓ Column comment updated for {table_name}.{actual_col_name}")
        
        cursor.close()
        db_pool.release(conn)
        return True
    except Exception as e:
        print(f"❌ Error updating column comment: {e}")
        conn.rollback()
        cursor.close()
        db_pool.release(conn)
        raise e


# ============================================================================
# AI RESPONSE FUNCTIONS
# ============================================================================

def chat_mode(profile, question):
    """Chat mode: General conversation"""
    response = profile.chat(question)
    st.markdown(response)
    return {"content": response}


def narrate_mode(profile, question, profile_name, show_sql):
    """Narrate mode: Results + explanation with optional SQL display"""
    # Show SQL if requested
    sql = None
    if show_sql:
        with st.spinner("Generating SQL..."):
            sql = get_sql_for_question(question, profile_name)
            if sql:
                st.code(sql, language="sql")
    
    # Get narration
    try:
        with st.spinner("Getting results and explanation..."):
            response = profile.narrate(question)
            st.markdown(response)
        
        return {"content": response, "sql": sql}
    except Exception as e:
        error_msg = str(e)
        if 'ORA-28509' in error_msg or 'ORA-28511' in error_msg or 'RDS_LINK' in error_msg:
            st.error("❌ Database Link Error: Cannot connect to external database")
            st.warning("⚠️ Your AI profile includes objects that reference an unavailable external database (RDS_LINK).")
            st.info("💡 **Solution:** Remove objects with database links from the profile's object_list, or fix the RDS_LINK connection.")
            with st.expander("🔍 View Full Error"):
                st.exception(e)
            return {"content": "Database link error - see details above", "sql": sql}
        else:
            st.error(f"❌ Error: {e}")
            st.exception(e)
            return {"content": f"Error: {e}", "sql": sql}


def sql_only_mode(question, profile_name):
    """SQL Only mode: Just generate and show SQL"""
    with st.spinner("Generating SQL..."):
        sql = get_sql_for_question(question, profile_name)
        
        if sql:
            st.markdown("**Generated SQL:**")
            st.code(sql, language="sql")
            
            # Get SQL ID for feedback
            sql_info = get_last_sql_id()
            
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                # Add execute button
                if st.button("🚀 Execute SQL", width='stretch'):
                    with st.spinner("Executing..."):
                        df = execute_sql(sql)
                        if df is not None:
                            st.success(f"✅ {len(df)} rows returned")
                            st.dataframe(df, width='stretch')
            
            with col2:
                # Add feedback button (always show, even if sql_id not found)
                if st.button("📝 Give Feedback", width='stretch'):
                    st.session_state.show_feedback = True
                    st.session_state.feedback_sql_id = sql_info['sql_id'] if sql_info else 'unknown'
                    st.session_state.feedback_original_sql = sql
                    st.session_state.feedback_question = question
                    st.rerun()
            
            with col3:
                if sql_info:
                    st.caption(f"✓ SQL ID: {sql_info['sql_id'][:8]}...")
                else:
                    st.caption("⚠️ SQL ID not found")
            
            return {"content": "**Generated SQL:**", "sql": sql}
        else:
            st.error("Failed to generate SQL")
            return {"content": "Failed to generate SQL"}


def runsql_mode(question, profile_name, show_sql, show_table):
    """RunSQL mode: Execute query and show results"""
    with st.spinner("Generating and executing SQL..."):
        # Get SQL
        sql = get_sql_for_question(question, profile_name)
        
        if not sql:
            st.error("Failed to generate SQL")
            return {"content": "Failed to generate SQL"}
        
        # Get SQL ID for feedback
        sql_info = get_last_sql_id()
        
        # Show SQL if requested
        if show_sql:
            st.code(sql, language="sql")
        
        # Execute SQL
        df = execute_sql(sql)
        
        if df is not None:
            st.markdown(f"**Results: {len(df)} rows**")
            
            if show_table:
                st.dataframe(df, width='stretch')
            else:
                st.write(df)
            
            # Always show feedback button after results
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("📝 Give Feedback", width='stretch'):
                    st.session_state.show_feedback = True
                    st.session_state.feedback_sql_id = sql_info['sql_id'] if sql_info else 'unknown'
                    st.session_state.feedback_original_sql = sql
                    st.session_state.feedback_question = question
                    st.rerun()
            with col2:
                if sql_info:
                    st.caption(f"✓ SQL ID available for feedback")
                else:
                    st.caption("⚠️ SQL ID not found - feedback may not work properly")
            
            return {
                "content": f"**Results: {len(df)} rows**",
                "sql": sql,
                "dataframe": df
            }
        else:
            st.info("No results found")
            return {"content": "No results", "sql": sql}


def show_feedback_form(profile_name):
    """Display feedback form for SQL query"""
    st.divider()
    st.subheader("📝 Provide Feedback to Improve AI")
    
    sql_id = st.session_state.get('feedback_sql_id', '')
    original_sql = st.session_state.get('feedback_original_sql', '')
    question = st.session_state.get('feedback_question', '')
    
    st.info(f"**Original Question:** {question}")
    st.code(original_sql, language="sql")
    
    with st.form(key="feedback_form"):
        feedback_type = st.radio(
            "Feedback Type",
            ["negative", "positive"],
            help="Negative: SQL is wrong. Positive: SQL is correct."
        )
        
        correct_sql = st.text_area(
            "Correct SQL (for negative feedback)",
            value=original_sql,
            height=150,
            help="Provide the correct SQL query"
        )
        
        feedback_content = st.text_input(
            "Explanation",
            placeholder="Why is this better? (e.g., 'This query is simpler and more efficient')",
            help="Explain why this SQL is better or correct"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("✅ Submit Feedback")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if submitted:
            if not feedback_content:
                st.error("Please provide an explanation")
            else:
                try:
                    submit_feedback(profile_name, sql_id, feedback_type, correct_sql, feedback_content)
                    st.success("✅ Feedback submitted successfully! AI will learn from this.")
                    st.balloons()
                    # Clear feedback state
                    st.session_state.show_feedback = False
                    import time
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to submit feedback: {e}")
        
        if cancel:
            st.session_state.show_feedback = False
            st.rerun()

# ============================================================================
# UI COMPONENTS
# ============================================================================

def setup_page():
    """Configure page settings"""
    st.set_page_config(
        page_title="Northwind Data Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Northwind Data Assistant")
    st.markdown("*Ask questions about your data in natural language*")


def setup_sidebar():
    """Setup sidebar with settings and options"""
    with st.sidebar:
        st.title("🤖 Northwind Data Assistant")
        
        # Create tabs
        tabs = st.tabs(["⚙️ Settings", "📝 Feedback"])
        
        # Settings Tab
        with tabs[0]:
            # Profile Selection
            st.subheader("🎯 AI Profile")
            
            # Initialize connection pool
            pool_success, pool_error = init_db_pool()
            if not pool_success:
                st.error("❌ Failed to initialize connection pool")
                if pool_error:
                    st.error(pool_error)
                st.stop()
            
            # Ensure select_ai connection
            success, error = connect_to_database()
            
            if success and pool_success:
                st.success("✅ Connected (Pool Active)")
            else:
                st.error("❌ Failed to connect")
                if error:
                    st.error(error)
                st.stop()
            
            # Get available profiles from database table
            try:
                profile_list = get_profile_list_from_db()
                
                # Filter out system profiles (AGENT$*, SYS$*, etc.) and only get user profiles
                available_profiles = [
                    row[0] for row in profile_list 
                    if not row[0].startswith(('AGENT$', 'SYS$', 'SYSTEM$'))
                ]
                
                if not available_profiles:
                    st.error("❌ No user profiles found in database")
                    st.info("Please create an AI profile first using DBMS_CLOUD_AI.CREATE_PROFILE")
                    st.stop()
                
                profile = st.selectbox(
                    "Select Profile",
                    available_profiles,
                    help="Select an AI profile configured in your database"
                )
                
                # Show profile details in expander
                with st.expander("📋 Profile Details"):
                    profile_attrs = get_profile_attributes(profile)
                    if profile_attrs:
                        for attr_name, attr_value in profile_attrs:
                            # Truncate long values for non-object_list attributes
                            if attr_name == 'object_list':
                                continue  # Handle separately below
                            display_value = str(attr_value)
                            if len(display_value) > 100:
                                display_value = display_value[:100] + "..."
                            st.text(f"{attr_name}: {display_value}")
                    else:
                        st.info("No attributes found")
                
                # Show object list (tables) in expander
                with st.expander("📊 Profile Object List (Tables)"):
                    object_list = get_profile_object_list(profile)
                    if object_list:
                        try:
                            # Parse object_list as JSON
                            objects = json.loads(str(object_list))
                            
                            for obj in objects:
                                # Extract table name from the JSON object
                                table_name = obj.get('name', '')
                                owner = obj.get('owner', '')
                                
                                if table_name:
                                    st.markdown(f"### 🗂️ {table_name}")
                                    if owner:
                                        st.markdown(f"**Owner:** {owner}")
                                    
                                    try:
                                        # Check if object is accessible
                                        is_accessible = check_object_accessible(table_name)
                                        
                                        if not is_accessible:
                                            st.warning(f"⚠️ {table_name} uses an unavailable database link (RDS_LINK)")
                                            st.info("💡 Remove this object from the profile's object_list to avoid errors")
                                            st.divider()
                                            continue
                                        
                                        table_comment, columns, obj_type = get_table_details(table_name)
                                        
                                        # Show object type
                                        st.caption(f"Type: {obj_type} ✅ Accessible")
                                        
                                        # Editable table comment
                                        st.markdown("**Table Comment:**")
                                        with st.form(key=f"form_table_{table_name}"):
                                            col1, col2 = st.columns([4, 1])
                                            with col1:
                                                new_table_comment = st.text_input(
                                                    "Comment",
                                                    value=table_comment if table_comment else "",
                                                    key=f"table_comment_{table_name}",
                                                    label_visibility="collapsed"
                                                )
                                            with col2:
                                                submitted = st.form_submit_button("💾 Save")
                                            
                                            if submitted:
                                                print(f"🔵 Save button clicked for table: {table_name}")
                                                print(f"🔵 New comment: {new_table_comment}")
                                                try:
                                                    result = update_table_comment(table_name, new_table_comment)
                                                    if result:
                                                        st.success("✅ Table comment updated!")
                                                        st.balloons()
                                                        import time
                                                        time.sleep(1)
                                                        st.rerun()
                                                except Exception as e:
                                                    st.error(f"Failed to update: {e}")
                                                    st.exception(e)
                                        
                                        # Show columns with editable comments
                                        if columns:
                                            st.markdown("**Columns:**")
                                            
                                            for idx, (col_name, data_type, data_length, nullable, col_comment) in enumerate(columns):
                                                null_str = "NULL" if nullable == 'Y' else "NOT NULL"
                                                type_str = f"{data_type}({data_length})" if data_length else data_type
                                                
                                                with st.form(key=f"form_col_{table_name}_{col_name}"):
                                                    col_a, col_b, col_c = st.columns([2, 2, 1])
                                                    
                                                    with col_a:
                                                        st.markdown(f"**{col_name}**")
                                                        st.caption(f"{type_str} • {null_str}")
                                                    
                                                    with col_b:
                                                        new_col_comment = st.text_input(
                                                            "Column comment",
                                                            value=col_comment if col_comment else "",
                                                            key=f"col_comment_{table_name}_{col_name}",
                                                            label_visibility="collapsed",
                                                            placeholder="Add comment..."
                                                        )
                                                    
                                                    with col_c:
                                                        submitted = st.form_submit_button("💾")
                                                    
                                                    if submitted:
                                                        print(f"🔵 Save column button clicked: {table_name}.{col_name}")
                                                        print(f"🔵 New comment: {new_col_comment}")
                                                        print(f"🔵 Object type: {obj_type}")
                                                        try:
                                                            result = update_column_comment(table_name, col_name, new_col_comment, obj_type)
                                                            if result:
                                                                st.success("✅ Updated!")
                                                                st.balloons()
                                                                import time
                                                                time.sleep(1)
                                                                st.rerun()
                                                        except Exception as e:
                                                            st.error(f"❌ {str(e)}")
                                        else:
                                            st.info("No columns found")
                                            
                                    except Exception as e:
                                        st.warning(f"Could not fetch details for {table_name}: {e}")
                                    
                                    st.divider()
                                    
                        except json.JSONDecodeError as e:
                            st.error(f"Could not parse object_list as JSON: {e}")
                            st.code(object_list)
                    else:
                        st.info("No object_list defined for this profile")
                        
            except Exception as e:
                st.error(f"❌ Error querying profiles table: {e}")
                st.exception(e)
                st.stop()
            
            # Query Mode
            st.subheader("💬 Mode")
            mode = st.radio(
                "Query Mode",
                ["Chat", "Narrate", "SQL Only", "RunSQL"],
                index=1,
                help="Narrate mode is recommended for most queries"
            )
            
            # Display Options
            st.subheader("🔧 Display")
            show_sql = st.checkbox("Show SQL", value=True)
            show_table = st.checkbox("Show as Table", value=True)
            
            # Sample Questions from DB
            st.subheader("💡 Examples")
            prompts = get_prompts_from_db()
            st.markdown("**Try asking:**")
            for prompt in prompts:
                st.markdown(f"- {prompt}")
            
            # Clear history
            st.divider()
            if st.button("🔄 Clear History", width='stretch'):
                st.session_state.messages = []
                st.rerun()

        # Feedback Tab
        with tabs[1]:
            st.subheader("📝 Provide Feedback")
            st.markdown("Select a recent SQL query and provide feedback to improve AI.")
            
            # Get recent queries
            recent_queries = get_recent_sql_queries(20)
            
            if not recent_queries:
                st.info("No recent SELECT AI queries found. Run some queries first!")
            else:
                # Create a DataFrame for display
                df_queries = pd.DataFrame(
                    recent_queries,
                    columns=['SQL ID', 'SQL Text', 'Timestamp', 'Original Query']
                )
                
                # Show in a table
                st.markdown("**Recent SELECT AI Queries:**")
                st.dataframe(
                    df_queries,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "SQL Text": st.column_config.TextColumn(
                            "SQL Text",
                            width="large",
                        ),
                        "Original Query": st.column_config.TextColumn(
                            "Original Query",
                            width="medium",
                        )
                    }
                )
                
                # Select query using selectbox
                st.markdown("**Select Query for Feedback:**")
                query_options = [f"{row[2]} - {row[0][:8]}..." for row in recent_queries]
                selected_idx = st.selectbox(
                    "Choose a query",
                    range(len(query_options)),
                    format_func=lambda i: query_options[i],
                    label_visibility="collapsed"
                )
                
                if selected_idx is not None:
                    selected_query = recent_queries[selected_idx]
                    sql_id = selected_query[0]
                    sql_text = selected_query[1]
                    timestamp = selected_query[2]
                    nl_query_raw = selected_query[3] if len(selected_query) > 3 else "N/A"
                    
                    # Extract just the NL query part from SELECT AI statement
                    nl_query = extract_nl_query_from_select_ai(nl_query_raw)
                    
                    # Show original NL query
                    st.info(f"**Original Question:** {nl_query}")
                    
                    st.code(sql_text, language="sql")
                    st.caption(f"SQL ID: {sql_id} | Executed: {timestamp}")
                    
                    # Feedback form
                    with st.form(key="feedback_tab_form"):
                        st.markdown("### Feedback Details")
                        
                        feedback_type = st.radio(
                            "Feedback Type",
                            ["negative", "positive"],
                            help="Negative: SQL is incorrect. Positive: SQL is correct."
                        )
                        
                        corrected_sql = st.text_area(
                            "Corrected SQL",
                            value=sql_text,
                            height=150,
                            help="For NEGATIVE: Edit to show the correct SQL. For POSITIVE: Keep as-is to confirm this SQL is correct."
                        )
                        
                        feedback_content = st.text_area(
                            "Explanation (Required)",
                            placeholder="Why is this better? What was wrong? How does this improve the query?",
                            help="Provide detailed explanation for the AI to learn",
                            height=100
                        )
                        
                        submitted = st.form_submit_button("✅ Submit Feedback", width='stretch')
                        
                        if submitted:
                            if not feedback_content.strip():
                                st.error("❌ Please provide an explanation")
                            else:
                                try:
                                    submit_feedback(profile, sql_id, feedback_type, corrected_sql, feedback_content)
                                    st.success("✅ Feedback submitted successfully! AI will learn from this.")
                                    st.balloons()
                                    import time
                                    time.sleep(1.5)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Failed to submit feedback: {e}")
                                    st.exception(e)
        
        return profile, mode, show_sql, show_table


def display_chat_history(show_sql, show_table):
    """Display previous chat messages"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                # Display SQL if available
                if show_sql and "sql" in msg and msg.get("sql"):
                    st.code(msg["sql"], language="sql")
                
                # Display DataFrame if available
                if show_table and "dataframe" in msg:
                    df = msg.get("dataframe")
                    if df is not None and isinstance(df, pd.DataFrame):
                        st.dataframe(df, width='stretch')
                
                # Display content
                if "content" in msg and msg.get("content"):
                    st.markdown(msg["content"])


def process_user_input(prompt, profile_name, mode, show_sql, show_table):
    """Process user question and generate response"""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response
    with st.chat_message("assistant"):
        profile = get_ai_profile(profile_name)
        if not profile:
            return
        
        try:
            # Route to appropriate mode
            if mode == "Chat":
                response_data = chat_mode(profile, prompt)
            elif mode == "Narrate":
                response_data = narrate_mode(profile, prompt, profile_name, show_sql)
            elif mode == "SQL Only":
                response_data = sql_only_mode(prompt, profile_name)
            elif mode == "RunSQL":
                response_data = runsql_mode(prompt, profile_name, show_sql, show_table)
            else:
                response_data = {"content": "Unknown mode"}
            
            # Save to history
            response_data["role"] = "assistant"
            st.session_state.messages.append(response_data)
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.exception(e)


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application logic"""
    # Setup
    setup_page()
    profile_name, mode, show_sql, show_table = setup_sidebar()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hello! Ask me anything about the Northwind database."
        })
    
    # Display chat history
    display_chat_history(show_sql, show_table)
    
    # Handle user input
    if prompt := st.chat_input("Ask a question (e.g., 가장 비싼 제품 5개는?)"):
        process_user_input(prompt, profile_name, mode, show_sql, show_table)
    
    # Show feedback form if requested (persistent across reruns)
    if st.session_state.get('show_feedback', False):
        show_feedback_form(profile_name)
    
    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "<small>Powered by Oracle Select AI</small>"
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
