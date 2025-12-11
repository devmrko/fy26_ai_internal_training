## Oracle Autonomous AI Database: Select AI Agent 교육 과정

#### 문서 개요

본 교육 과정은 Oracle Autonomous Database의 **Select AI Agent** 기능을 활용하여 지능형 자율 에이전트를 구축하는 방법을 단계별로 학습합니다.

---

### 목차

#### [1부] Select AI Agent 개념 및 아키텍처
- 1. Select AI Agent란 무엇인가?
- 2. 작동 원리: ReAct 패턴
- 3. 아키텍처 및 구성 요소 (Agent, Tool, Task, Team)

#### [2부] 핸즈온: 기본 에이전트 구축하기
- **Step 1**: 사전 준비 및 권한 설정
- **Step 2**: tool(Tool) 생성 - SQL, PL/SQL
- **Step 3**: 작업(Task) 생성
- **Step 4**: 에이전트(Agent) 생성
- **Step 5**: 팀(Team) 구성 및 활성화
- **Step 6**: 에이전트 실행 및 테스트

#### [3부] 고급 Tool 활용
- **Step 7**: 고급 Tool (RAG, WebSearch, Notification)
- **Step 8**: 실전 응용 예제

**지원 Tool 유형**: SQL, PL/SQL, RAG, WebSearch, Notification

---

### 학습 목표
1. Select AI Agent의 핵심 개념과 아키텍처 이해
2. Agent, Tool, Task, Team을 생성하고 실행
3. 실전 에이전트 구축 (SQL, PL/SQL, Email Notification)

### 사전 요구사항
- Oracle Autonomous Database 접근 권한
- SQL 기본 지식
- NORTHWIND_AI 프로파일 생성 완료 (1회차 실습)

---

### [1부] Select AI Agent 개념 및 아키텍처

#### 1. Select AI Agent란 무엇인가?

**Select AI Agent**는 Oracle Autonomous Database에 내장된 대화형 자율 에이전트 프레임워크입니다. 

##### 핵심 개념
기존 Select AI가 **단일 tool(NL2SQL)**를 사용한 질의응답에 집중했다면, Select AI Agent는 **여러 tool를 조합**하여 사용하고 **ReAct 패턴(Reasoning and Acting)**을 통해 추론과 행동을 반복하며 작업을 완수하는 에이전트 프레임워크입니다.

**주요 차이점:**
- **Select AI**: 자연어 → SQL 변환 → 결과 반환 (단일 작업)
- **Select AI Agent**: 추론 → tool 선택 → 실행 → 결과 평가 → 재추론 → ... → 최종 답변 (다단계 작업)

##### 핵심 기능 (Key Features)

##### 1.1 통합 지능 (Integrated Intelligence)
계획, tool 사용, 성찰을 결합하여 에이전트가 작업에 대해 추론하고, tool를 선택 및 실행하며, 결과를 관찰하고, 계획을 조정하여 대화 전반에 걸쳐 응답을 개선합니다.

- 에이전트는 단계를 계획하고, tool를 실행하며, 관찰 결과를 평가합니다
- 결과가 기대에 미치지 못할 때 접근 방식을 업데이트합니다
- 이러한 루프는 정확성을 강화하고, 재작업을 줄이며, 대화를 올바른 방향으로 유지합니다

##### 1.2 유연한 tool (Flexible Tooling)
내장 RAG 및 NL2SQL, 커스텀 PL/SQL 프로시저, 외부 REST 서비스를 지원하고 사용하며, 오케스트레이션 구성 요소나 별도의 인프라 없이 데이터베이스에 핵심 로직을 유지하면서 필요에 따라 외부 기능을 통합할 수 있습니다.

**지원되는 tool 유형:**

| tool 유형 | tool_type | 설명 | 예시 |
|----------|-----------|------|------|
| **SQL Tool** | `SQL` | NL2SQL을 통한 데이터 조회 | "고객 목록 보여줘" |
| **RAG Tool** | `RAG` | 벡터 검색으로 문서 검색 | "제품 매뉴얼에서 A/S 정책 찾아줘" |
| **PL/SQL Tool** | `function` | 커스텀 프로시저/함수 실행 | 재고 업데이트, 주문 생성 |
| **WebSearch Tool** | `WEBSEARCH` | openai를 이용한 웹검색 | 최신 환율, 제품 가격 조회 |
| **Notification Tool** | `NOTIFICATION` | 이메일/Slack 알림 (OCI SMTP 이용) | 알림, 리포트 전송 |

**하나의 작업에서 여러 tool를 순차적으로 조합:**
- SQL Tool로 데이터 조회 → PL/SQL Tool로 처리 → Notification Tool로 결과 알림

##### 1.3 문맥 인식 대화 (Context-Aware Conversations)
턴 간 컨텍스트를 유지하고, 응답을 개인화하며, 선호도를 저장하고, 멀티턴 세션 동안 수정 및 확인을 위한 human-in-the-loop 제어를 지원하기 위해 단기 및 장기 메모리를 유지합니다.

- **단기 기억(Short-term memory)**: 현재 대화를 일관성 있게 유지
- **장기 기억(Long-term memory)**: 선호도와 이전 결과를 기록하여 후속 상호작용 및 인간 검토자의 감독 지원
- **멀티턴 대화**: 여러 차례의 질문과 답변을 통해 작업 완수

##### 1.4 확장성 및 보안 (Scalable and Secure)
Autonomous AI Database 내부에서 실행되어 보안 제어, 감사 및 성능을 상속받고, 데이터 이동을 줄이며, 대규모 엔터프라이즈 배포 및 규제 환경을 위한 거버넌스를 표준화합니다.

- 에이전트는 데이터베이스의 보안, 감사 및 성능 특성을 활용합니다
- 처리를 데이터에 가깝게 유지하여 이동을 줄이고 거버넌스 관행에 부합합니다
- 엔터프라이즈 규모의 안정적인 운영

##### 1.5 빠른 개발 (Faster Development)
익숙한 SQL 및 PL/SQL로 에이전트, 작업 및 tool를 정의하고, 기존 프로시저를 재사용하며, 별도의 인프라를 구축하지 않고 운영 데이터 및 팀에 가까운 로직을 유지하면서 기능을 더 빠르게 제공할 수 있습니다.

- SQL/PL/SQL 기반 개발로 진입 장벽 낮음
- 기존 데이터베이스 자산 재활용
- 별도의 AI 인프라 불필요

---

#### 2. 작동 원리: ReAct 패턴

Select AI Agent는 **ReAct (Reasoning and Acting)** 패턴을 사용합니다. 이 패턴은 추론(Reasoning)과 행동(Acting)을 루프로 결합하여, 에이전트가 생각하고, tool를 선택하며, 결과를 관찰하고, 확신할 수 있는 답변을 제시할 때까지 반복합니다.

**동작 방식:**
- 사용자의 AI 프로파일에 지정된 LLM이 tool를 통해 추론과 행동을 번갈아 수행합니다
- 데이터베이스는 이러한 행동을 처리하고 관찰(Observation) 결과를 반환합니다
- 에이전트는 각 반복마다 다음 패턴을 따릅니다:

##### ReAct 사이클

**각 반복(iteration)의 패턴:**

| **1. Query (질문)** |
|:---|
| 사용자가 질문하거나 요청을 명시합니다.<br>에이전트는 이를 읽고 주요 세부 사항을 추출하며<br>다음 단계를 계획할 준비를 합니다.<br>예: "이번 달 매출이 가장 높은 고객은 누구인가요?" |

                 ↓

| **2. Thought and Action (사고 및 행동)** |
|:---|
| 에이전트는 옵션에 대해 추론하고, tool를 선택하며,<br>작업에 필요한 데이터를 수집하거나 상태를 변경하기<br>위해 tool를 실행합니다.<br>Thought: "매출 정보검색을 위해 DB를 확인해야 함"<br>Action: SQL_Tool 실행 |

                 ↓

