/*******************************************************************************
 * Procedure: SYNC_DICT_FROM_EXADR
 *
 * 목적:
 *   ExaCC(원본 DB)의 데이터 딕셔너리를 DB Link를 통해 동기화하고,
 *   변경분에 대한 벡터 임베딩을 자동 생성하는 통합 프로시저.
 *   DBMS_SCHEDULER 잡으로 등록하여 주기적 실행 가능.
 *
 * 처리 흐름:
 *   ┌──────────────────────────────────────────────────────────┐
 *   │ Phase 1: dict_tables MERGE (all_tables@DBLINK_DR)       │
 *   │   → 신규 테이블 INSERT, 변경 테이블 is_changed='Y'      │
 *   ├──────────────────────────────────────────────────────────┤
 *   │ Phase 2: dict_columns MERGE (all_tab_columns@DBLINK_DR) │
 *   │   → 신규 컬럼 INSERT, 변경 컬럼 is_changed='Y'          │
 *   │   → 컬럼 변경 시 소속 테이블도 is_changed='Y'로 갱신    │
 *   ├──────────────────────────────────────────────────────────┤
 *   │ Phase 3: doc_text 생성 (is_changed='Y' 테이블만)        │
 *   │   → 4000자 초과 시 파트 분할                             │
 *   ├──────────────────────────────────────────────────────────┤
 *   │ Phase 4: 벡터 임베딩 (PENDING → DONE/ERROR)             │
 *   │   → OCI GenAI cohere.embed-v4.0                         │
 *   ├──────────────────────────────────────────────────────────┤
 *   │ Phase 5: is_changed 플래그 초기화                        │
 *   └──────────────────────────────────────────────────────────┘
 *
 * 파라미터:
 *   p_owner_list  : 동기화 대상 스키마 (콤마 구분, 기본값 'ADM')
 *   p_db_link     : DB Link 이름 (기본값 'DBLINK_DR')
 *   p_embed_batch : 임베딩 커밋 단위 (기본값 50)
 *
 * 사전 요구사항:
 *   - DB Link (DBLINK_DR) 생성 완료
 *   - GENAI_VECTOR_CRED Credential 생성 완료
 *   - dict_tables, dict_columns, dict_embeddings 테이블 생성 완료
 *
 * DBMS_SCHEDULER 등록 예시:
 *   -- 매일 새벽 2시 실행
 *   BEGIN
 *       DBMS_SCHEDULER.CREATE_JOB(
 *           job_name        => 'JOB_SYNC_DICT',
 *           job_type        => 'PLSQL_BLOCK',
 *           job_action      => 'BEGIN sync_dict_from_exadr; END;',
 *           start_date      => TRUNC(SYSDATE+1) + 2/24,
 *           repeat_interval => 'FREQ=DAILY; BYHOUR=2; BYMINUTE=0; BYSECOND=0',
 *           enabled         => TRUE,
 *           comments        => '데이터 딕셔너리 동기화 + 벡터 임베딩 갱신'
 *       );
 *   END;
 *
 *   -- 매주 월요일 새벽 3시 실행
 *   BEGIN
 *       DBMS_SCHEDULER.CREATE_JOB(
 *           job_name        => 'JOB_SYNC_DICT_WEEKLY',
 *           job_type        => 'PLSQL_BLOCK',
 *           job_action      => 'BEGIN sync_dict_from_exadr(p_owner_list => ''ADM,HR''); END;',
 *           start_date      => NEXT_DAY(TRUNC(SYSDATE), 'MONDAY') + 3/24,
 *           repeat_interval => 'FREQ=WEEKLY; BYDAY=MON; BYHOUR=3',
 *           enabled         => TRUE,
 *           comments        => '주간 딕셔너리 동기화 (ADM, HR 스키마)'
 *       );
 *   END;
 *
 *   -- 잡 확인
 *   SELECT job_name, state, last_start_date, next_run_date
 *   FROM user_scheduler_jobs WHERE job_name LIKE 'JOB_SYNC%';
 *
 *   -- 실행 이력 확인
 *   SELECT job_name, status, actual_start_date, run_duration, additional_info
 *   FROM user_scheduler_job_run_details
 *   WHERE job_name LIKE 'JOB_SYNC%'
 *   ORDER BY actual_start_date DESC FETCH FIRST 10 ROWS ONLY;
 *
 * 작성일: 2026-03-18
 ******************************************************************************/

