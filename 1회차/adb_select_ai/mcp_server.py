"""
Oracle Select AI MCP Server
Simple interface to query Oracle database using natural language
"""

import os
from dotenv import load_dotenv

# ============================================================================
# CONFIGURATION - 환경 변수 사용 (보안)
# ============================================================================
# .env 파일 로드
load_dotenv()

WALLET_DIR = os.getenv("WALLET_DIR")

DB_USER = os.getenv("DB_USER", "NORTHWIND")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

DEFAULT_PROFILE = os.getenv("AI_PROFILE", "NORTHWIND_AI")

# 필수 환경 변수 체크
if not all([WALLET_DIR, DB_PASSWORD, DB_DSN, WALLET_PASSWORD]):
    raise ValueError(
        "Required environment variables not set: "
        "WALLET_DIR, DB_PASSWORD, DB_DSN, WALLET_PASSWORD"
    )

# Set TNS_ADMIN before any database operations (MUST be before select_ai import)
os.environ['TNS_ADMIN'] = WALLET_DIR

# Now import select_ai and fastmcp AFTER setting TNS_ADMIN
from fastmcp import FastMCP
import select_ai

# Create MCP server
mcp = FastMCP("Oracle Select AI")

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

def ensure_connection():
    """Ensure database is connected (reconnect if needed)"""
    try:
        if not select_ai.is_connected():
            select_ai.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN,
                wallet_location=WALLET_DIR,
                wallet_password=WALLET_PASSWORD
            )
        return True
    except Exception as e:
        import sys, traceback
        print(f"❌ Connection error: {e}", file=sys.stderr, flush=True)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
        return False


def get_profile(profile_name: str):
    """Get AI profile object"""
    try:
        return select_ai.Profile(profile_name=profile_name)
    except Exception as e:
        raise Exception(f"Failed to load profile '{profile_name}': {e}")


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
def ask_database(
    question: str,
    profile_name: str = DEFAULT_PROFILE
) -> str:
    """
    Ask a question about the Northwind database in natural language.
    Returns results with explanation.
    
    Examples:
    - "What are the top 5 most expensive products?"
    - "Show me total sales for 1997"
    - "Which employee has the most orders?"
    
    Args:
        question: Natural language question about the data
        profile_name: AI profile to use (default: NORTHWIND_AI3)
    
    Returns:
        Natural language explanation of the query results
    """
    try:
        # Ensure connected
        if not ensure_connection():
            return "Error: Could not connect to database"
        
        # Get profile and execute
        profile = get_profile(profile_name)
        response = profile.narrate(question)
        
        return response
    
    except Exception as e:
        import sys, traceback
        error_msg = f"Error: {str(e)}"
        print(f"❌ [ask_database] {error_msg}\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        return error_msg


@mcp.tool()
def generate_sql(
    question: str,
    profile_name: str = DEFAULT_PROFILE
) -> str:
    """
    Generate SQL code from natural language without executing it.
    Use this when you just want to see the SQL query.
    
    Examples:
    - "Generate SQL to find top selling products"
    - "Show me the SQL for customer orders"
    
    Args:
        question: Natural language description of what you want to query
        profile_name: AI profile to use (default: NORTHWIND_AI3)
    
    Returns:
        SQL query as a string
    """
    try:
        # Ensure connected
        if not ensure_connection():
            return "Error: Could not connect to database"
        
        # Get profile and generate SQL
        profile = get_profile(profile_name)
        sql = profile.generate(f"showsql {question}")
        
        return str(sql)
    
    except Exception as e:
        import sys, traceback
        error_msg = f"Error: {str(e)}"
        print(f"❌ [generate_sql] {error_msg}\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        return error_msg


@mcp.tool()
def chat_with_ai(
    message: str,
    profile_name: str = DEFAULT_PROFILE
) -> str:
    """
    Have a general conversation with the AI about the database.
    Use this for questions about the database schema, concepts, or general help.
    
    Examples:
    - "What tables are in the Northwind database?"
    - "What is the Northwind database about?"
    - "How do I find customer information?"
    
    Args:
        message: Your question or message
        profile_name: AI profile to use (default: NORTHWIND_AI3)
    
    Returns:
        AI's response
    """
    try:
        # Ensure connected
        if not ensure_connection():
            return "Error: Could not connect to database"
        
        # Get profile and chat
        profile = get_profile(profile_name)
        response = profile.chat(message)
        
        return response
    
    except Exception as e:
        import sys, traceback
        error_msg = f"Error: {str(e)}"
        print(f"❌ [chat_with_ai] {error_msg}\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        return error_msg




# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    # Start MCP server
    # This will be called by Cursor/Claude Desktop
    import sys
    print("="*80, file=sys.stderr, flush=True)
    print("Starting Oracle Select AI MCP Server...", file=sys.stderr, flush=True)
    print(f"✓ .env file loaded from: {os.getcwd()}", file=sys.stderr, flush=True)
    print(f"✓ Wallet directory: {WALLET_DIR}", file=sys.stderr, flush=True)
    print(f"✓ Database DSN: {DB_DSN}", file=sys.stderr, flush=True)
    print(f"✓ Database user: {DB_USER}", file=sys.stderr, flush=True)
    print(f"✓ Default AI profile: {DEFAULT_PROFILE}", file=sys.stderr, flush=True)
    print(f"✓ Available tools: ask_database, generate_sql, chat_with_ai", file=sys.stderr, flush=True)
    print("="*80, file=sys.stderr, flush=True)
    
    mcp.run()