| **3. Observation (관찰)** |
|:---|
| tool 또는 쿼리 결과, 확인 메시지, 오류를 포함합니다.<br>이는 에이전트의 다음 추론 라운드에 대한 입력이<br>됩니다. 에이전트는 관찰 결과를 기록하고 결과가<br>다음 단계 또는 최종 응답을 지원하는지 확인합니다.<br>결과: CustomerID=5, Total=₩15,000,000 |

                 ↓  (필요시 2-3 반복)

| **4. Final Response (최종 답변)** |
|:---|
| 충분히 성공적인 thought-action과 observation 후에,<br>에이전트는 명확한 답변을 작성하고, 중요한 결정을<br>설명하며, 다음 단계나 후속 조치를 공유합니다.<br>답변: "이번 달 가장 많이 구매하신 고객은<br>'ABC Company'이며, 총 ₩15,000,000입니다." |

---

#### 3. 아키텍처 및 구성 요소

Select AI Agent는 작업을 **4개의 계층**으로 구성합니다: Planning, Tool Use, Reflection, Memory Management. 이러한 계층은 추론, tool 실행, 평가 및 멀티턴 상호작용을 위한 컨텍스트를 조정합니다.

##### 4계층 아키텍처

| **Layer 1: Planning (계획)** |
|:---|
| 사용자 요청을 해석하고, 순서가 있는 작업으로 분해하며,<br>후보 tool를 선택하고, 세션 컨텍스트, 이전 결과 및 관련<br>지식을 사용하여 계획을 작성합니다.<br>• 요청 분석, 누락된 세부 정보 식별<br>• 순서가 있는 작업 시퀀스 제안<br>• 정책, 데이터 범위, 예상 결과에 맞는 tool 선택 |

                            ↓

| **Layer 2: Tool Use (tool 사용)** |
|:---|
| 각 작업에 대한 tool를 선택하고 실행합니다.<br>지원되는 유형: RAG, NL2SQL, 커스텀 PL/SQL 프로시저,<br>웹 검색 및 이메일과 같은 외부 REST 서비스<br>• 각 단계는 파라미터와 함께 tool를 호출<br>• 내장 tool는 검색 및 SQL 생성 처리<br>• 커스텀 PL/SQL은 도메인 로직 캡슐화<br>• REST tool는 외부 서비스에 연결 |

                            ↓

| **Layer 3: Reflection (성찰)** |
|:---|
| tool 결과를 기대치와 비교하여 평가하고 최종 응답으로<br>진행합니다. 결과가 잘못되었거나, tool 호출 오류가 있거나,<br>사용자가 승인하지 않은 결과인 경우 에이전트는 추론을<br>수정하거나 다른 tool를 선택하거나 계획을 업데이트합니다.<br>• 관찰 결과를 목표와 비교<br>• 결과가 맞지 않으면 계획 조정, 다른 tool 선택<br>• 필요시 명확한 질문 |

                            ↓

| **Layer 4: Memory Management (기억 관리)** |
|:---|
| 에이전트 팀별로 세션 컨텍스트 및 지식을 저장합니다.<br>• 단기 기억: 에이전트 팀별 최근 메시지 및 중간 결과 보유<br>• 장기 기억: 선호도, 이력, 전략을 기록하여 지속성,<br>개인화 및 계획 개선<br>• 세션 간 유용한 지식을 지속하여 시간이 지남에 따라<br>에이전트 팀 전반의 지침 및 응답 품질 향상 |


##### 4가지 핵심 객체

Select AI Agent는 다음 4가지 객체의 조합으로 동작합니다:

##### 3.1 Agent (에이전트)
**정의된 목적을 위해 작업을 수행하는 구성된 작업자**

에이전트는 요청에 대해 추론하고, tool를 선택하며, 단계를 실행하고, 결과를 평가하며, 데이터베이스 컨텍스트에 기반한 응답을 생성합니다.

**주요 특징:**
- AI 프로파일(LLM) 연결 및 역할(Role) 정의
- 정의된 컨텍스트에 기반한 응답 생성
- 여러 작업(Task)을 수행할 수 있음

> **상세 구현은 Step 4 참조**

##### 3.2 Tool (tool)
**데이터 업데이트, 문서 검색 또는 외부 서비스 호출과 같은 작업을 수행**

tool는 파라미터를 받아 실행되며, 추론을 위한 관찰(observation) 결과를 반환합니다. tool는 반복 가능한 작업을 캡슐화하고, 부작용을 제어 및 관찰 가능하게 유지하여 감사 및 디버깅을 지원합니다.

**tool 유형별 예시:**
| tool 유형 | 특성 | 사용 사례 |
|----------|------|----------|
| **SQL** | 결정적 | 자연어 → SQL 쿼리 실행 |
| **PL/SQL Function** | 결정적 | 비즈니스 로직 실행 (반품 승인 번호 생성 등) |
| **RAG** | 비결정적 | 벡터 검색으로 문서 찾기 |
| **WEBSEARCH** | 비결정적 | 웹 검색, 최신 정보 조회 |
| **NOTIFICATION** | 결정적 | 이메일/Slack 알림 발송 |

> **상세 구현은 Step 2 참조**

##### 3.3 Task (작업)
**작업 단위를 나타내며, tool 선택, 파라미터 매핑 및 실행 정책을 안내**

작업은 목표, 입력, tool 선택 및 가드레일을 지정합니다. 다운스트림 단계가 읽고 요약할 수 있는 구조화된 출력을 반환합니다.

**Task의 주요 요소:**
- **Instruction (지침)**: 에이전트가 따라야 할 규칙과 절차
- **Tools (tool 목록)**: 이 작업에서 사용 가능한 tool들
- **Human Tool (선택)**: 사용자에게 추가 정보 요청 가능 여부
- **가드레일(Guardrails)**: 어떤 제약과 정책이 있는가?

> **상세 구현은 Step 3 참조**

##### 3.4 Agent Team (팀)
**하나 이상의 에이전트가 에이전트 워크플로우를 수행**

팀은 에이전트-작업 쌍을 실행하여 다단계 상호작업을 안정적으로 완료합니다. 팀은 공유 컨텍스트를 유지하고 통합된 응답을 생성합니다.

**Team의 주요 기능:**
- **에이전트 조율**: 여러 에이전트 간 작업 분배 및 조정
- **컨텍스트 공유**: 팀 전체에서 대화 컨텍스트 유지
- **통합 응답**: 여러 에이전트의 결과를 하나의 응답으로 통합
- **프로세스 제어**: `sequential`(순차), `parallel`(병렬, 향후 지원)

**예시:** `Northwind_Support_Team`은 `Northwind_Support_Bot` 에이전트가 `Customer_Service_Task` 작업을 수행하도록 조율합니다.

> **상세 구현은 Step 5 참조**

##### 3.5 객체 간 관계도

**실행 흐름:**
```
사용자 요청
    ↓
Team (Northwind_Support_Team)
    ↓
Agent (Northwind_Support_Bot)
    ↓
Task (Customer_Service_Task)
    ↓
Tools (SQL_Analysis_Tool, EMAIL_NOTIFY)
```

1. 사용자가 팀에 요청
2. 팀이 에이전트에게 작업 할당
3. 에이전트가 작업(Task) 실행
4. 작업에 정의된 tool들을 ReAct 패턴으로 사용

---

### [2부] 핸즈온: Northwind 스마트 에이전트 구축하기

> **학습 목표**: Agent, Tool, Task, Team을 직접 생성하고 실행하여 완전한 AI Agent 시스템 구축  
> **실습 단계**: Step 1 (권한) → Step 2 (Tool) → Step 3 (Task) → Step 4 (Agent) → Step 5 (Team) → Step 6 (테스트)

---

### 실습 시나리오