CREATE OR REPLACE PROCEDURE sync_dict_from_exadr(
    p_owner_list  IN VARCHAR2 DEFAULT 'ADM',
    p_db_link     IN VARCHAR2 DEFAULT 'DBLINK_DR',
    p_embed_batch IN NUMBER   DEFAULT 20
)
AS
    -- 임베딩 설정
    c_credential CONSTANT VARCHAR2(100) := 'GENAI_VECTOR_CRED';
    c_model      CONSTANT VARCHAR2(100) := 'cohere.embed-v4.0';
    c_url        CONSTANT VARCHAR2(500) :=
        'https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/embedText';
    c_max_len    CONSTANT NUMBER := 4000;

    v_params        CLOB;
    v_sql           CLOB;
    v_tbl_cnt       NUMBER := 0;
    v_col_cnt       NUMBER := 0;
    v_embed_ok      NUMBER := 0;
    v_embed_err     NUMBER := 0;
    v_changed_cnt   NUMBER := 0;

    -- doc_text 생성용 변수
    v_header        CLOB;
    v_chunk         CLOB;
    v_header_len    NUMBER;
    v_all_len       NUMBER;
    v_col_count     NUMBER;
    v_total_parts   NUMBER;
    v_per_part      NUMBER;
    v_part          NUMBER;
    v_idx           NUMBER;

    TYPE t_col_arr IS TABLE OF CLOB INDEX BY PLS_INTEGER;
    v_cols          t_col_arr;

    v_in_clause     VARCHAR2(4000);

    -- owner IN 절 생성 헬퍼
    FUNCTION make_in_clause(p_list VARCHAR2) RETURN VARCHAR2 IS
        v_result VARCHAR2(4000) := '';
        v_item   VARCHAR2(128);
        v_pos    NUMBER := 1;
        v_len    NUMBER := LENGTH(p_list);
        v_start  NUMBER := 1;
    BEGIN
        FOR i IN 1..v_len + 1 LOOP
            IF i > v_len OR SUBSTR(p_list, i, 1) = ',' THEN
                v_item := TRIM(SUBSTR(p_list, v_start, i - v_start));
                IF v_item IS NOT NULL THEN
                    IF v_result IS NOT NULL THEN
                        v_result := v_result || ',';
                    END IF;
                    v_result := v_result || '''' || UPPER(v_item) || '''';
                END IF;
                v_start := i + 1;
            END IF;
        END LOOP;
        RETURN v_result;
    END;

