/*******************************************************************************
 * Select AI Agent Tool: SQL Analyzer
 *
 * 목적:
 *   DB Link를 통해 원본 DB의 query_analyzer_stby 패키지를 호출하여
 *   SQL 실행계획, 테이블 통계, 인덱스 정보를 분석하는 Agent Tool.
 *
 * 사전 요구사항:
 *   1. 원본 DB에 query_analyzer_stby 패키지 및 analyze_sql_vc 래퍼 함수 생성 완료
 *   2. DB Link (DBLINK_DR) 생성 완료
 *   3. DB Link를 통한 analyze_sql_vc 호출 테스트 완료
 *   4. DBMS_CLOUD_AI_AGENT 실행 권한
 *
 * 실행 순서:
 *   Step 1: 래퍼 함수 생성 (analyze_sql_via_dblink)
 *           ※ DB Link 함수(@DBLINK)는 Tool에 직접 등록 불가 → 래퍼 필수
 *   Step 2: Tool 등록 (SQL_Analyzer)
 *   Step 3: Task 생성 (sql_analysis_task)
 *   Step 4: Agent/Team 구성
 *   Step 5: 테스트
 ******************************************************************************/

-- =============================================================================
-- Step 1: 래퍼 함수 생성
-- 설명: DB Link 함수(@DBLINK)는 Agent Tool에 직접 등록 불가 → 로컬 래퍼 필수
--       호출 시 ai_analysis_request/result 테이블에 자동 기록 (AUTONOMOUS_TRANSACTION)
-- 실행 계정: GENAI (또는 Agent Tool 소유 스키마)
--
-- 사전 요구사항: ai_analysis_request, ai_analysis_result, ai_analysis_log 테이블 생성 완료
--               (query_analysis.md 섹션 2 참조)
-- =============================================================================

CREATE OR REPLACE FUNCTION analyze_sql_via_dblink(
    p_sql_text IN VARCHAR2,
    p_schema   IN VARCHAR2 DEFAULT NULL
) RETURN VARCHAR2
AS
    PRAGMA AUTONOMOUS_TRANSACTION;

    v_result     VARCHAR2(32767);
    v_request_id NUMBER;
    v_error_code NUMBER;
BEGIN
    ---------------------------------------------------------------------------
    -- 1. 요청 기록
    ---------------------------------------------------------------------------
    INSERT INTO ai_analysis_request (
        sql_text, status, requested_by, source_db, created_at, updated_at
    ) VALUES (
        p_sql_text, 'PROCESSING',
        SYS_CONTEXT('USERENV', 'SESSION_USER'),
        'DBLINK_DR',
        SYSTIMESTAMP, SYSTIMESTAMP
    ) RETURNING request_id INTO v_request_id;

    INSERT INTO ai_analysis_log (request_id, log_level, message)
    VALUES (v_request_id, 'INFO', '분석 요청 접수: schema=' || NVL(p_schema, '(current)'));

    ---------------------------------------------------------------------------
    -- 2. DB Link 호출
    ---------------------------------------------------------------------------
    BEGIN
        v_result := analyze_sql_vc@DBLINK_DR(
            p_sql_text => p_sql_text,
            p_schema   => p_schema
        );
    EXCEPTION
        WHEN OTHERS THEN
            v_result := '{"error_code":-99999,"error_message":"DB Link call failed: '
                        || REPLACE(SQLERRM, '"', '\"')
                        || '","table_stats":null,"index_info":null,"execution_plan":null}';
            INSERT INTO ai_analysis_log (request_id, log_level, message)
            VALUES (v_request_id, 'ERROR', 'DB Link 호출 실패: ' || SUBSTR(SQLERRM, 1, 3800));
    END;

    ---------------------------------------------------------------------------
    -- 3. 결과 저장
    ---------------------------------------------------------------------------
    v_error_code := JSON_VALUE(v_result, '$.error_code' RETURNING NUMBER);

    UPDATE ai_analysis_request
    SET status        = CASE WHEN NVL(v_error_code, -1) = 0 THEN 'DONE' ELSE 'ERROR' END,
        exec_plan     = JSON_VALUE(v_result, '$.execution_plan'),
        table_stats   = JSON_QUERY(v_result, '$.table_stats'),
        index_info    = JSON_QUERY(v_result, '$.index_info'),
        error_message = CASE WHEN NVL(v_error_code, -1) != 0
                             THEN JSON_VALUE(v_result, '$.error_message')
                        END,
        updated_at    = SYSTIMESTAMP
    WHERE request_id = v_request_id;

    INSERT INTO ai_analysis_result (request_id, analysis)
    VALUES (v_request_id, v_result);

    INSERT INTO ai_analysis_log (request_id, log_level, message)
    VALUES (v_request_id,
            CASE WHEN NVL(v_error_code, -1) = 0 THEN 'INFO' ELSE 'ERROR' END,
            CASE WHEN NVL(v_error_code, -1) = 0
                 THEN '분석 완료 (error_code=0)'
                 ELSE '분석 에러: ' || JSON_VALUE(v_result, '$.error_message')
            END);

    COMMIT;

    RETURN v_result;