**목표**: Northwind 회사의 **고객 지원 에이전트**를 구축합니다.

**에이전트의 역할:**
- 고객 문의에 대해 주문 정보를 조회
- 제품 정보 및 재고 확인
- 반품 요청 시 RMA(Return Merchandise Authorization) 번호 자동 생성
- 친절하고 정확한 응대

**사용할 기술:**
- `SQL Tool`: 데이터베이스 조회
- `PL/SQL Tool`: 반품 승인 번호 생성 로직

---

#### Step 1: 사전 준비 및 권한 설정

##### 1.1 필요 권한 확인

Select AI Agent를 사용하려면 다음 패키지에 대한 실행 권한이 필요합니다:
- `DBMS_CLOUD_AI_AGENT` - 에이전트 생성 및 관리
- `DBMS_CLOUD_AI` - AI 프로파일 사용

##### 1.2 권한 부여 (ADMIN 계정에서 실행)

**중요**: Select AI Agent를 사용하려면 반드시 ADMIN 계정에서 아래 권한을 부여해야 합니다!

```sql
-- ===============================================
-- Step 1.2: 권한 부여
-- 설명: NORTHWIND 사용자에게 Agent 사용 권한 부여
-- 실행 계정: ADMIN (필수!)
-- ===============================================

-- 1. Agent 패키지 실행 권한 부여
GRANT EXECUTE ON C##CLOUD$SERVICE.DBMS_CLOUD_AI_AGENT TO NORTHWIND;
GRANT EXECUTE ON C##CLOUD$SERVICE.DBMS_CLOUD_AI TO NORTHWIND; -- 이미 select ai 세션에서 부여

-- 2. LOB 데이터 처리 권한 (AI Agent 응답 처리용)
-- 설명: AI Agent의 CLOB 응답을 읽고 처리하기 위해 필요
GRANT EXECUTE ON DBMS_LOB TO NORTHWIND;
```

##### 1.3 네트워크 ACL 설정 (선택사항)

외부 API(WebSearch, 이메일 등)를 사용할 경우 네트워크 접근 권한이 필요합니다.

```sql
-- ===============================================
-- Step 1.3: 네트워크 ACL 설정 
-- 설명: OCI SMTP, email 사용을 위한 네트워크 접근 권한
-- 실행 계정: ADMIN
-- ===============================================
  
  -- SMTP 서버 접근 권한 (Email Notification 사용 시)
  -- 상세 설정은 Step 11.3 Notification Tool 섹션 참조
  DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
    host       => 'smtp.email.us-chicago-1.oci.oraclecloud.com',
    lower_port => 587,
    upper_port => 587,
    ace        => xs$ace_type(
      privilege_list => xs$name_list('connect'),
      principal_name => 'NORTHWIND',
      principal_type => xs_acl.ptype_db
    )
  );
END;
/

```

---

##### 1.4 Helper Function 생성 (CLOB 응답 처리용)

Agent 실행 시 CLOB 응답을 안정적으로 처리하기 위한 함수를 생성합니다.

```sql
-- ===============================================
-- Step 1.4: run_team_clob 함수 생성
-- 설명: AI Agent 실행 시 CLOB 응답을 AUTONOMOUS_TRANSACTION으로 처리
-- 실행 계정: NORTHWIND
-- ===============================================

CREATE OR REPLACE FUNCTION NORTHWIND.run_team_clob (
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

    -- Commit any internal work so the autonomous transaction ends cleanly
    COMMIT;

    RETURN l_answer;
END;
/
```

**함수 설명:**
- `PRAGMA AUTONOMOUS_TRANSACTION`: 독립적인 트랜잭션으로 실행하여 CLOB 처리 안정성 확보
- AI Agent의 응답을 CLOB 타입으로 반환
- 멀티턴 대화 시 conversation_id를 params로 전달 가능

---

##### 1.5 AI 프로파일 확인

1회차에서 생성한 `NORTHWIND_AI` 프로파일이 있는지 확인합니다.

```sql
-- ===============================================
-- Step 1.5: AI 프로파일 확인
-- 설명: Select AI Agent가 사용할 LLM 프로파일 확인
-- 실행 계정: NORTHWIND
-- ===============================================

-- 프로파일 목록 조회
SELECT p.profile_name,
       p.status,
       CAST(p.created AS DATE) AS created,
       a.attribute_name,
       DBMS_LOB.SUBSTR(a.attribute_value, 4000, 1) AS attribute_value
FROM   user_cloud_ai_profiles p
JOIN   user_cloud_ai_profile_attributes a
       USING (profile_id)
WHERE p.PROFILE_NAME = 'NORTHWIND_AI'
ORDER BY p.profile_name, a.attribute_name;

```

---

#### Step 2: tool(Tool) 생성

에이전트가 사용할 **tool**을 만듭니다. tool는 에이전트가 실제로 작업을 수행하는 수단입니다.

##### 2.1 SQL Tool 생성 (데이터 조회용)

**목적**: 자연어 질문을 SQL 쿼리로 변환하여 데이터베이스를 조회하는 tool

**작동 방식**:
```
사용자: "10월에 가장 많이 팔린 제품은?"
   ↓
SQL Tool → NL2SQL 변환
   ↓
SELECT product_name, SUM(quantity) FROM orders...
   ↓
결과 반환
```

```sql
-- ===============================================
-- Step 2.1: SQL Tool 생성
-- 설명: 자연어를 SQL로 변환하여 데이터 조회
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name   => 'SQL_Analysis_Tool',
    attributes  => '{
                      "tool_type": "SQL", 
                      "tool_params": {
                        "profile_name": "NORTHWIND_AI"
                      }
                    }',
    description => 'Queries the database for products, orders, customers, and sales data. 
                    Use this tool when you need to look up information from the database.'
  );
END;
/

-- 생성 확인
SELECT t.tool_name,
       t.description,
       t.status,
       a.attribute_name,
       DBMS_LOB.SUBSTR(a.attribute_value, 4000, 1) AS attribute_value,
       CAST(a.last_modified AS DATE) AS last_modified
FROM   user_ai_agent_tools t
JOIN   user_ai_agent_tool_attributes a
       USING (tool_id)
WHERE t.TOOL_NAME = upper('SQL_Analysis_Tool')
ORDER  BY t.tool_name, a.attribute_name;
```

**Tool 속성 설명:**
- `tool_name`: tool를 식별하는 고유 이름 (필수)
- `attributes`: JSON 형식의 tool 구성 (필수)
  - `tool_type`: 내장 tool 유형 지정 (`SQL`, `RAG`, `WEBSEARCH`, `NOTIFICATION`)
  - `tool_params`: 내장 tool 등록을 위한 파라미터
    - `profile_name`: SQL tool에서 사용할 AI 프로파일
- `description`: tool를 식별하는 데 도움이 되는 사용자 정의 설명

---

##### 2.2 PL/SQL Tool 생성 (반품 처리 로직)

**목적**: 실제 비즈니스 로직을 수행하는 tool (RMA 번호 생성)

**배경**: SQL Tool은 **조회**만 가능합니다. 데이터를 생성하거나 복잡한 로직을 실행하려면 PL/SQL 함수가 필요합니다.

###### 2.2.1 비즈니스 로직 함수 생성
```sql
-- ===============================================
-- 반품 테이블 생성
-- 실행 계정: NORTHWIND
-- ===============================================
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
);

-- 코멘트 추가 
COMMENT ON TABLE returns IS '제품 반품 정보를 관리하는 테이블';
COMMENT ON COLUMN returns.return_id IS '반품 고유 ID (자동 생성)';
COMMENT ON COLUMN returns.rma_number IS 'RMA(Return Merchandise Authorization) 번호';
COMMENT ON COLUMN returns.order_id IS '주문 번호 (orders 테이블 참조)';
COMMENT ON COLUMN returns.reason IS '반품 사유';
COMMENT ON COLUMN returns.created_date IS '반품 요청일';
COMMENT ON COLUMN returns.status IS '반품 상태 (PENDING, APPROVED, REJECTED, COMPLETED)';
COMMENT ON COLUMN returns.processed_date IS '반품 처리 완료일';
COMMENT ON COLUMN returns.refund_amount IS '환불 금액';
COMMENT ON COLUMN returns.notes IS '추가 메모';

```

