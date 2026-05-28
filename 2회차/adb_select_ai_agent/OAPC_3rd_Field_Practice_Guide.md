# OAPC 3차 현장 실습 가이드

## 목적

이 문서는 2026-05-29 OAPC 3차 현장 교육에서 기존 `README.md`의 기본값을 어떻게 바꿔 진행할지 정리한 운영 가이드입니다.

기본 교재는 `NORTHWIND` 사용자와 `NORTHWIND_AI` 프로파일을 기준으로 설명하지만, 현장 교육에서는 참석자별로 배정된 `TRAINxx` 계정을 그대로 사용합니다.

## 실습 계정 규칙

| 항목 | README 기본값 | OAPC 현장 실습값 |
|------|---------------|------------------|
| 스키마/사용자 | `NORTHWIND` | 배정받은 `TRAINxx` |
| AI 프로파일 | `NORTHWIND_AI` | `TRAINxx_AI` |
| Tool/Task/Agent/Team | 각 계정 안에 생성 | 각자 동일한 이름으로 생성 가능 |
| SQL 실행 위치 | Database Actions SQL Worksheet 권장 | 동일 |

현장 실습에서는 아래처럼 현재 로그인 사용자를 기준으로 프로파일명을 동적으로 잡으면 계정별 수정이 줄어듭니다.

```sql
-- 현재 계정이 TRAIN05이면 TRAIN05_AI 반환
SELECT USER || '_AI' AS PROFILE_NAME FROM DUAL;
```

## 강사용 데모 환경

2026-05-28 기준으로 다음 경로를 실제 DB에서 검증했습니다.

| 검증 항목 | 결과 |
|----------|------|
| `TRAIN05` 접속 | 정상 |
| `TRAIN05_AI` 프로파일 | `ENABLED` |
| 현재 모델 | `xai.grok-4.3` |
| Northwind 핵심 테이블 | `CATEGORIES`, `PRODUCTS`, `CUSTOMERS`, `ORDERS`, `ORDER_DETAILS` 확인 |
| Agent 권한 | `DBMS_CLOUD_AI_AGENT`, `DBMS_CLOUD_AI`, `DBMS_LOB` 권한 필요 |
| SQL Tool 질문 | 정상 응답 |
| PL/SQL RMA Tool 호출 | 영어/한국어 반품 요청 모두 정상 호출 |
| Ask Oracle 공식 APEX 앱 | App ID `108`, Alias `ASKORACLE` 설치 완료 |

CLI(sqlplus/sqlcl)로 한국어를 실행할 때는 클라이언트 문자셋을 UTF-8로 맞춰야 합니다. Database Actions에서는 보통 별도 설정이 필요 없습니다.

```bash
export NLS_LANG=KOREAN_KOREA.AL32UTF8
```

## 강사용 사전 권한 부여 SQL

수강생 계정에서 `DBMS_CLOUD_AI_AGENT must be declared`가 발생하면 ADMIN 계정으로 아래 권한을 부여합니다.

```sql
GRANT EXECUTE ON C##CLOUD$SERVICE.DBMS_CLOUD_AI_AGENT TO <TRAIN_USER>;
GRANT EXECUTE ON C##CLOUD$SERVICE.DBMS_CLOUD_AI TO <TRAIN_USER>;
GRANT EXECUTE ON DBMS_LOB TO <TRAIN_USER>;

GRANT SELECT ON DBA_AI_AGENT_TASKS TO <TRAIN_USER>;
GRANT SELECT ON DBA_AI_AGENT_TASK_ATTRIBUTES TO <TRAIN_USER>;
GRANT SELECT ON DBA_AI_AGENT_TOOLS TO <TRAIN_USER>;
GRANT SELECT ON DBA_AI_AGENT_TOOL_ATTRIBUTES TO <TRAIN_USER>;
GRANT SELECT ON DBA_AI_AGENT_TEAMS TO <TRAIN_USER>;
GRANT SELECT ON DBA_AI_AGENT_TEAM_ATTRIBUTES TO <TRAIN_USER>;
```