EXCEPTION
    WHEN OTHERS THEN
        -- 로깅 실패해도 결과는 반환
        ROLLBACK;
        RETURN NVL(v_result,
            '{"error_code":-99999,"error_message":"DB Link call failed: '
            || REPLACE(SQLERRM, '"', '\"')
            || '","table_stats":null,"index_info":null,"execution_plan":null}');
END;
/

-- =============================================================================
-- Step 2: Agent Tool 등록
-- 설명: AI Agent가 SQL 분석 요청 시 호출할 Tool
-- 실행 계정: NORTHWIND
-- =============================================================================

BEGIN
    DBMS_CLOUD_AI_AGENT.DROP_TOOL('SQL_Analyzer');
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

BEGIN
    DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
        tool_name   => 'SQL_Analyzer',
        attributes  => '{
            "instruction": "Use this tool to analyze SQL query performance. It returns the execution plan, table statistics (num_rows, blocks, last_analyzed), and index information (columns, uniqueness, type, leaf_blocks, distinct_keys). Pass the SQL text as p_sql_text and the schema name as p_schema. The result is JSON with fields: error_code (0=success), execution_plan, table_stats, index_info. IMPORTANT NOTES: 1) A-Rows=0 is NORMAL — the tool executes SQL via DBMS_SQL without fetching rows, so A-Rows always shows 0. Do NOT interpret this as an anomaly. 2) When assessing table size, use realistic scale: under 100K rows is small, 100K-10M is medium, over 10M is large. Do not suggest partitioning for small tables. When presenting results, highlight: 1) full scan vs index scan, 2) stale statistics (last_analyzed date), 3) missing or unused indexes, 4) join method efficiency for multi-table queries.",
            "function": "analyze_sql_via_dblink"
        }',
        description => 'Analyzes SQL performance: execution plan, table stats, and index info via Standby DB. Use when asked about query tuning, slow SQL, or execution plans.'
    );
END;
/

-- =============================================================================
-- Step 3: Task 생성
-- 설명: SQL 분석 요청을 처리하는 Task
-- 실행 계정: NORTHWIND
-- =============================================================================

BEGIN
    DBMS_CLOUD_AI_AGENT.DROP_TASK('sql_analysis_task');
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

BEGIN
    DBMS_CLOUD_AI_AGENT.CREATE_TASK(
        task_name   => 'sql_analysis_task',
        attributes  => '{
            "instruction": "사용자의 SQL 성능 분석 요청을 처리합니다. 사용자가 SQL 텍스트와 스키마를 제공하면 SQL_Analyzer tool을 호출하여 분석하고, 결과를 다음 형식으로 정리하여 답변하세요:\n\n1. **실행계획 요약**: 주요 오퍼레이션(Full Scan, Index Scan, Join 방식 등)\n2. **성능 포인트**: E-Rows vs A-Rows 차이, Full Table Scan 여부\n3. **테이블 통계**: 행 수, 블록 수, 통계 수집일(오래되었으면 경고)\n4. **인덱스 분석**: 사용된/미사용 인덱스, 개선 제안\n5. **튜닝 권고**: 구체적인 개선 방안\n\n사용자 요청: {query}",
            "tools": ["SQL_Analyzer"]
        }'
    );
END;
/

-- =============================================================================
-- Step 4: Agent 및 Team 구성
-- 설명: SQL 분석 전담 Agent와 Team 생성
-- 실행 계정: NORTHWIND
--
-- ※ 기존 팀에 추가하려면 이 Step을 건너뛰고
--   기존 CREATE_TEAM의 agents 배열에 추가하세요.
-- =============================================================================

BEGIN
    DBMS_CLOUD_AI_AGENT.DROP_AGENT('SQL_Analysis_Agent');
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

BEGIN
    DBMS_CLOUD_AI_AGENT.CREATE_AGENT(
        agent_name  => 'SQL_Analysis_Agent',
        attributes  => '{
            "profile_name": "SQL_ANALYSIS_AI",
            "role": "You are an Oracle SQL performance analyst. When analyzing SQL, always call the SQL_Analyzer tool first, then interpret the results for the user in Korean. Focus on actionable tuning recommendations."
        }'
    );
END;
/

BEGIN
    DBMS_CLOUD_AI_AGENT.DROP_TEAM(team_name => 'SQL_Analysis_Team', force => TRUE);
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

BEGIN
    DBMS_CLOUD_AI_AGENT.CREATE_TEAM(
        team_name   => 'SQL_Analysis_Team',
        attributes  => '{
            "agents": [
                {"name": "SQL_Analysis_Agent", "task": "sql_analysis_task"}
            ],
            "process": "sequential"
        }'
    );
END;
/

-- =============================================================================
-- Step 5: 테스트
-- =============================================================================

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

-- 테스트 2: 특정 SQL 튜닝 요청
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
