"""
Oracle AI Agent MCP Server (stdio)

Oracle Select AI Agent의 SQL_Analysis_Team / DICT_SEARCH_TEAM을
MCP Tool로 노출하는 서버.

Dify에서 사용 시 mcp-proxy로 stdio → HTTP 변환하여 연결.

사용법:
  1) 직접 실행 (stdio):
     python sql_analysis_mcp_server.py

  2) mcp-proxy로 HTTP 변환 (Dify 연동):
     npx @anthropic-ai/mcp-proxy --port 8081 -- python sql_analysis_mcp_server.py

  3) Claude Desktop / Cursor 설정:
     {
       "mcpServers": {
         "oracle-ai": {
           "command": "python",
           "args": ["<path>/sql_analysis_mcp_server.py"],
           "env": { ... }
         }
       }
     }
"""

import os
import sys
import json
import atexit
from contextlib import contextmanager
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

WALLET_DIR = os.getenv("WALLET_DIR")
DB_USER = os.getenv("DB_USER", "GENAI")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")
DEFAULT_TEAM = os.getenv("DEFAULT_TEAM", "SQL_Analysis_Team")

POOL_MIN = int(os.getenv("POOL_MIN", "2"))
POOL_MAX = int(os.getenv("POOL_MAX", "10"))
POOL_INCREMENT = int(os.getenv("POOL_INCREMENT", "1"))

# 필수 환경 변수 체크
if not all([WALLET_DIR, DB_PASSWORD, DB_DSN, WALLET_PASSWORD]):
    raise ValueError(
        "Required environment variables not set: "
        "WALLET_DIR, DB_PASSWORD, DB_DSN, WALLET_PASSWORD"
    )

# TNS_ADMIN 설정 (oracledb import 전에)
os.environ["TNS_ADMIN"] = WALLET_DIR

import oracledb
from fastmcp import FastMCP

# MCP 서버 생성
mcp = FastMCP("Oracle AI Agent")


# ============================================================================
# CONNECTION POOL
# ============================================================================

_pool: oracledb.ConnectionPool | None = None


def init_pool() -> oracledb.ConnectionPool:
    """Connection pool 초기화 (싱글턴). 서버 시작 시 1회 호출."""
    global _pool
    if _pool is None:
        _pool = oracledb.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            wallet_location=WALLET_DIR,
            wallet_password=WALLET_PASSWORD,
            min=POOL_MIN,
            max=POOL_MAX,
            increment=POOL_INCREMENT,
        )
        print(
            f"  Pool created: min={POOL_MIN}, max={POOL_MAX}, increment={POOL_INCREMENT}",
            file=sys.stderr, flush=True,
        )
    return _pool


def close_pool():
    """서버 종료 시 pool 정리."""
    global _pool
    if _pool is not None:
        try:
            _pool.close(force=True)
            print("  Pool closed.", file=sys.stderr, flush=True)
        except Exception:
            pass
        _pool = None


@contextmanager
def get_connection():
    """
    Pool에서 connection을 빌려 쓰고 자동 반환하는 context manager.

    사용법:
        with get_connection() as conn:
            cursor = conn.cursor()
            ...
    """
    pool = init_pool()
    conn = pool.acquire()
    try:
        yield conn
    finally:
        pool.release(conn)


# ============================================================================
# MCP TOOLS
# ============================================================================