## 현장용 빠른 실행 SQL

아래 블록은 `TRAINxx` 계정으로 로그인한 상태에서 실행합니다. `USER || '_AI'`를 사용하므로 계정별로 `TRAIN05_AI` 같은 값을 직접 바꾸지 않아도 됩니다.

```sql
-- ===============================================
-- OAPC 3차 검증 완료 빠른 실행 스크립트
-- 실행 계정: TRAINxx
-- 전제조건: TRAINxx_AI 프로파일과 Northwind 5개 테이블 존재
-- ===============================================

CREATE OR REPLACE FUNCTION run_team_clob (
    p_team_name   IN VARCHAR2,
    p_user_prompt IN VARCHAR2,
    p_params      IN CLOB
) RETURN CLOB
AS
    PRAGMA AUTONOMOUS_TRANSACTION;
    l_answer CLOB;
BEGIN
    l_answer := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
        team_name   => p_team_name,
        user_prompt => p_user_prompt,
        params      => p_params
    );
    COMMIT;
    RETURN l_answer;
END;
/

DECLARE
  e_exists EXCEPTION;
  PRAGMA EXCEPTION_INIT(e_exists, -955);
BEGIN
  EXECUTE IMMEDIATE q'[
    CREATE TABLE returns (
      return_id       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      rma_number      VARCHAR2(50) NOT NULL UNIQUE,
      order_id        NUMBER NOT NULL,
      reason          VARCHAR2(500),
      created_date    DATE DEFAULT SYSDATE NOT NULL,
      status          VARCHAR2(20) DEFAULT 'PENDING',
      processed_date  DATE,
      refund_amount   NUMBER(10,2),
      notes           VARCHAR2(1000)
    )]';
EXCEPTION
  WHEN e_exists THEN NULL;
END;
/

CREATE OR REPLACE FUNCTION generate_return (
    p_order_id IN NUMBER,
    p_reason   IN VARCHAR2
) RETURN VARCHAR2 IS
    v_rma_number VARCHAR2(100);
BEGIN
    v_rma_number := 'RMA-' || p_order_id || '-' ||
                    SUBSTR(LOWER(p_reason), 1, 5) || '-' ||
                    TRUNC(DBMS_RANDOM.VALUE(100, 999));

    INSERT INTO returns (rma_number, order_id, reason, created_date)
    VALUES (v_rma_number, p_order_id, p_reason, SYSDATE);

    RETURN v_rma_number;
END;
/

BEGIN DBMS_CLOUD_AI_AGENT.DROP_TEAM(team_name => 'Northwind_Support_Team', force => TRUE); EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN DBMS_CLOUD_AI_AGENT.DROP_AGENT('Northwind_Support_Bot'); EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN DBMS_CLOUD_AI_AGENT.DROP_TASK('Customer_Service_Task'); EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN DBMS_CLOUD_AI_AGENT.DROP_TOOL('SQL_Analysis_Tool'); EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN DBMS_CLOUD_AI_AGENT.DROP_TOOL('Return_Auth_Generator'); EXCEPTION WHEN OTHERS THEN NULL; END;
/

DECLARE
  l_profile VARCHAR2(128) := USER || '_AI';
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name   => 'SQL_Analysis_Tool',
    attributes  => '{"tool_type":"SQL","tool_params":{"profile_name":"' || l_profile || '"}}',
    description => 'Queries products, orders, customers, and sales data using Select AI NL2SQL.'
  );

  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name   => 'Return_Auth_Generator',
    attributes  => '{"instruction":"Use this tool to generate a Return Merchandise Authorization number when a customer wants to return a product. Required parameters: order_id number and reason string.","function":"generate_return"}',
    description => 'Generates RMA numbers for product returns.'
  );

  DBMS_CLOUD_AI_AGENT.CREATE_TASK(
    task_name => 'Customer_Service_Task',
    attributes => '{"instruction":"You are a customer service agent for Northwind Traders. User request: {query}. Workflow: (1) For product/order/customer/inventory/sales lookup questions, use SQL_Analysis_Tool. (2) If the user asks for return, refund, RMA, 반품, 환불, or 반품 승인번호 and gives an order number, call Return_Auth_Generator. Extract order_id from the order number and set reason to the user stated reason such as defective, damaged, 파손, 불량. Do not only look up the order when a return authorization is requested. (3) If order_id is missing, ask for it. Answer in Korean unless the user asks otherwise.","tools":["SQL_Analysis_Tool","Return_Auth_Generator"],"enable_human_tool":true}'
  );

  DBMS_CLOUD_AI_AGENT.CREATE_AGENT(
    agent_name => 'Northwind_Support_Bot',
    attributes => '{"profile_name":"' || l_profile || '","role":"You are an experienced customer support representative for Northwind Traders. You are precise with database facts, careful about missing order details, and concise in customer-facing responses."}'
  );

  DBMS_CLOUD_AI_AGENT.CREATE_TEAM(
    team_name  => 'Northwind_Support_Team',
    attributes => '{"agents":[{"name":"Northwind_Support_Bot","task":"Customer_Service_Task"}],"process":"sequential"}'
  );
END;
/

SELECT tool_name, status FROM user_ai_agent_tools ORDER BY tool_name;
SELECT task_name, status FROM user_ai_agent_tasks ORDER BY task_name;
SELECT agent_name FROM user_ai_agents ORDER BY agent_name;
SELECT agent_team_name, status FROM user_ai_agent_teams ORDER BY agent_team_name;
```

