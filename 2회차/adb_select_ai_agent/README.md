# Oracle Autonomous AI Database: Select AI Agent 교육 과정

## 문서 개요

본 교육 과정은 Oracle Autonomous Database의 **Select AI Agent** 기능을 활용하여 지능형 자율 에이전트를 구축하는 방법을 단계별로 학습합니다.

### 학습 목표
1. Select AI Agent의 핵심 개념과 아키텍처 이해
2. ReAct (Reasoning and Acting) 패턴 학습
3. Northwind 데이터베이스를 활용한 실전 에이전트 구축
4. Python을 통한 에이전트 애플리케이션 개발

### 사전 요구사항
- Oracle Autonomous Database 접근 권한
- SQL 기본 지식
- Python 기초 (선택사항)
- NORTHWIND_AI 프로파일 생성 완료 (1회차 실습)

### 예상 소요 시간
- **1부 (개념)**: 30분
- **2부 (핸즈온)**: 60분
- **3부 (Python SDK)**: 30분
- **4부 (심화)**: 선택사항
- **총계**: 약 2시간

---

## 목차

### [1부] Select AI Agent 개념 및 아키텍처
1. Select AI Agent란 무엇인가?
   - 핵심 개념
   - 주요 기능
2. 작동 원리: ReAct 패턴
   - ReAct 사이클
   - 실행 예시
3. 아키텍처 및 구성 요소
   - 4계층 아키텍처
   - 4가지 핵심 객체 (Tool, Task, Agent, Team)

### [2부] 핸즈온: Northwind 스마트 에이전트 구축
- **Step 1**: 사전 준비 및 권한 설정
- **Step 2**: 도구(Tool) 생성
  - SQL Tool (데이터 조회)
  - PL/SQL Tool (반품 처리)
- **Step 3**: 작업(Task) 생성
- **Step 4**: 에이전트(Agent) 생성
- **Step 5**: 팀(Team) 구성 및 활성화
- **Step 6**: 에이전트 실행 및 테스트
  - 단순 조회 테스트
  - 복합 추론 테스트
  - Human Tool 테스트
  - 트러블슈팅

### [3부] 고급 기능: Python SDK로 Agent 제어
- **Step 7**: Python 환경 설정
- **Step 8**: Python에서 Agent 실행
- **Step 9**: 멀티턴 대화 구현
- **Step 10**: 웹 API로 Agent 노출 (FastAPI)
- **Step 11**: 고급 Tool (RAG, WebSearch, Notification)
- **Step 12**: 실전 응용 예제
- **Step 13**: Built-in Tools 확장 가이드

### [4부] 참고 자료 및 심화 학습
- 주요 패키지 및 함수
- 데이터 딕셔너리 뷰
- 유용한 관리 쿼리
- 트러블슈팅 가이드
- 보안 Best Practices
- 성능 최적화

### [5부] 실습 가이드
- 20분 빠른 시작 가이드
- FAQ (자주 묻는 질문)
- 다음 단계
- 연습 문제
- 실전 프로젝트 아이디어

---

## [1부] Select AI Agent 개념 및 아키텍처

### 1. Select AI Agent란 무엇인가?

**Select AI Agent**는 Oracle Autonomous Database에 내장된 대화형 자율 에이전트 프레임워크입니다. 

#### 핵심 개념
기존 Select AI가 **단순 질의응답**에 집중했다면, Select AI Agent는 **복잡한 작업을 스스로 계획하고 실행**할 수 있는 진정한 의미의 AI 에이전트입니다.

```
┌─────────────────────────────────────────────────────┐
│  사용자: "지난 달 가장 많이 팔린 제품의           │
│           재고가 얼마나 남았는지 확인하고,          │
│           부족하면 발주 요청서를 작성해줘"         │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Select AI Agent                                 │
│  1. SQL로 판매 데이터 조회 (SQL Tool)               │
│  2. 재고 정보 확인 (SQL Tool)                       │
│  3. 발주 필요 여부 판단 (Reasoning)                 │
│  4. 발주 요청서 생성 (PL/SQL Tool)                  │
│  5. 결과 리포트 작성 (Final Response)               │
└─────────────────────────────────────────────────────┘
```

#### 핵심 기능 (Key Features)

##### 1.1 통합 지능 (Integrated Intelligence)
에이전트는 다음 3가지 능력을 통합합니다:
- **계획(Planning)**: 복잡한 작업을 단계별로 분해
- **도구 사용(Tool Use)**: 데이터베이스 조회, 함수 호출, API 실행
- **성찰(Reflection)**: 중간 결과를 검토하고 계획 수정

##### 1.2 유연한 도구 (Flexible Tooling)
다양한 도구를 에이전트가 자유롭게 활용할 수 있습니다:
| 도구 유형 | 설명 | 예시 |
|----------|------|------|
| **SQL Tool** | NL2SQL을 통한 데이터 조회 | "고객 목록 보여줘" |
| **RAG Tool** | 벡터 검색으로 문서 검색 | "제품 매뉴얼에서 A/S 정책 찾아줘" |
| **PL/SQL Tool** | 사용자 정의 함수 실행 | 재고 업데이트, 주문 생성 |
| **REST API Tool** | 외부 시스템 연동 | Slack 알림, 이메일 발송 |
| **WebSearch Tool** | 인터넷 정보 검색 | 최신 환율 정보 |

##### 1.3 문맥 인식 대화 (Context-Aware Conversations)
- **단기 기억**: 현재 대화 세션의 문맥 유지
- **장기 기억**: 이전 대화 내용 기반 개인화된 응답
- **멀티턴 대화**: 추가 질문을 통해 정보 수집

##### 1.4 확장성 및 보안 (Scalable and Secure)
데이터베이스 내부에서 실행되므로:
- 데이터 이동 없이 안전한 처리
- DB의 접근 제어 및 감사 기능 활용
- 고성능 병렬 처리
- 엔터프라이즈급 안정성

---

### 2. 작동 원리: ReAct 패턴

Select AI Agent는 **ReAct (Reasoning and Acting)** 패턴을 사용합니다. 이는 Google DeepMind와 Princeton 대학이 제안한 방법론으로, LLM이 추론과 행동을 반복하며 문제를 해결하도록 합니다.

#### ReAct 사이클

```
┌────────────────────────────────────────────────────┐
│  Query (질문)                                   │
│  "이번 달 매출이 가장 높은 고객은 누구야?"          │
└────────────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────────────┐
│  Thought (사고)                                 │
│  "매출 정보를 보려면 Orders 테이블을 조회해야 해"   │
└────────────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────────────┐
│  Action (행동)                                  │
│  SQL_Tool 실행: SELECT customer_id, SUM(amount)... │
└────────────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────────────┐
│  Observation (관찰)                             │
│  결과: CustomerID=5, Total=₩15,000,000             │
└────────────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────────────┐
│  Thought (재사고)                               │
│  "고객 이름을 확인하려면 Customers 테이블 필요"     │
└────────────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────────────┐
│  Action (재행동)                                │
│  SQL_Tool 실행: SELECT company_name FROM...        │
└────────────────────────────────────────────────────┘
                 ↓
┌────────────────────────────────────────────────────┐
│  Final Response (최종 답변)                     │
│  "이번 달 가장 많이 구매하신 고객은                 │
│   'ABC Company'이며, 총 ₩15,000,000입니다."       │
└────────────────────────────────────────────────────┘
```

#### ReAct 실행 예시 (실제 로그)

실제 에이전트 실행 시 다음과 같은 로그를 확인할 수 있습니다:

```
Thought: 사용자가 주문 10248에 대한 반품을 요청했다. 
         먼저 이 주문이 존재하는지 확인해야 한다.

Action: SQL_Analysis_Tool
Action Input: {"query": "주문 10248의 상세 정보를 보여줘"}

Observation: Order ID 10248, Customer: VINET, Product: Queso Cabrales, Amount: $440

Thought: 주문이 확인되었다. 이제 반품 승인 번호(RMA)를 생성해야 한다.

Action: Return_Auth_Generator
Action Input: {"order_id": 10248, "reason": "defective"}

Observation: RMA-10248-def-742

Final Answer: 주문 10248에 대한 반품이 접수되었습니다. 
              RMA 번호는 RMA-10248-def-742입니다.
```

---

### 3. 아키텍처 및 구성 요소

Select AI Agent는 **4계층 아키텍처**를 통해 지능형 작업을 수행합니다.

#### 4계층 아키텍처

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Planning (계획)                           │
│  - 작업을 단계별로 분해                              │
│  - 도구 선택 및 실행 순서 결정                       │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Layer 2: Tool Use (도구 사용)                       │
│  - 선택된 도구를 실제로 실행                         │
│  - 파라미터 생성 및 결과 수집                        │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Layer 3: Reflection (성찰)                         │
│  - 실행 결과 평가                                    │
│  - 추가 작업 필요 여부 판단                          │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Layer 4: Memory Management (기억 관리)              │
│  - 대화 컨텍스트 저장                                │
│  - 이전 대화 참조                                    │
└─────────────────────────────────────────────────────┘
```

#### 4가지 핵심 객체

Select AI Agent는 다음 4가지 객체의 조합으로 동작합니다:

##### 3.1 Agent (에이전트)
**특정 목적을 위해 설정된 작업자**

```sql
CREATE_AGENT(
    agent_name => 'Northwind_Support_Bot',
    attributes => '{
        "profile_name": "NORTHWIND_AI",          -- 사용할 LLM 프로파일
        "role": "고객 지원 담당자. 주문과 반품을 처리합니다."
    }'
)
```

- **AI 프로파일**: 사용할 LLM 모델 지정 (GPT-4, Claude, Cohere 등)
- **역할(Role)**: 에이전트의 페르소나와 행동 방식 정의
- 하나의 에이전트는 여러 작업(Task)을 수행할 수 있습니다

##### 3.2 Tool (도구)
**에이전트가 수행할 수 있는 구체적인 행동**

```sql
CREATE_TOOL(
    tool_name => 'SQL_Analysis_Tool',
    attributes => '{
        "tool_type": "SQL",
        "tool_params": {"profile_name": "NORTHWIND_AI"}
    }',
    description => '데이터베이스 테이블을 조회하는 도구'
)
```

**도구 유형별 예시:**
| 도구 유형 | 생성 방법 | 사용 사례 |
|----------|----------|----------|
| `SQL` | `tool_type: "SQL"` | 자연어 → SQL 쿼리 실행 |
| `PL/SQL Function` | `function: "함수명"` | 비즈니스 로직 실행 |
| `RAG` | `tool_type: "RAG"` | 벡터 검색으로 문서 찾기 |
| `REST API` | `endpoint_url: "..."` | 외부 시스템 호출 |

##### 3.3 Task (작업)
**에이전트가 수행해야 할 업무 단위**

```sql
CREATE_TASK(
    task_name => 'Customer_Service_Task',
    attributes => '{
        "instruction": "
            1. 제품/주문 문의 → SQL_Analysis_Tool 사용
            2. 반품 요청 → Return_Auth_Generator 사용
            3. 항상 친절하게 응대
        ",
        "tools": ["SQL_Analysis_Tool", "Return_Auth_Generator"],
        "enable_human_tool": "true"    -- 사용자에게 추가 정보 요청 가능
    }'
)
```

**Task는 다음을 정의합니다:**
- **목표**: 무엇을 달성할 것인가?
- **지침**: 어떻게 수행할 것인가?
- **도구 목록**: 어떤 도구를 사용할 수 있는가?

##### 3.4 Agent Team (팀)
**여러 에이전트의 협업 단위**

```sql
CREATE_TEAM(
    team_name => 'Northwind_Support_Team',
    attributes => '{
        "agents": [
            {"name": "Northwind_Support_Bot", "task": "Customer_Service_Task"}
        ],
        "process": "sequential"    -- 순차 실행 (또는 "parallel")
    }'
)
```

**팀의 실행 모드:**
- `sequential`: 에이전트들이 순서대로 작업 수행
- `parallel`: 여러 에이전트가 동시에 작업 수행 (향후 지원 예정)

#### 객체 간 관계도

```
┌──────────────────────────────────────────────────┐
│  TEAM: Northwind_Support_Team                    │
│  ├─ AGENT: Northwind_Support_Bot                 │
│  │   ├─ Profile: NORTHWIND_AI (GPT-4)            │
│  │   └─ Role: 고객 지원 담당자                    │
│  │                                                │
│  └─ TASK: Customer_Service_Task                  │
│      ├─ TOOL: SQL_Analysis_Tool                  │
│      └─ TOOL: Return_Auth_Generator              │
└──────────────────────────────────────────────────┘
```

**실행 흐름:**
1. 사용자가 팀에 요청 → `SET_TEAM('Northwind_Support_Team')`
2. 팀이 에이전트에게 작업 할당 → `Northwind_Support_Bot`
3. 에이전트가 작업(Task) 실행 → `Customer_Service_Task`
4. 작업에 정의된 도구들을 ReAct 패턴으로 사용 → `SQL_Analysis_Tool`, `Return_Auth_Generator`

---

## [2부] 핸즈온: Northwind 스마트 에이전트 구축하기

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

### Step 1: 사전 준비 및 권한 설정

#### 1.1 필요 권한 확인

Select AI Agent를 사용하려면 다음 패키지에 대한 실행 권한이 필요합니다:
- `DBMS_CLOUD_AI_AGENT` - 에이전트 생성 및 관리
- `DBMS_CLOUD_AI` - AI 프로파일 사용

#### 1.2 권한 부여 (ADMIN 계정에서 실행)

```sql
-- ===============================================
-- Step 1.2: 권한 부여
-- 설명: NORTHWIND 사용자에게 Agent 사용 권한 부여
-- 실행 계정: ADMIN
-- ===============================================

-- Agent 패키지 실행 권한
GRANT EXECUTE ON DBMS_CLOUD_AI_AGENT TO NORTHWIND;
GRANT EXECUTE ON DBMS_CLOUD_AI TO NORTHWIND;

-- 확인
SELECT * FROM DBA_TAB_PRIVS 
WHERE GRANTEE = 'NORTHWIND' 
  AND TABLE_NAME LIKE 'DBMS_CLOUD%';
```

**팁**: 권한이 제대로 부여되었는지 확인하세요. `EXECUTE` 권한이 두 개의 패키지에 모두 있어야 합니다.

#### 1.3 네트워크 ACL 설정 (선택사항)

외부 API(WebSearch, 이메일 등)를 사용할 경우 네트워크 접근 권한이 필요합니다.

```sql
-- ===============================================
-- Step 1.3: 네트워크 ACL 설정 (선택사항)
-- 설명: 외부 API 사용을 위한 네트워크 접근 권한
-- 실행 계정: ADMIN
-- 실습 필수 여부: (SQL/PL/SQL Tool만 사용 시 불필요)
-- ===============================================

BEGIN
  -- OpenAI API 접근 권한 (예시)
  DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
    host => 'api.openai.com',
    ace  => xs$ace_type(
              privilege_list => xs$name_list('http', 'https'),
              principal_name => 'NORTHWIND',
              principal_type => xs_acl.ptype_db
            )
  );
  
  -- Cohere API 접근 권한 (예시)
  DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
    host => 'api.cohere.ai',
    ace  => xs$ace_type(
              privilege_list => xs$name_list('http', 'https'),
              principal_name => 'NORTHWIND',
              principal_type => xs_acl.ptype_db
            )
  );
