# SQL 성능 분석 — Select AI Agent 구축 가이드

## 아키텍처

```
ExaCC (송도, Primary)
    ↓  Active Data Guard (동기 복제)
ExaCI (OCI Seoul, Standby)  ← query_analyzer_stby 패키지 + analyze_sql_vc 래퍼 함수
    ↓  DB Link (DBLINK_DR)
Autonomous AI Lakehouse (OCI Seoul)
    └── genai 스키마: analyze_sql_via_dblink 래퍼 → SQL_Analyzer Tool
        └── Select AI Agent → SQL 실행계획/통계/인덱스 분석 → 튜닝 권고
```

**목적**: Standby DB에서 SQL 실행계획, 테이블 통계, 인덱스 정보를 수집하고,
AI Agent가 이를 해석하여 성능 튜닝 권고를 제공하는 파이프라인 구축.

**분석 흐름**:
```
사용자 질문 (SQL 분석 요청)
    → Select AI Agent (SQL_Analysis_Team)
    → SQL_Analyzer Tool 호출
    → analyze_sql_via_dblink (ADB 래퍼)
    → analyze_sql_vc@DBLINK_DR (DB Link 호출)
    → query_analyzer_stby.collect_query_info (Standby DB 실행)
        ├── DBMS_SQL 실행 → V$SQL 캐싱 → SQL_ID 확보
        ├── DBMS_XPLAN.DISPLAY_CURSOR (ALLSTATS LAST) → 실행계획
        ├── ALL_TABLES → 테이블 통계 (JSON)
        └── ALL_INDEXES + ALL_IND_COLUMNS → 인덱스 정보 (JSON)
    → JSON 결과 반환 → Agent가 해석 → 한국어 튜닝 권고 응답
```

---

## 목차