```sql
-- ===============================================
-- Step 2.2.1: 반품 승인 번호 생성 함수
-- 설명: RMA (Return Merchandise Authorization) 번호를 생성하는 PL/SQL 함수
-- 실행 계정: NORTHWIND
-- ===============================================

CREATE OR REPLACE FUNCTION generate_return (
    p_order_id IN NUMBER,
    p_reason   IN VARCHAR2
) RETURN VARCHAR2 IS
    v_rma_number VARCHAR2(100);
BEGIN
    /*
    RMA 번호 생성 규칙:
    RMA-[주문번호]-[사유코드]-[난수]
    예: RMA-10248-def-742
    */
    v_rma_number := 'RMA-' 
                    || p_order_id 
                    || '-' 
                    || SUBSTR(LOWER(p_reason), 1, 3)  -- 사유 앞 3글자
                    || '-' 
                    || TRUNC(DBMS_RANDOM.VALUE(100, 999));  -- 100-999 난수
    
    -- 실제 환경에서는 여기서 Returns 테이블에 INSERT 할 수 있습니다
    INSERT INTO returns (rma_number, order_id, reason, created_date)
    VALUES (v_rma_number, p_order_id, p_reason, SYSDATE);
    
    RETURN v_rma_number;
END;
/

-- 함수 테스트
DECLARE
    v_result VARCHAR2(100);
BEGIN
    -- SELECT 문이 아닌 변수 할당 방식으로 호출
    v_result := generate_return(10248, 'defective');
    DBMS_OUTPUT.PUT_LINE('Generated RMA: ' || v_result);
END;

select * from returns;
```

###### 2.2.2 함수를 Agent Tool로 등록

```sql
-- ===============================================
-- Step 2.2.2: PL/SQL Tool 등록
-- 설명: generate_return_auth 함수를 에이전트 tool로 등록
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
    DBMS_CLOUD_AI_AGENT.DROP_TOOL('Return_Auth_Generator');
    EXCEPTION WHEN OTHERS THEN NULL;
END;

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name   => 'Return_Auth_Generator',
    attributes  => '{
                      "instruction": "Use this tool to generate a Return Merchandise Authorization (RMA) number when a customer wants to return a product. This tool requires two parameters: order_id (number) and reason (string describing why they want to return).",
                      "function": "generate_return_auth"
                    }',
    description => 'Generates RMA numbers for product returns. Call this when customer requests a return or refund.'
  );
END;
/

-- 생성 확인
SELECT t.tool_name,
       t.description,
       t.status,
       a.attribute_name,
       DBMS_LOB.SUBSTR(a.attribute_value, 4000, 1) AS attribute_value
FROM   user_ai_agent_tools t
JOIN   user_ai_agent_tool_attributes a
       USING (tool_id)
WHERE t.TOOL_NAME = upper('Return_Auth_Generator')
ORDER BY t.tool_name, a.attribute_name;
```

**PL/SQL Tool 속성 설명:**
- `instruction`: tool가 무엇을 수행해야 하는지, 어떻게 수행하는지를 설명하는 명확하고 간결한 설명문
  - **LLM에 전송됨** (에이전트가 이를 읽고 tool를 사용)
  - 필요한 파라미터와 타입을 명시 (order_id, reason 등)
  - 필수 속성
- `function`: tool가 사용될 때 호출할 PL/SQL 프로시저 또는 함수를 지정
  - 커스텀 tool의 필수 파라미터
- `description`: tool를 식별하는 데 도움이 되는 사용자 정의 설명
  - **LLM에 전송되지 않음** (데이터베이스에만 저장)
  - 관리 및 문서화 목적

---

##### 2.3 생성된 tool 확인

```sql
-- ===============================================
-- Step 2.3: 생성된 tool 목록 확인
-- 실행 계정: NORTHWIND
-- ===============================================

-- 모든 tool 조회
SELECT 
    TOOL_NAME,
    SUBSTR(DESCRIPTION, 1, 50) AS SHORT_DESC,
    CREATED
FROM USER_AI_AGENT_TOOLS
ORDER BY CREATED DESC;

-- tool 상세 정보 (tool_type 포함)
SELECT 
    t.TOOL_NAME,
    a.ATTRIBUTE_NAME,
    a.ATTRIBUTE_VALUE,
    t.DESCRIPTION
FROM USER_AI_AGENT_TOOLS t
LEFT JOIN USER_AI_AGENT_TOOL_ATTRIBUTES a
    ON t.TOOL_NAME = a.TOOL_NAME;
```

---

** tool 실행 로그 확인**

```sql
-- ===============================================
-- tool 실행 로그 확인
-- 실행 계정: NORTHWIND
-- ===============================================
-- tool이 실제로 호출되었는지 확인
SELECT 
    CONVERSATION_PROMPT_ID,
    CONVERSATION_ID,
    PROMPT,
    PROMPT_RESPONSE,
    PROMPT_ACTION,
    CREATED
FROM USER_CLOUD_AI_CONVERSATION_PROMPTS
ORDER BY CREATED DESC
FETCH FIRST 5 ROWS ONLY;
```

**팁**: `PROMPT_ACTION`이 'AGENT'이면 AI Agent가 실행된 것이고, 'SQL'이면 Select AI가 직접 SQL을 생성한 것입니다.

**방법 4: Tool 실행 히스토리 상세 조회**

AI Agent가 실제로 어떤 tool를 호출했는지, 각 tool에 어떤 입력을 주고 어떤 출력을 받았는지 추적합니다.

```sql
-- ===============================================
-- Tool 실행 히스토리 조회
-- 뷰: USER_AI_AGENT_TOOL_HISTORY
-- 목적: 각 tool 호출의 입력/출력 추적, 성능 분석
-- ===============================================

SELECT 
    TOOL_NAME,              -- 실행된 tool 이름
    INPUT,                  -- tool에 전달된 입력 (CLOB)
    LENGTH(OUTPUT) AS OUTPUT_LENGTH,  -- 출력 길이 (바이트)
    TOOL_OUTPUT,            -- tool의 실행 결과 (CLOB)
    START_DATE              -- tool 실행 시작 시각
FROM USER_AI_AGENT_TOOL_HISTORY
ORDER BY START_DATE DESC;

-- 최근 10개만 조회
SELECT 
    TOOL_NAME,
    SUBSTR(INPUT, 1, 100) AS INPUT_PREVIEW,
    LENGTH(OUTPUT) AS OUTPUT_LENGTH,
    SUBSTR(TOOL_OUTPUT, 1, 200) AS OUTPUT_PREVIEW,
    START_DATE,
    END_DATE,
    (END_DATE - START_DATE) * 24 * 3600 AS DURATION_SECONDS  -- 실행 시간 (초)
FROM USER_AI_AGENT_TOOL_HISTORY
ORDER BY START_DATE DESC
FETCH FIRST 10 ROWS ONLY;
```

**특정 tool의 실행 이력 분석:**

```sql
-- ===============================================
-- SQL_Analysis_Tool의 사용 패턴 분석
-- 실행 계정: NORTHWIND
-- ===============================================
SELECT 
    TOOL_NAME,
    COUNT(*) AS EXECUTION_COUNT,
    AVG(LENGTH(OUTPUT)) AS AVG_OUTPUT_SIZE,
    MIN(START_DATE) AS FIRST_USED,
    MAX(START_DATE) AS LAST_USED
FROM USER_AI_AGENT_TOOL_HISTORY
WHERE TOOL_NAME = upper('SQL_Analysis_Tool')
GROUP BY TOOL_NAME;

```