END;
/

-- ACL 설정 확인
SELECT HOST, LOWER_PORT, UPPER_PORT, ACE_ORDER
FROM DBA_NETWORK_ACLS
WHERE ACL LIKE '%NORTHWIND%';
```

#### 1.4 AI 프로파일 확인

1회차에서 생성한 `NORTHWIND_AI` 프로파일이 있는지 확인합니다.

```sql
-- ===============================================
-- Step 1.4: AI 프로파일 확인
-- 설명: Select AI Agent가 사용할 LLM 프로파일 확인
-- 실행 계정: NORTHWIND
-- ===============================================

-- 프로파일 목록 조회
SELECT PROFILE_NAME, PROVIDER, MODEL, STATUS
FROM USER_CLOUD_AI_PROFILES
WHERE PROFILE_NAME = 'NORTHWIND_AI';

-- 만약 없다면 생성 (1회차 참조)
-- BEGIN
--   DBMS_CLOUD_AI.CREATE_PROFILE(
--     profile_name => 'NORTHWIND_AI',
--     attributes   => '{"provider": "openai", 
--                       "credential_name": "OPENAI_CRED",
--                       "model": "gpt-4"}'
--   );
-- END;
-- /
```

**Step 1 체크리스트:**
- [ ] DBMS_CLOUD_AI_AGENT 실행 권한 있음
- [ ] DBMS_CLOUD_AI 실행 권한 있음
- [ ] NORTHWIND_AI 프로파일 존재 확인
- [ ] (선택) 네트워크 ACL 설정 완료

---

### Step 2: 도구(Tool) 생성

에이전트가 사용할 **무기**를 만듭니다. 도구는 에이전트가 실제로 작업을 수행하는 수단입니다.

#### 2.1 SQL Tool 생성 (데이터 조회용)

**목적**: 자연어 질문을 SQL 쿼리로 변환하여 데이터베이스를 조회하는 도구

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
SELECT TOOL_NAME, TOOL_TYPE, DESCRIPTION 
FROM USER_AI_AGENT_TOOLS
WHERE TOOL_NAME = 'SQL_Analysis_Tool';
```

**Tool 속성 설명:**
- `tool_name`: 도구의 고유 이름 (에이전트가 이 이름으로 도구를 호출)
- `tool_type`: `SQL` - 이 도구가 SQL 쿼리 실행 도구임을 명시
- `tool_params.profile_name`: 사용할 AI 프로파일 (NL2SQL 변환에 사용)
- `description`: 에이전트가 **이 설명을 보고** 언제 이 도구를 사용할지 판단합니다

**중요**: `description`이 매우 중요합니다! 에이전트는 이 설명을 읽고 도구 사용 여부를 결정하므로, 명확하고 구체적으로 작성하세요.

---

#### 2.2 PL/SQL Tool 생성 (반품 처리 로직)

**목적**: 실제 비즈니스 로직을 수행하는 도구 (RMA 번호 생성)

**배경**: SQL Tool은 **조회**만 가능합니다. 데이터를 생성하거나 복잡한 로직을 실행하려면 PL/SQL 함수가 필요합니다.

##### 2.2.1 비즈니스 로직 함수 생성

```sql
-- ===============================================
-- Step 2.2.1: 반품 승인 번호 생성 함수
-- 설명: RMA (Return Merchandise Authorization) 번호를 생성하는 PL/SQL 함수
-- 실행 계정: NORTHWIND
-- ===============================================

CREATE OR REPLACE FUNCTION generate_return_auth (
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
    -- INSERT INTO returns (rma_number, order_id, reason, created_date)
    -- VALUES (v_rma_number, p_order_id, p_reason, SYSDATE);
    
    RETURN v_rma_number;
END;
/

-- 함수 테스트
SELECT generate_return_auth(10248, 'defective') AS RMA_NUMBER FROM DUAL;
SELECT generate_return_auth(10249, 'wrong item') AS RMA_NUMBER FROM DUAL;
```

**출력 예시:**
```
RMA_NUMBER
-----------------------
RMA-10248-def-742
RMA-10249-wro-581
```

##### 2.2.2 함수를 Agent Tool로 등록

```sql
-- ===============================================
-- Step 2.2.2: PL/SQL Tool 등록
-- 설명: generate_return_auth 함수를 에이전트 도구로 등록
-- 실행 계정: NORTHWIND
-- ===============================================

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
SELECT TOOL_NAME, TOOL_TYPE, DESCRIPTION 
FROM USER_AI_AGENT_TOOLS
WHERE TOOL_NAME = 'Return_Auth_Generator';
```

**PL/SQL Tool 속성 설명:**
- `instruction`: 도구를 **어떻게 사용**하는지 상세 설명
  - 필요한 파라미터 명시 (order_id, reason)
  - 파라미터 타입 명시 (number, string)
- `function`: 실제 실행할 PL/SQL 함수 이름
- `description`: 도구를 **언제 사용**하는지 설명

**Instruction vs Description:**
- `description`: "언제" 이 도구를 사용하는가? (에이전트의 도구 선택 기준)
- `instruction`: "어떻게" 이 도구를 사용하는가? (파라미터, 사용법)

---

#### 2.3 생성된 도구 확인

```sql
-- ===============================================
-- Step 2.3: 생성된 도구 목록 확인
-- 실행 계정: NORTHWIND
-- ===============================================

-- 모든 도구 조회
SELECT 
    TOOL_NAME,
    TOOL_TYPE,
    SUBSTR(DESCRIPTION, 1, 50) AS SHORT_DESC,
    CREATED
FROM USER_AI_AGENT_TOOLS
ORDER BY CREATED DESC;

-- 도구 상세 정보 (JSON 형식)
SELECT 
    TOOL_NAME,
    JSON_QUERY(ATTRIBUTES, '$' PRETTY) AS ATTRIBUTES_DETAIL
FROM USER_AI_AGENT_TOOLS
WHERE TOOL_NAME IN ('SQL_Analysis_Tool', 'Return_Auth_Generator');
```

**예상 출력:**
```
TOOL_NAME              TOOL_TYPE    SHORT_DESC
--------------------- ------------ ---------------------------
Return_Auth_Generator PLSQL        Generates RMA numbers for...
SQL_Analysis_Tool     SQL          Queries the database for...
```

**Step 2 체크리스트:**
- [ ] SQL_Analysis_Tool 생성 완료
- [ ] generate_return_auth 함수 생성 및 테스트 완료
- [ ] Return_Auth_Generator Tool 등록 완료
- [ ] USER_AI_AGENT_TOOLS 뷰에서 두 도구 확인

---

### Step 3: 작업(Task) 생성

**Task**는 에이전트의 **업무 매뉴얼**입니다. 무엇을 하고, 어떻게 할지를 구체적으로 정의합니다.

#### 3.1 Task 개념 이해

**Task는 다음을 포함합니다:**
1. **Instruction (지침)**: 에이전트가 따라야 할 규칙과 절차
2. **Tools (도구 목록)**: 이 작업에서 사용 가능한 도구들
3. **Human Tool (선택)**: 사용자에게 추가 정보 요청 가능 여부

```
┌─────────────────────────────────────────┐
│  TASK: Customer_Service_Task            │
│                                         │
│  [지침]                                 │
│  • 제품 문의 → SQL Tool 사용            │
│  • 반품 요청 → RMA Generator 사용       │
│  • 정보 부족 시 → 사용자에게 질문       │
│                                         │
│  [사용 가능 도구]                       │
│  ✓ SQL_Analysis_Tool                   │
│  ✓ Return_Auth_Generator               │
│  ✓ Human_Tool (자동 활성화)             │
└─────────────────────────────────────────┘
```

#### 3.2 Task 생성

```sql
-- ===============================================
-- Step 3: Customer Service Task 생성
-- 설명: 고객 지원 업무를 정의하는 Task
-- 실행 계정: NORTHWIND
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TASK(
    task_name  => 'Customer_Service_Task',
    attributes => '{
      "instruction": "
        You are a helpful customer service assistant for Northwind Traders.
        
        WORKFLOW:
        1. When user asks about products, orders, customers, or sales data:
           - Use SQL_Analysis_Tool to query the database
           - Present the results in a clear, friendly manner
        
        2. When user wants to return a product:
           - Ask for Order ID if not provided
           - Ask for return reason if not provided
           - Use Return_Auth_Generator to create an RMA number
           - Provide the RMA number and next steps
        
        3. When you lack information:
           - Politely ask the user for specific details
           - Never make assumptions about order numbers or reasons
        
        TONE: Always be polite, professional, and helpful.
      ",
      "tools": ["SQL_Analysis_Tool", "Return_Auth_Generator"],
      "enable_human_tool": "true"
    }'
  );
END;
/
```

**Instruction 작성 팁:**
- **구체적으로**: "친절하게"보다 "항상 존댓말 사용, 감사 인사 포함"이 좋습니다
- **시나리오별로**: 상황에 따른 행동 지침을 명확히
- **예외 처리**: 정보가 부족할 때 어떻게 할지 명시
- **영어 사용**: 현재 버전에서는 영어 지침이 가장 잘 동작합니다

#### 3.3 enable_human_tool 이해

`enable_human_tool: true`로 설정하면, 에이전트가 **사용자에게 질문**할 수 있습니다.

**예시:**
```
사용자: "반품하고 싶어요"

에이전트 (enable_human_tool=true):
  "어떤 주문을 반품하시겠어요? 주문 번호를 알려주세요."

에이전트 (enable_human_tool=false):
  "주문 번호가 필요합니다." (더 이상 진행 불가)
```

#### 3.4 Task 확인

```sql
-- Task 목록 조회
SELECT TASK_NAME, 
       SUBSTR(JSON_VALUE(ATTRIBUTES, '$.instruction'), 1, 100) AS INSTRUCTION_PREVIEW,
       CREATED
FROM USER_AI_AGENT_TASKS
WHERE TASK_NAME = 'Customer_Service_Task';

-- Task에 연결된 도구 목록 확인
SELECT 
    TASK_NAME,
    JSON_QUERY(ATTRIBUTES, '$.tools' PRETTY) AS AVAILABLE_TOOLS
FROM USER_AI_AGENT_TASKS
WHERE TASK_NAME = 'Customer_Service_Task';
```

**Step 3 체크리스트:**
- [ ] Customer_Service_Task 생성 완료
- [ ] Instruction에 명확한 워크플로우 정의
- [ ] SQL_Analysis_Tool과 Return_Auth_Generator가 tools 목록에 포함
- [ ] enable_human_tool이 true로 설정

---

### Step 4: 에이전트(Agent) 생성

**Agent**는 실제로 작업을 수행하는 **주체**입니다. 에이전트에게 성격과 전문성을 부여합니다.

#### 4.1 Agent 개념

에이전트는 다음을 가집니다:
- **Profile**: 사용할 LLM 모델 (GPT-4, Claude 등)
- **Role**: 에이전트의 페르소나 (경력 10년 CS 전문가, 친절한 상담원 등)

```
┌───────────────────────────────────────────┐
│  AGENT: Northwind_Support_Bot             │
│                                           │
│  Profile: NORTHWIND_AI (GPT-4)         │
│  Role: 고객 지원 전문가                │
│                                           │
│  → Task 할당 받아 실행                    │
└───────────────────────────────────────────┘
```

#### 4.2 Agent 생성

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

#### 4.3 Agent 확인

```sql
-- Agent 목록 조회
SELECT 
    AGENT_NAME,
    JSON_VALUE(ATTRIBUTES, '$.profile_name') AS PROFILE,
    SUBSTR(JSON_VALUE(ATTRIBUTES, '$.role'), 1, 100) AS ROLE_PREVIEW,
    CREATED
FROM USER_AI_AGENTS
WHERE AGENT_NAME = 'Northwind_Support_Bot';
```

**Step 4 체크리스트:**
- [ ] Northwind_Support_Bot 에이전트 생성 완료
- [ ] NORTHWIND_AI 프로파일 연결 확인
- [ ] 명확한 Role 정의 완료

---

### Step 5: 팀(Team) 구성 및 활성화

**Team**은 에이전트와 작업을 **연결**하는 최종 단계입니다. 팀을 활성화해야 에이전트를 사용할 수 있습니다.

#### 5.1 Team 개념

```
┌────────────────────────────────────────────┐
│  TEAM: Northwind_Support_Team              │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  AGENT: Northwind_Support_Bot        │ │
│  │  ↓                                   │ │
│  │  TASK: Customer_Service_Task         │ │
│  │    → Tool: SQL_Analysis_Tool         │ │
│  │    → Tool: Return_Auth_Generator     │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  Process: sequential (순차 실행)           │
└────────────────────────────────────────────┘
```

#### 5.2 Team 생성

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
```json
"agents": [
  {"name": "Sales_Analyst", "task": "Data_Analysis_Task"},
  {"name": "Support_Bot", "task": "Customer_Service_Task"},
  {"name": "Inventory_Manager", "task": "Stock_Management_Task"}
]
```

#### 5.3 팀 활성화 (중요!)

팀을 생성했다고 끝이 아닙니다. **현재 세션에 팀을 활성화**해야 사용할 수 있습니다.

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

#### 5.4 Team 확인

```sql
-- ===============================================
-- Step 5.3: Team 정보 확인
-- ===============================================

-- Team 목록
SELECT TEAM_NAME, CREATED
FROM USER_AI_AGENT_TEAMS
WHERE TEAM_NAME = 'Northwind_Support_Team';

-- Team 상세 정보 (에이전트-작업 매핑)
SELECT 
    TEAM_NAME,
    JSON_QUERY(ATTRIBUTES, '$' PRETTY) AS TEAM_CONFIG
FROM USER_AI_AGENT_TEAMS
WHERE TEAM_NAME = 'Northwind_Support_Team';

-- 전체 구성 요약 (에이전트, 작업, 도구)
SELECT 
    'Agent' AS OBJECT_TYPE, AGENT_NAME AS NAME FROM USER_AI_AGENTS
UNION ALL
SELECT 
    'Task' AS OBJECT_TYPE, TASK_NAME AS NAME FROM USER_AI_AGENT_TASKS
UNION ALL
SELECT 
    'Tool' AS OBJECT_TYPE, TOOL_NAME AS NAME FROM USER_AI_AGENT_TOOLS
UNION ALL
SELECT 
    'Team' AS OBJECT_TYPE, TEAM_NAME AS NAME FROM USER_AI_AGENT_TEAMS;
```

**예상 출력:**
```
OBJECT_TYPE  NAME
------------ ---------------------------
Agent        Northwind_Support_Bot
Task         Customer_Service_Task
Tool         SQL_Analysis_Tool
Tool         Return_Auth_Generator
Team         Northwind_Support_Team
```

**Step 5 체크리스트:**
- [ ] Northwind_Support_Team 생성 완료
- [ ] 에이전트-Task 매핑 확인
- [ ] SET_TEAM으로 팀 활성화 완료
- [ ] GET_TEAM으로 활성 팀 확인

---

### Step 6: 에이전트 실행 및 테스트

드디어 에이전트를 사용할 시간입니다! `SELECT AI AGENT` 구문으로 자연어로 대화합니다.

#### 6.1 기본 문법

```sql
-- 기본 형식
SELECT AI AGENT '자연어 질문';

-- 또는
SELECT AI AGENT "자연어 질문";

-- 결과를 변수에 저장
VARIABLE response CLOB;
EXEC :response := DBMS_CLOUD_AI_AGENT.RUN_TEAM('Northwind_Support_Team', '질문');
PRINT response;
```