@mcp.tool()
def analyze_sql(
    sql_text: str,
    schema: str = "ADM",
    team_name: str = DEFAULT_TEAM,
) -> str:
    """
    SQL 성능 분석을 요청합니다.
    Oracle Standby DB에서 실행계획, 테이블 통계, 인덱스 정보를 수집하고
    AI Agent가 해석하여 튜닝 권고를 제공합니다.

    Args:
        sql_text: 분석할 SQL 쿼리 (예: "SELECT * FROM ADM.TCODE WHERE LGRP_CD = 'SYS'")
        schema: 대상 스키마명 (기본: ADM)
        team_name: 사용할 Agent Team (기본: SQL_Analysis_Team)

    Returns:
        AI Agent의 SQL 성능 분석 결과 (실행계획 요약, 튜닝 권고 등)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # conversation_id 생성
            cursor.execute("SELECT DBMS_CLOUD_AI.CREATE_CONVERSATION() FROM DUAL")
            conv_id = cursor.fetchone()[0]

            # RUN_TEAM 호출
            result_var = cursor.var(oracledb.CLOB)
            user_prompt = f"{sql_text} 쿼리를 분석해줘. 스키마는 {schema}이야."
            params_json = json.dumps({"conversation_id": conv_id})

            cursor.execute(
                """
                DECLARE
                    l_result CLOB;
                BEGIN
                    l_result := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
                        team_name   => :team_name,
                        user_prompt => :user_prompt,
                        params      => :params
                    );
                    :result := l_result;
                END;
                """,
                team_name=team_name,
                user_prompt=user_prompt,
                params=params_json,
                result=result_var,
            )

            result = result_var.getvalue()
            if result and hasattr(result, "read"):
                result = result.read()

            cursor.close()
            return str(result) if result else "분석 결과를 가져올 수 없습니다."

    except Exception as e:
        import traceback
        return f"Error: {e}\n{traceback.format_exc()}"


@mcp.tool()
def analyze_sql_raw(
    sql_text: str,
    schema: str = "ADM",
) -> str:
    """
    SQL 성능 원시 데이터를 조회합니다 (AI 해석 없이).
    DB Link를 통해 Standby DB에서 실행계획, 테이블 통계, 인덱스 정보를
    JSON으로 직접 반환합니다. 직접 분석이 필요할 때 사용하세요.

    Args:
        sql_text: 분석할 SQL 쿼리
        schema: 대상 스키마명 (기본: ADM)

    Returns:
        JSON 결과 (execution_plan, table_stats, index_info, error_code)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            result_var = cursor.var(oracledb.STRING, 32767)
            cursor.execute(
                """
                BEGIN
                    :result := analyze_sql_via_dblink(
                        p_sql_text => :sql_text,
                        p_schema   => :schema
                    );
                END;
                """,
                result=result_var,
                sql_text=sql_text,
                schema=schema,
            )

            result = result_var.getvalue()
            cursor.close()

            # JSON 포맷팅
            if result:
                try:
                    parsed = json.loads(result)
                    return json.dumps(parsed, indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    return result

            return "결과를 가져올 수 없습니다."

    except Exception as e:
        import traceback
        return f"Error: {e}\n{traceback.format_exc()}"


@mcp.tool()
def get_analysis_history(limit: int = 10) -> str:
    """
    최근 SQL 분석 요청 이력을 조회합니다.

    Args:
        limit: 조회할 최대 건수 (기본: 10)

    Returns:
        최근 분석 요청 목록 (request_id, status, sql_preview, 시각)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT request_id, status, requested_by,
                       SUBSTR(sql_text, 1, 80) AS sql_preview,
                       error_message,
                       TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
                FROM ai_analysis_request
                ORDER BY created_at DESC
                FETCH FIRST :lmt ROWS ONLY
                """,
                lmt=limit,
            )

            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            results = []
            for row in rows:
                record = {}
                for i, col in enumerate(columns):
                    val = row[i]
                    if hasattr(val, "read"):
                        val = val.read()
                    record[col] = str(val) if val is not None else None
                results.append(record)

            cursor.close()

            if not results:
                return "분석 이력이 없습니다."

            return json.dumps(results, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def search_table_column(
    question: str,
    top_n: int = 20,
    team_name: str = "DICT_SEARCH_TEAM",
) -> str:
    """
    자연어로 테이블/컬럼을 검색합니다.
    벡터 유사도 검색으로 질문과 관련된 테이블, 컬럼, 데이터타입, 코멘트를 찾아
    AI Agent가 정리하여 답변합니다.

    Args:
        question: 자연어 검색 질문 (예: "고객 주문 정보", "배송 주소 컬럼", "사용자 권한 관련 테이블")
        top_n: 벡터 검색 결과 수 (기본: 20)
        team_name: 사용할 Agent Team (기본: DICT_SEARCH_TEAM)

    Returns:
        관련 테이블/컬럼 정보와 AI 해석 결과
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # conversation_id 생성
            cursor.execute("SELECT DBMS_CLOUD_AI.CREATE_CONVERSATION() FROM DUAL")
            conv_id = cursor.fetchone()[0]

            # RUN_TEAM 호출
            result_var = cursor.var(oracledb.CLOB)
            params_json = json.dumps({"conversation_id": conv_id})

            cursor.execute(
                """
                DECLARE
                    l_result CLOB;
                BEGIN
                    l_result := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
                        team_name   => :team_name,
                        user_prompt => :user_prompt,
                        params      => :params
                    );
                    :result := l_result;
                END;
                """,
                team_name=team_name,
                user_prompt=question,
                params=params_json,
                result=result_var,
            )

            result = result_var.getvalue()
            if result and hasattr(result, "read"):
                result = result.read()

            cursor.close()
            return str(result) if result else "검색 결과를 가져올 수 없습니다."

    except Exception as e:
        import traceback
        return f"Error: {e}\n{traceback.format_exc()}"


@mcp.tool()
def search_table_column_raw(
    question: str,
    top_n: int = 20,
) -> str:
    """
    자연어로 테이블/컬럼을 벡터 검색합니다 (AI 해석 없이 원시 결과).
    search_dict 함수를 직접 호출하여 유사도 점수와 함께 매칭된 테이블/컬럼 정보를 반환합니다.

    Args:
        question: 자연어 검색 질문 (예: "고객 주문 정보", "배송 주소 컬럼")
        top_n: 반환할 결과 수 (기본: 20)

    Returns:
        유사도 순으로 정렬된 테이블/컬럼 정보 텍스트
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            result_var = cursor.var(oracledb.CLOB)
            cursor.execute(
                """
                BEGIN
                    :result := search_dict(
                        p_question => :question,
                        p_top_n    => :top_n
                    );
                END;
                """,
                result=result_var,
                question=question,
                top_n=top_n,
            )

            result = result_var.getvalue()
            if result and hasattr(result, "read"):
                result = result.read()

            cursor.close()
            return str(result) if result else "검색 결과 없음"

    except Exception as e:
        import traceback
        return f"Error: {e}\n{traceback.format_exc()}"


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("=" * 70, file=sys.stderr, flush=True)
    print("Starting Oracle AI Agent MCP Server...", file=sys.stderr, flush=True)
    print(f"  Wallet: {WALLET_DIR}", file=sys.stderr, flush=True)
    print(f"  DSN: {DB_DSN}", file=sys.stderr, flush=True)
    print(f"  User: {DB_USER}", file=sys.stderr, flush=True)
    print(f"  Default Team: {DEFAULT_TEAM}", file=sys.stderr, flush=True)

    # 서버 시작 시 pool 생성
    init_pool()
    atexit.register(close_pool)

    print("  Tools:", file=sys.stderr, flush=True)
    print("    - analyze_sql              (SQL 성능 분석 — AI 튜닝 권고)", file=sys.stderr, flush=True)
    print("    - analyze_sql_raw          (SQL 성능 원시 JSON)", file=sys.stderr, flush=True)
    print("    - get_analysis_history     (분석 이력 조회)", file=sys.stderr, flush=True)
    print("    - search_table_column      (테이블/컬럼 자연어 검색 — AI 해석)", file=sys.stderr, flush=True)
    print("    - search_table_column_raw  (테이블/컬럼 벡터 검색 — 원시 결과)", file=sys.stderr, flush=True)
    print("=" * 70, file=sys.stderr, flush=True)

    mcp.run()