BEGIN
    v_in_clause := make_in_clause(p_owner_list);
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('동기화 시작: ' || TO_CHAR(SYSTIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'));
    DBMS_OUTPUT.PUT_LINE('대상 스키마: ' || p_owner_list);
    DBMS_OUTPUT.PUT_LINE('DB Link: ' || p_db_link);
    DBMS_OUTPUT.PUT_LINE('========================================');

    ---------------------------------------------------------------------------
    -- Phase 1: dict_tables MERGE
    ---------------------------------------------------------------------------
    v_sql := '
    MERGE INTO dict_tables tgt
    USING (
        SELECT t.owner, t.table_name, tc.comments, t.num_rows
        FROM all_tables@' || p_db_link || ' t
        LEFT JOIN all_tab_comments@' || p_db_link || ' tc
            ON tc.owner = t.owner AND tc.table_name = t.table_name
        WHERE t.owner IN (' || v_in_clause || ')
    ) src
    ON (tgt.owner = src.owner AND tgt.table_name = src.table_name)
    WHEN MATCHED THEN
        UPDATE SET tgt.comments   = src.comments,
                   tgt.num_rows   = src.num_rows,
                   tgt.is_changed = CASE WHEN NVL(tgt.comments, ''~'') != NVL(src.comments, ''~'')
                                         OR NVL(tgt.num_rows, -1) != NVL(src.num_rows, -1)
                                         THEN ''Y'' ELSE tgt.is_changed END,
                   tgt.updated_at = SYSTIMESTAMP
    WHEN NOT MATCHED THEN
        INSERT (owner, table_name, comments, num_rows, is_changed)
        VALUES (src.owner, src.table_name, src.comments, src.num_rows, ''Y'')';

    EXECUTE IMMEDIATE v_sql;
    v_tbl_cnt := SQL%ROWCOUNT;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('[Phase 1] dict_tables MERGE: ' || v_tbl_cnt || '건');

    ---------------------------------------------------------------------------
    -- Phase 2: dict_columns MERGE
    ---------------------------------------------------------------------------
    v_sql := '
    MERGE INTO dict_columns tgt
    USING (
        SELECT t.table_id,
               c.owner, c.table_name, c.column_name, c.column_id,
               c.data_type, c.data_length, c.data_precision, c.data_scale, c.nullable,
               cc.comments
        FROM all_tab_columns@' || p_db_link || ' c
        JOIN dict_tables t
            ON t.owner = c.owner AND t.table_name = c.table_name
        LEFT JOIN all_col_comments@' || p_db_link || ' cc
            ON cc.owner = c.owner
           AND cc.table_name = c.table_name
           AND cc.column_name = c.column_name
        WHERE c.owner IN (' || v_in_clause || ')
    ) src
    ON (tgt.owner = src.owner AND tgt.table_name = src.table_name
        AND tgt.column_name = src.column_name)
    WHEN MATCHED THEN
        UPDATE SET tgt.table_id       = src.table_id,
                   tgt.column_id      = src.column_id,
                   tgt.data_type      = src.data_type,
                   tgt.data_length    = src.data_length,
                   tgt.data_precision = src.data_precision,
                   tgt.data_scale     = src.data_scale,
                   tgt.nullable       = src.nullable,
                   tgt.comments       = src.comments,
                   tgt.is_changed     = CASE
                                            WHEN NVL(tgt.comments,  ''~'') != NVL(src.comments,  ''~'')
                                              OR NVL(tgt.data_type,  ''~'') != NVL(src.data_type,  ''~'')
                                              OR NVL(tgt.nullable,   ''~'') != NVL(src.nullable,   ''~'')
                                            THEN ''Y'' ELSE tgt.is_changed
                                        END,
                   tgt.updated_at     = SYSTIMESTAMP
    WHEN NOT MATCHED THEN
        INSERT (table_id, owner, table_name, column_name, column_id,
                data_type, data_length, data_precision, data_scale,
                nullable, comments, is_changed)
        VALUES (src.table_id, src.owner, src.table_name, src.column_name, src.column_id,
                src.data_type, src.data_length, src.data_precision, src.data_scale,
                src.nullable, src.comments, ''Y'')';

    EXECUTE IMMEDIATE v_sql;
    v_col_cnt := SQL%ROWCOUNT;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('[Phase 2] dict_columns MERGE: ' || v_col_cnt || '건');

    -- 컬럼이 변경된 테이블도 is_changed='Y'로 마킹
    UPDATE dict_tables t
    SET    t.is_changed = 'Y', t.updated_at = SYSTIMESTAMP
    WHERE  t.is_changed = 'N'
    AND    EXISTS (
        SELECT 1 FROM dict_columns c
        WHERE c.table_id = t.table_id AND c.is_changed = 'Y'
    );
    COMMIT;

    -- 변경 대상 수 확인
    SELECT COUNT(*) INTO v_changed_cnt FROM dict_tables WHERE is_changed = 'Y';
    DBMS_OUTPUT.PUT_LINE('[Phase 2] 임베딩 갱신 대상: ' || v_changed_cnt || '건');

    IF v_changed_cnt = 0 THEN
        DBMS_OUTPUT.PUT_LINE('변경 없음 — 임베딩 갱신 생략');
        DBMS_OUTPUT.PUT_LINE('동기화 완료: ' || TO_CHAR(SYSTIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'));
        RETURN;
    END IF;

    ---------------------------------------------------------------------------
    -- Phase 3: doc_text 생성 (is_changed='Y'인 테이블만)
    ---------------------------------------------------------------------------
    FOR t IN (
        SELECT table_id, owner, table_name, comments, num_rows
        FROM dict_tables
        WHERE is_changed = 'Y'
    ) LOOP
        -- 테이블 헤더 JSON
        v_header := '{"owner":"' || t.owner || '","tableName":"' || t.table_name || '"'
                 || CASE WHEN t.comments IS NOT NULL
                         THEN ',"comments":"' || REPLACE(t.comments, '"', '\"') || '"'
                         ELSE '' END
                 || CASE WHEN t.num_rows IS NOT NULL
                         THEN ',"numRows":' || t.num_rows
                         ELSE '' END
                 || ',"columns":[';
        v_header_len := LENGTH(v_header) + 2;

        -- 컬럼 JSON 조각 수집
        v_col_count := 0;
        v_cols.DELETE;
        v_all_len := 0;
        FOR c IN (
            SELECT column_name, column_id, data_type, data_length, nullable, comments
            FROM dict_columns
            WHERE table_id = t.table_id
            ORDER BY column_id
        ) LOOP
            v_col_count := v_col_count + 1;
            v_cols(v_col_count) :=
                '{"col":"' || c.column_name
                || '","type":"' || c.data_type
                || CASE WHEN c.data_length IS NOT NULL THEN '(' || c.data_length || ')' ELSE '' END
                || '"'
                || CASE WHEN c.nullable = 'N' THEN ',"notNull":true' ELSE '' END
                || CASE WHEN c.comments IS NOT NULL
                        THEN ',"desc":"' || REPLACE(REPLACE(c.comments, '"', '\"'), CHR(10), ' ') || '"'
                        ELSE '' END
                || '}';
            v_all_len := v_all_len + LENGTH(v_cols(v_col_count)) + 1;
        END LOOP;

        -- 기존 임베딩 삭제
        DELETE FROM dict_embeddings WHERE table_id = t.table_id;

        -- 단일/분할 파트 생성
        IF v_col_count = 0 OR (v_header_len + v_all_len) <= c_max_len THEN
            v_chunk := v_header;
            FOR i IN 1..v_col_count LOOP
                v_chunk := v_chunk || CASE WHEN i > 1 THEN ',' END || v_cols(i);
            END LOOP;
            v_chunk := v_chunk || ']}';
            INSERT INTO dict_embeddings (table_id, part_no, total_parts, doc_text)
            VALUES (t.table_id, 1, 1, v_chunk);
        ELSE
            v_total_parts := CEIL(v_all_len / (c_max_len - v_header_len - 20));
            v_per_part := CEIL(v_col_count / v_total_parts);
            v_part := 0;
            v_idx := 1;
            WHILE v_idx <= v_col_count LOOP
                v_part := v_part + 1;
                v_chunk := v_header;
                FOR i IN v_idx..LEAST(v_idx + v_per_part - 1, v_col_count) LOOP
                    v_chunk := v_chunk || CASE WHEN i > v_idx THEN ',' END || v_cols(i);
                END LOOP;
                v_chunk := v_chunk || ']}';
                INSERT INTO dict_embeddings (table_id, part_no, total_parts, doc_text)
                VALUES (t.table_id, v_part, v_total_parts, v_chunk);
                v_idx := v_idx + v_per_part;
            END LOOP;
        END IF;
    END LOOP;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('[Phase 3] doc_text 생성 완료');

    ---------------------------------------------------------------------------
    -- Phase 4: 벡터 임베딩
    ---------------------------------------------------------------------------
    v_params := '{"provider":"ocigenai","credential_name":"' || c_credential
             || '","url":"' || c_url || '","model":"' || c_model || '"}';

    FOR rec IN (
        SELECT ROWID AS rid, table_id, part_no, doc_text
        FROM dict_embeddings
        WHERE embed_status = 'PENDING' AND doc_text IS NOT NULL
    ) LOOP
        BEGIN
            UPDATE dict_embeddings
            SET doc_vector   = DBMS_VECTOR.UTL_TO_EMBEDDING(rec.doc_text, JSON(v_params)),
                embed_status = 'DONE',
                updated_at   = SYSTIMESTAMP
            WHERE ROWID = rec.rid;

            v_embed_ok := v_embed_ok + 1;
            IF MOD(v_embed_ok, p_embed_batch) = 0 THEN
                COMMIT;
            END IF;
        EXCEPTION WHEN OTHERS THEN
            UPDATE dict_embeddings
            SET embed_status = 'ERROR', updated_at = SYSTIMESTAMP
            WHERE ROWID = rec.rid;
            v_embed_err := v_embed_err + 1;
            DBMS_OUTPUT.PUT_LINE('  ERROR [table_id=' || rec.table_id
                || ' P' || rec.part_no || ']: ' || SQLERRM);
        END;
    END LOOP;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('[Phase 4] 임베딩 완료: 성공=' || v_embed_ok || ', 실패=' || v_embed_err);

    ---------------------------------------------------------------------------
    -- Phase 5: is_changed 플래그 초기화
    ---------------------------------------------------------------------------
    UPDATE dict_tables SET is_changed = 'N', updated_at = SYSTIMESTAMP
    WHERE is_changed = 'Y';

    UPDATE dict_columns SET is_changed = 'N', updated_at = SYSTIMESTAMP
    WHERE is_changed = 'Y';

    COMMIT;

    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('동기화 완료: ' || TO_CHAR(SYSTIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'));
    DBMS_OUTPUT.PUT_LINE('  테이블 MERGE: ' || v_tbl_cnt || '건');
    DBMS_OUTPUT.PUT_LINE('  컬럼 MERGE: ' || v_col_cnt || '건');
    DBMS_OUTPUT.PUT_LINE('  임베딩 갱신: ' || v_changed_cnt || '건 (성공=' || v_embed_ok || ', 실패=' || v_embed_err || ')');
    DBMS_OUTPUT.PUT_LINE('========================================');

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('동기화 실패: ' || SQLERRM);
        RAISE;
END;
/