---

#### 6.2 테스트 케이스 1: 단순 데이터 조회

**목적**: SQL Tool이 제대로 작동하는지 확인

```sql
-- ===============================================
-- 테스트 1-1: 제품 조회
-- 예상 도구: SQL_Analysis_Tool
-- ===============================================

SELECT AI AGENT "What is the most expensive product in our inventory?";
```

**예상 동작:**
```
[Thought] 사용자가 가장 비싼 제품을 묻고 있다. Products 테이블을 조회해야 한다.
[Action] SQL_Analysis_Tool
[Action Input] "가장 비싼 제품 찾기"
[Observation] Côte de Blaye - $263.50
[Answer] 가장 비싼 제품은 "Côte de Blaye"로 $263.50입니다.
```

**더 많은 조회 테스트:**

```sql
-- 테스트 1-2: 고객 정보
SELECT AI AGENT "Show me all customers from Germany";

-- 테스트 1-3: 주문 통계
SELECT AI AGENT "How many orders were placed in 1996?";

-- 테스트 1-4: 직원 정보
SELECT AI AGENT "Who is the sales representative for customer ALFKI?";

-- 테스트 1-5: 복잡한 집계
SELECT AI AGENT "What are the top 5 products by total revenue?";
```

---

#### 6.3 테스트 케이스 2: 복합 추론 (Multi-turn)

**목적**: 에이전트가 여러 단계의 추론을 거쳐 작업을 완수하는지 확인

```sql
-- ===============================================
-- 테스트 2-1: 반품 요청 (모든 정보 제공)
-- 예상 도구: Return_Auth_Generator
-- ===============================================

SELECT AI AGENT "I received order 10248 but it is defective. I need to return it.";
```

**예상 동작:**
```
[Thought] 사용자가 주문 10248을 반품하려 한다. 이유는 'defective'다.
         필요한 정보: order_id (O), reason (O) → 충분함
[Action] Return_Auth_Generator
[Action Input] {"order_id": 10248, "reason": "defective"}
[Observation] RMA-10248-def-742
[Answer] 주문 10248에 대한 반품이 접수되었습니다. 
         RMA 번호는 RMA-10248-def-742입니다. 
         이 번호로 제품을 반송해 주시면 처리해 드리겠습니다.
```

---

#### 6.4 테스트 케이스 3: Human Tool 활용

**목적**: 정보가 부족할 때 에이전트가 사용자에게 질문하는지 확인

```sql
-- ===============================================
-- 테스트 3-1: 정보 불충분 상황
-- 예상 도구: Human_Tool (사용자에게 질문)
-- ===============================================

SELECT AI AGENT "I want to return an order";
```

**예상 동작:**
```
[Thought] 사용자가 반품을 원하지만, 어떤 주문인지 모른다.
         order_id가 필요하다.
[Action] Human_Tool
[Question] "어떤 주문을 반품하시겠어요? 주문 번호를 알려주세요."
```

**이어서 대화:**
```sql
-- 같은 세션에서 이어서 대답
SELECT AI AGENT "Order 10249";
```

```
[Thought] 사용자가 주문 번호 10249를 알려줬다. 반품 이유를 물어봐야 한다.
[Action] Human_Tool
[Question] "주문 10249를 반품하시는 이유를 알려주시겠어요?"
```

---

#### 6.5 테스트 케이스 4: 복합 작업

**목적**: 여러 도구를 조합하여 사용하는지 확인

```sql
-- ===============================================
-- 테스트 4-1: 조회 + 반품
-- 예상 도구: SQL_Analysis_Tool → Return_Auth_Generator
-- ===============================================

SELECT AI AGENT "Show me the details of order 10250, and if the total is over $1000, I want to return it because it's too expensive";
```

**예상 동작:**
```
[Thought] 먼저 주문 10250의 상세 정보를 확인해야 한다.
[Action] SQL_Analysis_Tool
[Action Input] "주문 10250 상세 정보"
[Observation] Order 10250: Total = $1552.60

[Thought] 총액이 $1552.60으로 $1000을 초과한다. 
         사용자가 반품을 원하므로 RMA를 생성한다.
[Action] Return_Auth_Generator
[Action Input] {"order_id": 10250, "reason": "too expensive"}
[Observation] RMA-10250-too-897

[Answer] 주문 10250의 총액은 $1552.60으로 $1000을 초과합니다.
         반품이 접수되었으며, RMA 번호는 RMA-10250-too-897입니다.
```

---

#### 6.6 에이전트 실행 로그 확인

에이전트가 어떤 사고 과정을 거쳤는지 상세 로그를 볼 수 있습니다.

```sql
-- ===============================================
-- Step 6.6: 에이전트 실행 히스토리 조회
-- ===============================================

-- 최근 실행 내역
SELECT 
    CONVERSATION_ID,
    USER_PROMPT,
    SUBSTR(RESPONSE, 1, 100) AS RESPONSE_PREVIEW,
    CREATED
FROM USER_AI_AGENT_CHAT_HISTORY
ORDER BY CREATED DESC
FETCH FIRST 10 ROWS ONLY;

-- 특정 대화의 상세 로그 (도구 호출 내역)
SELECT 
    STEP_NUMBER,
    THOUGHT,
    ACTION_NAME,
    ACTION_INPUT,
    OBSERVATION
FROM USER_AI_AGENT_EXECUTION_LOG
WHERE CONVERSATION_ID = 'your-conversation-id'  -- 위에서 조회한 ID
ORDER BY STEP_NUMBER;
```

**로그 예시:**
```
STEP  THOUGHT                          ACTION              OBSERVATION
----  -------------------------------  ------------------  ---------------
1     제품 정보를 조회해야 함          SQL_Analysis_Tool   Product: Chai, $18
2     정보를 충분히 확보함             None                N/A
```

---

#### 6.7 트러블슈팅

##### 문제 1: "No active team" 오류
```
ORA-XXXXX: No active team set for this session
```
**해결**: `EXEC DBMS_CLOUD_AI_AGENT.SET_TEAM('Northwind_Support_Team');` 실행

##### 문제 2: 에이전트가 도구를 사용하지 않음
**원인**: Tool의 `description`이 불명확
**해결**: `description`을 더 구체적으로 수정
```sql
BEGIN
  DBMS_CLOUD_AI_AGENT.UPDATE_TOOL(
    tool_name => 'SQL_Analysis_Tool',
    attributes => '{"description": "Use this tool WHENEVER the user asks about products, orders, customers, inventory, or any data in the database."}'
  );
END;
/
```

##### 문제 3: 에이전트가 무한 루프에 빠짐
**원인**: Instruction이 모호하거나 모순됨
**해결**: Task의 `instruction`을 더 명확하게 수정

**Step 6 체크리스트:**
- [ ] 기본 데이터 조회 테스트 성공
- [ ] 반품 처리 (RMA 생성) 테스트 성공
- [ ] Human Tool (추가 정보 요청) 동작 확인
- [ ] 실행 로그 확인 방법 숙지

---

## [3부] 고급 기능: Python SDK로 Agent 제어하기

데이터베이스 외부(웹 앱, 모바일 앱, Slack 봇 등)에서 에이전트를 사용하는 방법을 학습합니다.

### 왜 Python SDK가 필요한가?

**SQL 세션의 한계:**
- 웹 애플리케이션에서 사용 불가
- REST API로 노출하기 어려움
- 대화 세션 관리가 복잡

**Python SDK의 장점:**
- 웹 프레임워크(Flask, FastAPI)와 통합
- 대화 세션 자동 관리
- 멀티 사용자 동시 지원

---

### Step 7: Python 환경 설정

#### 7.1 필요 라이브러리 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Oracle Database 드라이버 설치
pip install oracledb

# 환경 변수 관리
pip install python-dotenv
```

#### 7.2 환경 변수 설정

`.env` 파일 생성:

```bash
# .env
DB_USER=NORTHWIND
DB_PASSWORD=your_password_here
DB_DSN=your_database_dsn
WALLET_DIR=/path/to/wallet
WALLET_PASSWORD=wallet_password
```

**DSN 형식 예시:**
```
(description=(retry_count=3)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=xxx.oraclecloud.com))(connect_data=(service_name=xxx_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))
```

---

### Step 8: Python에서 Agent 실행

#### 8.1 기본 Agent 호출 스크립트

파일: `agent_client.py`

```python
#!/usr/bin/env python3
"""
Northwind Select AI Agent 클라이언트
Oracle ADB의 Select AI Agent를 Python에서 호출하는 예제
"""

import os
import oracledb
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def connect_to_database():
    """데이터베이스 연결 생성"""
    try:
        connection = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN"),
            config_dir=os.getenv("WALLET_DIR"),
            wallet_location=os.getenv("WALLET_DIR"),
            wallet_password=os.getenv("WALLET_PASSWORD")
        )
        print("데이터베이스 연결 성공!")
        return connection
    except Exception as e:
        print(f"연결 실패: {e}")
        raise

def create_conversation(cursor):
    """새로운 대화 세션 생성"""
    conversation_id = cursor.callfunc(
        "DBMS_CLOUD_AI.CREATE_CONVERSATION", 
        str
    )
    print(f"대화 세션 시작: {conversation_id}")
    return conversation_id

def ask_agent(cursor, team_name, user_prompt, conversation_id=None):
    """
    Agent에게 질문하고 응답 받기
    
    Args:
        cursor: 데이터베이스 커서
        team_name: 팀 이름
        user_prompt: 사용자 질문
        conversation_id: 대화 세션 ID (멀티턴 대화용, 선택사항)
    
    Returns:
        에이전트 응답 (문자열)
    """
    try:
        # 파라미터 구성
        params = {}
        if conversation_id:
            params["conversation_id"] = conversation_id
        
        # RUN_TEAM 호출
        response = cursor.callfunc(
            "DBMS_CLOUD_AI_AGENT.RUN_TEAM",
            str,
            keywordParameters={
                "team_name": team_name,
                "user_prompt": user_prompt,
                "params": str(params) if params else None
            }
        )
        return response
    
    except oracledb.Error as e:
        error_obj, = e.args
        print(f"에러 발생: {error_obj.message}")
        return None

def main():
    """메인 실행 함수"""
    
    # 1. DB 연결
    connection = connect_to_database()
    cursor = connection.cursor()
    
    # 2. 대화 세션 생성
    conversation_id = create_conversation(cursor)
    
    # 3. 에이전트에게 질문
    print("\n" + "="*60)
    print("사용자: I want to return order 10248 because it's defective")
    print("="*60)
    
    response = ask_agent(
        cursor=cursor,
        team_name="Northwind_Support_Team",
        user_prompt="I want to return order 10248 because it's defective",
        conversation_id=conversation_id
    )
    
    if response:
        print("\nAgent 응답:")
        print(response)
    
    # 4. 연결 종료
    cursor.close()
    connection.close()
    print("\n연결 종료")

if __name__ == "__main__":
    main()
```

**실행:**
```bash
python agent_client.py
```

**예상 출력:**
```
데이터베이스 연결 성공!
대화 세션 시작: CONV-ABC123...

============================================================
사용자: I want to return order 10248 because it's defective
============================================================

Agent 응답:
I've processed your return request for order 10248. Your Return 
Merchandise Authorization (RMA) number is: RMA-10248-def-742

Please use this RMA number when shipping back the defective item.

연결 종료
```

---

### Step 9: 멀티턴 대화 구현

**멀티턴 대화**는 이전 대화 내용을 기억하며 연속적으로 대화하는 것입니다.

#### 9.1 대화형 Agent 챗봇

파일: `chatbot.py`

```python
#!/usr/bin/env python3
"""
대화형 Northwind Agent 챗봇
멀티턴 대화를 지원하는 커맨드라인 챗봇
"""

import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    """데이터베이스 연결"""
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
        config_dir=os.getenv("WALLET_DIR"),
        wallet_location=os.getenv("WALLET_DIR"),
        wallet_password=os.getenv("WALLET_PASSWORD")
    )

def chat_session():
    """대화형 세션 시작"""
    connection = create_connection()
    cursor = connection.cursor()
    
    # 대화 세션 생성
    conversation_id = cursor.callfunc("DBMS_CLOUD_AI.CREATE_CONVERSATION", str)
    print(f"\n{'='*60}")
    print(f"Northwind Support Bot에 오신 것을 환영합니다!")
    print(f"{'='*60}")
    print(f"대화 ID: {conversation_id}")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.\n")
    
    turn_number = 0
    
    while True:
        # 사용자 입력
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '종료', 'q']:
            print("\n👋 대화를 종료합니다. 감사합니다!")
            break
        
        if not user_input:
            continue
        
        turn_number += 1
        
        try:
            # 에이전트 호출
            params = f'{{"conversation_id": "{conversation_id}"}}'
            
            response = cursor.callfunc(
                "DBMS_CLOUD_AI_AGENT.RUN_TEAM",
                str,
                keywordParameters={
                    "team_name": "Northwind_Support_Team",
                    "user_prompt": user_input,
                    "params": params
                }
            )
            
            print(f"\nBot: {response}\n")
            print(f"{'-'*60}\n")
            
        except oracledb.Error as e:
            print(f"\n에러: {e}\n")
    
    # 연결 종료
    cursor.close()
    connection.close()

if __name__ == "__main__":
    chat_session()
```

**실행 예시:**
```bash
$ python chatbot.py

============================================================
Northwind Support Bot에 오신 것을 환영합니다!
============================================================
대화 ID: CONV-550E8400...
종료하려면 'quit' 또는 'exit'를 입력하세요.

You: What products do we sell?

Bot: We sell a variety of products including beverages, condiments, 
confections, dairy products, grains/cereals, meat/poultry, produce, 
and seafood. We have a total of 77 products in our catalog. 
Would you like to know more about a specific category?

------------------------------------------------------------

You: Show me the top 3 most expensive ones

Bot: Here are our top 3 most expensive products:
1. Côte de Blaye - $263.50 (Beverages)
2. Thüringer Rostbratwurst - $123.79 (Meat/Poultry)
3. Mishi Kobe Niku - $97.00 (Meat/Poultry)

------------------------------------------------------------

You: I want to return order 10248

Bot: I can help you with that return. Could you please tell me 
the reason for returning order 10248?

------------------------------------------------------------

You: It arrived damaged

Bot: I've created a return authorization for order 10248. 
Your RMA number is: RMA-10248-it -456

Please include this RMA number when shipping back the damaged items.

------------------------------------------------------------

You: quit