---

#### Step 3: 작업(Task) 생성

**Task**는 에이전트의 **업무 매뉴얼**입니다. 무엇을 하고, 어떻게 할지를 구체적으로 정의합니다.

##### 3.1 Task 개념 이해

**Task는 다음을 포함합니다:**
1. **Instruction (지침)**: 에이전트가 따라야 할 규칙과 절차
2. **Tools (tool 목록)**: 이 작업에서 사용 가능한 tool들
3. **Human Tool (선택)**: 사용자에게 추가 정보 요청 가능 여부


| **TASK: Customer_Service_Task** |
|:---|
| **[지침]**<br>• 제품 문의 → SQL Tool 사용<br>• 반품 요청 → RMA Generator 사용<br>• 이메일 발송 → EMAIL_NOTIFY 사용<br>• 정보 부족 시 → 사용자에게 질문 |
| **[사용 가능 tool]**<br>✓ SQL_Analysis_Tool<br>✓ Return_Auth_Generator<br>✓ EMAIL_NOTIFY<br>✓ Human_Tool (자동 활성화) |


##### 3.2 Task 생성

```sql
-- ===============================================
-- Step 3: Customer Service Task 생성
-- 설명: 고객 지원 업무를 정의하는 Task
-- 실행 계정: NORTHWIND
-- 전제조건: SQL_Analysis_Tool, Return_Auth_Generator, EMAIL_NOTIFY tool가 생성되어 있어야 함
--          (EMAIL_NOTIFY 생성 방법은 Step 11.3 참조)
-- ===============================================
-- task의 instruction에 {query}가 들어가 있지 않으면 오동작함, 패치 예정이라고 함

BEGIN
  DBMS_CLOUD_AI_AGENT.DROP_TASK('Customer_Service_Task');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

DECLARE
    v_attributes CLOB;
BEGIN
    v_attributes := JSON_OBJECT(
        'instruction' VALUE 'You are a customer service agent. deal with customer inquiry based on user request:{query}' ||
                           '1. For product/order questions use SQL_Analysis_Tool ' ||
                           '2. For sending email about the information using EMAIL_NOTIFY ' ||
                           '3. Always be polite and professional',
        'tools' VALUE JSON_ARRAY('SQL_Analysis_Tool', 'EMAIL_NOTIFY'),
        'enable_human_tool' VALUE true
    );
    
    DBMS_CLOUD_AI_AGENT.CREATE_TASK(
        task_name => 'Customer_Service_Task',
        attributes => v_attributes
    );
END;
/
```

**Task Instruction 속성:**
- 작업이 무엇을 수행해야 하는지 설명하는 명확하고 간결한 설명문
- **LLM에 전송되는 프롬프트에 포함됨**

**Instruction 작성 팁:**
- **구체적으로**: 명확하게 작성 필요
- **시나리오별로**: 상황에 따른 행동 지침을 명확히 (WORKFLOW 섹션)
- **예외 처리**: 정보가 부족할 때 어떻게 할지 명시

##### 3.3 enable_human_tool 이해

**정의**: 작업 중 정보나 명확한 설명이 필요할 때 에이전트가 사용자에게 질문할 수 있도록 활성화합니다.

**속성 정보:**
- **기본값**: `true`
- **위치**: Agent 또는 Task 속성에 설정 가능
- **우선순위**: **Task의 enable_human_tool이 Agent 설정을 덮어씁니다**
  - Agent: `false`, Task: `true` → 작업 실행 중 LLM이 질문함
  - Agent: `true`, Task: `false` → 작업 실행 중 질문하지 않음

**예시:**
```
사용자: "반품하고 싶어요"

에이전트 (enable_human_tool=true):
  "어떤 주문을 반품하시겠어요? 주문 번호를 알려주세요."
  → 사용자 응답 대기 → 작업 계속 진행

에이전트 (enable_human_tool=false):
  "주문 번호가 필요합니다." 
  → 더 이상 진행 불가, 작업 실패 또는 불완전한 결과
```

##### 3.4 Task 확인

```sql
-- ===============================================
-- Task 확인
-- 실행 계정: NORTHWIND
-- ===============================================
-- Task에 연결된 tool 목록 확인
SELECT t.owner,
       t.task_name,
       t.status,
       JSON_OBJECTAGG(a.attribute_name VALUE DBMS_LOB.SUBSTR(a.attribute_value, 4000, 1)) AS task_config
FROM   dba_ai_agent_tasks t
LEFT JOIN dba_ai_agent_task_attributes a
       ON t.task_id = a.task_id
WHERE t.TASK_NAME = upper('Customer_Service_Task')
GROUP BY t.owner, t.task_name, t.status
ORDER BY t.owner, t.task_name;
```

---

#### Step 4: 에이전트(Agent) 생성

**Agent**는 실제로 작업을 수행하는 **주체**입니다. 에이전트에게 성격과 전문성을 부여합니다.

##### 4.1 Agent 속성 (CREATE_AGENT Attributes)

에이전트의 속성은 역할과 AI 프로파일 이름을 정의합니다.

**필수 속성:**
- **profile_name**: 에이전트가 LLM에 요청을 보내는 데 사용하는 AI 프로파일 
- **role**: 에이전트의 기능을 정의하고 컨텍스트를 제공 
  - **LLM에 전송됨**
  - 에이전트의 페르소나, 전문성, 행동 방식 정의

**선택 속성:**
- **enable_human_tool**: 기본값 `true`
  - 정보나 명확한 설명을 위해 에이전트가 사용자에게 질문할 수 있도록 활성화

##### 4.2 Agent 생성

```sql
-- ===============================================
-- Step 4: Northwind Support Agent 생성
-- 설명: 고객 지원 업무를 수행할 에이전트 생성
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_AGENT(
    agent_name => 'Northwind_Support_Bot',
    attributes => '{
                    "profile_name": "NORTHWIND_AI",
                    "role": "You are an experienced Customer Support Representative for Northwind Traders with 10 years of experience. You specialize in handling product inquiries, order tracking, and return processing. You are patient, detail-oriented, and always prioritize customer satisfaction."
                  }'
  );
END;
/
```

---

**Role 작성 가이드:**

좋은 Role 예시:
```json
"role": "You are a senior data analyst at Northwind. You have deep knowledge 
         of the sales database and can provide insights on customer behavior, 
         product performance, and market trends. You explain data in simple terms."
```

나쁜 Role 예시:
```json
"role": "helpful assistant"  너무 모호함
```

##### 4.3 Agent 확인

```sql
-- ===============================================
-- Agent 목록 조회
-- 실행 계정: NORTHWIND
-- ===============================================
SELECT 
    AGENT_NAME,
    DESCRIPTION,
    CREATED
FROM USER_AI_AGENTS
WHERE AGENT_NAME = upper('Northwind_Support_Bot');
```

---

#### Step 5: 팀(Team) 구성 및 활성화

**Team**은 에이전트와 작업을 **연결**하는 최종 단계입니다. 팀을 활성화해야 에이전트를 사용할 수 있습니다.

##### 5.1 Team 개념

##### 5.2 Team 생성

```sql
-- ===============================================
-- Step 5.1: Team 생성
-- 설명: 에이전트와 Task를 연결하여 팀 구성
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TEAM(
    team_name  => 'Northwind_Support_Team',
    attributes => '{
                    "agents": [
                      {
                        "name": "Northwind_Support_Bot",
                        "task": "Customer_Service_Task"
                      }
                    ],
                    "process": "sequential"
                  }'
  );
END;
/
```

**Team 속성 설명:**
- `agents`: 팀에 포함된 에이전트 목록 (배열)
  - `name`: 에이전트 이름
  - `task`: 해당 에이전트가 수행할 작업
