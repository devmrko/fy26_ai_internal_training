"""
Northwind AI Agent Assistant - Oracle Select AI Agent Interface
Hierarchical team, task, and tool selection with chat interface
"""

import os
from dotenv import load_dotenv

# ⚠️ 중요: TNS_ADMIN을 oracledb 임포트 전에 설정해야 함!

# .env 파일 로드
load_dotenv()

# 지갑 경로 설정
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

# TNS_ADMIN 설정
os.environ['TNS_ADMIN'] = WALLET_DIR
print(f"✓ TNS_ADMIN 설정됨: {WALLET_DIR}")
print(f"✓ DB_DSN: {DB_DSN}")

# 이제 다른 모듈들을 import
import streamlit as st
import pandas as pd
import oracledb
import json

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def connect_to_database():
    """Connect to Oracle database"""
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            config_dir=WALLET_DIR,
            wallet_location=WALLET_DIR,
            wallet_password=WALLET_PASSWORD
        )
        print("✓ 데이터베이스 연결 성공!")
        return conn, None
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return None, str(e)


@st.cache_data(ttl=60)
def get_teams():
    """Get all AI Agent teams from database"""
    try:
        conn, error = connect_to_database()
        if error:
            return None
        
        cursor = conn.cursor()
        query = """
            SELECT 
                t.agent_team_name,
                t.status,
                DBMS_LOB.SUBSTR(a.attribute_value, 4000, 1) AS team_config
            FROM user_ai_agent_teams t
            LEFT JOIN user_ai_agent_team_attributes a
                ON t.agent_team_name = a.agent_team_name
            WHERE a.attribute_name = 'agents'
            ORDER BY t.agent_team_name
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        teams = []
        for row in rows:
            # The attribute_value for 'agents' is already the agents array
            # Convert CLOB to string if necessary
            agents_json = row[2]
            if hasattr(agents_json, 'read'):
                agents_json = agents_json.read()
            agents_list = json.loads(agents_json) if agents_json else []
            team_data = {
                'name': str(row[0]),
                'status': str(row[1]),
                'agents': agents_list  # Store agents directly
            }
            teams.append(team_data)
        
        cursor.close()
        conn.close()
        return teams
    except Exception as e:
        st.error(f"Failed to fetch teams: {e}")
        return None


@st.cache_data(ttl=60)
def get_tasks_for_agent(agent_name):
    """Get tasks assigned to a specific agent"""
    try:
        conn, error = connect_to_database()
        if error:
            return None
        
        cursor = conn.cursor()
        query = """
            SELECT 
                t.task_name,
                t.status,
                a.attribute_name,
                DBMS_LOB.SUBSTR(a.attribute_value, 4000, 1) AS attribute_value
            FROM user_ai_agent_tasks t
            LEFT JOIN user_ai_agent_task_attributes a
                ON t.task_name = a.task_name
            ORDER BY t.task_name, a.attribute_name
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Group by task_name
        tasks_dict = {}
        for row in rows:
            task_name = str(row[0])
            if task_name not in tasks_dict:
                tasks_dict[task_name] = {
                    'name': task_name,
                    'status': str(row[1]),
                    'attributes': {}
                }
            if row[2]:  # attribute_name
                # Convert CLOB to string if necessary
                attr_value = row[3]
                if hasattr(attr_value, 'read'):
                    attr_value = attr_value.read()
                tasks_dict[task_name]['attributes'][str(row[2])] = str(attr_value) if attr_value else ''
        
        cursor.close()
        conn.close()
        return list(tasks_dict.values())
    except Exception as e:
        st.error(f"Failed to fetch tasks: {e}")
        return None