## 검증 질문

SQL 조회 검증:

```sql
DECLARE
  l_res     CLOB;
  l_conv_id VARCHAR2(100);
BEGIN
  l_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION();
  l_res := run_team_clob(
             p_team_name   => 'Northwind_Support_Team',
             p_user_prompt => '가장 비싼 제품 3개와 가격을 알려줘.',
             p_params      => '{"conversation_id": "' || l_conv_id || '"}'
           );
  DBMS_OUTPUT.PUT_LINE(DBMS_LOB.SUBSTR(l_res, 4000, 1));
END;
/
```

RMA Tool 호출 검증:

```sql
DECLARE
  l_res     CLOB;
  l_conv_id VARCHAR2(100);
BEGIN
  l_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION();
  l_res := run_team_clob(
             p_team_name   => 'Northwind_Support_Team',
             p_user_prompt => '주문번호 10248 상품이 파손되었습니다. 반품 승인번호를 생성해 주세요.',
             p_params      => '{"conversation_id": "' || l_conv_id || '"}'
           );
  DBMS_OUTPUT.PUT_LINE(DBMS_LOB.SUBSTR(l_res, 4000, 1));
END;
/

SELECT return_id, rma_number, order_id, reason, status, created_date
FROM returns
ORDER BY return_id DESC
FETCH FIRST 5 ROWS ONLY;
```

## Ask Oracle Demo 연결

공식 Ask Oracle APEX 설치 가이드는 `README.md`의 부록을 참고합니다.

강사용 데모 URL:

```text
https://yh0olybn5pqce4n-d8aukro81636mon0.adb.ap-seoul-1.oraclecloudapps.com/ords/r/oapc_demo/askoracle/home
```

Settings URL:

```text
https://yh0olybn5pqce4n-d8aukro81636mon0.adb.ap-seoul-1.oraclecloudapps.com/ords/r/oapc_demo/askoracle/settings
```

Ask Oracle에서 사용할 값:

| 모드 | 값 |
|------|-----|
| NL2SQL Profile | `TRAIN05_AI` |
| Agent Team | `NORTHWIND_SUPPORT_TEAM` |