👋 대화를 종료합니다. 감사합니다!
```

**멀티턴 대화의 핵심:**
- 같은 `conversation_id`를 계속 사용
- 에이전트가 이전 대화 내용을 기억
- 자연스러운 대화 흐름 유지

---

### Step 10: 웹 API로 Agent 노출하기 (FastAPI)

#### 10.1 FastAPI 애플리케이션

파일: `api_server.py`

```python
"""
Northwind Agent REST API
Select AI Agent를 REST API로 노출
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import oracledb
import os
from dotenv import load_dotenv
from typing import Optional
import uuid

load_dotenv()

app = FastAPI(title="Northwind Agent API", version="1.0")

# 대화 세션 저장소 (실제 환경에서는 Redis 등 사용)
conversations = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    turn_number: int

def get_db_connection():
    """데이터베이스 연결 생성"""
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
        config_dir=os.getenv("WALLET_DIR"),
        wallet_location=os.getenv("WALLET_DIR"),
        wallet_password=os.getenv("WALLET_PASSWORD")
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Agent와 대화하기
    
    POST /chat
    Body: {"message": "질문", "session_id": "선택사항"}
    """
    
    # 세션 ID 관리
    if request.session_id and request.session_id in conversations:
        session_id = request.session_id
        conv_id = conversations[session_id]['conversation_id']
        turn_number = conversations[session_id]['turn_number'] + 1
    else:
        session_id = str(uuid.uuid4())
        connection = get_db_connection()
        cursor = connection.cursor()
        conv_id = cursor.callfunc("DBMS_CLOUD_AI.CREATE_CONVERSATION", str)
        cursor.close()
        connection.close()
        
        conversations[session_id] = {
            'conversation_id': conv_id,
            'turn_number': 0
        }
        turn_number = 1
    
    # Agent 호출
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        params = f'{{"conversation_id": "{conv_id}"}}'
        
        response = cursor.callfunc(
            "DBMS_CLOUD_AI_AGENT.RUN_TEAM",
            str,
            keywordParameters={
                "team_name": "Northwind_Support_Team",
                "user_prompt": request.message,
                "params": params
            }
        )
        
        # 턴 번호 업데이트
        conversations[session_id]['turn_number'] = turn_number
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            turn_number=turn_number
        )
        
    except oracledb.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()
        connection.close()

@app.delete("/session/{session_id}")
async def end_session(session_id: str):
    """대화 세션 종료"""
    if session_id in conversations:
        del conversations[session_id]
        return {"message": "Session ended"}
    return {"message": "Session not found"}

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 10.2 API 실행 및 테스트

**서버 실행:**
```bash
# FastAPI 설치
pip install fastapi uvicorn

# 서버 시작
python api_server.py
```

**API 테스트 (curl):**
```bash
# 첫 번째 질문
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the most expensive product?"}'

# 응답 예시:
# {
#   "response": "The most expensive product is Côte de Blaye at $263.50",
#   "session_id": "abc-123-def",
#   "turn_number": 1
# }

# 같은 세션에서 후속 질문
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many units do we have in stock?",
    "session_id": "abc-123-def"
  }'
```

**Swagger UI 접속:**
```
http://localhost:8000/docs
```

---

### Step 11: 고급 Tool - RAG, WebSearch, Notification

Select AI Agent는 SQL/PL/SQL 외에도 다양한 내장 도구를 지원합니다.

#### 11.1 RAG Tool (문서 검색)

**사용 사례**: 제품 매뉴얼, FAQ, 정책 문서 검색

```sql
-- ===============================================
-- RAG Tool 생성 (벡터 인덱스 필요)
-- ===============================================

-- 전제조건: 벡터 인덱스와 RAG 프로파일 생성 (1회차 참조)

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'Product_Manual_Search',
    attributes => '{
                    "tool_type": "RAG",
                    "tool_params": {
                      "profile_name": "NORTHWIND_RAG_PROFILE"
                    }
                  }',
    description => 'Searches product manuals and documentation. Use when user asks about product usage, specifications, or troubleshooting.'
  );
END;
/
```

**사용 예시:**
```sql
SELECT AI AGENT "How do I install the Chai tea maker?";
```

#### 11.2 WebSearch Tool (인터넷 검색)

**사용 사례**: 최신 정보, 환율, 경쟁사 정보 조회

```sql
-- ===============================================
-- WebSearch Tool 생성
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'Internet_Search',
    attributes => '{
                    "tool_type": "websearch",
                    "tool_params": {
                      "profile_name": "NORTHWIND_AI"
                    }
                  }',
    description => 'Searches the internet for current information. Use for exchange rates, competitor prices, or information not in our database.'
  );
END;
/
```

**사용 예시:**
```sql
SELECT AI AGENT "What is the current USD to EUR exchange rate?";
```

#### 11.3 Notification Tool (이메일/Slack)

**사용 사례**: 주문 확인 이메일, 재고 부족 알림

```sql
-- ===============================================
-- Email Notification Tool 생성
-- 전제조건: DBMS_CLOUD_NOTIFICATION 설정 완료
-- ===============================================

BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'Email_Sender',
    attributes => '{
                    "tool_type": "notification",
                    "tool_params": {
                      "notification_type": "email",
                      "sender": "support@northwind.com",
                      "subject_template": "Order Confirmation"
                    }
                  }',
    description => 'Sends email notifications to customers. Use for order confirmations, shipping updates, or important alerts.'
  );
END;
/
```

**사용 예시:**
```sql
SELECT AI AGENT "Send a confirmation email to customer ALFKI about order 10248";
```

---

### Step 12: 실전 응용 예제

#### 12.1 복합 비즈니스 프로세스 자동화

**시나리오**: 재고가 부족한 제품을 자동으로 발주

```sql
-- 1. 재고 확인 및 발주 함수 생성
CREATE OR REPLACE FUNCTION auto_reorder_check (
    p_product_id IN NUMBER
) RETURN VARCHAR2 IS
    v_stock_level NUMBER;
    v_reorder_level NUMBER;
    v_product_name VARCHAR2(100);
    v_order_id VARCHAR2(50);
BEGIN
    -- 현재 재고 확인
    SELECT units_in_stock, reorder_level, product_name
    INTO v_stock_level, v_reorder_level, v_product_name
    FROM products
    WHERE product_id = p_product_id;
    
    -- 재발주 필요 여부 판단
    IF v_stock_level <= v_reorder_level THEN
        v_order_id := 'PO-' || p_product_id || '-' || TO_CHAR(SYSDATE, 'YYYYMMDD');
        
        -- 실제로는 여기서 발주 테이블에 INSERT
        -- INSERT INTO purchase_orders...
        
        RETURN 'REORDER_NEEDED: ' || v_product_name || 
               ' (Current: ' || v_stock_level || 
               ', Reorder Level: ' || v_reorder_level || 
               '). Purchase Order: ' || v_order_id;
    ELSE
        RETURN 'STOCK_OK: ' || v_product_name || 
               ' has sufficient stock (' || v_stock_level || ' units)';
    END IF;
END;
/

-- 2. Tool 등록
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'Inventory_Manager',
    attributes => '{"function": "auto_reorder_check",
                    "instruction": "Check inventory levels and create reorder if needed. Requires product_id."}',
    description => 'Manages inventory and creates purchase orders for low stock items.'
  );
END;
/

-- 3. Task 업데이트 (도구 추가)
BEGIN
  DBMS_CLOUD_AI_AGENT.UPDATE_TASK(
    task_name => 'Customer_Service_Task',
    attributes => '{
                    "tools": [
                      "SQL_Analysis_Tool", 
                      "Return_Auth_Generator",
                      "Inventory_Manager"
                    ]
                  }'
  );
END;
/

-- 4. 테스트
SELECT AI AGENT "Check if we need to reorder Chai (product ID 1)";
```

#### 12.2 데이터 분석 리포트 생성

```sql
-- 판매 분석 리포트 생성 함수
CREATE OR REPLACE FUNCTION generate_sales_report (
    p_year IN NUMBER
) RETURN CLOB IS
    v_report CLOB;
BEGIN
    -- 복잡한 분석 로직 수행
    SELECT JSON_OBJECT(
        'year' VALUE p_year,
        'total_revenue' VALUE SUM(unit_price * quantity),
        'total_orders' VALUE COUNT(DISTINCT order_id),
        'top_product' VALUE (
            SELECT product_name 
            FROM products p 
            WHERE p.product_id = od.product_id 
            AND ROWNUM = 1
        )
        RETURNING CLOB
    )
    INTO v_report
    FROM order_details od
    JOIN orders o ON od.order_id = o.order_id
    WHERE EXTRACT(YEAR FROM o.order_date) = p_year;
    
    RETURN v_report;
END;
/

-- Tool 등록 및 사용
-- (생략 - 위와 동일한 패턴)
```

---

### Step 13: Built-in Tools 확장 가이드

Select AI Agent는 다양한 내장 도구를 지원합니다.

#### 13.1 지원 도구 유형

| 도구 유형 | Tool Type | 설명 | 사용 예시 |
|----------|-----------|------|----------|
| SQL | `SQL` | NL2SQL 쿼리 실행 | 데이터 조회, 통계 |
| PL/SQL | `function` | 사용자 함수 실행 | 비즈니스 로직, 데이터 변경 |
| RAG | `RAG` | 벡터 검색 | 문서, 매뉴얼 검색 |
| WebSearch | `websearch` | 인터넷 검색 | 최신 정보, 환율 |
| Email | `notification` | 이메일 발송 | 알림, 리포트 전송 |
| Slack | `notification` | Slack 메시지 | 팀 협업 알림 |
| REST API | `rest_api` | 외부 API 호출 | 결제, 배송 추적 |

#### 13.2 REST API Tool 예시

외부 API를 호출하는 도구를 만들 수 있습니다.

```sql
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'Shipping_Tracker',
    attributes => '{
                    "tool_type": "rest_api",
                    "endpoint_url": "https://api.shipping.com/track",
                    "http_method": "GET",
                    "parameters": {
                      "tracking_number": "string"
                    },
                    "credential_name": "SHIPPING_API_CRED"
                  }',
    description => 'Tracks shipment status using external shipping API.'
  );
END;
/
```

#### 13.3 Slack Notification Tool 예시

```sql
-- Slack Notification 설정 (ADMIN 계정)
BEGIN
  DBMS_CLOUD_NOTIFICATION.CREATE_NOTIFICATION_CHANNEL(
    channel_name => 'SLACK_CHANNEL',
    channel_type => 'SLACK',
    attributes   => '{
                      "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
                    }'
  );
END;
/

-- Tool 등록 (NORTHWIND 계정)
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'Slack_Notifier',
    attributes => '{
                    "tool_type": "notification",
                    "tool_params": {
                      "channel_name": "SLACK_CHANNEL"
                    }
                  }',
    description => 'Sends notifications to Slack channel. Use for urgent alerts or team notifications.'
  );
END;
/
```

**사용 예시:**
```sql
SELECT AI AGENT "Notify the team on Slack that we're running low on Chai (product 1)";
```

---

## [4부] 참고 자료 및 심화 학습

### 주요 패키지

#### DBMS_CLOUD_AI_AGENT 패키지

모든 Select AI Agent 관련 기능을 제공하는 핵심 패키지입니다.

**주요 프로시저 및 함수:**

| 함수/프로시저 | 용도 | 예시 |
|-------------|------|------|
| `CREATE_TOOL` | 도구 생성 | SQL, PL/SQL, RAG 도구 생성 |
| `CREATE_TASK` | 작업 생성 | 에이전트의 업무 정의 |
| `CREATE_AGENT` | 에이전트 생성 | 작업 수행 주체 생성 |
| `CREATE_TEAM` | 팀 생성 | 에이전트-작업 매핑 |
| `SET_TEAM` | 팀 활성화 | 세션에 팀 설정 |
| `RUN_TEAM` | 팀 실행 | Python 등에서 호출 |
| `UPDATE_TOOL` | 도구 수정 | 도구 속성 변경 |
| `DROP_TOOL` | 도구 삭제 | 도구 제거 |

---

### 주요 뷰 (Views)

에이전트 객체들을 조회할 수 있는 데이터 딕셔너리 뷰입니다.

#### USER_AI_AGENTS
내가 생성한 에이전트 목록

```sql
SELECT 
    AGENT_NAME,
    JSON_VALUE(ATTRIBUTES, '$.profile_name') AS PROFILE,
    JSON_VALUE(ATTRIBUTES, '$.role') AS ROLE,
    CREATED,
    LAST_MODIFIED
FROM USER_AI_AGENTS
ORDER BY CREATED DESC;
```

**주요 컬럼:**
- `AGENT_NAME`: 에이전트 이름
- `ATTRIBUTES`: JSON 형식의 에이전트 설정 (profile, role 등)
- `CREATED`: 생성 일시
- `LAST_MODIFIED`: 마지막 수정 일시

---

#### USER_AI_AGENT_TASKS
내가 생성한 작업 목록

```sql
SELECT 
    TASK_NAME,
    JSON_QUERY(ATTRIBUTES, '$.tools') AS TOOLS,
    SUBSTR(JSON_VALUE(ATTRIBUTES, '$.instruction'), 1, 200) AS INSTRUCTION,
    CREATED
FROM USER_AI_AGENT_TASKS
ORDER BY CREATED DESC;
```

**주요 컬럼:**
- `TASK_NAME`: 작업 이름
- `ATTRIBUTES`: JSON 형식의 작업 설정 (instruction, tools 등)

---

#### USER_AI_AGENT_TOOLS
내가 생성한 도구 목록

```sql
SELECT 
    TOOL_NAME,
    TOOL_TYPE,
    DESCRIPTION,
    JSON_QUERY(ATTRIBUTES, '$' PRETTY) AS ATTRIBUTES_DETAIL,
    CREATED
FROM USER_AI_AGENT_TOOLS
ORDER BY CREATED DESC;
```

**주요 컬럼:**
- `TOOL_NAME`: 도구 이름
- `TOOL_TYPE`: 도구 유형 (SQL, PLSQL, RAG 등)
- `DESCRIPTION`: 도구 설명
- `ATTRIBUTES`: JSON 형식의 도구 설정

---

#### USER_AI_AGENT_TEAMS
내가 생성한 팀 목록

```sql
SELECT 
    TEAM_NAME,
    JSON_QUERY(ATTRIBUTES, '$.agents' PRETTY) AS AGENTS,
    JSON_VALUE(ATTRIBUTES, '$.process') AS PROCESS_TYPE,
    CREATED
FROM USER_AI_AGENT_TEAMS
ORDER BY CREATED DESC;
```

**주요 컬럼:**
- `TEAM_NAME`: 팀 이름
- `ATTRIBUTES`: JSON 형식의 팀 설정 (agents, process 등)

---

#### USER_AI_AGENT_CHAT_HISTORY
에이전트와의 대화 기록

```sql
SELECT 
    CONVERSATION_ID,
    USER_PROMPT,
    RESPONSE,
    CREATED
FROM USER_AI_AGENT_CHAT_HISTORY
WHERE CONVERSATION_ID = 'your-conv-id'
ORDER BY CREATED;
```

**주요 컬럼:**
- `CONVERSATION_ID`: 대화 세션 ID
- `USER_PROMPT`: 사용자 질문
- `RESPONSE`: 에이전트 응답
- `CREATED`: 대화 시각

---

#### USER_AI_AGENT_EXECUTION_LOG
에이전트의 상세 실행 로그 (디버깅용)

```sql
SELECT 
    CONVERSATION_ID,
    STEP_NUMBER,
    THOUGHT,
    ACTION_NAME,
    ACTION_INPUT,
    OBSERVATION,
    CREATED
FROM USER_AI_AGENT_EXECUTION_LOG
WHERE CONVERSATION_ID = 'your-conv-id'
ORDER BY STEP_NUMBER;
```

**주요 컬럼:**
- `STEP_NUMBER`: 실행 단계 번호
- `THOUGHT`: 에이전트의 사고 과정
- `ACTION_NAME`: 사용한 도구 이름
- `ACTION_INPUT`: 도구에 전달한 입력
- `OBSERVATION`: 도구 실행 결과

**사용 예시**: 에이전트가 왜 특정 도구를 선택했는지, 어떤 파라미터를 전달했는지 확인