@st.cache_data(ttl=60)
def get_tools_for_task(task_name):
    """Get tools assigned to a specific task"""
    try:
        conn, error = connect_to_database()
        if error:
            return None
        
        cursor = conn.cursor()
        query = """
            SELECT 
                t.tool_name,
                t.description,
                t.status,
                a.attribute_name,
                DBMS_LOB.SUBSTR(a.attribute_value, 4000, 1) AS attribute_value
            FROM user_ai_agent_tools t
            LEFT JOIN user_ai_agent_tool_attributes a
                ON t.tool_name = a.tool_name
            ORDER BY t.tool_name, a.attribute_name
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Group by tool_name
        tools_dict = {}
        for row in rows:
            tool_name = str(row[0])
            if tool_name not in tools_dict:
                # Convert description CLOB to string if necessary
                description = row[1]
                if hasattr(description, 'read'):
                    description = description.read()
                tools_dict[tool_name] = {
                    'name': tool_name,
                    'description': str(description) if description else '',
                    'status': str(row[2]),
                    'attributes': {}
                }
            if row[3]:  # attribute_name
                # Convert CLOB to string if necessary
                attr_value = row[4]
                if hasattr(attr_value, 'read'):
                    attr_value = attr_value.read()
                tools_dict[tool_name]['attributes'][str(row[3])] = str(attr_value) if attr_value else ''
        
        cursor.close()
        conn.close()
        return list(tools_dict.values())
    except Exception as e:
        st.error(f"Failed to fetch tools: {e}")
        return None


@st.cache_data(ttl=30)
def get_conversation_history():
    """Get all conversation history from database"""
    try:
        conn, error = connect_to_database()
        if error:
            return None
        
        cursor = conn.cursor()
        query = """
            SELECT 
                c.conversation_id,
                c.conversation_title,
                CAST(c.created AS DATE) AS created,
                COUNT(p.conversation_prompt_id) AS message_count
            FROM user_cloud_ai_conversations c
            LEFT JOIN user_cloud_ai_conversation_prompts p
                ON c.conversation_id = p.conversation_id
            GROUP BY c.conversation_id, c.conversation_title, CAST(c.created AS DATE)
            ORDER BY CAST(c.created AS DATE) DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        conversations = []
        for row in rows:
            conv_data = {
                'id': str(row[0]),
                'title': str(row[1]) if row[1] else 'Untitled Conversation',
                'created': row[2],
                'message_count': int(row[3])
            }
            conversations.append(conv_data)
        
        cursor.close()
        conn.close()
        return conversations
    except Exception as e:
        st.error(f"Failed to fetch conversations: {e}")
        return None


def get_conversation_messages(conversation_id):
    """Get messages from a specific conversation"""
    try:
        conn, error = connect_to_database()
        if error:
            return None
        
        cursor = conn.cursor()
        query = """
            SELECT 
                prompt,
                prompt_response,
                CAST(created AS DATE) AS created
            FROM user_cloud_ai_conversation_prompts
            WHERE conversation_id = :conv_id
            ORDER BY created ASC
        """
        cursor.execute(query, conv_id=conversation_id)
        rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            # User message
            messages.append({
                'role': 'user',
                'content': str(row[0]),
                'timestamp': row[2]
            })
            # Assistant message
            response = row[1]
            if hasattr(response, 'read'):
                response = response.read()
            messages.append({
                'role': 'assistant',
                'content': str(response) if response else '',
                'timestamp': row[2]
            })
        
        cursor.close()
        conn.close()
        return messages
    except Exception as e:
        st.error(f"Failed to fetch conversation messages: {e}")
        return None


def execute_agent_query(team_name, question, conversation_id=None):
    """Execute AI Agent query"""
    try:
        conn, error = connect_to_database()
        if error:
            return None, error
        
        cursor = conn.cursor()
        
        # Set the team
        cursor.execute(f"BEGIN DBMS_CLOUD_AI_AGENT.SET_TEAM('{team_name}'); END;")
        conn.commit()
        
        # Create or use existing conversation
        if not conversation_id:
            cursor.execute("SELECT DBMS_CLOUD_AI.CREATE_CONVERSATION() FROM DUAL")
            conversation_id = cursor.fetchone()[0]
        
        # Execute agent query
        plsql_block = """
        DECLARE
            l_result CLOB;
        BEGIN
            l_result := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
                team_name => :team_name,
                user_prompt => :user_prompt,
                params => :params
            );
            
            :result := l_result;
        END;
        """
        
        result_var = cursor.var(oracledb.CLOB)
        params_json = json.dumps({"conversation_id": conversation_id})
        cursor.execute(
            plsql_block, 
            team_name=team_name,
            user_prompt=question, 
            params=params_json,
            result=result_var
        )
        
        result = result_var.getvalue()
        if result:
            result = result.read() if hasattr(result, 'read') else str(result)
        
        cursor.close()
        conn.close()
        
        return result, conversation_id
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        return None, None


