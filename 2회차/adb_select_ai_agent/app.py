"""
Northwind AI Agent Assistant - Oracle Select AI Agent Interface
Hierarchical team, task, and tool selection with chat interface
"""

import os
import time
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

@st.cache_resource
def get_connection_pool():
    """Create and return a connection pool (cached)"""
    try:
        pool = oracledb.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            wallet_location=WALLET_DIR,
            wallet_password=WALLET_PASSWORD,
            min=2,
            max=10,
            increment=1
        )
        return pool, None
    except Exception as e:
        return None, str(e)


def get_connection():
    """Get a connection from the pool"""
    pool, error = get_connection_pool()
    if error:
        return None, error
    try:
        connection = pool.acquire()
        return connection, None
    except Exception as e:
        return None, str(e)


def connect_to_database():
    """Get a connection from the pool"""
    return get_connection()


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
                TO_CHAR(c.created, 'YYYY-MM-DD HH24:MI:SS') AS created,
                COUNT(p.conversation_prompt_id) AS message_count
            FROM user_cloud_ai_conversations c
            LEFT JOIN user_cloud_ai_conversation_prompts p
                ON c.conversation_id = p.conversation_id
            GROUP BY c.conversation_id, c.conversation_title, TO_CHAR(c.created, 'YYYY-MM-DD HH24:MI:SS')
            ORDER BY TO_CHAR(c.created, 'YYYY-MM-DD HH24:MI:SS') DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        conversations = []
        for row in rows:
            conv_data = {
                'id': str(row[0]),
                'title': str(row[1]) if row[1] else 'Untitled Conversation',
                'created': row[2] if row[2] else '',  # Already a string from TO_CHAR
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
    """Get messages from a specific conversation with all execution steps"""
    try:
        conn, error = connect_to_database()
        if error:
            return None
        
        cursor = conn.cursor()
        query = """
            SELECT 
                prompt,
                prompt_response,
                prompt_action,
                TO_CHAR(created, 'YYYY-MM-DD HH24:MI:SS') AS created
            FROM user_cloud_ai_conversation_prompts
            WHERE conversation_id = :conv_id
            ORDER BY created ASC
        """
        cursor.execute(query, conv_id=conversation_id)
        rows = cursor.fetchall()
        
        messages = []
        current_prompt = None
        execution_steps = []
        
        for row in rows:
            prompt = str(row[0])
            response = row[1]
            if hasattr(response, 'read'):
                response = response.read()
            response = str(response) if response else ''
            
            prompt_action = str(row[2]) if row[2] else 'UNKNOWN'
            timestamp = row[3] if row[3] else ''  # Already a string from TO_CHAR
            
            # If this is a new prompt, save previous message and start new one
            if prompt != current_prompt:
                # Save previous message if exists
                if current_prompt is not None and execution_steps:
                    # Get the final response (usually the last step)
                    final_response = execution_steps[-1]['response'] if execution_steps else ''
                    messages.append({
                        'role': 'assistant',
                        'content': final_response,
                        'execution_steps': execution_steps,
                        'timestamp': execution_steps[0].get('timestamp') if execution_steps else None
                    })
                
                # Add user message for new prompt
                if prompt:
                    messages.append({
                        'role': 'user',
                        'content': prompt,
                        'timestamp': timestamp
                    })
                
                # Reset for new message
                current_prompt = prompt
                execution_steps = []
            
            # Add this execution step
            execution_steps.append({
                'action': prompt_action,
                'response': response,
                'timestamp': timestamp
            })
        
        # Don't forget the last message
        if current_prompt is not None and execution_steps:
            final_response = execution_steps[-1]['response'] if execution_steps else ''
            messages.append({
                'role': 'assistant',
                'content': final_response,
                'execution_steps': execution_steps,
                'timestamp': execution_steps[0].get('timestamp') if execution_steps else None
            })
        
        cursor.close()
        conn.close()
        return messages
    except Exception as e:
        st.error(f"Failed to fetch conversation messages: {e}")
        return None


def execute_agent_query(team_name, question, conversation_id=None):
    """Execute AI Agent query and retrieve detailed thought process"""
    try:
        conn, error = connect_to_database()
        if error:
            return None, None, error
        
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
        
        # Small delay to ensure database commits all records
        time.sleep(0.5)
        
        # Query the database to get execution steps for this prompt
        # Use DBMS_LOB.COMPARE for CLOB comparison
        detail_query = """
            SELECT 
                prompt_action,
                prompt_response
            FROM user_cloud_ai_conversation_prompts
            WHERE conversation_id = :conv_id
            AND DBMS_LOB.COMPARE(prompt, :user_prompt) = 0
        """
        
        try:
            cursor.execute(detail_query, conv_id=conversation_id, user_prompt=question)
            detail_rows = cursor.fetchall()
            st.info(f"✅ Query successful! Found {len(detail_rows)} execution steps")
        except Exception as query_error:
            st.error(f"Detail query failed: {query_error}")
            st.error(f"Query was: {detail_query}")
            st.error(f"Params: conv_id={conversation_id}, prompt={question}")
            raise
        
        execution_steps = []
        
        for idx, row in enumerate(detail_rows, 1):
            action_type = str(row[0]) if row[0] else "UNKNOWN"
            response = row[1]
            if hasattr(response, 'read'):
                response = response.read()
            response = str(response) if response else ''
            
            st.info(f"📝 Step {idx}: Action={action_type}, Response length={len(response)}")
            
            execution_steps.append({
                'action': action_type,
                'response': response,
                'timestamp': ''  # No timestamp for now
            })
        
        cursor.close()
        conn.close()
        
        st.success(f"🎉 Returning {len(execution_steps)} execution steps to UI")
        
        # Return all execution steps along with the final result
        return result, execution_steps, conversation_id
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        return None, None, None


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
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            # Display timestamp if available
            if "timestamp" in msg and msg["timestamp"]:
                st.caption(f"🕒 {msg['timestamp']}")
            
            # Display content
            st.markdown(msg["content"])
            
            # For assistant messages, show execution steps if available
            if msg["role"] == "assistant":
                # Check for execution_steps (new format)
                if "execution_steps" in msg and msg["execution_steps"]:
                    execution_steps = msg["execution_steps"]
                    with st.expander("🔍 View Execution Details", expanded=False):
                        st.write(f"**Total Steps:** {len(execution_steps)}")
                        st.divider()
                        
                        for step_idx, step in enumerate(execution_steps, 1):
                            action_type = step['action']
                            response = step['response']
                            timestamp = step.get('timestamp', '')
                            
                            # Action type emoji
                            action_emoji = {
                                "AGENT": "🤖",
                                "SQL": "🗃️",
                                "RAG": "📚",
                                "PLSQL": "⚙️",
                                "TOOL": "🔧",
                                "UNKNOWN": "❓"
                            }.get(action_type, "💬")
                            
                            st.subheader(f"{action_emoji} Step {step_idx}: {action_type}")
                            if timestamp:
                                st.caption(f"🕒 {timestamp}")
                            
                            # Try to parse response as JSON
                            try:
                                parsed = json.loads(response)
                                if isinstance(parsed, dict):
                                    # Display thought/action/observation if available
                                    if "thought" in parsed:
                                        st.write("**💭 Thought:**")
                                        st.info(parsed["thought"])
                                    
                                    if "action" in parsed:
                                        st.write("**⚡ Action:**")
                                        st.code(parsed["action"], language="sql")
                                    
                                    if "observation" in parsed:
                                        st.write("**👁️ Observation:**")
                                        st.success(parsed["observation"])
                                    
                                    if "response" in parsed or "answer" in parsed:
                                        st.write("**📝 Response:**")
                                        st.markdown(parsed.get("response") or parsed.get("answer"))
                                    
                                    # Show full JSON
                                    with st.expander("📋 Full JSON", expanded=False):
                                        st.json(parsed)
                                else:
                                    st.code(response)
                            except (json.JSONDecodeError, TypeError):
                                # Not JSON, display as text
                                st.text_area("Response:", response, height=150, disabled=True, key=f"hist_msg{idx}_step{step_idx}")
                            
                            if step_idx < len(execution_steps):
                                st.divider()
                
                # Check for old format (prompt_action only)
                elif "prompt_action" in msg:
                    action_type = msg["prompt_action"]
                    action_emoji = {
                        "AGENT": "🤖",
                        "SQL": "🗃️",
                        "RAG": "📚",
                        "UNKNOWN": "❓"
                    }.get(action_type, "💬")
                    
                    st.caption(f"{action_emoji} Action Type: **{action_type}**")


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
            result, execution_steps, new_conversation_id = execute_agent_query(team_name, prompt, conversation_id)
            
            if result and execution_steps:
                # Display main result
                st.markdown(result)
                
                # Show all execution steps
                if execution_steps:
                    with st.expander("🔍 View Execution Details", expanded=True):
                        st.write(f"**Total Steps:** {len(execution_steps)}")
                        st.divider()
                        
                        for idx, step in enumerate(execution_steps, 1):
                            action_type = step['action']
                            response = step['response']
                            timestamp = step.get('timestamp', '')
                            
                            # Action type emoji
                            action_emoji = {
                                "AGENT": "🤖",
                                "SQL": "🗃️",
                                "RAG": "📚",
                                "PLSQL": "⚙️",
                                "TOOL": "🔧",
                                "UNKNOWN": "❓"
                            }.get(action_type, "💬")
                            
                            st.subheader(f"{action_emoji} Step {idx}: {action_type}")
                            if timestamp:
                                st.caption(f"🕒 {timestamp}")
                            
                            # Try to parse response as JSON
                            try:
                                parsed = json.loads(response)
                                if isinstance(parsed, dict):
                                    # Display thought/action/observation if available
                                    if "thought" in parsed:
                                        st.write("**💭 Thought:**")
                                        st.info(parsed["thought"])
                                    
                                    if "action" in parsed:
                                        st.write("**⚡ Action:**")
                                        st.code(parsed["action"], language="sql")
                                    
                                    if "observation" in parsed:
                                        st.write("**👁️ Observation:**")
                                        st.success(parsed["observation"])
                                    
                                    if "response" in parsed or "answer" in parsed:
                                        st.write("**� Response:**")
                                        st.markdown(parsed.get("response") or parsed.get("answer"))
                                    
                                    # Show full JSON
                                    with st.expander("📋 Full JSON", expanded=False):
                                        st.json(parsed)
                                else:
                                    st.code(response)
                            except (json.JSONDecodeError, TypeError):
                                # Not JSON, display as text
                                st.text_area("Response:", response, height=150, disabled=True, key=f"step_{idx}")
                            
                            if idx < len(execution_steps):
                                st.divider()
                
                # Add to session - store execution steps for later display
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result,
                    "execution_steps": execution_steps
                })
                
                if new_conversation_id:
                    st.session_state.conversation_id = new_conversation_id
            else:
                error_msg = "Failed to get response from AI Agent"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg,
                    "execution_steps": []
                })


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