---

### 유용한 관리 쿼리

#### 모든 객체 삭제 (초기화)

```sql
-- ===============================================
-- 전체 Agent 객체 삭제 (처음부터 다시 시작)
-- ===============================================

-- 1. 팀 삭제 (가장 먼저)
BEGIN
  FOR rec IN (SELECT team_name FROM USER_AI_AGENT_TEAMS) LOOP
    DBMS_CLOUD_AI_AGENT.DROP_TEAM(rec.team_name);
  END LOOP;
END;
/

-- 2. 에이전트 삭제
BEGIN
  FOR rec IN (SELECT agent_name FROM USER_AI_AGENTS) LOOP
    DBMS_CLOUD_AI_AGENT.DROP_AGENT(rec.agent_name);
  END LOOP;
END;
/

-- 3. 작업 삭제
BEGIN
  FOR rec IN (SELECT task_name FROM USER_AI_AGENT_TASKS) LOOP
    DBMS_CLOUD_AI_AGENT.DROP_TASK(rec.task_name);
  END LOOP;
END;
/

-- 4. 도구 삭제 (가장 마지막)
BEGIN
  FOR rec IN (SELECT tool_name FROM USER_AI_AGENT_TOOLS) LOOP
    DBMS_CLOUD_AI_AGENT.DROP_TOOL(rec.tool_name);
  END LOOP;
END;
/
```

#### 에이전트 성능 모니터링

```sql
-- 도구별 사용 빈도
SELECT 
    ACTION_NAME AS TOOL_NAME,
    COUNT(*) AS USAGE_COUNT,
    AVG(EXECUTION_TIME_MS) AS AVG_EXECUTION_TIME
FROM USER_AI_AGENT_EXECUTION_LOG
WHERE CREATED >= SYSDATE - 7  -- 최근 7일
GROUP BY ACTION_NAME
ORDER BY USAGE_COUNT DESC;

-- 에이전트 응답 시간 분석
SELECT 
    TEAM_NAME,
    AVG(RESPONSE_TIME_MS) AS AVG_RESPONSE_TIME,
    MAX(RESPONSE_TIME_MS) AS MAX_RESPONSE_TIME,
    COUNT(*) AS TOTAL_REQUESTS
FROM USER_AI_AGENT_METRICS
WHERE CREATED >= SYSDATE - 1  -- 최근 1일
GROUP BY TEAM_NAME;
```

---

### 트러블슈팅 가이드

#### 문제 1: 에이전트가 응답하지 않음

**증상:**
```sql
SELECT AI AGENT "test";
-- 오랜 시간 대기 후 타임아웃
```

**원인 및 해결:**
1. **팀이 활성화되지 않음**
   ```sql
   EXEC DBMS_CLOUD_AI_AGENT.SET_TEAM('Northwind_Support_Team');
   ```

2. **AI 프로파일 크레덴셜 만료**
   ```sql
   -- 프로파일 상태 확인
   SELECT PROFILE_NAME, STATUS FROM USER_CLOUD_AI_PROFILES;
   
   -- 크레덴셜 재생성 필요 시
   BEGIN
     DBMS_CLOUD.UPDATE_CREDENTIAL(...);
   END;
   /
   ```

3. **LLM API 할당량 초과**
   - OpenAI, Cohere 등의 API 할당량 확인
   - 다른 프로파일로 전환 시도

---

#### 문제 2: 에이전트가 잘못된 도구를 선택함

**증상:**
```sql
SELECT AI AGENT "Return order 10248";
-- SQL Tool을 사용하려 시도 (RMA Generator를 써야 함)
```

**해결:**
1. **Tool Description 개선**
   ```sql
   BEGIN
     DBMS_CLOUD_AI_AGENT.UPDATE_TOOL(
       tool_name => 'Return_Auth_Generator',
       attributes => '{
         "description": "IMPORTANT: Use this tool ONLY when user explicitly wants to RETURN or REFUND an order. Do NOT use SQL tool for returns."
       }'
     );
   END;
   /
   ```

2. **Task Instruction 명확화**
   ```sql
   BEGIN
     DBMS_CLOUD_AI_AGENT.UPDATE_TASK(
       task_name => 'Customer_Service_Task',
       attributes => '{
         "instruction": "
           CRITICAL RULES:
           - Keywords: return, refund, RMA → Use Return_Auth_Generator
           - Keywords: show, find, list, what, how many → Use SQL_Analysis_Tool
         "
       }'
     );
   END;
   /
   ```

---

#### 문제 3: 에이전트가 환각(Hallucination)을 보임

**증상:**
```sql
SELECT AI AGENT "What is order 99999's status?";
-- Agent: "Order 99999 has been shipped" (존재하지 않는 주문)
```

**해결:**
1. **Tool Instruction에 검증 로직 추가**
   ```sql
   "instruction": "Before providing information, verify that the data exists. If no data is found, clearly state that to the user."
   ```

2. **PL/SQL 함수에 예외 처리 추가**
   ```sql
   CREATE OR REPLACE FUNCTION generate_return_auth (
       p_order_id IN NUMBER,
       p_reason   IN VARCHAR2
   ) RETURN VARCHAR2 IS
       v_order_exists NUMBER;
   BEGIN
       -- 주문 존재 여부 확인
       SELECT COUNT(*) INTO v_order_exists
       FROM orders WHERE order_id = p_order_id;
       
       IF v_order_exists = 0 THEN
           RETURN 'ERROR: Order ' || p_order_id || ' does not exist';
       END IF;
       
       -- RMA 생성 로직...
   END;
   /
   ```

---

#### 문제 4: Python 연결 오류

**증상:**
```python
oracledb.DatabaseError: DPY-6001: cannot connect to database
```

**체크리스트:**
- [ ] Wallet 파일이 올바른 경로에 있는가?
- [ ] `sqlnet.ora`에서 `WALLET_LOCATION` 확인
- [ ] `.env` 파일의 경로가 절대 경로인가?
- [ ] DB 방화벽에서 내 IP가 허용되어 있는가?

**디버깅:**
```python
# 연결 테스트
import oracledb
oracledb.init_oracle_client()  # Instant Client 초기화

print("Oracle Client Version:", oracledb.__version__)
print("Wallet Location:", os.getenv("WALLET_DIR"))
print("DSN:", os.getenv("DB_DSN"))
```

---

### 추가 학습 자료

#### Oracle 공식 문서
- [Select AI Agent 개요](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/select-ai-agent1.html)
- [DBMS_CLOUD_AI_AGENT 패키지 레퍼런스](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/dbms-cloud-ai-agent-package.html)
- [Agent Views 레퍼런스](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/dbms-cloud-ai-agent-views.html)
- [실습 예제 모음](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/examples-using-select-ai-agent.html)

#### 추가 리소스
- Oracle LiveLabs: Select AI Agent 핸즈온 워크샵
- Oracle Blogs: AI/ML 카테고리
- Oracle Cloud Customer Connect: 커뮤니티 Q&A

---

### 심화 과제

다음 기능들을 직접 구현해 보세요:

#### 과제 1: 다중 에이전트 시스템
- **Sales Analyst Agent**: 데이터 분석 전담
- **Support Agent**: 고객 지원 전담  
- **Inventory Agent**: 재고 관리 전담
- 하나의 팀으로 협업하도록 구성

#### 과제 2: RAG 기반 FAQ 봇
- 제품 매뉴얼 PDF를 벡터화
- RAG Tool을 활용한 Q&A 시스템
- "How do I clean the espresso machine?" 같은 질문 처리

#### 과제 3: Slack 봇 통합
- Slack 메시지를 받아 Agent에게 전달
- Agent 응답을 Slack으로 전송
- 슬래시 커맨드 (`/northwind ask ...`) 구현

#### 과제 4: 실시간 대시보드
- Streamlit으로 Agent 챗봇 UI 구성
- 대화 기록 시각화
- Tool 사용 통계 차트

---

### 보안 Best Practices

#### 1. 크레덴셜 관리
```sql
-- 크레덴셜을 안전하게 저장
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'OPENAI_CRED',
    username        => 'openai',
    password        => 'sk-...'  -- API Key
  );
END;
/

-- 일반 사용자는 크레덴셜 내용을 볼 수 없음
-- Agent는 크레덴셜을 사용만 가능
```

#### 2. 권한 최소화
```sql
-- Agent 사용자에게 필요한 최소 권한만 부여
GRANT SELECT ON products TO northwind_agent_user;
GRANT SELECT ON orders TO northwind_agent_user;
-- INSERT, UPDATE, DELETE는 부여하지 않음

-- 특정 PL/SQL 함수만 실행 가능하도록
GRANT EXECUTE ON generate_return_auth TO northwind_agent_user;
```

#### 3. 입력 검증
```sql
-- PL/SQL 함수에서 입력 검증
CREATE OR REPLACE FUNCTION generate_return_auth (
    p_order_id IN NUMBER,
    p_reason   IN VARCHAR2
) RETURN VARCHAR2 IS
BEGIN
    -- 입력 검증
    IF p_order_id IS NULL OR p_order_id <= 0 THEN
        RETURN 'ERROR: Invalid order ID';
    END IF;
    
    IF p_reason IS NULL OR LENGTH(TRIM(p_reason)) < 3 THEN
        RETURN 'ERROR: Please provide a valid return reason';
    END IF;
    
    -- SQL Injection 방지를 위한 파라미터 바인딩
    -- (PL/SQL 함수는 자동으로 방지됨)
    
    -- 비즈니스 로직...
END;
/
```

#### 4. 감사 로그
```sql
-- 모든 Agent 호출 기록 남기기
CREATE TABLE agent_audit_log (
    log_id NUMBER GENERATED ALWAYS AS IDENTITY,
    user_name VARCHAR2(100),
    conversation_id VARCHAR2(100),
    user_prompt CLOB,
    tools_used VARCHAR2(1000),
    created_date TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- Trigger로 자동 기록 (선택사항)
```

---

### 성능 최적화 팁

#### 1. 프로파일 선택
- **복잡한 추론**: GPT-4, Claude-3 Opus
- **빠른 응답**: GPT-3.5-turbo, Claude-3 Haiku
- **비용 절감**: Cohere Command, Llama-2

#### 2. Tool Description 최적화
```sql
-- 나쁜 예: 너무 길고 모호
"This tool can be used to search the database for various information including but not limited to products, orders, customers..."

-- 좋은 예: 짧고 명확
"Queries product, order, and customer data. Use for: 'show', 'find', 'list', 'what', 'how many'"
```

#### 3. 대화 기록 정리
```sql
-- 오래된 대화 기록 삭제 (성능 향상)
DELETE FROM USER_AI_AGENT_CHAT_HISTORY
WHERE CREATED < SYSDATE - 30;  -- 30일 이상 된 기록

COMMIT;
```

---

### 전체 구축 체크리스트

**환경 준비**
- [ ] Oracle ADB 접근 권한 확인
- [ ] ADMIN 계정으로 권한 부여 완료
- [ ] NORTHWIND_AI 프로파일 생성 완료

**Agent 구축 (SQL)**
- [ ] SQL_Analysis_Tool 생성
- [ ] generate_return_auth 함수 생성
- [ ] Return_Auth_Generator Tool 등록
- [ ] Customer_Service_Task 생성
- [ ] Northwind_Support_Bot Agent 생성
- [ ] Northwind_Support_Team 팀 생성 및 활성화

**테스트**
- [ ] 데이터 조회 테스트 성공
- [ ] 반품 처리 테스트 성공
- [ ] 멀티턴 대화 테스트 성공
- [ ] 실행 로그 확인

**Python 통합**
- [ ] Python 환경 설정
- [ ] 기본 Agent 호출 스크립트 실행
- [ ] 대화형 챗봇 구현
- [ ] (선택) FastAPI 웹 서버 구축

**고급 기능**
- [ ] (선택) RAG Tool 추가
- [ ] (선택) WebSearch Tool 추가
- [ ] (선택) Notification Tool 추가

---

## [5부] 실습 가이드

### 처음부터 끝까지 따라하기 (20분 완성)

#### 빠른 시작 가이드

**1단계: 연결 및 확인 (2분)**
```sql
-- SQL Developer 또는 SQL*Plus로 NORTHWIND 사용자로 접속

-- AI 프로파일 확인
SELECT PROFILE_NAME FROM USER_CLOUD_AI_PROFILES WHERE PROFILE_NAME = 'NORTHWIND_AI';

-- 권한 확인
SELECT * FROM USER_TAB_PRIVS WHERE TABLE_NAME LIKE '%CLOUD_AI%';
```

**2단계: 도구 생성 (3분)**
```sql
-- SQL Tool
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'SQL_Analysis_Tool',
    attributes => '{"tool_type": "SQL", "tool_params": {"profile_name": "NORTHWIND_AI"}}',
    description => 'Query database for products, orders, customers'
  );
END;
/

-- PL/SQL 함수
CREATE OR REPLACE FUNCTION generate_return_auth (
    p_order_id IN NUMBER,
    p_reason   IN VARCHAR2
) RETURN VARCHAR2 IS
BEGIN
    RETURN 'RMA-' || p_order_id || '-' || SUBSTR(p_reason, 1, 3) || '-' || TRUNC(DBMS_RANDOM.VALUE(100, 999));
END;
/

-- PL/SQL Tool
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'Return_Auth_Generator',
    attributes => '{"instruction": "Generate RMA for returns. Requires order_id and reason.", "function": "generate_return_auth"}',
    description => 'Generate RMA numbers for returns'
  );
END;
/
```

**3단계: Task, Agent, Team 생성 (3분)**
```sql
-- Task
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TASK(
    task_name => 'Customer_Service_Task',
    attributes => '{"instruction": "Help customers with orders and returns. Use SQL_Analysis_Tool for queries, Return_Auth_Generator for returns.", "tools": ["SQL_Analysis_Tool", "Return_Auth_Generator"], "enable_human_tool": "true"}'
  );
END;
/

-- Agent
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_AGENT(
    agent_name => 'Northwind_Support_Bot',
    attributes => '{"profile_name": "NORTHWIND_AI", "role": "Customer support specialist"}'
  );
END;
/

-- Team
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TEAM(
    team_name => 'Northwind_Support_Team',
    attributes => '{"agents": [{"name": "Northwind_Support_Bot", "task": "Customer_Service_Task"}], "process": "sequential"}'
  );
END;
/

-- 활성화
EXEC DBMS_CLOUD_AI_AGENT.SET_TEAM('Northwind_Support_Team');
```

**4단계: 테스트 (2분)**
```sql
-- 간단한 조회
SELECT AI AGENT "What is the most expensive product?";

-- 반품 처리
SELECT AI AGENT "I want to return order 10248 because it's defective";
```

**완료! 🎉**

---

### 올인원 스크립트 (복사해서 바로 실행)

바쁘신 분들을 위한 **한 번에 실행하는 스크립트**입니다.