# ============================================================================
# UI COMPONENTS
# ============================================================================

def setup_page():
    """Configure page settings"""
    st.set_page_config(
        page_title="AI Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Northwind AI Agent Assistant")
    st.markdown("*Select a team and ask questions using AI Agents*")


def setup_sidebar():
    """Setup sidebar with team, task, and tool selection"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Connection status
        st.subheader("🔌 Database")
        conn, error = connect_to_database()
        
        if conn:
            st.success("✅ Connected")
            conn.close()
        else:
            st.error("❌ Failed to connect")
            if error:
                st.error(error)
            st.stop()
        
        # Team Selection
        st.subheader("👥 Select Team")
        teams = get_teams()
        
        if not teams:
            st.warning("⚠️ No teams found")
            return None, None, None
        
        team_names = [team['name'] for team in teams]
        selected_team_name = st.selectbox(
            "Available Teams",
            team_names,
            help="Select an AI Agent team"
        )
        
        selected_team = next((t for t in teams if t['name'] == selected_team_name), None)
        
        if selected_team:
            # Display team information
            with st.expander("📋 Team Details", expanded=True):
                st.write(f"**Status:** {selected_team['status']}")
                
                # Show agents in team
                agents = selected_team.get('agents', [])
                if agents:
                    st.write("**Agents:**")
                    for agent in agents:
                        st.write(f"- {agent.get('name', 'Unknown')}")
                        agent_task = agent.get('task', 'No task assigned')
                        st.write(f"  → Task: {agent_task}")
            
            # Task Selection
            st.subheader("📝 Task Agents")
            agents = selected_team.get('agents', [])
            
            if agents:
                agent_options = [f"{a.get('name', 'Unknown')} → {a.get('task', 'No task')}" 
                               for a in agents]
                selected_agent_idx = st.selectbox(
                    "Select Agent & Task",
                    range(len(agent_options)),
                    format_func=lambda x: agent_options[x],
                    help="Select an agent to view its task and tools"
                )
                
                selected_agent = agents[selected_agent_idx]
                task_name = selected_agent.get('task')
                
                if task_name:
                    # Get task details
                    tasks = get_tasks_for_agent(selected_agent.get('name'))
                    task_info = next((t for t in tasks if t['name'] == task_name), None) if tasks else None
                    
                    if task_info:
                        with st.expander("🔍 Task Details", expanded=True):
                            st.write(f"**Task Name:** {task_info['name']}")
                            st.write(f"**Status:** {task_info['status']}")
                            
                            # Show instruction
                            instruction = task_info['attributes'].get('instruction', 'No instruction')
                            st.text_area("Instruction:", instruction, height=150, disabled=True)
                            
                            # Show tools
                            tools_str = task_info['attributes'].get('tools', '[]')
                            try:
                                tools_list = json.loads(tools_str)
                                if tools_list:
                                    st.write("**Available Tools:**")
                                    for tool in tools_list:
                                        st.write(f"- {tool}")
                            except:
                                st.write(f"Tools: {tools_str}")
                        
                        # Tool Details
                        st.subheader("🔧 Tool Information")
                        all_tools = get_tools_for_task(task_name)
                        
                        if all_tools:
                            tool_names = [tool['name'] for tool in all_tools]
                            selected_tool_name = st.selectbox(
                                "Select Tool",
                                tool_names,
                                help="View tool details"
                            )
                            
                            selected_tool = next((t for t in all_tools if t['name'] == selected_tool_name), None)
                            
                            if selected_tool:
                                with st.expander("🛠️ Tool Details", expanded=True):
                                    st.write(f"**Tool Name:** {selected_tool['name']}")
                                    st.write(f"**Status:** {selected_tool['status']}")
                                    st.write(f"**Description:** {selected_tool['description']}")
                                    
                                    # Show tool attributes
                                    if selected_tool['attributes']:
                                        st.write("**Attributes:**")
                                        for attr_name, attr_value in selected_tool['attributes'].items():
                                            with st.container():
                                                st.write(f"**{attr_name}:**")
                                                try:
                                                    # Try to parse as JSON for better display
                                                    parsed = json.loads(attr_value)
                                                    st.json(parsed)
                                                except:
                                                    st.code(attr_value)
                            
                            return selected_team_name, task_name, selected_tool_name
                        else:
                            st.info("No tools found for this task")
        
        # Conversation History
        st.divider()
        st.subheader("� Conversation History")
        
        conversations = get_conversation_history()
        
        # New conversation option
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("➕ New Conversation", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_id = None
                st.session_state.selected_conversation = None
                st.rerun()
        with col2:
            if st.button("🔄", help="Refresh list"):
                st.cache_data.clear()
                st.rerun()
        
        # Display conversation list
        if conversations:
            # Create a select box for conversations
            conv_options = ["(Current Session)"] + [
                f"{conv['title'][:30]}... ({conv['message_count']} msgs)" 
                if len(conv['title']) > 30 
                else f"{conv['title']} ({conv['message_count']} msgs)"
                for conv in conversations
            ]
            
            selected_conv_idx = st.selectbox(
                "Select a conversation",
                range(len(conv_options)),
                format_func=lambda x: conv_options[x],
                key="conversation_selector",
                help="Choose a conversation to continue"
            )
            
            # Load selected conversation
            if selected_conv_idx > 0:  # Not current session
                selected_conv = conversations[selected_conv_idx - 1]
                
                # Show conversation details
                with st.expander("📋 Conversation Info", expanded=False):
                    st.write(f"**ID:** {selected_conv['id'][:20]}...")
                    st.write(f"**Created:** {selected_conv['created']}")
                    st.write(f"**Messages:** {selected_conv['message_count']}")
                
                # Load this conversation button
                if st.button("� Load This Conversation", use_container_width=True):
                    # Load messages from database
                    messages = get_conversation_messages(selected_conv['id'])
                    if messages:
                        st.session_state.messages = messages
                        st.session_state.conversation_id = selected_conv['id']
                        st.session_state.selected_conversation = selected_conv
                        st.success(f"Loaded: {selected_conv['title']}")
                        st.rerun()
        else:
            st.info("No conversation history found")
        
        # Sample Questions
        st.divider()
        st.subheader("💡 Example Questions")
        st.markdown("""
        **Try asking:**
        - What is the most expensive product?
        - Show me recent orders
        - I need to return order 10248
        - Send me product information by email
        """)
        
        return selected_team_name, None, None


def display_chat_history():
    """Display previous chat messages"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            # Display timestamp if available
            if "timestamp" in msg and msg["timestamp"]:
                st.caption(f"🕒 {msg['timestamp']}")
            st.markdown(msg["content"])


