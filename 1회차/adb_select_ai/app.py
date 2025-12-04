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

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def connect_to_database():
    """Connect to Oracle database"""
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
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            config_dir=WALLET_DIR,
            wallet_location=WALLET_DIR,
            wallet_password=WALLET_PASSWORD
        )
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
        conn.close()
        
        return result[0] if result and result[0] else None
    except Exception as e:
        st.error(f"SQL generation failed: {e}")
        return None


def execute_sql(sql):
    """Execute SQL and return results as DataFrame"""
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            config_dir=WALLET_DIR,
            wallet_location=WALLET_DIR,
            wallet_password=WALLET_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        cursor.close()
        conn.close()
        
        if rows and columns:
            return pd.DataFrame(rows, columns=columns)
        return None
    except Exception as e:
        st.error(f"SQL execution failed: {e}")
        return None


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
    with st.spinner("Getting results and explanation..."):
        response = profile.narrate(question)
        st.markdown(response)
    
    return {"content": response, "sql": sql}


def sql_only_mode(question, profile_name):
    """SQL Only mode: Just generate and show SQL"""
    with st.spinner("Generating SQL..."):
        sql = get_sql_for_question(question, profile_name)
        
        if sql:
            st.markdown("**Generated SQL:**")
            st.code(sql, language="sql")
            
            # Add execute button
            if st.button("🚀 Execute SQL"):
                with st.spinner("Executing..."):
                    df = execute_sql(sql)
                    if df is not None:
                        st.success(f"✅ {len(df)} rows returned")
                        st.dataframe(df, use_container_width=True)
            
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
        
        # Show SQL if requested
        if show_sql:
            st.code(sql, language="sql")
        
        # Execute SQL
        df = execute_sql(sql)
        
        if df is not None:
            st.markdown(f"**Results: {len(df)} rows**")
            
            if show_table:
                st.dataframe(df, use_container_width=True)
            else:
                st.write(df)
            
            return {
                "content": f"**Results: {len(df)} rows**",
                "sql": sql,
                "dataframe": df
            }
        else:
            st.info("No results found")
            return {"content": "No results", "sql": sql}


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
        st.header("⚙️ Settings")
        
        # Connection status
        st.subheader("🔌 Database")
        
        # Ensure connection on every run
        success, error = connect_to_database()
        
        if success:
            st.success("✅ Connected")
        else:
            st.error("❌ Failed to connect")
            if error:
                st.error(error)
            st.stop()
        
        # AI Profile
        st.subheader("🎯 AI Profile")
        
        # Get available profiles from database
        try:
            profile_objects = select_ai.Profile.list()
            if profile_objects:
                # Extract profile names from profile objects
                available_profiles = [p.profile_name for p in profile_objects]
            else:
                st.warning("⚠️ No profiles found in database")
                available_profiles = ["NORTHWIND_AI"]  # fallback
            
            profile = st.selectbox(
                "Select Profile",
                available_profiles,
                help="Select an AI profile configured in your database"
            )
        except Exception as e:
            st.warning(f"⚠️ Could not fetch profiles: {e}")
            profile = st.selectbox(
                "Select Profile",
                ["NORTHWIND_AI"],
                help="Using default profile"
            )
        
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
        
        # Sample Questions
        st.subheader("💡 Examples")
        st.markdown("""
        **Try asking:**
        - 가장 비싼 제품 5개는?
        - 재고가 10개 미만인 제품은?
        - 1997년 총 매출은?
        - 고객별 주문 횟수는?
        """)
        
        # Clear history
        st.divider()
        if st.button("🔄 Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
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
                        st.dataframe(df, use_container_width=True)
                
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