```sql
-- ===============================================
-- Northwind Select AI Agent - 올인원 설정 스크립트
-- 설명: 아래 전체를 복사하여 SQL Developer에서 실행하세요
-- 실행 계정: NORTHWIND
-- 소요 시간: 약 1분
-- ===============================================

-- 1. 기존 객체 정리 (있다면)
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_count FROM USER_AI_AGENT_TEAMS WHERE TEAM_NAME = 'Northwind_Support_Team';
  IF v_count > 0 THEN DBMS_CLOUD_AI_AGENT.DROP_TEAM('Northwind_Support_Team'); END IF;
  
  SELECT COUNT(*) INTO v_count FROM USER_AI_AGENTS WHERE AGENT_NAME = 'Northwind_Support_Bot';
  IF v_count > 0 THEN DBMS_CLOUD_AI_AGENT.DROP_AGENT('Northwind_Support_Bot'); END IF;
  
  SELECT COUNT(*) INTO v_count FROM USER_AI_AGENT_TASKS WHERE TASK_NAME = 'Customer_Service_Task';
  IF v_count > 0 THEN DBMS_CLOUD_AI_AGENT.DROP_TASK('Customer_Service_Task'); END IF;
  
  SELECT COUNT(*) INTO v_count FROM USER_AI_AGENT_TOOLS WHERE TOOL_NAME = 'Return_Auth_Generator';
  IF v_count > 0 THEN DBMS_CLOUD_AI_AGENT.DROP_TOOL('Return_Auth_Generator'); END IF;
  
  SELECT COUNT(*) INTO v_count FROM USER_AI_AGENT_TOOLS WHERE TOOL_NAME = 'SQL_Analysis_Tool';
  IF v_count > 0 THEN DBMS_CLOUD_AI_AGENT.DROP_TOOL('SQL_Analysis_Tool'); END IF;
END;
/

-- 2. PL/SQL 함수 생성
CREATE OR REPLACE FUNCTION generate_return_auth (
    p_order_id IN NUMBER,
    p_reason   IN VARCHAR2
) RETURN VARCHAR2 IS
BEGIN
    RETURN 'RMA-' || p_order_id || '-' || SUBSTR(p_reason, 1, 3) || '-' || TRUNC(DBMS_RANDOM.VALUE(100, 999));
END;
/

-- 3. SQL Tool 생성
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'SQL_Analysis_Tool',
    attributes => '{"tool_type": "SQL", "tool_params": {"profile_name": "NORTHWIND_AI"}}',
    description => 'Query database for products, orders, customers, and sales data'
  );
END;
/

-- 4. PL/SQL Tool 생성
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'Return_Auth_Generator',
    attributes => '{"instruction": "Generate RMA number. Requires order_id (number) and reason (string).", "function": "generate_return_auth"}',
    description => 'Generate RMA numbers for product returns'
  );
END;
/

-- 5. Task 생성
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TASK(
    task_name => 'Customer_Service_Task',
    attributes => '{"instruction": "You are a helpful customer service assistant for Northwind Traders. Use SQL_Analysis_Tool for data queries. Use Return_Auth_Generator when customer wants to return a product. Always be polite.", "tools": ["SQL_Analysis_Tool", "Return_Auth_Generator"], "enable_human_tool": "true"}'
  );
END;
/

-- 6. Agent 생성
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_AGENT(
    agent_name => 'Northwind_Support_Bot',
    attributes => '{"profile_name": "NORTHWIND_AI", "role": "Experienced Customer Support Representative"}'
  );
END;
/

-- 7. Team 생성
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TEAM(
    team_name => 'Northwind_Support_Team',
    attributes => '{"agents": [{"name": "Northwind_Support_Bot", "task": "Customer_Service_Task"}], "process": "sequential"}'
  );
END;
/

-- 8. Team 활성화
EXEC DBMS_CLOUD_AI_AGENT.SET_TEAM('Northwind_Support_Team');

-- 9. 테스트
SELECT AI AGENT "What is the most expensive product in our catalog?";

-- 10. 생성된 객체 확인
SELECT 
    'Tool' AS OBJECT_TYPE, 
    TOOL_NAME AS NAME, 
    CREATED 
FROM USER_AI_AGENT_TOOLS
UNION ALL
SELECT 'Task', TASK_NAME, CREATED FROM USER_AI_AGENT_TASKS
UNION ALL
SELECT 'Agent', AGENT_NAME, CREATED FROM USER_AI_AGENTS
UNION ALL
SELECT 'Team', TEAM_NAME, CREATED FROM USER_AI_AGENT_TEAMS
ORDER BY CREATED;

-- 완료! 이제 SELECT AI AGENT '질문'으로 대화할 수 있습니다.
```

**팁**: 위 스크립트를 `setup_agent.sql` 파일로 저장하고 `@setup_agent.sql`로 실행할 수 있습니다.

---

**5단계: 확인 및 정리 (2분)**
```sql
-- 모든 객체 확인
SELECT 'Tool' AS TYPE, TOOL_NAME AS NAME FROM USER_AI_AGENT_TOOLS
UNION ALL
SELECT 'Task', TASK_NAME FROM USER_AI_AGENT_TASKS
UNION ALL
SELECT 'Agent', AGENT_NAME FROM USER_AI_AGENTS
UNION ALL
SELECT 'Team', TEAM_NAME FROM USER_AI_AGENT_TEAMS;

-- 활성 팀 확인
SELECT DBMS_CLOUD_AI_AGENT.GET_TEAM() AS ACTIVE_TEAM FROM DUAL;
```

---

### Streamlit 웹 앱 예제

Streamlit으로 멋진 Agent 챗봇 UI를 만들어보세요!

**파일: `streamlit_agent_app.py`**

```python
"""
Northwind Select AI Agent - Streamlit Web App
사용법: streamlit run streamlit_agent_app.py
"""

import streamlit as st
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Northwind AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# 제목
st.title("Northwind AI Assistant")
st.markdown("*Powered by Oracle Select AI Agent*")

# 사이드바 - 설정
with st.sidebar:
    st.header("설정")
    
    # 데이터베이스 연결 상태
    if st.button("DB 연결 테스트"):
        try:
            conn = oracledb.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                dsn=os.getenv("DB_DSN"),
                config_dir=os.getenv("WALLET_DIR"),
                wallet_location=os.getenv("WALLET_DIR"),
                wallet_password=os.getenv("WALLET_PASSWORD")
            )
            conn.close()
            st.success("연결 성공!")
        except Exception as e:
            st.error(f"연결 실패: {e}")
    
    st.divider()
    
    # 대화 초기화
    if st.button("대화 기록 삭제"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.success("대화가 초기화되었습니다.")
    
    st.divider()
    
    # 통계
    st.subheader("통계")
    if 'messages' in st.session_state:
        st.metric("대화 턴 수", len(st.session_state.messages) // 2)

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None

# 데이터베이스 연결 함수
@st.cache_resource
def get_db_connection():
    """데이터베이스 연결 (캐싱)"""
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
        config_dir=os.getenv("WALLET_DIR"),
        wallet_location=os.getenv("WALLET_DIR"),
        wallet_password=os.getenv("WALLET_PASSWORD")
    )

def create_conversation():
    """새 대화 세션 생성"""
    conn = get_db_connection()
    cursor = conn.cursor()
    conv_id = cursor.callfunc("DBMS_CLOUD_AI.CREATE_CONVERSATION", str)
    cursor.close()
    return conv_id

def ask_agent(user_prompt, conversation_id):
    """Agent에게 질문"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        params = f'{{"conversation_id": "{conversation_id}"}}' if conversation_id else None
        
        response = cursor.callfunc(
            "DBMS_CLOUD_AI_AGENT.RUN_TEAM",
            str,
            keywordParameters={
                "team_name": "Northwind_Support_Team",
                "user_prompt": user_prompt,
                "params": params
            }
        )
        return response
    except Exception as e:
        return f"에러: {str(e)}"
    finally:
        cursor.close()

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    
    # 첫 메시지라면 대화 세션 생성
    if st.session_state.conversation_id is None:
        with st.spinner("대화 세션 생성 중..."):
            st.session_state.conversation_id = create_conversation()
    
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Agent 응답 받기
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            response = ask_agent(prompt, st.session_state.conversation_id)
            st.markdown(response)
    
    # Assistant 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": response})

# 샘플 질문 제공
if len(st.session_state.messages) == 0:
    st.info("샘플 질문을 클릭해보세요!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("제품 정보"):
            st.session_state.sample_prompt = "What are the top 5 most expensive products?"
    
    with col2:
        if st.button("주문 통계"):
            st.session_state.sample_prompt = "How many orders were placed last month?"
    
    with col3:
        if st.button("반품 처리"):
            st.session_state.sample_prompt = "I want to return order 10248 because it's defective"
    
    if 'sample_prompt' in st.session_state:
        st.rerun()
```

**실행 방법:**

```bash
# Streamlit 설치
pip install streamlit

# 앱 실행
streamlit run streamlit_agent_app.py

# 브라우저가 자동으로 열림 (http://localhost:8501)
```

**화면 예시:**
```
┌─────────────────────────────────────────────────────┐
│  Northwind AI Assistant                          │
│  Powered by Oracle Select AI Agent                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  You:                                            │
│  What is the most expensive product?                │
│                                                     │
│  Assistant:                                      │
│  The most expensive product in our inventory is     │
│  "Côte de Blaye" priced at $263.50. This is a      │
│  premium French wine from our beverages category.   │
│                                                     │
│  ─────────────────────────────────────────────────  │
│                                                     │
│  You:                                            │
│  How many do we have in stock?                      │
│                                                     │
│  Assistant:                                      │
│  We currently have 17 units of Côte de Blaye in     │
│  stock. The reorder level is set at 15 units.      │
│                                                     │
├─────────────────────────────────────────────────────┤
│  무엇을 도와드릴까요? [_______________] [Send]       │
└─────────────────────────────────────────────────────┘

┌───────────────┐
│  설정      │
│  DB 연결   │
│  대화 초기화│
│               │
│  통계      │
│  대화 턴: 2   │
└───────────────┘
```

---

### 📖 FAQ (자주 묻는 질문)

#### Q1: Select AI와 Select AI Agent의 차이는?

| 구분 | Select AI | Select AI Agent |
|------|-----------|----------------|
| 기능 | 단순 NL2SQL | 복합 작업 자동화 |
| 도구 | SQL만 가능 | SQL, PL/SQL, API, RAG 등 |
| 추론 | 1회성 변환 | ReAct 패턴으로 다단계 추론 |
| 메모리 | 없음 | 대화 컨텍스트 유지 |
| 사용 예시 | "Show me orders" | "Check inventory and reorder if low" |

**요약**: Select AI Agent는 Select AI의 **슈퍼셋**입니다.

---

#### Q2: 여러 LLM 모델을 혼합 사용할 수 있나요?

**가능합니다!** 에이전트마다 다른 프로파일을 사용할 수 있습니다.

```sql
-- GPT-4 기반 분석 에이전트
CREATE_AGENT(
  agent_name => 'Analyst',
  attributes => '{"profile_name": "GPT4_PROFILE", ...}'
);

-- Cohere 기반 고객 지원 에이전트
CREATE_AGENT(
  agent_name => 'Support',
  attributes => '{"profile_name": "COHERE_PROFILE", ...}'
);
```

**활용 전략:**
- 복잡한 분석: GPT-4 (정확도 우선)
- 간단한 응대: GPT-3.5 (속도/비용 우선)

---

#### Q3: 에이전트가 사용할 수 있는 테이블을 제한할 수 있나요?

**가능합니다!** SQL Tool의 프로파일에서 제한합니다.

```sql
-- 특정 테이블만 접근 가능한 프로파일 생성
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'NORTHWIND_AI_LIMITED',
    attributes   => '{
                      "provider": "openai",
                      "credential_name": "OPENAI_CRED",
                      "model": "gpt-4",
                      "object_list": [
                        {"owner": "NORTHWIND", "name": "PRODUCTS"},
                        {"owner": "NORTHWIND", "name": "ORDERS"}
                      ]
                    }'
  );
END;
/

-- 이 프로파일을 사용하는 Tool은 PRODUCTS, ORDERS만 접근 가능
```

---

#### Q4: 에이전트 응답 시간이 너무 느려요

**원인별 해결책:**

1. **LLM API 응답 지연**
   - 더 빠른 모델 사용 (GPT-4 → GPT-3.5)
   - 로컬 LLM 사용 (Llama-2, Mistral)

2. **복잡한 SQL 쿼리**
   - 인덱스 최적화
   - 프로파일에 샘플 쿼리 추가 (hint 제공)

3. **너무 많은 도구**
   - Task의 tools 목록을 필요한 것만 포함
   - 도구별로 별도 Task 생성

**성능 측정:**
```sql
SELECT 
    AVG(RESPONSE_TIME_MS) / 1000 AS AVG_SECONDS,
    MIN(RESPONSE_TIME_MS) / 1000 AS MIN_SECONDS,
    MAX(RESPONSE_TIME_MS) / 1000 AS MAX_SECONDS
FROM USER_AI_AGENT_CHAT_HISTORY
WHERE CREATED >= SYSDATE - 1;
```

---

#### Q5: 에이전트가 도구를 안 쓰고 직접 답변해요

**원인**: LLM이 자체 지식으로 답변 가능하다고 판단

**해결:**
```sql
-- Task instruction에 강제 조항 추가
BEGIN
  DBMS_CLOUD_AI_AGENT.UPDATE_TASK(
    task_name => 'Customer_Service_Task',
    attributes => '{
      "instruction": "
        CRITICAL: You MUST use tools to answer questions.
        NEVER answer from your own knowledge.
        ALWAYS use SQL_Analysis_Tool to verify data before responding.
      "
    }'
  );
END;
/
```

---

#### Q6: 한국어로 질문하면 작동하나요?

**작동합니다!** 하지만 주의사항이 있습니다.

```sql
-- 한국어 질문 가능
SELECT AI AGENT "가장 비싼 제품은 뭐야?";

-- 한국어 응답 가능
-- "가장 비싼 제품은 Côte de Blaye이며 가격은 $263.50입니다."
```

**권장사항:**
- **Instruction과 Description은 영어**: LLM의 추론 성능이 더 좋음
- **사용자 질문과 응답은 한국어 가능**: 자연스럽게 번역됨

---

#### Q7: 대화 기록을 삭제하고 싶어요

```sql
-- 특정 대화 삭제
BEGIN
  DBMS_CLOUD_AI.DELETE_CONVERSATION('conversation-id');
END;
/

-- 모든 대화 기록 삭제
DELETE FROM USER_AI_AGENT_CHAT_HISTORY;
DELETE FROM USER_AI_AGENT_EXECUTION_LOG;
COMMIT;
```

---

#### Q8: Agent 비용은 얼마나 드나요?

**비용 구성:**
1. **LLM API 비용**: OpenAI, Cohere 등의 사용량 기반 과금
   - GPT-4: ~$0.03/1K tokens
   - GPT-3.5: ~$0.002/1K tokens
   
2. **ADB 비용**: 데이터베이스 사용 비용 (기존과 동일)

3. **데이터 전송**: 보통 무시 가능한 수준

**비용 절감 팁:**
- 응답 길이 제한: `max_tokens` 설정
- 캐싱: 동일 질문은 캐싱된 응답 사용
- 저렴한 모델: 간단한 작업은 GPT-3.5 사용

**예상 비용 (월 1,000회 사용 기준):**
- GPT-3.5 사용: ~$5-10
- GPT-4 사용: ~$50-100

---

### 다음 단계

Select AI Agent를 마스터했다면:

1. **실제 비즈니스 문제에 적용**
   - 고객 센터 자동화
   - 데이터 분석 어시스턴트
   - 자동 리포팅 시스템