- `process`: 실행 방식
  - `sequential`: 에이전트들이 순서대로 실행 (현재 권장)
  - `parallel`: 동시 실행 (향후 지원 예정)

**참고**: 현재는 에이전트 1개만 사용하지만, 향후 여러 전문 에이전트를 협업시킬 수 있습니다.

##### 5.3 팀 활성화 (중요!)

**현재 세션에 팀을 활성화**해야 사용할 수 있습니다.

```sql
-- ===============================================
-- Step 5.2: Team 활성화
-- 설명: 현재 데이터베이스 세션에서 사용할 팀 지정
-- 실행 계정: NORTHWIND
-- ===============================================

EXEC DBMS_CLOUD_AI_AGENT.SET_TEAM('Northwind_Support_Team');

-- 활성화된 팀 확인
SELECT DBMS_CLOUD_AI_AGENT.GET_TEAM() AS ACTIVE_TEAM FROM DUAL;
```

**출력 예시:**
```
ACTIVE_TEAM
-------------------------
Northwind_Support_Team
```

**중요**: `SET_TEAM`은 **세션 단위**로 적용됩니다. 새로운 SQL 세션을 열면 다시 설정해야 합니다.

##### 5.4 Team 확인

```sql
-- ===============================================
-- Step 5.3: Team 정보 확인
-- 실행 계정: NORTHWIND
-- ===============================================

-- Team 목록
SELECT t.owner,
       t.agent_team_name,
       t.status,
       JSON_OBJECTAGG(
         a.attribute_name
         VALUE DBMS_LOB.SUBSTR(a.attribute_value, 4000, 1)
       ) AS team_config
FROM   dba_ai_agent_teams t
LEFT JOIN dba_ai_agent_team_attributes a
       ON t.owner           = a.owner
      AND t.agent_team_name = a.agent_team_name
WHERE t.AGENT_TEAM_NAME = upper('Northwind_Support_Team')
GROUP BY t.owner, t.agent_team_name, t.status
ORDER BY t.owner, t.agent_team_name;

-- Team 상세 정보 (에이전트-작업 매핑), table 권한 필요
SELECT t.owner,
       t.agent_team_name,
       t.status,
       JSON_OBJECTAGG(
         a.attribute_name
         VALUE DBMS_LOB.SUBSTR(a.attribute_value, 4000, 1)
       ) AS team_config
FROM   dba_ai_agent_teams t
LEFT JOIN dba_ai_agent_team_attributes a
       ON t.owner           = a.owner
      AND t.agent_team_name = a.agent_team_name
GROUP BY t.owner, t.agent_team_name, t.status
ORDER BY t.owner, t.agent_team_name;

```

---

#### Step 6: 에이전트 실행 및 테스트

드디어 에이전트를 사용할 시간입니다! `SELECT AI AGENT` 구문으로 자연어로 대화합니다.

##### 6.1 테스트 케이스 1: 단순 데이터 조회

**목적**: SQL Tool이 제대로 작동하는지 확인

```sql
-- ===============================================
-- 테스트 1-1: 제품 조회
-- 예상 tool: SQL_Analysis_Tool
-- 실행 계정: NORTHWIND
-- ===============================================

-- conversation ID 생성, 예: 45947AFB-7E7F-740E-E063-551A000A7755
DECLARE
    l_team_cov_id varchar2(4000);
BEGIN
    l_team_cov_id := DBMS_CLOUD_AI.create_conversation();
   DBMS_OUTPUT.PUT_LINE('Created conversation with ID: ' || l_team_cov_id);
END;
/

DECLARE
  l_res     CLOB;
BEGIN
  l_res := run_team_clob(
             p_team_name   => 'Northwind_Support_Team',
             p_user_prompt => 'query what is most expensive product?',
             p_params      => '{"conversation_id": "' || '45947AFB-7E7F-740E-E063-551A000A7755' || '"}'
           );

  DBMS_OUTPUT.PUT_LINE('conversation id: '  || '45947AFB-7E7F-740E-E063-551A000A7755' || '"}');
  DBMS_OUTPUT.PUT_LINE(DBMS_LOB.SUBSTR(l_res, 4000, 1));
END;
/

DECLARE
  l_res     CLOB;
BEGIN
  l_res := run_team_clob(
             p_team_name   => 'Northwind_Support_Team',
             p_user_prompt => 'What was last response?',
             p_params      => '{"conversation_id": "' || '45947AFB-7E7F-740E-E063-551A000A7755' || '"}'
           );

  DBMS_OUTPUT.PUT_LINE('conversation id: '  || '45947AFB-7E7F-740E-E063-551A000A7755' || '"}');
  DBMS_OUTPUT.PUT_LINE(DBMS_LOB.SUBSTR(l_res, 4000, 1));
END;
/

```

---

##### 6.2 테스트 케이스 2: 복합 추론 (Multi-turn)

**목적**: 에이전트가 여러 단계의 추론을 거쳐 작업을 완수하는지 확인

```sql
-- ===============================================
-- 테스트 2-1: 반품 요청 (모든 정보 제공)
-- 예상 tool: Return_Auth_Generator
-- 실행 계정: NORTHWIND
-- ===============================================

DECLARE
  l_res     CLOB;
BEGIN
  l_res := run_team_clob(
             p_team_name   => 'Northwind_Support_Team',
             p_user_prompt => 'I received order 10248 but it is defective. I need to return it.',
             p_params      => '{"conversation_id": "' || '45947AFB-7E7F-740E-E063-551A000A7755' || '"}'
           );

  DBMS_OUTPUT.PUT_LINE('conversation id: '  || '45947AFB-7E7F-740E-E063-551A000A7755' || '"}');
  DBMS_OUTPUT.PUT_LINE(DBMS_LOB.SUBSTR(l_res, 4000, 1));
END;
/

DECLARE
  l_res     CLOB;
BEGIN
  l_res := run_team_clob(
             p_team_name   => 'Northwind_Support_Team',
             p_user_prompt => 'What was last response?',
             p_params      => '{"conversation_id": "' || '45947AFB-7E7F-740E-E063-551A000A7755' || '"}'
           );

  DBMS_OUTPUT.PUT_LINE('conversation id: '  || '45947AFB-7E7F-740E-E063-551A000A7755' || '"}');
  DBMS_OUTPUT.PUT_LINE(DBMS_LOB.SUBSTR(l_res, 4000, 1));
END;
/

Select * from returns;

```

**대화 이력 조회 (Conversation History):**

멀티턴 대화의 전체 흐름을 추적하려면 다음 쿼리를 사용하세요.

```sql
-- ===============================================
-- 특정 대화 세션의 전체 이력 조회
-- 설명: 대화 제목과 각 턴의 프롬프트/응답을 시간 순으로 조회
-- 실행 계정: NORTHWIND
-- ===============================================

SELECT 
    c.CONVERSATION_TITLE,              -- 대화 제목 (첫 번째 프롬프트 기반)
    p.CONVERSATION_PROMPT_ID,          -- 각 턴의 고유 ID
    p.PROMPT,                          -- 사용자 질문
    SUBSTR(p.PROMPT_RESPONSE, 1, 100) AS RESPONSE_PREVIEW,  -- 응답 미리보기
    p.CREATED                          -- 실행 시각
FROM USER_CLOUD_AI_CONVERSATIONS c
JOIN USER_CLOUD_AI_CONVERSATION_PROMPTS p
    ON c.CONVERSATION_ID = p.CONVERSATION_ID
WHERE c.CONVERSATION_ID = '451951AB-96D9-0CE7-E063-1418000A4366'
ORDER BY p.CREATED ASC;
```

---

##### 6.3 에이전트 사고 과정 확인

에이전트가 어떤 추론(Thought) 과정을 거쳤는지 확인할 수 있습니다.