1. [사전 준비](#1-사전-준비)
2. [분석 결과 저장 테이블 생성](#2-분석-결과-저장-테이블-생성)
3. [Standby DB 패키지 (query_analyzer_stby)](#3-standby-db-패키지)
4. [래퍼 함수 (ExaCI → ADB)](#4-래퍼-함수)
5. [Select AI Agent 구성](#5-select-ai-agent-구성)
6. [테스트 및 대화 이력 조회](#6-테스트-및-대화-이력-조회)

---

## 1. 사전 준비

**사용 계정**: `GENAI`

### 1.1 DB Link 확인

```sql
SELECT db_link, username, host FROM user_db_links;
```

### 1.2 Credential 확인

```sql
SELECT credential_name, username
FROM user_credentials;
```

| Credential | 용도 |
|---|---|
| `OCI_GENAI_CRED` | AI 모델 호출 (Select AI Profile) |
| `GENAI_VECTOR_CRED` | Vector Embedding 호출 |

### 1.3 AI Profile 확인

```sql
SELECT profile_name, status, created
FROM user_cloud_ai_profiles;
```

---

## 2. 분석 결과 저장 테이블 생성

분석 요청/결과/로그를 저장하는 3개 테이블.
`analyze_sql_via_dblink` 래퍼 함수가 Tool 호출 시 자동으로 요청/결과를 기록한다.

### 2.1 ai_analysis_request (분석 요청)

```sql
CREATE SEQUENCE ai_analysis_request_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE ai_analysis_request (
    request_id    NUMBER DEFAULT ai_analysis_request_seq.NEXTVAL
                  CONSTRAINT ai_req_pk PRIMARY KEY,
    sql_text      CLOB           NOT NULL,
    exec_plan     CLOB,
    table_stats   CLOB,
    index_info    CLOB,
    status        VARCHAR2(20)   DEFAULT 'PENDING'
                  CONSTRAINT ai_req_status_chk
                  CHECK (status IN ('PENDING', 'PROCESSING', 'DONE', 'ERROR')),
    error_message VARCHAR2(4000),
    source_db     VARCHAR2(128),           -- 요청 원본 DB 식별자
    requested_by  VARCHAR2(128),           -- 요청자
    created_at    TIMESTAMP      DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at    TIMESTAMP      DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX ai_req_status_idx ON ai_analysis_request (status, created_at);
CREATE INDEX ai_req_created_idx ON ai_analysis_request (created_at);

COMMENT ON TABLE ai_analysis_request IS 'AI 쿼리 분석 요청 테이블';
COMMENT ON COLUMN ai_analysis_request.request_id    IS '요청 ID (PK, 자동 채번)';
COMMENT ON COLUMN ai_analysis_request.sql_text      IS '분석 대상 SQL 원문';
COMMENT ON COLUMN ai_analysis_request.exec_plan     IS 'DBMS_XPLAN 실행계획 텍스트';
COMMENT ON COLUMN ai_analysis_request.table_stats   IS '참조 테이블 통계 (JSON)';
COMMENT ON COLUMN ai_analysis_request.index_info    IS '참조 테이블 인덱스 정보 (JSON)';
COMMENT ON COLUMN ai_analysis_request.status        IS '처리 상태: PENDING / PROCESSING / DONE / ERROR';
COMMENT ON COLUMN ai_analysis_request.error_message IS '에러 발생 시 메시지';
COMMENT ON COLUMN ai_analysis_request.source_db     IS '요청 원본 DB 식별자';
COMMENT ON COLUMN ai_analysis_request.requested_by  IS '요청자 (DB 사용자명)';
COMMENT ON COLUMN ai_analysis_request.created_at    IS '요청 생성 시각';
COMMENT ON COLUMN ai_analysis_request.updated_at    IS '최종 수정 시각';
```

### 2.2 ai_analysis_result (분석 결과)

```sql
CREATE TABLE ai_analysis_result (
    result_id     NUMBER GENERATED ALWAYS AS IDENTITY
                  CONSTRAINT ai_result_pk PRIMARY KEY,
    request_id    NUMBER         NOT NULL
                  CONSTRAINT ai_result_req_fk
                  REFERENCES ai_analysis_request (request_id),
    analysis      CLOB,                    -- LLM 분석 결과 전문
    suggestions   CLOB,                    -- 구조화된 최적화 제안 (JSON)
    model_used    VARCHAR2(200),           -- 사용된 LLM 모델명
    token_count   NUMBER,                  -- 토큰 사용량 (추적용)
    elapsed_secs  NUMBER(10,2),            -- LLM 처리 소요 시간(초)
    created_at    TIMESTAMP      DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX ai_result_req_idx ON ai_analysis_result (request_id);

COMMENT ON TABLE ai_analysis_result IS 'AI 쿼리 분석 결과 테이블';
COMMENT ON COLUMN ai_analysis_result.result_id    IS '결과 ID (PK, 자동 생성)';
COMMENT ON COLUMN ai_analysis_result.request_id   IS '요청 ID (FK → ai_analysis_request)';
COMMENT ON COLUMN ai_analysis_result.analysis     IS 'LLM 분석 결과 전문';
COMMENT ON COLUMN ai_analysis_result.suggestions  IS '구조화된 최적화 제안 (JSON)';
COMMENT ON COLUMN ai_analysis_result.model_used   IS '사용된 LLM 모델명';
COMMENT ON COLUMN ai_analysis_result.token_count  IS '토큰 사용량';
COMMENT ON COLUMN ai_analysis_result.elapsed_secs IS 'LLM 처리 소요 시간(초)';
COMMENT ON COLUMN ai_analysis_result.created_at   IS '결과 생성 시각';
```

### 2.3 ai_analysis_log (처리 로그)

```sql
CREATE TABLE ai_analysis_log (
    log_id        NUMBER GENERATED ALWAYS AS IDENTITY
                  CONSTRAINT ai_log_pk PRIMARY KEY,
    request_id    NUMBER,
    log_level     VARCHAR2(10)   DEFAULT 'INFO'
                  CONSTRAINT ai_log_level_chk
                  CHECK (log_level IN ('INFO', 'WARN', 'ERROR', 'DEBUG')),
    message       VARCHAR2(4000),
    created_at    TIMESTAMP      DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX ai_log_req_idx ON ai_analysis_log (request_id, created_at);

COMMENT ON TABLE ai_analysis_log IS 'AI 분석 처리 로그 테이블';
```

### 2.4 테이블 관계

```
ai_analysis_request (1) ──── (N) ai_analysis_result
         │
         └──── (N) ai_analysis_log
```

### 2.5 확인 쿼리

```sql
SELECT table_name, num_rows
FROM user_tables
WHERE table_name LIKE 'AI_ANALYSIS%'
ORDER BY table_name;
```

---

## 3. Standby DB 패키지

> **소스 파일**: 별도 관리 (`query_analyzer_stby.sql`)
>
> 여기서는 패키지의 구조와 핵심 동작 방식만 설명합니다.

### 3.1 개요

`query_analyzer_stby` — ADG Standby DB에서 SQL 분석을 수행하는 PL/SQL 패키지.
PLAN_TABLE 쓰기 없이 V$ 메모리 뷰만 사용하여 Read-Only 환경에서 동작한다.

**특징**:
- `AUTHID CURRENT_USER` — 호출자 권한으로 실행
- V$ 뷰 + `DBMS_XPLAN.DISPLAY_CURSOR` 기반 (쓰기 불필요)
- 에러를 RAISE하지 않고 `error_code`로 반환 (Agent Tool 호출에 적합)

### 3.2 사전 권한 (Standby DB에서 SYS/DBA 실행)

```sql
GRANT SELECT ON V_$DATABASE                TO <user>;
GRANT SELECT ON V_$SQL                     TO <user>;
GRANT SELECT ON V_$SQL_PLAN                TO <user>;
GRANT SELECT ON V_$SQL_PLAN_STATISTICS_ALL TO <user>;
GRANT SELECT ON V_$SESSION                 TO <user>;
GRANT EXECUTE ON DBMS_XPLAN               TO <user>;
GRANT EXECUTE ON DBMS_SQL                  TO <user>;
```

### 3.3 주요 함수

| 함수 | 설명 |
|---|---|
| `collect_query_info` | 메인 분석 함수. 아래 5단계를 순차 수행하여 `t_analysis_result` 반환 |
| `find_sql_id` | V$SQL에서 SQL 텍스트 앞 1000자를 LIKE 매칭하여 SQL_ID 검색 |
| `get_execution_plan_by_sqlid` | DBMS_XPLAN.DISPLAY_CURSOR로 실행계획 추출 |
| `extract_table_names_from_cursor` | V$SQL_PLAN에서 참조 테이블명 추출 |
| `get_table_stats` | ALL_TABLES에서 테이블 통계 조회 (JSON 배열) |
| `get_index_info` | ALL_INDEXES/ALL_IND_COLUMNS에서 인덱스 정보 조회 (JSON 배열) |

### 3.4 collect_query_info 처리 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│ 0. 입력 검증 (SQL 텍스트 비어있는지, 스키마 존재 여부)           │
├─────────────────────────────────────────────────────────────────┤
│ 1. STATISTICS_LEVEL = ALL 세션 설정                             │
│    → 실행통계(A-Rows, A-Time, Buffers) 수집 활성화              │
├─────────────────────────────────────────────────────────────────┤
│ 2. SQL_ID 확보                                                  │
│    → DBMS_SQL로 SQL 실행 → Shared Pool 캐싱 → V$SQL 검색       │
├─────────────────────────────────────────────────────────────────┤
│ 3. DBMS_XPLAN.DISPLAY_CURSOR (ALLSTATS LAST 포맷)              │
│    → 실행계획 + 실제 처리 건수/시간/I/O 통계 추출                │
├─────────────────────────────────────────────────────────────────┤
│ 4. V$SQL_PLAN에서 참조 테이블명 추출                             │
├─────────────────────────────────────────────────────────────────┤
│ 5. ALL_TABLES / ALL_INDEXES에서 통계 조회                       │
├─────────────────────────────────────────────────────────────────┤
│ 6. STATISTICS_LEVEL = TYPICAL 복원                              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.5 에러 코드

| 코드 | 상수 | 설명 |
|---|---|---|
| 0 | `QA_SUCCESS` | 정상 완료 |
| -20001 | `QA_ERR_TABLE_NOT_FOUND` | 테이블/뷰 없음 (ORA-00942) |
| -20002 | `QA_ERR_COLUMN_NOT_FOUND` | 컬럼명 잘못됨 (ORA-00904) |
| -20003 | `QA_ERR_SQL_SYNTAX` | SQL 구문 오류 |
| -20004 | `QA_ERR_SQL_EMPTY` | 입력 SQL 비어있음 |
| -20010 | `QA_ERR_SQLID_NOT_FOUND` | V$SQL에서 SQL_ID 미발견 |
| -20011 | `QA_ERR_PLAN_NOT_FOUND` | 실행계획 없음 |
| -20020 | `QA_ERR_INSUFFICIENT_PRIV` | 권한 부족 |
| -20021 | `QA_ERR_NOT_STANDBY` | Standby DB가 아닌 환경 |
| -20022 | `QA_ERR_SESSION_SETTING` | 세션 설정 실패 |
| -20030 | `QA_ERR_SCHEMA_NOT_FOUND` | 스키마 없음 |
| -20031 | `QA_ERR_NO_TABLES_IN_PLAN` | 실행계획에서 테이블 추출 불가 |

---

## 4. 래퍼 함수

DB Link를 통해 Standby DB의 `query_analyzer_stby` 패키지를 호출하기 위한 래퍼 함수들.

### 4.1 analyze_sql_vc (ExaCI — Standby DB측)

`collect_query_info`의 `t_analysis_result` 레코드를 `JSON_OBJECT`로 변환하여 `VARCHAR2`로 반환.
DB Link 함수 호출은 스칼라 타입만 지원하므로 이 래퍼가 필요하다.

```sql
-- 실행 위치: ExaCI (Standby DB)
-- 실행 계정: GENAI
CREATE OR REPLACE FUNCTION analyze_sql_vc(
    p_sql_text    IN VARCHAR2,
    p_schema      IN VARCHAR2 DEFAULT NULL,
    p_plan_format IN VARCHAR2 DEFAULT 'ALLSTATS LAST',
    p_sql_id      IN VARCHAR2 DEFAULT NULL
) RETURN VARCHAR2
AUTHID CURRENT_USER
AS
    v_r query_analyzer_stby.t_analysis_result;
BEGIN
    v_r := query_analyzer_stby.collect_query_info(
        p_sql_text    => p_sql_text,
        p_schema      => p_schema,
        p_plan_format => p_plan_format,
        p_sql_id      => p_sql_id
    );

    RETURN JSON_OBJECT(
        'error_code'     VALUE v_r.error_code,
        'error_message'  VALUE v_r.error_message,
        'table_stats'    VALUE v_r.table_stats FORMAT JSON,
        'index_info'     VALUE v_r.index_info  FORMAT JSON,
        'execution_plan' VALUE DBMS_LOB.SUBSTR(v_r.execution_plan, 20000, 1)
        RETURNING VARCHAR2(32767)
    );

EXCEPTION
    WHEN OTHERS THEN
        RETURN JSON_OBJECT(
            'error_code'     VALUE SQLCODE,
            'error_message'  VALUE SUBSTR(SQLERRM, 1, 1000),
            'table_stats'    VALUE NULL,
            'index_info'     VALUE NULL,
            'execution_plan' VALUE NULL
            RETURNING VARCHAR2(32767)
        );
END analyze_sql_vc;
/
```

> **AUTHID CURRENT_USER 필수**: Definer's Rights로 만들면 DB Link를 통해
> 호출 시 Role 기반 권한이 비활성화되어 V$ 뷰 접근이 실패한다.
> 호출자의 Direct Grant 권한으로 실행되도록 `AUTHID CURRENT_USER` 지정.

### 4.2 analyze_sql_via_dblink (ADB측)

> **전체 코드**: [`create_sql_analyzer_tool.sql`](create_sql_analyzer_tool.sql) Step 1 참조.

DB Link 함수(`@DBLINK_DR`)는 Select AI Agent Tool에 직접 등록할 수 없으므로 로컬 래퍼가 필요하다.
이 래퍼는 `PRAGMA AUTONOMOUS_TRANSACTION`으로 호출마다 분석 요청/결과를 자동 기록한다.

**처리 흐름**:
```
1. ai_analysis_request INSERT (status='PROCESSING')
   ai_analysis_log INSERT (INFO: 분석 요청 접수)
2. analyze_sql_vc@DBLINK_DR 호출
   → 실패 시 ai_analysis_log INSERT (ERROR: DB Link 호출 실패)
3. JSON 결과에서 error_code 추출
   → 0: ai_analysis_request UPDATE (status='DONE', exec_plan, table_stats, index_info)
   → 그 외: ai_analysis_request UPDATE (status='ERROR', error_message)
4. ai_analysis_result INSERT (JSON 결과 전문)
   ai_analysis_log INSERT (INFO/ERROR: 분석 완료/에러)
5. COMMIT (AUTONOMOUS_TRANSACTION이므로 Agent 세션에 영향 없음)
```

**로깅 확인 쿼리**:
```sql
-- 최근 분석 요청 이력
SELECT request_id, status, requested_by,
       SUBSTR(sql_text, 1, 60) AS sql_preview,
       error_message, created_at
FROM ai_analysis_request
ORDER BY created_at DESC
FETCH FIRST 10 ROWS ONLY;

-- 분석 결과 상세
SELECT r.request_id,
       SUBSTR(r.sql_text, 1, 60) AS sql_preview,
       r.status,
       SUBSTR(res.analysis, 1, 200) AS result_preview,
       r.created_at
FROM ai_analysis_request r
JOIN ai_analysis_result res ON r.request_id = res.request_id
ORDER BY r.created_at DESC
FETCH FIRST 10 ROWS ONLY;

-- 처리 로그 조회
SELECT l.log_id, l.request_id, l.log_level, l.message, l.created_at
FROM ai_analysis_log l
ORDER BY l.created_at DESC
FETCH FIRST 20 ROWS ONLY;
```

---

## 5. Select AI Agent 구성

> **전체 스크립트**: [`create_sql_analyzer_tool.sql`](create_sql_analyzer_tool.sql)에
> 래퍼 함수 + Tool + Task + Agent + Team 생성이 모두 포함되어 있습니다.
> 여기서는 각 구성 요소의 역할과 설정 의도를 설명합니다.

### 5.1 AI Profile 생성

```sql
BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'SQL_ANALYSIS_AI',
        attributes   => '{"provider":"oci",
                          "credential_name":"OCI_GENAI_CRED",
                          "model":"xai.grok-4-1-fast-non-reasoning",
                          "region":"us-chicago-1",
                          "temperature":0.2,
                          "max_tokens":4096}'
    );
END;
/
```

- `temperature: 0.2` — 분석 결과의 일관성을 위해 낮게 설정
- `max_tokens: 4096` — 실행계획 해석 + 튜닝 권고를 충분히 담을 수 있는 크기

### 5.2 Tool 등록 (SQL_Analyzer)

`analyze_sql_via_dblink` 함수를 Agent Tool로 등록.

**instruction 핵심 포인트**:
- **A-Rows=0 정상**: DBMS_SQL로 실행만 하고 FETCH하지 않으므로 A-Rows는 항상 0. 이상 징후로 해석하지 말 것
- **테이블 크기 기준**: 10만 건 미만 = 소규모, 10만~1천만 = 중규모, 1천만 이상 = 대규모. 소규모 테이블에 파티셔닝 제안 금지
- **분석 결과 강조 항목**: Full Scan vs Index Scan, 통계 수집일, 미사용 인덱스, Join 방식

### 5.3 Task 생성 (sql_analysis_task)

Agent가 분석 결과를 5개 항목으로 구조화하여 응답하도록 지시:

1. **실행계획 요약** — 주요 오퍼레이션 (Full Scan, Index Scan, Join 방식 등)
2. **성능 포인트** — E-Rows vs A-Rows 차이, Full Table Scan 여부
3. **테이블 통계** — 행 수, 블록 수, 통계 수집일 (오래되었으면 경고)
4. **인덱스 분석** — 사용된/미사용 인덱스, 개선 제안
5. **튜닝 권고** — 구체적인 개선 방안

### 5.4 Agent 생성 (SQL_Analysis_Agent)

- `profile_name`: `SQL_ANALYSIS_AI`
- `role`: Oracle SQL 성능 분석 전문가. SQL_Analyzer Tool 호출 후 결과를 한국어로 해석

### 5.5 Team 생성 (SQL_Analysis_Team)

- Agent 1개의 단일 순차 실행 구조
- 향후 DDL 분석 Agent 등을 추가하여 다중 Agent 구조로 확장 가능

---

## 6. 테스트 및 대화 이력 조회

### 6.1 Team 실행 테스트

> **주의**: `DBMS_CLOUD_AI.CREATE_CONVERSATION()`으로 conversation_id를 먼저 생성해야 함.
> NULL 전달 시 `ORA-01400: cannot insert NULL` 에러 발생.

```sql
-- 테스트 1: 단순 테이블 분석
DECLARE
    v_result  CLOB;
    v_conv_id VARCHAR2(4000);
BEGIN
    v_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION();
    v_result := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
        team_name   => 'SQL_Analysis_Team',
        user_prompt => 'SELECT * FROM ADM.TCODE 쿼리를 분석해줘. 스키마는 ADM이야.',
        params      => '{"conversation_id": "' || v_conv_id || '"}'
    );
    DBMS_OUTPUT.PUT_LINE('conversation_id: ' || v_conv_id);
    DBMS_OUTPUT.PUT_LINE(DBMS_LOB.SUBSTR(v_result, 4000, 1));
END;
/

-- 테스트 2: WHERE 조건 포함 SQL 분석
DECLARE
    v_result  CLOB;
    v_conv_id VARCHAR2(4000);
BEGIN
    v_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION();
    v_result := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
        team_name   => 'SQL_Analysis_Team',
        user_prompt => 'SELECT * FROM ADM.TCODE WHERE LGRP_CD = ''SYS'' 이 쿼리가 느린데 분석해줘. 스키마는 ADM.',
        params      => '{"conversation_id": "' || v_conv_id || '"}'
    );
    DBMS_OUTPUT.PUT_LINE('conversation_id: ' || v_conv_id);
    DBMS_OUTPUT.PUT_LINE(DBMS_LOB.SUBSTR(v_result, 4000, 1));
END;
/
```

### 6.2 대화 이력 조회

```sql
-- 최근 대화 목록
SELECT
    c.CONVERSATION_TITLE,
    p.CONVERSATION_PROMPT_ID,
    p.PROMPT,
    SUBSTR(p.PROMPT_RESPONSE, 1, 100) AS RESPONSE_PREVIEW,
    p.CREATED
FROM USER_CLOUD_AI_CONVERSATIONS c
JOIN USER_CLOUD_AI_CONVERSATION_PROMPTS p
    ON c.CONVERSATION_ID = p.CONVERSATION_ID
ORDER BY p.CREATED DESC
FETCH FIRST 10 ROWS ONLY;
```

```sql
-- 상세 프롬프트 이력
SELECT
    CONVERSATION_PROMPT_ID,
    CONVERSATION_ID,
    CONVERSATION_TITLE,
    PROFILE_NAME,
    PROMPT_ACTION,
    PROMPT,
    PROMPT_RESPONSE,
    CREATED,
    CLIENT_IP,
    SID,
    SERIAL#
FROM USER_CLOUD_AI_CONVERSATION_PROMPTS
ORDER BY CREATED DESC
FETCH FIRST 10 ROWS ONLY;
```

### 6.3 Agent 구성 요소 확인

```sql
-- Tool 확인
SELECT tool_name, description FROM user_cloud_ai_tools;

-- Agent 확인
SELECT agent_name FROM user_cloud_ai_agents;

-- Team 확인
SELECT team_name FROM user_cloud_ai_teams;

-- Profile 확인
SELECT profile_name, status, created FROM user_cloud_ai_profiles;
```