2. **다른 Oracle AI 기능과 통합**
   - OML (Oracle Machine Learning)
   - Spatial AI
   - Graph Analytics

3. **엔터프라이즈 배포**
   - 멀티 테넌시 설계
   - 로드 밸런싱
   - 모니터링 및 알림

---

### 문의 및 지원

**문제가 발생했을 때:**
1. `USER_AI_AGENT_EXECUTION_LOG` 뷰에서 상세 로그 확인
2. Oracle Cloud 콘솔에서 ADB 로그 확인
3. Oracle Support (My Oracle Support)에 문의

**추가 도움:**
- Oracle LiveLabs 실습 자료
- Oracle Community Forums
- GitHub에서 예제 코드 검색

---

### 학습 정리

#### 핵심 개념 요약

1. **Select AI Agent = ReAct + Tools + Memory**
   - ReAct: 추론과 행동의 반복
   - Tools: 다양한 작업 수행 수단
   - Memory: 대화 컨텍스트 유지

2. **4가지 핵심 객체**
   ```
   Tool → Task → Agent → Team
   (도구)  (업무)  (실행자) (조직)
   ```

3. **구축 순서**
   ```
   권한 설정 → 도구 생성 → 작업 정의 → 
   에이전트 생성 → 팀 구성 → 활성화 → 테스트
   ```

#### Select AI vs Select AI Agent

| 항목 | Select AI | Select AI Agent |
|------|-----------|----------------|
| **복잡도** | 간단 (1단계) | 복합 (다단계) |
| **지능** | NL2SQL 변환 | 추론 + 계획 + 실행 |
| **도구** | SQL만 | SQL, PL/SQL, API, RAG 등 |
| **상태** | Stateless | Stateful (대화 기억) |
| **적용** | 데이터 조회 | 업무 자동화, 워크플로우 |

#### 언제 무엇을 사용할까?

**Select AI를 사용:**
- 단순한 데이터 조회
- 일회성 분석
- 빠른 프로토타이핑

**Select AI Agent를 사용:**
- 복합적인 비즈니스 프로세스
- 고객 지원 자동화
- 대화형 애플리케이션
- 여러 시스템 통합 필요

---

### 연습 문제

#### 초급: 기본 에이전트 수정

**문제 1**: 에이전트에게 할인 코드 생성 기능 추가
- `generate_discount_code(customer_id, discount_percent)` 함수 생성
- Tool로 등록
- Task에 추가
- 테스트: "Give me a 10% discount code for customer ALFKI"

**문제 2**: 주문 취소 기능 추가
- `cancel_order(order_id, reason)` 함수 생성
- Tool로 등록
- 테스트: "Cancel order 10248 because customer requested"

---

#### 중급: 복합 워크플로우

**문제 3**: 재고 알림 시스템
1. 재고가 10개 이하인 제품을 찾는 SQL Tool
2. 발주를 생성하는 PL/SQL Tool
3. 담당자에게 이메일 보내는 Notification Tool
4. 모두를 조합하는 "Inventory_Management_Task" 생성

**문제 4**: 월간 판매 리포트 에이전트
1. 특정 월의 판매 데이터를 분석하는 함수
2. 리포트를 PDF로 생성
3. 이메일로 자동 발송

---

#### 고급: 다중 에이전트 협업

**문제 5**: 3-Agent 시스템 구축
1. **Data Analyst**: 데이터 분석 전담
2. **Support Bot**: 고객 응대 전담
3. **Manager Bot**: 승인 및 의사결정 전담

이들이 하나의 팀으로 협업하도록 구성:
```
사용자 → Support Bot (1차 응대)
      → Data Analyst (데이터 확인)
      → Manager Bot (승인)
      → Support Bot (최종 응답)
```

---

### 실전 프로젝트 아이디어

#### 1. 스마트 헬프데스크
- **기능**: FAQ 자동 응답, 티켓 생성, 담당자 배정
- **도구**: RAG (FAQ 검색), PL/SQL (티켓 생성), Email (알림)
- **효과**: 고객 대기 시간 80% 감소

#### 2. 데이터 분석 어시스턴트
- **기능**: 자연어로 복잡한 데이터 분석 요청
- **도구**: SQL (데이터 조회), PL/SQL (통계 계산), WebSearch (벤치마크)
- **효과**: 비개발자도 데이터 분석 가능

#### 3. 자동 주문 처리 시스템
- **기능**: 이메일/슬랙으로 주문 접수 → 재고 확인 → 주문 생성 → 배송 요청
- **도구**: Email (주문 수신), SQL (재고 확인), PL/SQL (주문 생성), REST API (배송)
- **효과**: 주문 처리 시간 90% 단축

#### 4. 실시간 비즈니스 인텔리전스
- **기능**: "오늘 매출이 어제보다 낮은 이유를 분석해줘"
- **도구**: SQL (데이터), PL/SQL (분석 알고리즘), Notification (알림)
- **효과**: 즉각적인 인사이트 제공

---

### 마스터 체크리스트

**기초 (필수)**
- [ ] ReAct 패턴 이해
- [ ] Tool, Task, Agent, Team 개념 이해
- [ ] SQL Tool 생성 및 사용
- [ ] PL/SQL Tool 생성 및 사용
- [ ] SELECT AI AGENT 구문으로 대화

**중급 (권장)**
- [ ] Python으로 Agent 호출
- [ ] 멀티턴 대화 구현
- [ ] 실행 로그 분석 및 디버깅
- [ ] Task Instruction 최적화

**고급 (선택)**
- [ ] RAG Tool 통합
- [ ] REST API로 Agent 노출
- [ ] 다중 에이전트 시스템 설계
- [ ] 프로덕션 배포 (보안, 모니터링)

---

### Quick Reference

#### 자주 사용하는 SQL 구문

```sql
-- Agent 실행
SELECT AI AGENT '질문';

-- 팀 활성화
EXEC DBMS_CLOUD_AI_AGENT.SET_TEAM('팀이름');

-- 활성 팀 확인
SELECT DBMS_CLOUD_AI_AGENT.GET_TEAM() FROM DUAL;

-- 최근 대화 조회
SELECT * FROM USER_AI_AGENT_CHAT_HISTORY ORDER BY CREATED DESC FETCH FIRST 5 ROWS ONLY;

-- 실행 로그 조회
SELECT * FROM USER_AI_AGENT_EXECUTION_LOG WHERE CONVERSATION_ID = '...' ORDER BY STEP_NUMBER;

-- 도구 목록
SELECT TOOL_NAME, TOOL_TYPE FROM USER_AI_AGENT_TOOLS;

-- 팀 목록
SELECT TEAM_NAME FROM USER_AI_AGENT_TEAMS;
```

#### 자주 사용하는 Python 코드

```python
# 기본 호출
response = cursor.callfunc(
    "DBMS_CLOUD_AI_AGENT.RUN_TEAM",
    str,
    keywordParameters={
        "team_name": "팀이름",
        "user_prompt": "질문",
        "params": '{"conversation_id": "..."}'
    }
)

# 대화 세션 생성
conv_id = cursor.callfunc("DBMS_CLOUD_AI.CREATE_CONVERSATION", str)

# 대화 세션 삭제
cursor.callproc("DBMS_CLOUD_AI.DELETE_CONVERSATION", [conv_id])
```

---

## 완료!

축하합니다! Oracle Select AI Agent의 핵심 개념과 실습을 완료하셨습니다.

**다음 학습 경로:**
1. 자신의 데이터베이스에 Agent 구축하기
2. 실제 비즈니스 문제에 적용하기
3. 고급 기능(RAG, API 통합) 탐구하기
4. 프로덕션 환경에 배포하기

**피드백 및 개선사항:**
- GitHub Issues에 질문 올리기
- 실습 과정에서 어려웠던 부분 공유
- 새로운 Use Case 제안

---

---

## [부록] 추가 예제 및 샘플 코드

### 유용한 SQL 스니펫 모음

#### 스니펫 1: Agent 상태 종합 대시보드

```sql
-- ===============================================
-- Agent 상태 한눈에 보기
-- ===============================================

SET LINESIZE 200
SET PAGESIZE 100

PROMPT ========================================
PROMPT  Select AI Agent 상태 대시보드
PROMPT ========================================

PROMPT
PROMPT [1] 생성된 객체 개수
PROMPT ----------------------------------------

SELECT 
    'Tools' AS CATEGORY,
    COUNT(*) AS COUNT
FROM USER_AI_AGENT_TOOLS
UNION ALL
SELECT 'Tasks', COUNT(*) FROM USER_AI_AGENT_TASKS
UNION ALL
SELECT 'Agents', COUNT(*) FROM USER_AI_AGENTS
UNION ALL
SELECT 'Teams', COUNT(*) FROM USER_AI_AGENT_TEAMS;

PROMPT
PROMPT [2] 활성 팀
PROMPT ----------------------------------------

SELECT DBMS_CLOUD_AI_AGENT.GET_TEAM() AS ACTIVE_TEAM FROM DUAL;

PROMPT
PROMPT [3] 최근 대화 (5건)
PROMPT ----------------------------------------

SELECT 
    TO_CHAR(CREATED, 'MM-DD HH24:MI') AS TIME,
    SUBSTR(USER_PROMPT, 1, 50) AS QUESTION,
    SUBSTR(RESPONSE, 1, 50) AS ANSWER
FROM USER_AI_AGENT_CHAT_HISTORY
ORDER BY CREATED DESC
FETCH FIRST 5 ROWS ONLY;

PROMPT
PROMPT [4] 도구 사용 통계 (최근 24시간)
PROMPT ----------------------------------------

SELECT 
    ACTION_NAME,
    COUNT(*) AS USAGE
FROM USER_AI_AGENT_EXECUTION_LOG
WHERE CREATED >= SYSDATE - 1
  AND ACTION_NAME IS NOT NULL
GROUP BY ACTION_NAME
ORDER BY USAGE DESC;
```

---

#### 스니펫 2: 대화형 SQL*Plus 스크립트

```sql
-- ===============================================
-- 대화형 Agent 세션 (SQL*Plus)
-- 사용법: @chat_session.sql
-- ===============================================

SET SERVEROUTPUT ON
SET FEEDBACK OFF
SET VERIFY OFF

ACCEPT user_question CHAR PROMPT '질문: '

DECLARE
    v_response CLOB;
    v_conv_id VARCHAR2(100);
BEGIN
    -- 대화 세션 생성 (또는 기존 세션 재사용)
    BEGIN
        v_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION;
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('대화 세션 재사용');
    END;
    
    -- Agent 실행
    v_response := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
        team_name => 'Northwind_Support_Team',
        user_prompt => '&user_question',
        params => '{"conversation_id": "' || v_conv_id || '"}'
    );
    
    -- 응답 출력
    DBMS_OUTPUT.PUT_LINE(' ');
    DBMS_OUTPUT.PUT_LINE('Agent:');
    DBMS_OUTPUT.PUT_LINE(v_response);
    DBMS_OUTPUT.PUT_LINE(' ');
END;
/

-- 다시 실행하려면
@chat_session.sql
```

---

#### 스니펫 3: 배치 테스트 스크립트

```sql
-- ===============================================
-- Agent 배치 테스트 (여러 질문 자동 실행)
-- ===============================================

DECLARE
    TYPE question_array IS TABLE OF VARCHAR2(1000);
    v_questions question_array;
    v_response CLOB;
    v_conv_id VARCHAR2(100);
    v_start_time TIMESTAMP;
    v_end_time TIMESTAMP;
    v_duration NUMBER;
BEGIN
    -- 테스트 질문 목록
    v_questions := question_array(
        'What is the most expensive product?',
        'How many orders were placed in 1996?',
        'Show me customers from Germany',
        'I want to return order 10248 because it is damaged',
        'What are the top 5 products by revenue?'
    );
    
    -- 대화 세션 생성
    v_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION;
    
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE(' Agent 배치 테스트');
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('');
    
    -- 각 질문 실행
    FOR i IN 1..v_questions.COUNT LOOP
        DBMS_OUTPUT.PUT_LINE('['||i||'/' || v_questions.COUNT || '] ' || v_questions(i));
        
        v_start_time := SYSTIMESTAMP;
        
        v_response := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
            team_name => 'Northwind_Support_Team',
            user_prompt => v_questions(i),
            params => '{"conversation_id": "' || v_conv_id || '"}'
        );
        
        v_end_time := SYSTIMESTAMP;
        v_duration := EXTRACT(SECOND FROM (v_end_time - v_start_time));
        
        DBMS_OUTPUT.PUT_LINE('응답: ' || SUBSTR(v_response, 1, 100) || '...');
        DBMS_OUTPUT.PUT_LINE('소요시간: ' || ROUND(v_duration, 2) || '초');
        DBMS_OUTPUT.PUT_LINE('----------------------------------------');
        DBMS_OUTPUT.PUT_LINE('');
    END LOOP;
    
    DBMS_OUTPUT.PUT_LINE('배치 테스트 완료!');
END;
/
```

---

### Python 유틸리티 함수 모음

파일: `agent_utils.py`

