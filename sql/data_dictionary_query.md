# Data Dictionary Vector Search — Select AI Agent 구축 가이드

## 아키텍처

```
ExaCC (송도, Primary)
    ↓  Active Data Guard (동기 복제)
ExaCI (OCI Seoul, Standby)
    ↓  DB Link (DBLINK_DR)
Autonomous AI Lakehouse (OCI Seoul)
    └── genai 스키마: dict_tables / dict_columns / dict_embeddings
        └── Select AI Agent → 벡터 유사도 검색으로 테이블/컬럼 탐색
```

**목적**: ExaCC 원본 DB의 데이터 딕셔너리(테이블/컬럼 메타데이터)를 ADB에 동기화하고,
벡터 임베딩을 생성하여 자연어로 "고객 주문 정보가 어느 테이블에 있어?" 같은 질문에 답하는 Agent 구축.

**데이터 흐름**:
```
[ExaCC] all_tables/all_tab_columns
    → DB Link MERGE → [ADB] dict_tables / dict_columns
    → JSON 변환 → [ADB] dict_embeddings.doc_text
    → OCI GenAI Embedding → [ADB] dict_embeddings.doc_vector
    → VECTOR_DISTANCE 유사도 검색 → Select AI Agent 응답
```

---

## 목차

1. [사전 준비](#1-사전-준비)
2. [Credential 및 AI Profile 생성](#2-credential-및-ai-profile-생성)
3. [딕셔너리 저장 테이블 생성](#3-딕셔너리-저장-테이블-생성)
4. [딕셔너리 동기화 프로시저](#4-딕셔너리-동기화-프로시저)
5. [JSON Duality View 생성](#5-json-duality-view-생성)
6. [임베딩 생성](#6-임베딩-생성)
7. [벡터 검색 함수 생성](#7-벡터-검색-함수-생성)
8. [Select AI Agent 구성 (Tool → Task → Agent → Team)](#8-select-ai-agent-구성)
9. [테스트 및 대화 이력 조회](#9-테스트-및-대화-이력-조회)

---

## 1. 사전 준비

**사용 계정**: `GENAI`

### 1.1 DB Link 확인

```sql
SELECT db_link, username, host FROM user_db_links;
```

> 결과에 `DBLINK_DR`이 있어야 합니다. 없으면 ADMIN에게 DB Link 생성 요청.

### 1.2 Credential 확인

```sql
SELECT credential_name, username FROM user_credentials;
```

| Credential | 용도 |
|-----------|------|
| `OCI_GENAI_CRED` | AI Profile용 (LLM 호출 — text generation) |
| `GENAI_VECTOR_CRED` | Vector Embedding용 (DBMS_VECTOR 패키지) |

---

## 2. Credential 및 AI Profile 생성

### 2.1 Vector Embedding Credential 생성

> `DBMS_VECTOR.CREATE_CREDENTIAL`을 사용합니다 (DBMS_CLOUD와는 별도).

```sql
DECLARE
    jo json_object_t;
BEGIN
    jo := json_object_t();
    jo.put('user_ocid',       'your-user-ocid');         -- OCI 사용자 OCID
    jo.put('tenancy_ocid',    'your-tenancy-ocid');      -- OCI 테넌시 OCID
    jo.put('compartment_ocid','your-compartment-ocid');  -- OCI 구획 OCID
    jo.put('fingerprint',     'your-api-key-fingerprint');
    jo.put('private_key',     '-----BEGIN PRIVATE KEY-----
... (API Key 개인 키) ...
-----END PRIVATE KEY-----');

    DBMS_VECTOR.CREATE_CREDENTIAL(
        credential_name => 'GENAI_VECTOR_CRED',
        params          => JSON(jo.to_string)
    );
END;
/
```

### 2.2 Vector Embedding 테스트

```sql
SELECT DBMS_VECTOR.UTL_TO_EMBEDDING(
    '테스트 문장입니다',
    JSON('{
        "provider": "ocigenai",
        "credential_name": "GENAI_VECTOR_CRED",
        "url": "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/embedText",
        "model": "cohere.embed-v4.0"
    }')
) FROM DUAL;
```

> 벡터 값(숫자 배열)이 반환되면 성공.

### 2.3 AI Profile 생성 (LLM 호출용)

```sql
BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'DICT_SEARCH_PROFILE',
        attributes   => '{"provider": "oci",
                          "credential_name": "OCI_GENAI_CRED",
                          "model": "xai.grok-4-1-fast-non-reasoning",
                          "region": "us-chicago-1",
                          "temperature": 0.2,
                          "max_tokens": 4096}'
    );
END;
/
```

**확인**:
```sql
SELECT profile_name, status, created FROM user_cloud_ai_profiles;
```

---

## 3. 딕셔너리 저장 테이블 생성

원본 DB의 데이터 딕셔너리를 로컬에 캐싱하는 3개 테이블과 벡터 인덱스를 생성합니다.

```
dict_tables  ← 테이블 메타데이터 (owner, table_name, comments, num_rows)
    │ 1:N (table_id FK)
dict_columns ← 컬럼 메타데이터 (column_name, data_type, nullable, comments)
    │
dict_embeddings ← 임베딩 (doc_text → doc_vector, 테이블당 1~N파트)
```

### 3.1 dict_tables (테이블 메타데이터)

```sql
CREATE SEQUENCE seq_dict_tables START WITH 1;

CREATE TABLE dict_tables (
    table_id       NUMBER DEFAULT seq_dict_tables.NEXTVAL NOT NULL,
    owner          VARCHAR2(128) NOT NULL,
    table_name     VARCHAR2(128) NOT NULL,
    comments       VARCHAR2(4000),
    num_rows       NUMBER,
    is_changed     VARCHAR2(1) DEFAULT 'Y',   -- 변경 감지 플래그 (Y=재임베딩 필요)
    created_at     TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at     TIMESTAMP,
    CONSTRAINT pk_dict_tables PRIMARY KEY (table_id),
    CONSTRAINT uk_dict_tables UNIQUE (owner, table_name)
);
```

### 3.2 dict_columns (컬럼 메타데이터)

```sql
CREATE SEQUENCE seq_dict_columns START WITH 1;

CREATE TABLE dict_columns (
    column_seq     NUMBER DEFAULT seq_dict_columns.NEXTVAL NOT NULL,
    table_id       NUMBER NOT NULL,
    owner          VARCHAR2(128) NOT NULL,
    table_name     VARCHAR2(128) NOT NULL,
    column_name    VARCHAR2(128) NOT NULL,
    column_id      NUMBER,
    data_type      VARCHAR2(128),
    data_length    NUMBER,
    data_precision NUMBER,
    data_scale     NUMBER,
    nullable       VARCHAR2(1),
    comments       VARCHAR2(4000),
    is_changed     VARCHAR2(1) DEFAULT 'Y',
    created_at     TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at     TIMESTAMP,
    CONSTRAINT pk_dict_columns PRIMARY KEY (column_seq),
    CONSTRAINT uk_dict_columns UNIQUE (owner, table_name, column_name),
    CONSTRAINT fk_dict_columns FOREIGN KEY (table_id) REFERENCES dict_tables (table_id)
);

ALTER TABLE dict_columns ADD CONSTRAINT fk_dict_columns_tables
    FOREIGN KEY (owner, table_name) REFERENCES dict_tables (owner, table_name);
```

### 3.3 dict_embeddings (벡터 임베딩)

```sql
CREATE TABLE dict_embeddings (
    table_id       NUMBER NOT NULL,
    part_no        NUMBER DEFAULT 1,          -- 컬럼이 많은 테이블은 여러 파트로 분할
    total_parts    NUMBER DEFAULT 1,
    doc_text       CLOB,                      -- 임베딩 입력 JSON 텍스트
    doc_vector     VECTOR,                    -- 임베딩 벡터
    embed_status   VARCHAR2(10) DEFAULT 'PENDING',  -- PENDING → DONE / ERROR
    created_at     TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at     TIMESTAMP,
    CONSTRAINT pk_dict_embeddings PRIMARY KEY (table_id, part_no),
    CONSTRAINT fk_dict_embeddings FOREIGN KEY (table_id) REFERENCES dict_tables (table_id)
);
```

### 3.4 벡터 인덱스

```sql
-- HNSW 알고리즘 (메모리 최적화, 코사인 유사도)
CREATE VECTOR INDEX idx_dict_embed_vec ON dict_embeddings (doc_vector)
    ORGANIZATION NEIGHBOR PARTITIONS
    DISTANCE COSINE
    WITH TARGET ACCURACY 95;
```

---

## 4. 딕셔너리 동기화 프로시저

DB Link를 통해 원본 DB(ExaCC)의 `all_tables`, `all_tab_columns`, `all_tab_comments`, `all_col_comments`를
로컬 `dict_tables`, `dict_columns`에 MERGE합니다.

> 변경이 감지되면 `is_changed = 'Y'`로 설정 → 이후 임베딩 재생성 대상이 됩니다.

### 4.1 테이블 메타데이터 동기화

```sql
-- 대상 스키마를 변경하려면 WHERE 절의 'ADM'을 수정하세요.
BEGIN
    EXECUTE IMMEDIATE '
    MERGE INTO dict_tables tgt
    USING (
        SELECT t.owner, t.table_name, tc.comments, t.num_rows
        FROM all_tables@DBLINK_DR t
        LEFT JOIN all_tab_comments@DBLINK_DR tc
            ON tc.owner = t.owner AND tc.table_name = t.table_name
        WHERE t.owner = ''ADM''
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
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('dict_tables 동기화 완료');
END;
/
```

### 4.2 컬럼 메타데이터 동기화

```sql
BEGIN
    EXECUTE IMMEDIATE '
    MERGE INTO dict_columns tgt
    USING (
        SELECT t.table_id,
               c.owner, c.table_name, c.column_name, c.column_id,
               c.data_type, c.data_length, c.data_precision, c.data_scale, c.nullable,
               cc.comments
        FROM all_tab_columns@DBLINK_DR c
        JOIN dict_tables t
            ON t.owner = c.owner AND t.table_name = c.table_name
        LEFT JOIN all_col_comments@DBLINK_DR cc
            ON cc.owner = c.owner
           AND cc.table_name = c.table_name
           AND cc.column_name = c.column_name
        WHERE c.owner = ''ADM''
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
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('dict_columns 동기화 완료');
END;
/
```

### 4.3 동기화 결과 확인

```sql
-- 동기화된 테이블 수
SELECT COUNT(*) AS table_count FROM dict_tables;

-- 동기화된 컬럼 수
SELECT COUNT(*) AS column_count FROM dict_columns;

-- 변경 감지된 테이블 (재임베딩 필요)
SELECT owner, table_name, comments, num_rows
FROM dict_tables
WHERE is_changed = 'Y';
```

---

## 5. JSON Duality View 생성

테이블-컬럼 관계를 JSON으로 한번에 조회할 수 있는 Duality View.
디버깅이나 데이터 확인 시 유용합니다.

```sql
CREATE OR REPLACE JSON RELATIONAL DUALITY VIEW dict_tables_dv AS
SELECT JSON {
    '_id'        : t.table_id,
    'owner'      : t.owner,
    'tableName'  : t.table_name,
    'comments'   : t.comments,
    'numRows'    : t.num_rows,
    'columns'    : [
        SELECT JSON {
            '_id'           : c.column_seq,
            'columnName'    : c.column_name,
            'columnId'      : c.column_id,
            'dataType'      : c.data_type,
            'dataLength'    : c.data_length,
            'dataPrecision' : c.data_precision,
            'dataScale'     : c.data_scale,
            'nullable'      : c.nullable,
            'comments'      : c.comments
        }
        FROM dict_columns c WITH NOCHECK
        WHERE c.table_id = t.table_id
    ]
}
FROM dict_tables t WITH NOCHECK;
```

**확인**:
```sql
-- 특정 테이블의 JSON 구조 확인
SELECT * FROM dict_tables_dv WHERE JSON_VALUE(data, '$.tableName') = 'TCODE';
```

---

## 6. 임베딩 생성

### 6.1 doc_text 생성 (JSON 변환)

각 테이블의 메타데이터를 JSON 텍스트로 변환하여 `dict_embeddings.doc_text`에 저장합니다.
컬럼이 많아 4000자를 초과하면 여러 파트로 분할합니다.

```sql
DECLARE
    c_max_len    CONSTANT NUMBER := 4000;
    v_header     CLOB;
    v_chunk      CLOB;
    v_header_len NUMBER;
    v_all_len    NUMBER;
    v_col_cnt    NUMBER;
    v_total_parts NUMBER;
    v_per_part   NUMBER;
    v_part       NUMBER;
    v_idx        NUMBER;

    TYPE t_col_arr IS TABLE OF CLOB INDEX BY PLS_INTEGER;
    v_cols       t_col_arr;
BEGIN
    -- 기존 PENDING 데이터 초기화 (재실행 시)
    DELETE FROM dict_embeddings WHERE embed_status = 'PENDING';
    COMMIT;

    FOR t IN (
        SELECT table_id, owner, table_name, comments, num_rows
        FROM dict_tables
        WHERE is_changed = 'Y'   -- 변경된 테이블만 대상
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
        v_header_len := LENGTH(v_header) + 2;  -- +2 for ]}

        -- 컬럼 JSON 조각 수집
        v_col_cnt := 0;
        v_cols.DELETE;
        v_all_len := 0;
        FOR c IN (
            SELECT column_name, column_id, data_type, data_length, nullable, comments
            FROM dict_columns
            WHERE table_id = t.table_id
            ORDER BY column_id
        ) LOOP
            v_col_cnt := v_col_cnt + 1;
            v_cols(v_col_cnt) :=
                '{"col":"' || c.column_name
                || '","type":"' || c.data_type
                || CASE WHEN c.data_length IS NOT NULL THEN '(' || c.data_length || ')' ELSE '' END
                || '"'
                || CASE WHEN c.nullable = 'N' THEN ',"notNull":true' ELSE '' END
                || CASE WHEN c.comments IS NOT NULL
                        THEN ',"desc":"' || REPLACE(REPLACE(c.comments, '"', '\"'), CHR(10), ' ') || '"'
                        ELSE '' END
                || '}';
            v_all_len := v_all_len + LENGTH(v_cols(v_col_cnt)) + 1;
        END LOOP;

        -- 기존 임베딩 삭제 (재생성 대상)
        DELETE FROM dict_embeddings WHERE table_id = t.table_id;

        -- 4000자 이내면 단일 파트, 초과하면 분할
        IF v_col_cnt = 0 OR (v_header_len + v_all_len) <= c_max_len THEN
            v_chunk := v_header;
            FOR i IN 1..v_col_cnt LOOP
                v_chunk := v_chunk || CASE WHEN i > 1 THEN ',' END || v_cols(i);
            END LOOP;
            v_chunk := v_chunk || ']}';
            INSERT INTO dict_embeddings (table_id, part_no, total_parts, doc_text)
            VALUES (t.table_id, 1, 1, v_chunk);
        ELSE
            v_total_parts := CEIL(v_all_len / (c_max_len - v_header_len - 20));
            v_per_part := CEIL(v_col_cnt / v_total_parts);
            v_part := 0;
            v_idx := 1;
            WHILE v_idx <= v_col_cnt LOOP
                v_part := v_part + 1;
                v_chunk := v_header;
                FOR i IN v_idx..LEAST(v_idx + v_per_part - 1, v_col_cnt) LOOP
                    v_chunk := v_chunk || CASE WHEN i > v_idx THEN ',' END || v_cols(i);
                END LOOP;
                v_chunk := v_chunk || ']}';
                INSERT INTO dict_embeddings (table_id, part_no, total_parts, doc_text)
                VALUES (t.table_id, v_part, v_total_parts, v_chunk);
                v_idx := v_idx + v_per_part;
            END LOOP;
        END IF;

        -- 임베딩 완료 후 변경 플래그 초기화
        UPDATE dict_tables SET is_changed = 'N', updated_at = SYSTIMESTAMP
        WHERE table_id = t.table_id;
    END LOOP;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('doc_text 생성 완료');
END;
/
```

### 6.2 벡터 임베딩 실행

`doc_text`를 OCI GenAI Embedding API로 벡터화하여 `doc_vector`에 저장합니다.

```sql
DECLARE
    c_credential CONSTANT VARCHAR2(100) := 'GENAI_VECTOR_CRED';
    c_model      CONSTANT VARCHAR2(100) := 'cohere.embed-v4.0';
    c_url        CONSTANT VARCHAR2(500) :=
        'https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/embedText';
    v_params     CLOB;
    v_count      NUMBER := 0;
    v_error      NUMBER := 0;
BEGIN
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

            v_count := v_count + 1;
            IF MOD(v_count, 50) = 0 THEN
                COMMIT;
                DBMS_OUTPUT.PUT_LINE(v_count || '건 커밋');
            END IF;
        EXCEPTION WHEN OTHERS THEN
            UPDATE dict_embeddings
            SET embed_status = 'ERROR', updated_at = SYSTIMESTAMP
            WHERE ROWID = rec.rid;
            v_error := v_error + 1;
            DBMS_OUTPUT.PUT_LINE('ERROR [table_id=' || rec.table_id
                || ' P' || rec.part_no || ']: ' || SQLERRM);
        END;
    END LOOP;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('완료: 성공=' || v_count || ', 실패=' || v_error);
END;
/
```

### 6.3 임베딩 결과 확인

```sql
-- 상태별 건수
SELECT embed_status, COUNT(*) FROM dict_embeddings GROUP BY embed_status;

-- ERROR 건이 있다면 원인 확인
SELECT table_id, part_no, LENGTH(doc_text) AS text_len
FROM dict_embeddings
WHERE embed_status = 'ERROR';
```

---

## 7. 벡터 검색 함수 생성

자연어 질문을 벡터로 변환하고, `dict_embeddings`에서 코사인 유사도 검색을 수행합니다.

```sql
CREATE OR REPLACE FUNCTION search_dict(
    p_question IN VARCHAR2,
    p_top_n    IN NUMBER DEFAULT 20
) RETURN CLOB
IS
    c_credential CONSTANT VARCHAR2(100) := 'GENAI_VECTOR_CRED';
    c_model      CONSTANT VARCHAR2(100) := 'cohere.embed-v4.0';
    c_url        CONSTANT VARCHAR2(500) :=
        'https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/embedText';
    v_params     CLOB;
    v_query_vec  VECTOR;
    v_result     CLOB := '';
BEGIN
    v_params := '{"provider":"ocigenai","credential_name":"' || c_credential
             || '","url":"' || c_url || '","model":"' || c_model || '"}';

    -- 질문 임베딩
    v_query_vec := DBMS_VECTOR.UTL_TO_EMBEDDING(p_question, JSON(v_params));

    -- 벡터 유사도 검색 (코사인 거리 기준 가까운 순)
    FOR rec IN (
        SELECT e.table_id, e.part_no, e.doc_text,
               VECTOR_DISTANCE(e.doc_vector, v_query_vec, COSINE) AS distance
        FROM dict_embeddings e
        WHERE e.embed_status = 'DONE'
        ORDER BY VECTOR_DISTANCE(e.doc_vector, v_query_vec, COSINE)
        FETCH FIRST p_top_n ROWS ONLY
    ) LOOP
        v_result := v_result
                 || '--- [유사도: ' || ROUND(1 - rec.distance, 4) || '] ---' || CHR(10)
                 || rec.doc_text || CHR(10) || CHR(10);
    END LOOP;

    IF v_result IS NULL THEN
        v_result := '검색 결과 없음';
    END IF;

    RETURN v_result;
END;
/
```

**테스트**:
```sql
SELECT search_dict('고객 주문 정보') FROM DUAL;
```

---

## 8. Select AI Agent 구성

### 8.1 Tool 등록

```sql
BEGIN
    DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
        tool_name  => 'DICT_SEARCH',
        attributes => '{
            "instruction": "데이터베이스의 테이블/컬럼 정보를 벡터 검색합니다. 사용자가 테이블이나 컬럼을 찾을 때 사용하세요.",
            "function": "search_dict",
            "tool_inputs": [
                {"name": "p_question", "description": "검색할 자연어 질문 (예: 고객 주문 정보, 배송 주소 정보 컬럼)"},
                {"name": "p_top_n", "description": "반환할 결과 수 (기본값 20)"}
            ]
        }'
    );
END;
/
```

### 8.2 Agent 생성

```sql
BEGIN
    DBMS_CLOUD_AI_AGENT.CREATE_AGENT(
        agent_name => 'DICT_AGENT',
        attributes => '{
            "profile_name": "DICT_SEARCH_PROFILE",
            "role": "당신은 Oracle 데이터베이스 전문가입니다. 사용자가 테이블이나 컬럼을 찾으면 DICT_SEARCH 도구로 검색하고, 결과를 보기 좋게 정리해서 답변하세요. 테이블명, 컬럼명, 데이터타입, 코멘트를 포함하세요."
        }'
    );
END;
/
```

### 8.3 Task 생성

```sql
BEGIN
    DBMS_CLOUD_AI_AGENT.CREATE_TASK(
        task_name  => 'DICT_SEARCH_TASK',
        attributes => '{
            "instruction": "사용자의 질문에 맞는 테이블/컬럼을 찾아 답변하세요: {query}",
            "tools": ["DICT_SEARCH"],
            "enable_human_tool": false
        }'
    );
END;
/
```

### 8.4 Team 생성

```sql
BEGIN
    DBMS_CLOUD_AI_AGENT.CREATE_TEAM(
        team_name  => 'DICT_SEARCH_TEAM',
        attributes => '{
            "agents": [
                {"name": "DICT_AGENT", "task": "DICT_SEARCH_TASK"}
            ],
            "process": "sequential"
        }'
    );
END;
/
```

---

## 9. 테스트 및 대화 이력 조회

### 9.1 Agent 실행 (SET_TEAM 방식)

```sql
BEGIN
    DBMS_CLOUD_AI_AGENT.SET_TEAM('DICT_SEARCH_TEAM');
END;
/

SELECT AI AGENT '고객 주문 정보가 어느 테이블에 있어?';
```

### 9.2 Agent 실행 (RUN_TEAM 방식 — conversation_id 필요)

```sql
DECLARE
    v_result  CLOB;
    v_conv_id VARCHAR2(4000);
BEGIN
    v_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION();
    v_result := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
        team_name   => 'DICT_SEARCH_TEAM',
        user_prompt => '배송 주소 관련 컬럼이 있는 테이블을 찾아줘',
        params      => '{"conversation_id": "' || v_conv_id || '"}'
    );
    DBMS_OUTPUT.PUT_LINE('conversation_id: ' || v_conv_id);
    DBMS_OUTPUT.PUT_LINE(DBMS_LOB.SUBSTR(v_result, 4000, 1));
END;
/
```

### 9.3 대화 이력 조회

```sql
-- 최근 대화 10건
SELECT
    CONVERSATION_PROMPT_ID,
    CONVERSATION_ID,
    CONVERSATION_TITLE,
    PROFILE_NAME,
    PROMPT_ACTION,
    PROMPT,
    SUBSTR(PROMPT_RESPONSE, 1, 200) AS RESPONSE_PREVIEW,
    CREATED
FROM USER_CLOUD_AI_CONVERSATION_PROMPTS
ORDER BY CREATED DESC
FETCH FIRST 10 ROWS ONLY;
```

```sql
-- 특정 대화 세션의 전체 흐름
SELECT
    c.CONVERSATION_TITLE,
    p.CONVERSATION_PROMPT_ID,
    p.PROMPT,
    SUBSTR(p.PROMPT_RESPONSE, 1, 100) AS RESPONSE_PREVIEW,
    p.CREATED
FROM USER_CLOUD_AI_CONVERSATIONS c
JOIN USER_CLOUD_AI_CONVERSATION_PROMPTS p
    ON c.CONVERSATION_ID = p.CONVERSATION_ID
ORDER BY p.CREATED;
```

---

## 운영: 통합 동기화 프로시저

Step 4~6의 전체 파이프라인(동기화 → doc_text 생성 → 벡터 임베딩)을 하나의 프로시저로 통합하여,
수동 실행 또는 DBMS_SCHEDULER 잡으로 주기 실행할 수 있습니다.

> 소스 파일: [`sql/sync_dict_from_exadr.sql`](sync_dict_from_exadr.sql)

### 프로시저 구조

```
sync_dict_from_exadr(p_owner_list, p_db_link, p_embed_batch)
  │
  ├── Phase 1: dict_tables MERGE (all_tables@DB_LINK)
  │     → 신규 INSERT, 변경 시 is_changed='Y'
  ├── Phase 2: dict_columns MERGE (all_tab_columns@DB_LINK)
  │     → 컬럼 변경 시 소속 테이블도 is_changed='Y'로 갱신
  ├── Phase 3: doc_text 생성 (is_changed='Y'만 대상)
  │     → 4000자 초과 시 파트 분할
  ├── Phase 4: 벡터 임베딩 (PENDING → DONE/ERROR)
  │     → 배치 커밋 (기본 20건 단위)
  └── Phase 5: is_changed 플래그 초기화
        → 변경 없으면 Phase 3~5 자동 스킵
```

### 파라미터

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| `p_owner_list` | `'ADM'` | 동기화 대상 스키마 (콤마 구분, 예: `'ADM,HR,SALES'`) |
| `p_db_link` | `'DBLINK_DR'` | DB Link 이름 |
| `p_embed_batch` | `20` | 임베딩 커밋 단위 |

### 수동 실행

```sql
-- ADM 스키마만 동기화 (기본값)
BEGIN sync_dict_from_exadr; END;
/

-- 여러 스키마 동기화
BEGIN sync_dict_from_exadr(p_owner_list => 'ADM,HR,SALES'); END;
/
```

### 실행 결과 예시

```
========================================
동기화 시작: 2026-03-18 01:29:47
대상 스키마: ADM
DB Link: DBLINK_DR
========================================
[Phase 1] dict_tables MERGE: 31건
[Phase 2] dict_columns MERGE: 1005건
[Phase 2] 임베딩 갱신 대상: 31건
[Phase 3] doc_text 생성 완료
[Phase 4] 임베딩 완료: 성공=33, 실패=0
========================================
동기화 완료: 2026-03-18 01:30:30
  테이블 MERGE: 31건
  컬럼 MERGE: 1005건
  임베딩 갱신: 31건 (성공=33, 실패=0)
========================================
```

> 33 > 31인 이유: 컬럼이 많은 테이블 2개가 4000자 초과하여 2파트로 분할됨.

### 결과 확인 쿼리

```sql
-- 동기화된 테이블/컬럼 수
SELECT 'tables' AS type, COUNT(*) AS cnt FROM dict_tables WHERE owner = 'ADM'
UNION ALL
SELECT 'columns', COUNT(*) FROM dict_columns WHERE owner = 'ADM';

-- 임베딩 상태별 건수
SELECT embed_status, COUNT(*) AS cnt
FROM dict_embeddings e
JOIN dict_tables t ON t.table_id = e.table_id
WHERE t.owner = 'ADM'
GROUP BY embed_status;

-- 변경 플래그 확인 (정상이면 모두 'N')
SELECT is_changed, COUNT(*) AS cnt
FROM dict_tables WHERE owner = 'ADM'
GROUP BY is_changed;

-- 파트 분할된 테이블 확인
SELECT t.table_name, e.total_parts
FROM dict_embeddings e
JOIN dict_tables t ON t.table_id = e.table_id
WHERE e.total_parts > 1
GROUP BY t.table_name, e.total_parts;
```

### DBMS_SCHEDULER 잡 등록

```sql
-- 매일 새벽 2시 실행
BEGIN
    DBMS_SCHEDULER.CREATE_JOB(
        job_name        => 'JOB_SYNC_DICT',
        job_type        => 'PLSQL_BLOCK',
        job_action      => 'BEGIN sync_dict_from_exadr; END;',
        start_date      => TRUNC(SYSDATE+1) + 2/24,
        repeat_interval => 'FREQ=DAILY; BYHOUR=2; BYMINUTE=0; BYSECOND=0',
        enabled         => TRUE,
        comments        => '데이터 딕셔너리 동기화 + 벡터 임베딩 갱신'
    );
END;
/

-- 잡 상태 확인
SELECT job_name, state, last_start_date, next_run_date
FROM user_scheduler_jobs WHERE job_name LIKE 'JOB_SYNC%';

-- 실행 이력 확인
SELECT job_name, status, actual_start_date, run_duration, additional_info
FROM user_scheduler_job_run_details
WHERE job_name LIKE 'JOB_SYNC%'
ORDER BY actual_start_date DESC FETCH FIRST 10 ROWS ONLY;
```