```sql
-- ===============================================
-- Step 6.3: 에이전트 실행 히스토리 및 사고 과정 조회
-- 뷰: USER_CLOUD_AI_CONVERSATION_PROMPTS
-- 목적: AI Agent 호출 내역 추적, 디버깅, 감사
-- ===============================================

-- 최근 10개의 AI Agent 호출 내역 조회
SELECT 
     CONVERSATION_PROMPT_ID,    -- 고유 프롬프트 ID
     CONVERSATION_ID,            -- 대화 세션 ID (멀티턴 대화 추적용)
     CONVERSATION_TITLE,         -- 대화 제목
     PROFILE_NAME,               -- 사용된 AI 프로파일 (예: NORTHWIND_AI)
     PROMPT_ACTION,              -- 액션 유형 (AGENT, SQL, RAG 등)
     PROMPT,                     -- 사용자가 입력한 프롬프트
     PROMPT_RESPONSE,            -- AI Agent의 응답
     CREATED,                    -- 실행 시각
     CLIENT_IP,                  -- 클라이언트 IP
     SID,                        -- 세션 ID
     SERIAL#                     -- 세션 시리얼 번호
FROM USER_CLOUD_AI_CONVERSATION_PROMPTS
ORDER BY CREATED DESC
FETCH FIRST 10 ROWS ONLY;
```

**컬럼 설명 및 활용:**

| 컬럼명 | 설명 | 활용 예시 |
|--------|------|-----------|
| `CONVERSATION_PROMPT_ID` | 각 프롬프트의 고유 ID | 특정 실행 결과 추적 |
| `CONVERSATION_ID` | 대화 세션 ID | 멀티턴 대화 내역 그룹핑 |
| `CONVERSATION_TITLE` | 대화 제목 | 대화 주제별 분류 |
| `PROFILE_NAME` | 사용된 AI 프로파일 | 어떤 LLM이 사용되었는지 확인 |
| `PROMPT_ACTION` | 액션 유형 | AGENT, SQL, RAG 등 구분 |
| `PROMPT` | 입력 프롬프트 | 사용자 질문 확인 |
| `PROMPT_RESPONSE` | AI 응답 | 응답 품질 평가 |
| `CREATED` | 실행 시각 | 성능 분석, 시간대별 사용량 |
| `CLIENT_IP` | 클라이언트 IP | 보안 감사, 접근 추적 |
| `SID`, `SERIAL#` | 세션 정보 | 특정 세션의 모든 실행 추적 |


**5. 에이전트 오류 디버깅**
```sql
-- ===============================================
-- 에러가 포함된 응답 찾기
-- 실행 계정: NORTHWIND
-- ===============================================
SELECT 
    CONVERSATION_PROMPT_ID,
    PROMPT,
    PROMPT_RESPONSE,
    CREATED
FROM USER_CLOUD_AI_CONVERSATION_PROMPTS
WHERE UPPER(PROMPT_RESPONSE) LIKE '%ERROR%'
   OR UPPER(PROMPT_RESPONSE) LIKE '%ORA-%'
   OR UPPER(PROMPT_RESPONSE) LIKE '%FAILED%'
ORDER BY CREATED DESC;
```

---

#### Step 7: 고급 Tool - RAG, WebSearch, Notification

Select AI Agent는 SQL/PL/SQL 외에도 다양한 내장 tool를 지원합니다.

##### 7.1 RAG Tool (문서 검색)

**사용 사례**: 제품 매뉴얼, FAQ, 정책 문서 검색

```sql
-- ===============================================
-- RAG Tool 설정 - Object Storage 확인
-- 실행 계정: NORTHWIND
-- ===============================================

SELECT object_name, bytes 
FROM DBMS_CLOUD.LIST_OBJECTS(
    credential_name => 'OCI_KEY_CRED',
    location_uri    => 'https://swiftobjectstorage.us-chicago-1.oraclecloud.com/v1/apackrsct01/AIDP_OS'
);
/


BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
      profile_name => 'EMBED_PROFILE',
      attributes   => '{
          "provider": "oci",
          "credential_name": "OCI_KEY_CRED", 
          "embedding_model": "cohere.embed-v4.0"
      }'
  );
END;
/

BEGIN
  DBMS_CLOUD_AI.CREATE_VECTOR_INDEX(
    index_name => 'RAG_INDEX',
    attributes => '{
        "vector_db_provider": "oracle",
        "location": "https://swiftobjectstorage.us-chicago-1.oraclecloud.com/v1/apackrsct01/AIDP_OS",
        "object_storage_credential_name": "OCI_KEY_CRED",
        "profile_name": "EMBED_PROFILE",
        "vector_dimension": 1536,
        "vector_distance_metric": "cosine",
        "chunk_overlap": 128,
        "chunk_size": 1024
    }'
  );
END;
/

BEGIN
DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'RAG_PROFILE',
    attributes =>'{"provider": "oci",
        "credential_name": "OCI_KEY_CRED",
        "vector_index_name": "RAG_INDEX",
        "oci_compartment_id": "ocid1.compartment.oc1..aaaaaaaam3amapwxz6nyciqzb2v2iwg66t22g47vabo5ilnghbsskooeop3q",
        "temperature": 0.2,
        "max_tokens": 3000
    }');
END;
/

BEGIN
DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'RAG_TOOL',
    attributes => '{"tool_type": "RAG",
        "tool_params": {"profile_name": "RAG_PROFILE"}}'
    );
END;
/
```

##### 7.2 WebSearch Tool (인터넷 검색)

**사용 사례**: 최신 정보, 환율, 경쟁사 정보 조회, openai를 사용해서 호출해야 함

```sql
-- ===============================================
-- WebSearch Tool 생성 - OpenAI Credential
-- 실행 계정: NORTHWIND
-- ===============================================
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'OPENAI_CRED',
    username        => 'OPENAI',
    password        => ''
  );
END;
/

EXEC DBMS_CLOUD_AI_AGENT.DROP_TOOL('Websearch');
/

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name  => 'Websearch',
    attributes => '{
      "instruction": "검색어 관련 최신 가격/설명/뉴스를 웹에서 조회해 간단 요약",
      "tool_type": "WEBSEARCH",
      "tool_params": { "credential_name": "OPENAI_CRED" }
    }'
  );
END;
/
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TASK(
    task_name  => 'web_task',
    attributes => '{
      "instruction": "사용자 질문의 핵심 키워드를 뽑아 Websearch로 조회 후 5줄 이내로 요약, deal with customer inquiry based on user request:{query}",
      "tools": ["Websearch"]
    }'
  );
END;
/

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_AGENT(
    agent_name => 'A_WEB_SEARCHER',
    profile_name => 'WEBSEARCH_PROFILE',
    description => 'Agent that uses web search'
  );
END;
/

BEGIN
    DBMS_CLOUD_AI_AGENT.DROP_TEAM(team_name => 'WEB_TEAM', force => true);
    DBMS_CLOUD_AI_AGENT.CREATE_TEAM(
        team_name => 'WEB_TEAM',
        attributes => '{"agents": [{"name":"A_WEB_SEARCHER","task" : "web_task"}],
        "process": "sequential"
        }');
END;
/

DECLARE
l_answer CLOB;
    BEGIN
        l_answer := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
            team_name => 'WEB_TEAM',
            user_prompt => 'samsung electronic top 5 news for its stock today in Korean, and it should be not more than 1000 character',
            params => '{"conversation_id":"sess-ops-001"}'
        );
    DBMS_OUTPUT.PUT_LINE(l_answer);
END;
/

DECLARE
l_answer CLOB;
    BEGIN
        l_answer := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
            team_name => 'WEB_TEAM',
            user_prompt => 'what was last response',
            params => '{"conversation_id":"sess-ops-001"}'
        );
    DBMS_OUTPUT.PUT_LINE(l_answer);
END;
/

```


##### 7.3 Notification Tool (이메일/Slack)

**사용 사례**: 주문 확인 이메일, 재고 부족 알림

**전제조건: ADMIN 계정에서 권한 및 네트워크 ACL 설정**