def process_user_input(prompt, team_name):
    """Process user question and generate response"""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            conversation_id = st.session_state.get('conversation_id')
            result, new_conversation_id = execute_agent_query(team_name, prompt, conversation_id)
            
            if result:
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
                
                if new_conversation_id:
                    st.session_state.conversation_id = new_conversation_id
            else:
                error_msg = "Failed to get response from AI Agent"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application logic"""
    # Setup
    setup_page()
    selected_team, selected_task, selected_tool = setup_sidebar()
    
    if not selected_team:
        st.warning("⚠️ Please select a team from the sidebar to start chatting")
        st.stop()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"👋 Hello! I'm the AI Agent from **{selected_team}**. How can I help you today?"
        })
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    
    if "selected_conversation" not in st.session_state:
        st.session_state.selected_conversation = None
    
    # Display current conversation info
    if st.session_state.selected_conversation:
        conv_info = st.session_state.selected_conversation
        st.info(f"📝 Continuing conversation: **{conv_info['title']}** (ID: {conv_info['id'][:20]}...)")
    elif st.session_state.conversation_id:
        st.info(f"💬 Active conversation ID: {st.session_state.conversation_id[:20]}...")
    else:
        st.info("✨ New conversation - messages will be saved automatically")
    
    # Display chat history
    display_chat_history()
    
    # Handle user input
    if prompt := st.chat_input(f"Ask {selected_team} a question..."):
        process_user_input(prompt, selected_team)
    
    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        f"<small>Powered by Oracle Select AI Agent | Active Team: {selected_team}</small>"
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