```python
"""
Select AI Agent 유틸리티 함수 모음
재사용 가능한 헬퍼 함수들
"""

import oracledb
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
import json

load_dotenv()

class AgentClient:
    """Select AI Agent 클라이언트 클래스"""
    
    def __init__(self):
        """초기화 및 DB 연결"""
        self.connection = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN"),
            config_dir=os.getenv("WALLET_DIR"),
            wallet_location=os.getenv("WALLET_DIR"),
            wallet_password=os.getenv("WALLET_PASSWORD")
        )
        self.cursor = self.connection.cursor()
        print("AgentClient 초기화 완료")
    
    def list_tools(self) -> List[Dict]:
        """생성된 도구 목록 조회"""
        query = """
            SELECT TOOL_NAME, TOOL_TYPE, DESCRIPTION
            FROM USER_AI_AGENT_TOOLS
            ORDER BY CREATED DESC
        """
        self.cursor.execute(query)
        return [
            {"name": row[0], "type": row[1], "description": row[2]}
            for row in self.cursor.fetchall()
        ]
    
    def list_agents(self) -> List[Dict]:
        """생성된 에이전트 목록 조회"""
        query = """
            SELECT 
                AGENT_NAME,
                JSON_VALUE(ATTRIBUTES, '$.profile_name') AS PROFILE,
                JSON_VALUE(ATTRIBUTES, '$.role') AS ROLE
            FROM USER_AI_AGENTS
            ORDER BY CREATED DESC
        """
        self.cursor.execute(query)
        return [
            {"name": row[0], "profile": row[1], "role": row[2]}
            for row in self.cursor.fetchall()
        ]
    
    def list_teams(self) -> List[str]:
        """생성된 팀 목록 조회"""
        query = "SELECT TEAM_NAME FROM USER_AI_AGENT_TEAMS ORDER BY CREATED DESC"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_active_team(self) -> str:
        """현재 활성화된 팀 조회"""
        result = self.cursor.callfunc("DBMS_CLOUD_AI_AGENT.GET_TEAM", str)
        return result
    
    def set_team(self, team_name: str):
        """팀 활성화"""
        self.cursor.callproc("DBMS_CLOUD_AI_AGENT.SET_TEAM", [team_name])
        print(f"팀 '{team_name}' 활성화됨")
    
    def create_conversation(self) -> str:
        """새 대화 세션 생성"""
        conv_id = self.cursor.callfunc("DBMS_CLOUD_AI.CREATE_CONVERSATION", str)
        print(f"대화 세션 생성: {conv_id}")
        return conv_id
    
    def ask(self, question: str, conversation_id: Optional[str] = None, 
            team_name: str = "Northwind_Support_Team") -> str:
        """Agent에게 질문"""
        params = f'{{"conversation_id": "{conversation_id}"}}' if conversation_id else None
        
        response = self.cursor.callfunc(
            "DBMS_CLOUD_AI_AGENT.RUN_TEAM",
            str,
            keywordParameters={
                "team_name": team_name,
                "user_prompt": question,
                "params": params
            }
        )
        return response
    
    def get_chat_history(self, conversation_id: str) -> List[Dict]:
        """대화 기록 조회"""
        query = """
            SELECT 
                USER_PROMPT,
                RESPONSE,
                TO_CHAR(CREATED, 'YYYY-MM-DD HH24:MI:SS') AS TIME
            FROM USER_AI_AGENT_CHAT_HISTORY
            WHERE CONVERSATION_ID = :conv_id
            ORDER BY CREATED
        """
        self.cursor.execute(query, conv_id=conversation_id)
        return [
            {"question": row[0], "answer": row[1], "time": row[2]}
            for row in self.cursor.fetchall()
        ]
    
    def get_execution_log(self, conversation_id: str) -> List[Dict]:
        """실행 로그 조회 (디버깅용)"""
        query = """
            SELECT 
                STEP_NUMBER,
                THOUGHT,
                ACTION_NAME,
                ACTION_INPUT,
                OBSERVATION
            FROM USER_AI_AGENT_EXECUTION_LOG
            WHERE CONVERSATION_ID = :conv_id
            ORDER BY STEP_NUMBER
        """
        self.cursor.execute(query, conv_id=conversation_id)
        return [
            {
                "step": row[0],
                "thought": row[1],
                "action": row[2],
                "input": row[3],
                "observation": row[4]
            }
            for row in self.cursor.fetchall()
        ]
    
    def close(self):
        """연결 종료"""
        self.cursor.close()
        self.connection.close()
        print("연결 종료")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# 사용 예시
if __name__ == "__main__":
    with AgentClient() as client:
        # 객체 목록 조회
        print("\n도구 목록:")
        for tool in client.list_tools():
            print(f"  - {tool['name']} ({tool['type']})")
        
        print("\n에이전트 목록:")
        for agent in client.list_agents():
            print(f"  - {agent['name']} using {agent['profile']}")
        
        print("\n팀 목록:")
        for team in client.list_teams():
            print(f"  - {team}")
        
        # 대화 시작
        conv_id = client.create_conversation()
        
        # 질문
        response = client.ask("What is the most expensive product?", conv_id)
        print(f"\n응답:\n{response}")
```

---

### 트러블슈팅 도구

파일: `diagnose_agent.py`

```python
"""
Select AI Agent 진단 도구
Agent가 제대로 설정되었는지 확인
"""

import oracledb
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

def diagnose():
    """Agent 환경 진단"""
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}  Select AI Agent 진단 도구")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    issues_found = 0
    
    try:
        # 1. DB 연결 테스트
        print(f"{Fore.YELLOW}[1/7] 데이터베이스 연결 테스트...")
        conn = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN"),
            config_dir=os.getenv("WALLET_DIR"),
            wallet_location=os.getenv("WALLET_DIR"),
            wallet_password=os.getenv("WALLET_PASSWORD")
        )
        cursor = conn.cursor()
        print(f"{Fore.GREEN}  연결 성공\n")
        
        # 2. 권한 확인
        print(f"{Fore.YELLOW}[2/7] Agent 패키지 권한 확인...")
        cursor.execute("""
            SELECT COUNT(*) FROM USER_TAB_PRIVS 
            WHERE TABLE_NAME IN ('DBMS_CLOUD_AI_AGENT', 'DBMS_CLOUD_AI')
        """)
        priv_count = cursor.fetchone()[0]
        if priv_count >= 2:
            print(f"{Fore.GREEN}  권한 OK ({priv_count}/2)\n")
        else:
            print(f"{Fore.RED}  권한 부족 ({priv_count}/2)")
            print(f"     ADMIN 계정에서 GRANT EXECUTE 실행 필요\n")
            issues_found += 1
        
        # 3. AI 프로파일 확인
        print(f"{Fore.YELLOW}[3/7] AI 프로파일 확인...")
        cursor.execute("SELECT COUNT(*) FROM USER_CLOUD_AI_PROFILES")
        profile_count = cursor.fetchone()[0]
        if profile_count > 0:
            print(f"{Fore.GREEN}  프로파일 존재 ({profile_count}개)\n")
        else:
            print(f"{Fore.RED}  AI 프로파일 없음")
            print(f"     CREATE_PROFILE로 프로파일 생성 필요\n")
            issues_found += 1
        
        # 4. 도구 확인
        print(f"{Fore.YELLOW}[4/7] 생성된 도구 확인...")
        cursor.execute("SELECT COUNT(*) FROM USER_AI_AGENT_TOOLS")
        tool_count = cursor.fetchone()[0]
        if tool_count > 0:
            print(f"{Fore.GREEN}  도구 존재 ({tool_count}개)")
            cursor.execute("SELECT TOOL_NAME, TOOL_TYPE FROM USER_AI_AGENT_TOOLS")
            for row in cursor:
                print(f"     - {row[0]} ({row[1]})")
            print()
        else:
            print(f"{Fore.RED}  도구 없음")
            print(f"     CREATE_TOOL로 도구 생성 필요\n")
            issues_found += 1
        
        # 5. 팀 확인
        print(f"{Fore.YELLOW}[5/7] 팀 확인...")
        cursor.execute("SELECT COUNT(*) FROM USER_AI_AGENT_TEAMS")
        team_count = cursor.fetchone()[0]
        if team_count > 0:
            print(f"{Fore.GREEN}  팀 존재 ({team_count}개)\n")
        else:
            print(f"{Fore.RED}  팀 없음")
            print(f"     CREATE_TEAM으로 팀 생성 필요\n")
            issues_found += 1
        
        # 6. 활성 팀 확인
        print(f"{Fore.YELLOW}[6/7] 활성 팀 확인...")
        active_team = cursor.callfunc("DBMS_CLOUD_AI_AGENT.GET_TEAM", str)
        if active_team:
            print(f"{Fore.GREEN}  활성 팀: {active_team}\n")
        else:
            print(f"{Fore.RED}  활성화된 팀 없음")
            print(f"     SET_TEAM으로 팀 활성화 필요\n")
            issues_found += 1
        
        # 7. 테스트 실행
        print(f"{Fore.YELLOW}[7/7] Agent 테스트 실행...")
        if active_team:
            try:
                test_response = cursor.callfunc(
                    "DBMS_CLOUD_AI_AGENT.RUN_TEAM",
                    str,
                    keywordParameters={
                        "team_name": active_team,
                        "user_prompt": "Hello",
                        "params": None
                    }
                )
                print(f"{Fore.GREEN}  Agent 응답 성공")
                print(f"     응답: {test_response[:100]}...\n")
            except Exception as e:
                print(f"{Fore.RED}  Agent 실행 실패")
                print(f"     에러: {str(e)}\n")
                issues_found += 1
        else:
            print(f"{Fore.RED}  ⏭️  활성 팀이 없어 테스트 스킵\n")
        
        # 최종 결과
        print(f"{Fore.CYAN}{'='*60}")
        if issues_found == 0:
            print(f"{Fore.GREEN}  모든 검사 통과! Agent 사용 준비 완료")
        else:
            print(f"{Fore.RED}   {issues_found}개의 문제 발견")
            print(f"{Fore.YELLOW}  위의 메시지를 참고하여 문제를 해결하세요")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"{Fore.RED}진단 실패: {e}")

if __name__ == "__main__":
    # colorama 설치: pip install colorama
    diagnose()
```

**실행:**
```bash
pip install colorama
python diagnose_agent.py
```

---

### 실전 예제 프로젝트

#### 프로젝트 1: Slack 봇 통합

파일: `slack_bot.py`

```python
"""
Slack Bot with Select AI Agent
/ask 명령어로 Agent와 대화
"""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

# Slack 앱 초기화
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# DB 연결
def get_db_connection():
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
        config_dir=os.getenv("WALLET_DIR"),
        wallet_location=os.getenv("WALLET_DIR"),
        wallet_password=os.getenv("WALLET_PASSWORD")
    )

# /ask 명령어 핸들러
@app.command("/ask")
def handle_ask_command(ack, command, say):
    """
    /ask What is the most expensive product?
    """
    ack()
    
    question = command['text']
    
    # Agent에게 질문
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        response = cursor.callfunc(
            "DBMS_CLOUD_AI_AGENT.RUN_TEAM",
            str,
            keywordParameters={
                "team_name": "Northwind_Support_Team",
                "user_prompt": question,
                "params": None
            }
        )
        
        # Slack에 응답
        say({
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*질문:* {question}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Agent 응답:*\n{response}"
                    }
                }
            ]
        })
        
    except Exception as e:
        say(f"에러 발생: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Slack 봇 시작
    # pip install slack-bolt
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
```

---

#### 프로젝트 2: 비용 모니터링 대시보드

파일: `cost_monitor.py`

```python
"""
Select AI Agent 비용 모니터링
LLM API 사용량 및 예상 비용 계산
"""

import oracledb
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# 토큰당 비용 (예시)
COST_PER_1K_TOKENS = {
    'gpt-4': 0.03,
    'gpt-3.5-turbo': 0.002,
    'claude-3-opus': 0.015,
    'cohere-command': 0.001
}

def calculate_costs():
    """비용 계산"""
    
    conn = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
        config_dir=os.getenv("WALLET_DIR"),
        wallet_location=os.getenv("WALLET_DIR"),
        wallet_password=os.getenv("WALLET_PASSWORD")
    )
    cursor = conn.cursor()
    
    # 최근 30일 사용량
    query = """
        SELECT 
            COUNT(*) AS TOTAL_REQUESTS,
            SUM(TOKEN_COUNT) AS TOTAL_TOKENS
        FROM USER_AI_AGENT_CHAT_HISTORY
        WHERE CREATED >= SYSDATE - 30
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    
    if row:
        total_requests, total_tokens = row
        total_tokens = total_tokens or 0  # NULL 처리
        
        print("\n" + "="*60)
        print("  Select AI Agent 비용 리포트 (최근 30일)")
        print("="*60)
        print(f"\n총 요청 수: {total_requests:,}회")
        print(f"총 토큰 수: {total_tokens:,} tokens")
        
        print("\n모델별 예상 비용:")
        for model, cost in COST_PER_1K_TOKENS.items():
            estimated = (total_tokens / 1000) * cost
            print(f"  {model:20s}: ${estimated:,.2f}")
        
        print("\n" + "="*60 + "\n")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    calculate_costs()
```

---

### 고급 디버깅 기법

#### 디버깅 스크립트: Agent 사고 과정 시각화

파일: `trace_agent.py`

```python
"""
Agent 실행 추적 및 시각화
에이전트의 사고 과정을 단계별로 출력
"""

import oracledb
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()
console = Console()

def trace_agent_execution(question: str):
    """Agent 실행 추적"""
    
    conn = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
        config_dir=os.getenv("WALLET_DIR"),
        wallet_location=os.getenv("WALLET_DIR"),
        wallet_password=os.getenv("WALLET_PASSWORD")
    )
    cursor = conn.cursor()
    
    # 대화 세션 생성
    conv_id = cursor.callfunc("DBMS_CLOUD_AI.CREATE_CONVERSATION", str)
    
    console.print(f"\n[bold cyan]질문:[/bold cyan] {question}\n")
    
    # Agent 실행
    with console.status("[bold green]Agent 실행 중..."):
        response = cursor.callfunc(
            "DBMS_CLOUD_AI_AGENT.RUN_TEAM",
            str,
            keywordParameters={
                "team_name": "Northwind_Support_Team",
                "user_prompt": question,
                "params": f'{{"conversation_id": "{conv_id}"}}'
            }
        )
    
    # 실행 로그 조회
    cursor.execute("""
        SELECT 
            STEP_NUMBER,
            THOUGHT,
            ACTION_NAME,
            ACTION_INPUT,
            OBSERVATION
        FROM USER_AI_AGENT_EXECUTION_LOG
        WHERE CONVERSATION_ID = :conv_id
        ORDER BY STEP_NUMBER
    """, conv_id=conv_id)
    
    # 테이블로 출력
    table = Table(title="Agent 실행 추적")
    table.add_column("Step", style="cyan", width=6)
    table.add_column("Thought", style="yellow", width=30)
    table.add_column("Action", style="green", width=20)
    table.add_column("Observation", style="magenta", width=30)
    
    for row in cursor:
        table.add_row(
            str(row[0]),
            row[1][:27] + "..." if row[1] and len(row[1]) > 30 else row[1] or "",
            row[2] or "None",
            row[4][:27] + "..." if row[4] and len(row[4]) > 30 else row[4] or ""
        )
    
    console.print(table)
    
    # 최종 응답
    panel = Panel(response, title="[bold green]최종 응답", border_style="green")
    console.print(panel)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # rich 설치: pip install rich
    trace_agent_execution("I want to return order 10248 because it's defective")
```

**실행 결과 (색상 포함):**
```
질문: I want to return order 10248 because it's defective

╭─────────────────── Agent 실행 추적 ────────────────────╮
│ Step │ Thought                   │ Action            │ Observation      │
├──────┼───────────────────────────┼───────────────────┼──────────────────┤
│ 1    │ User wants to return...   │ Return_Auth_Gen...│ RMA-10248-def... │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────── 최종 응답 ────────────────────────╮
│ I've processed your return request for order 10248. Your    │
│ RMA number is: RMA-10248-def-742                            │
╰─────────────────────────────────────────────────────────────╯
```

---

### 추가 참고 자료

#### 샘플 프로젝트 저장소
```
northwind-agent/
├── sql/
│   ├── 01_setup_permissions.sql
│   ├── 02_create_tools.sql
│   ├── 03_create_tasks.sql
│   ├── 04_create_agents.sql
│   ├── 05_create_teams.sql
│   └── 99_cleanup.sql
├── python/
│   ├── agent_client.py
│   ├── chatbot.py
│   ├── api_server.py
│   ├── streamlit_app.py
│   └── utils/
│       ├── agent_utils.py
│       └── diagnose_agent.py
├── .env.example
├── requirements.txt
└── README.md
```

#### requirements.txt

```
oracledb==2.0.0
python-dotenv==1.0.0
fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.0
slack-bolt==1.18.0
rich==13.7.0
colorama==0.4.6
```

---

### 다음 교육 과정 안내

**3회차: Oracle AI Vector Search와 Agent 통합**
- 문서 임베딩 및 벡터 인덱스 생성
- RAG Tool 구축
- Semantic Search 에이전트
- 멀티모달 Agent (텍스트 + 이미지)

**4회차: 프로덕션 배포 및 운영**
- 고가용성 설계
- 모니터링 및 알림
- A/B 테스팅
- 비용 최적화

---

**Last Updated**: 2024-12-08  
**Version**: 2.0  
**Author**: Oracle AI Training Team  
**Contact**: training@oracle.com

---

**라이센스**: 본 문서는 교육 목적으로 자유롭게 사용 가능합니다.

**기여**: 개선사항이나 오류 발견 시 Pull Request 환영합니다!