```sql
-- ===============================================
-- 사전 작업: ADMIN 계정에서 실행 필수!
-- ===============================================

-- 1. SMTP 서버 접근을 위한 네트워크 ACL 설정
-- 설명: OCI Email Delivery Service를 통한 이메일 발송을 위해
--       SMTP 서버(smtp.email.us-chicago-1.oci.oraclecloud.com:587)에 
--       접근할 수 있도록 ACL 권한 부여, DB가 있는 region의 host 주소여야 함
BEGIN
  DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
    host       => 'smtp.email.us-chicago-1.oci.oraclecloud.com',
    lower_port => 587,
    upper_port => 587,
    ace        => xs$ace_type(
      privilege_list => xs$name_list('connect'),
      principal_name => 'NORTHWIND',
      principal_type => xs_acl.ptype_db
    )
  );
END;
/

```

**Email Notification 완전한 설정 및 실행 예제 (NORTHWIND 계정):**

**Step 1: OCI SMTP Credential 생성**

먼저 OCI Console에서 SMTP Credential을 생성해야 합니다:

1. **OCI Console** → **Identity & Security** → **Domains** → **Default Domain**
2. **Users** → 본인 계정 선택
3. **SMTP Credentials** → **Generate SMTP Credentials**
4. Username과 Password를 안전하게 저장 (Password는 한 번만 표시됨)

**Username 형식 예시:**
```
ocid1.user.oc1..aaaaaaaabezhmtxdqakpleu4mrcuivzn75hsi3wvkyn6wmbeg7afg6kfqnnq@ocid1.tenancy.oc1..aaaaaaaa6ma7kq3bsif76uzqidv22cajs3fpesgpqmmsgxihlbcemkklrsqa.fu.com
```

**Step 2: Database에 SMTP Credential 등록**

```sql
-- ===============================================
-- OCI SMTP Credential을 Database에 등록
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'OCI_SMTP_CRED',
    username        => 'ocid1.user.oc1..aaaaaaaabezhmtxdqakpleu4mrcuivzn75hsi3wvkyn6wmbeg7afg6kfqnnq@ocid1.tenancy.oc1..aaaaaaaa6ma7kq3bsif76uzqidv22cajs3fpesgpqmmsgxihlbcemkklrsqa.fu.com',
    password        => ''  -- OCI에서 생성된 SMTP Password
  );
END;
/

```

**Step 3: Email Notification Tool 생성**

```sql
-- ===============================================
-- Email Notification Tool 생성
-- 전제조건: Credential, ACL 설정 완료
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.DROP_TOOL('EMAIL_NOTIFY');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name  => 'EMAIL_NOTIFY',
    attributes => '{
      "tool_type": "NOTIFICATION",
      "tool_params": {
        "notification_type": "EMAIL",
        "credential_name": "OCI_SMTP_CRED",
        "smtp_host": "smtp.email.us-chicago-1.oci.oraclecloud.com",
        "smtp_port": 587,
        "sender": "jmko79@gmail.com",
        "recipient": "jmko79@gmail.com",
        "encryption": "STARTTLS"
      }
    }',
    description => 'Sends email notifications via OCI Email Delivery Service. Use when user requests to send email alerts or notifications.'
  );
END;
/

```

**파라미터 설명:**

| 파라미터 | 설명 | 예시 값 |
|----------|------|---------|
| `notification_type` | 알림 유형 | `EMAIL` (대문자 필수) |
| `credential_name` | SMTP 인증 정보 | `OCI_SMTP_CRED` |
| `smtp_host` | SMTP 서버 주소 | `smtp.email.us-chicago-1.oci.oraclecloud.com` |
| `smtp_port` | SMTP 포트 | `587` (STARTTLS) 또는 `465` (SSL) |
| `sender` | 발신자 이메일 | 승인된 이메일 주소 |
| `recipient` | 수신자 이메일 (선택) | 기본 수신자 |
| `encryption` | 암호화 방식 | `STARTTLS` 또는 `SSL` |

**Step 4: Email Alert Task 생성**

```sql
-- ===============================================
-- Email Notification을 위한 Task 생성
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.DROP_TASK('EMAIL_ALERT_TASK');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TASK(
    task_name  => 'EMAIL_ALERT_TASK',
    attributes => '{
      "instruction": "When the user asks to send a notification or email, use EMAIL_NOTIFY tool to send the email,  deal with customer inquiry based on user request:{query}",
      "tools": ["EMAIL_NOTIFY"]
    }'
  );
END;
/

```

**Step 5: Email Alert Agent 생성**

```sql
-- ===============================================
-- Email 발송을 담당하는 Agent 생성
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.DROP_AGENT('EmailAlertAgent');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_AGENT(
    agent_name => 'EmailAlertAgent',
    attributes => '{
      "profile_name": "NORTHWIND_AI",
      "role": "You are an email notification assistant. When asked to send an email, use the EMAIL_NOTIFY tool to deliver the message. Be concise and confirm the action."
    }'
  );
END;
/

```

**Step 6: Email Notification Team 생성**

```sql
-- ===============================================
-- Email Notification Team 생성
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.DROP_TEAM('EMAIL_NOTIFICATION_TEAM');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TEAM(
    team_name  => 'EMAIL_NOTIFICATION_TEAM',
    attributes => '{
      "agents": [
        {
          "name": "EmailAlertAgent",
          "task": "EMAIL_ALERT_TASK"
        }
      ],
      "process": "sequential"
    }'
  );
END;
/

```

**Step 7: Email 발송 실행**

```sql
-- ===============================================
-- Email Notification 실행 테스트
-- 실행 계정: NORTHWIND
-- ===============================================

SET SERVEROUTPUT ON SIZE UNLIMITED;

DECLARE
  v_response CLOB;
  v_conv_id  VARCHAR2(4000);
BEGIN
  -- 1. 새로운 대화 세션 생성
  v_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION();
  
  -- 2. Email 발송 요청
  v_response := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
    team_name   => 'EMAIL_NOTIFICATION_TEAM',
    user_prompt => 'Send an email notification saying: Oracle Select AI Agent test successful.',
    params      => '{"conversation_id": "' || v_conv_id || '"}'
  );
  
  -- 3. 결과 출력
  DBMS_OUTPUT.PUT_LINE('=== Email Notification Result ===');
  DBMS_OUTPUT.PUT_LINE('Conversation ID: ' || v_conv_id);
  DBMS_OUTPUT.PUT_LINE('Response: ' || DBMS_LOB.SUBSTR(v_response, 4000, 1));
END;

/

```

**실행 히스토리 확인:**

```sql
-- ===============================================
-- Email 발송 히스토리 조회
-- 실행 계정: NORTHWIND
-- ===============================================
SELECT 
    TOOL_NAME,
    SUBSTR(INPUT, 1, 100) AS INPUT_PREVIEW,
    SUBSTR(TOOL_OUTPUT, 1, 200) AS OUTPUT_PREVIEW,
    START_DATE,
    (END_DATE - START_DATE) * 24 * 3600 AS DURATION_SEC
FROM USER_AI_AGENT_TOOL_HISTORY
WHERE TOOL_NAME = 'EMAIL_NOTIFY'
ORDER BY START_DATE DESC
FETCH FIRST 10 ROWS ONLY;

-- 대화 히스토리에서 이메일 요청 확인
SELECT 
    CONVERSATION_ID,
    PROMPT,
    SUBSTR(PROMPT_RESPONSE, 1, 200) AS RESPONSE_PREVIEW,
    CREATED
FROM USER_CLOUD_AI_CONVERSATION_PROMPTS
WHERE UPPER(PROMPT) LIKE '%EMAIL%' 
   OR UPPER(PROMPT) LIKE '%NOTIFICATION%'
ORDER BY CREATED DESC
FETCH FIRST 10 ROWS ONLY;
```
