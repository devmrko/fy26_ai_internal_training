# SQL Analysis Agent MCP Server

Oracle Select AI Agent의 SQL_Analysis_Team을 MCP Tool로 노출하는 stdio 서버.

## 아키텍처

```
Dify / Claude Desktop / Cursor
    ↓  MCP Protocol (stdio 또는 mcp-proxy → HTTP)
SQL Analysis MCP Server (이 서버)
    ↓  oracledb (Wallet 인증)
Autonomous AI Lakehouse (OCI Seoul)
    ↓  DBMS_CLOUD_AI_AGENT.RUN_TEAM
SQL_Analysis_Team → SQL_Analyzer Tool
    ↓  DB Link (DBLINK_DR)
ExaCI Standby DB → query_analyzer_stby 패키지
```

## 제공 Tool

| Tool | 설명 |
|---|---|
| `analyze_sql` | SQL 성능 분석 요청 → AI Agent가 해석하여 튜닝 권고 반환 |
| `analyze_sql_raw` | 실행계획/통계/인덱스 원시 JSON 반환 (AI 해석 없이) |
| `get_analysis_history` | 최근 분석 요청 이력 조회 |

## 설정

```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 편집: WALLET_DIR, DB_PASSWORD, DB_DSN, WALLET_PASSWORD 입력
```

## 실행

### stdio 모드 (Claude Desktop / Cursor)

```bash
python sql_analysis_mcp_server.py
```

### Dify 연동 (mcp-proxy로 HTTP 변환)

```bash
# mcp-proxy 설치
npm install -g @anthropic-ai/mcp-proxy

# HTTP 서버로 변환 (포트 8081)
npx @anthropic-ai/mcp-proxy --port 8081 -- python sql_analysis_mcp_server.py
```

Dify에서 설정:
- Tool Type: **MCP**
- Transport: **Streamable HTTP**
- URL: `http://localhost:8081/mcp`

### Claude Desktop 설정 예시

`~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sql-analysis": {
      "command": "python",
      "args": ["/path/to/mcp/sql_analysis_mcp_server.py"],
      "env": {
        "WALLET_DIR": "/path/to/wallet",
        "DB_USER": "GENAI",
        "DB_PASSWORD": "...",
        "DB_DSN": "...",
        "WALLET_PASSWORD": "..."
      }
    }
  }
}
```
