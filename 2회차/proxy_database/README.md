# Oracle Autonomous AI Database: Select AI 심화 - Proxy Database 핸즈온 가이드

## 목차
1. [Select AI 아키텍처와 "Sidecar" 모델](#1-select-ai-아키텍처와-sidecar-모델)
2. [대화형 AI (Conversations) 및 문맥 유지](#2-대화형-ai-conversations-및-문맥-유지)
3. [메타데이터 보강을 통한 정확도 향상](#3-메타데이터-보강을-통한-정확도-향상)
4. [Select AI with RAG (검색 증강 생성)](#4-select-ai-with-rag-검색-증강-생성)
5. [보안 및 거버넌스: Real Application Security (RAS)](#5-보안-및-거버넌스-real-application-security-ras)
6. [엔터프라이즈 통합 및 확장](#6-엔터프라이즈-통합-및-확장)
7. [핸즈온 실습 가이드](#7-핸즈온-실습-가이드)
8. [DBMS_CLOUD_AI 패키지 핵심 레퍼런스](#8-dbms_cloud_ai-패키지-핵심-레퍼런스)

---

## 시작하기 전에

### 사전 준비 사항
- Oracle Autonomous Database 인스턴스 (Always Free 또는 유료)
- SQL Developer, SQL*Plus, 또는 Database Actions 접속 환경
- OCI (Oracle Cloud Infrastructure) 계정 및 API Keys
- 선택사항: 외부 데이터베이스 (PostgreSQL, MySQL 등) 접속 정보

### 핸즈온 학습 목표
이 가이드를 완료하면 다음을 수행할 수 있습니다:
- ✅ Select AI Sidecar 아키텍처를 이해하고 구성하기
- ✅ 여러 데이터베이스에 걸친 연합 쿼리 실행하기
- ✅ 대화형 AI를 활용한 연속적인 데이터 탐색하기
- ✅ RAG를 통해 비정형 데이터와 정형 데이터 통합하기
- ✅ RAS를 통한 세밀한 데이터 보안 정책 구현하기

---

## 1. Select AI 아키텍처와 "Sidecar" 모델

### 1.1 Sidecar(사이드카) 개념 및 필요성

**비즈니스 문제:** 기존 비즈니스 사용자는 SQL 기술 부족으로 인해 데이터 접근에 장벽이 있었습니다. 데이터 분석가나 개발자에게 매번 요청해야 하는 번거로움이 있었죠.

**해결책:** Select AI는 **"AI Sidecar"** 모델을 통해 이 문제를 해결합니다.

#### Sidecar 모델이란?
마치 오토바이 옆에 붙어있는 사이드카처럼, 기존 데이터베이스 시스템에 영향을 주지 않으면서 AI 기능을 제공하는 별도의 지능형 계층입니다.

**핵심 개념:**
* **개념:** Select AI Sidecar는 기존 데이터베이스와 함께 작동하는 Oracle Autonomous Database(ADB) 인스턴스(별도 또는 기존 인스턴스)를 사용하여 SQL 변환 및 연합 쿼리(Federated Query)를 오프로드(Offload)합니다[cite: 10].
* **역할:** 사용자의 자연어 질문을 해석하고, 연결된 여러 데이터 소스(온프레미스, 멀티 클라우드 등)에 대한 쿼리를 대신 수행합니다[cite: 11].
* **이점:** 복잡한 ETL 프로세스나 데이터 이동 없이, 비즈니스 사용자가 "지난달 재택근무 직원 수는?"과 같은 질문을 통해 즉각적인 인사이트를 얻을 수 있습니다 [cite: 8, 62-66].

#### 아키텍처 다이어그램 설명

```
┌─────────────────┐
│  비즈니스 사용자   │  "지난달 매출이 가장 높은 제품은?"
└────────┬────────┘
         │ 자연어 질문
         ▼
┌─────────────────────────────────┐
│   Select AI Sidecar (ADB)       │
│  ┌───────────────────────────┐  │
│  │ 1. 자연어 → SQL 변환      │  │
│  │ 2. 데이터 소스 위치 파악   │  │
│  │ 3. 연합 쿼리 생성          │  │
│  │ 4. 결과 집계 및 반환       │  │
│  └───────────────────────────┘  │
└───────┬─────────────────┬───────┘
        │                 │
        │                 │
┌───────▼──────┐   ┌─────▼────────┐   ┌──────────┐
│ Oracle DB    │   │ PostgreSQL   │   │ BigQuery │
│ (온프레미스)   │   │ (AWS RDS)    │   │ (GCP)    │
└──────────────┘   └──────────────┘   └──────────┘
```

### 1.2 연합 쿼리 (Federated Queries)

Select AI의 가장 강력한 기능 중 하나는 **여러 데이터베이스에 흩어진 데이터를 마치 하나의 데이터베이스처럼 조회**할 수 있다는 점입니다.

#### 작동 원리
* **작동 방식:** 예를 들어, "Acme Corp의 보류 중인 주문 보여줘"라는 질문에 대해 Google Cloud의 BigQuery에 있는 고객 데이터와 AWS Redshift의 주문 데이터를 조인하여 결과를 가져올 수 있습니다[cite: 52].
* **자동화:** Select AI는 조인, 데이터 위치 파악, 쿼리 최적화의 복잡성을 처리하므로 사용자는 데이터의 위치를 알 필요가 없습니다[cite: 53].

#### 지원 데이터 소스
Select AI는 다음과 같은 다양한 데이터 소스를 지원합니다 [cite: 2830-2832]:

| 카테고리 | 데이터 소스 |
|---------|------------|
| **관계형 DB** | Oracle Database, PostgreSQL, MySQL, Microsoft SQL Server |
| **클라우드 DW** | Snowflake, AWS Redshift, Google BigQuery, Azure Synapse |
| **NoSQL** | MongoDB, Cassandra |
| **데이터 레이크** | Apache Iceberg (Glue, Polaris, Unity Catalog) |

#### 실제 사용 사례

**시나리오:** 글로벌 이커머스 회사
- 고객 정보: Oracle Database (온프레미스)
- 주문 내역: AWS Redshift
- 제품 카탈로그: Google BigQuery
- 고객 리뷰: MongoDB

**기존 방법의 문제점:**
1. 각 시스템에 개별적으로 접속
2. 데이터를 추출하여 수동으로 통합
3. 복잡한 ETL 파이프라인 구축 및 유지보수
4. 실시간성 부족

**Select AI 방식:**
```sql
-- 사용자는 단순히 질문만 하면 됩니다
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '지난 주 가장 많이 팔린 제품과 그 제품에 대한 평균 리뷰 점수를 보여줘',
  profile_name => 'FEDERATED_PROFILE',
  action => 'runsql'
) FROM DUAL;
```

Select AI가 자동으로:
1. BigQuery에서 제품 판매 데이터 조회
2. MongoDB에서 리뷰 데이터 조회
3. 두 데이터를 조인하여 결과 반환

---

## 2. 대화형 AI (Conversations) 및 문맥 유지

### 2.1 대화형 쿼리의 차별점

#### 단발성 질문 vs 대화형 질문

**단발성 질문 (Natural Language Query):**
매번 독립적인 질문을 해야 하므로 탐색적 분석이 어렵습니다.

```
질문 1: "총 매출을 보여줘"
질문 2: "총 매출을 제품 카테고리별로 나눠줘" ❌ (처음부터 다시 설명)
질문 3: "총 매출을 제품 카테고리별, 지역별로 나눠줘" ❌ (또 다시 설명)
```

**대화형 질문 (Conversations):**
[cite_start]이전 질문과 답변의 문맥을 기억하여 자연스러운 탐색을 가능하게 합니다 [cite: 129-131].

```
질문 1: "총 스트리밍 횟수는?" 
       → Select AI가 쿼리 실행 및 문맥 저장

질문 2: "장르별로 나눠줘" ✅ 
       → '스트리밍 횟수'를 기억하고 GROUP BY 추가

질문 3: "고객 세그먼트도 추가해줘" ✅
       → 이전 쿼리에 또 다른 차원 추가 [cite: 135-137]
```

#### 실제 비즈니스 시나리오

**시나리오: 영업 데이터 탐색**

```
사용자: "지난 분기 매출을 보여줘"
AI: [쿼리 실행] 총 $1,250,000

사용자: "어느 지역이 가장 높아?"
AI: [이전 문맥 유지] 북미 지역이 $650,000로 가장 높습니다

사용자: "그 지역의 상위 5개 제품은?"
AI: [북미 지역 + 지난 분기 문맥 유지] 
    1. Product A - $150,000
    2. Product B - $120,000
    ...

사용자: "해당 제품들의 작년 동기 대비 성장률은?"
AI: [모든 이전 문맥 통합하여 분석]
```

### 2.2 프로파일 설정 (conversations: true)

대화 기능을 활성화하려면 AI 프로파일 생성 시 `conversations` 속성을 `true`로 설정해야 합니다.

#### 기본 프로파일 생성

```sql
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE (
    profile_name => 'CONVERSATION_PROFILE',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'credential_name' VALUE 'OCI_CRED',
      'object_list' VALUE JSON_ARRAY(
        JSON_OBJECT(
          'owner' VALUE 'ADMIN',
          'name' VALUE 'SALES_DATA'
        ),
        JSON_OBJECT(
          'owner' VALUE 'ADMIN',
          'name' VALUE 'CUSTOMERS'
        )
      ),
      'conversation' VALUE 'true',  -- 대화 기능 활성화
      'model' VALUE 'cohere.command-r-plus'
    )
  );
END;
/
```

#### 프로파일 활성화

```sql
-- 현재 세션에서 프로파일 설정
BEGIN
  DBMS_CLOUD_AI.SET_PROFILE(
    profile_name => 'CONVERSATION_PROFILE'
  );
END;
/
```

[cite: 157-167, 1101-1106]

### 2.3 대화 관리 (API)

Select AI는 대화 세션을 관리하기 위한 전용 프로시저와 함수를 제공합니다.

#### 주요 API 함수

| API | 설명 | 사용 시점 |
|-----|------|----------|
| **CREATE_CONVERSATION** | [cite: 2539, 2546] 새로운 대화 세션 생성 | 새로운 분석 세션 시작 시 |
| **SET_CONVERSATION_ID** | [cite: 2573] 기존 대화 세션 재개 | 이전 대화 이어가기 |
| **GET_CONVERSATION_ID** | [cite: 2577] 현재 활성 대화 ID 확인 | 현재 문맥 확인 필요 시 |
| **CLEAR_CONVERSATION_ID** | [cite: 2582] 대화 컨텍스트 초기화 | 새로운 주제로 전환 시 |
| **DROP_CONVERSATION** | [cite: 2594] 대화 세션 완전 삭제 | 대화 이력 제거 시 |

#### 실습: 대화 세션 관리

**Step 1: 새로운 대화 세션 생성**

```sql
DECLARE
  v_conversation_id NUMBER;
BEGIN
  v_conversation_id := DBMS_CLOUD_AI.CREATE_CONVERSATION(
    profile_name => 'CONVERSATION_PROFILE',
    description => '2024 Q4 매출 분석',
    attributes => JSON_OBJECT(
      'retention_days' VALUE 30,  -- 30일간 대화 이력 보관
      'max_history' VALUE 20      -- 최대 20개 이전 질문 기억
    )
  );
  
  DBMS_OUTPUT.PUT_LINE('Conversation ID: ' || v_conversation_id);
END;
/
```

**Step 2: 연속적인 질문하기**

```sql
-- 첫 번째 질문
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '2024년 10월 총 매출은?',
  action => 'runsql'
) as response FROM DUAL;

-- 두 번째 질문 (문맥 유지)
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '지역별로 나눠줘',
  action => 'runsql'
) as response FROM DUAL;

-- 세 번째 질문 (계속 문맥 유지)
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '가장 높은 지역의 상위 3개 제품도 보여줘',
  action => 'runsql'
) as response FROM DUAL;
```

**Step 3: 대화 ID 확인**

```sql
SELECT DBMS_CLOUD_AI.GET_CONVERSATION_ID() as current_conversation 
FROM DUAL;
```

**Step 4: 대화 컨텍스트 초기화 (새로운 주제 시작)**

```sql
BEGIN
  DBMS_CLOUD_AI.CLEAR_CONVERSATION_ID();
END;
/

-- 이제 이전 문맥 없이 새로운 질문 가능
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '재고가 100개 미만인 제품을 보여줘',
  action => 'runsql'
) as response FROM DUAL;
```

**Step 5: 이전 대화 재개**

```sql
-- 저장해둔 conversation_id로 이전 대화 재개
BEGIN
  DBMS_CLOUD_AI.SET_CONVERSATION_ID(
    conversation_id => 12345  -- Step 1에서 받은 ID
  );
END;
/

-- 이전 문맥(2024년 10월 매출 분석)이 복원됨
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '작년 동월 대비 증감율은?',
  action => 'runsql'
) as response FROM DUAL;
```

**Step 6: 대화 세션 삭제**

```sql
BEGIN
  DBMS_CLOUD_AI.DROP_CONVERSATION(
    conversation_id => 12345
  );
END;
/
```

#### 대화 이력 조회

```sql
-- 현재 대화의 모든 이력 보기
SELECT 
  conversation_id,
  prompt_number,
  prompt_text,
  generated_sql,
  response_time,
  created_date
FROM USER_CLOUD_AI_CONVERSATIONS
WHERE conversation_id = DBMS_CLOUD_AI.GET_CONVERSATION_ID()
ORDER BY prompt_number;
```

#### 모범 사례 (Best Practices)

✅ **DO:**
- 탐색적 데이터 분석 시 대화 기능 사용
- 관련된 연속 질문은 하나의 대화 세션에서 진행
- 주제가 바뀔 때는 `CLEAR_CONVERSATION_ID()` 호출
- 중요한 분석 세션은 의미있는 `description` 설정

❌ **DON'T:**
- 서로 관련 없는 질문을 같은 대화에서 진행
- 너무 오래된 대화 세션 무한정 유지
- 대화 ID 없이 문맥 의존적인 질문 사용

---

## 3. 메타데이터 보강을 통한 정확도 향상

### 3.1 LLM의 환각 방지와 Comments의 역할

#### 문제 상황: 모호한 스키마

많은 레거시 시스템이나 개발 초기 데이터베이스는 의미 없는 이름을 사용합니다:

```sql
-- ❌ 나쁜 예: LLM이 이해할 수 없음
TABLE1
  - C1 (NUMBER)
  - C2 (VARCHAR2)
  - C3 (DATE)
  - C4 (NUMBER)

TABLE2
  - ID (NUMBER)
  - VAL1 (VARCHAR2)
  - VAL2 (NUMBER)
```

**질문:** "영화 타이틀별 평균 평점을 보여줘"

**LLM 반응:**
```
❌ 오류: 'MOVIE_TITLE'이라는 컬럼을 찾을 수 없습니다
❌ 환각: 존재하지 않는 'MOVIES' 테이블 참조
❌ 잘못된 가정: C2가 타이틀이라고 추측하여 잘못된 SQL 생성
```

#### 해결책: Database Comments 활용

[cite_start]Select AI는 데이터베이스의 **Comments(주석)**를 활용하여 LLM에게 스키마의 의미를 전달합니다 [cite: 311-313].

### 3.2 주석 활용 실습

#### Step 1: 테스트 테이블 생성 (주석 없이)

```sql
-- 의미 없는 이름의 테이블 생성
CREATE TABLE TBL_001 (
  C1 NUMBER PRIMARY KEY,
  C2 VARCHAR2(200),
  C3 DATE,
  C4 NUMBER(3,1),
  C5 VARCHAR2(50)
);

-- 샘플 데이터 입력
INSERT INTO TBL_001 VALUES (1, 'The Shawshank Redemption', DATE '1994-09-23', 9.3, 'Drama');
INSERT INTO TBL_001 VALUES (2, 'The Godfather', DATE '1972-03-24', 9.2, 'Crime');
INSERT INTO TBL_001 VALUES (3, 'The Dark Knight', DATE '2008-07-18', 9.0, 'Action');
COMMIT;
```

#### Step 2: 주석 없이 질문하기

```sql
-- 프로파일 생성 (comments 없이)
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE (
    profile_name => 'PROFILE_NO_COMMENTS',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'credential_name' VALUE 'OCI_CRED',
      'object_list' VALUE JSON_ARRAY(
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'TBL_001')
      ),
      'comments' VALUE 'false'  -- 주석 미사용
    )
  );
END;
/

-- 질문
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '평점이 9.0 이상인 영화 제목을 보여줘',
  profile_name => 'PROFILE_NO_COMMENTS',
  action => 'showsql'
) FROM DUAL;

-- 예상 결과: 오류 또는 잘못된 SQL
-- LLM이 '영화 제목'을 어느 컬럼에서 찾아야 할지 모름
```

#### Step 3: 테이블과 컬럼에 주석 추가

```sql
-- 테이블 주석
COMMENT ON TABLE TBL_001 IS 
'Movie database containing film information including titles, release dates, ratings, and genres';

-- 컬럼별 주석
COMMENT ON COLUMN TBL_001.C1 IS 
'Unique movie identifier (Primary Key)';

COMMENT ON COLUMN TBL_001.C2 IS 
'Movie title or name';

COMMENT ON COLUMN TBL_001.C3 IS 
'Theatrical release date';

COMMENT ON COLUMN TBL_001.C4 IS 
'Average user rating on a scale of 0-10';

COMMENT ON COLUMN TBL_001.C5 IS 
'Primary genre classification (Drama, Action, Comedy, etc.)';
```

#### Step 4: 주석을 활용하는 프로파일 생성

```sql
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE (
    profile_name => 'PROFILE_WITH_COMMENTS',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'credential_name' VALUE 'OCI_CRED',
      'object_list' VALUE JSON_ARRAY(
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'TBL_001')
      ),
      'comments' VALUE 'true'  -- 주석 활성화
    )
  );
  
  DBMS_CLOUD_AI.SET_PROFILE('PROFILE_WITH_COMMENTS');
END;
/
```

[cite: 319-322, 350]

#### Step 5: 동일한 질문으로 재시도

```sql
-- 질문 1: 영화 제목 검색
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '평점이 9.0 이상인 영화 제목을 보여줘',
  action => 'runsql'
) as result FROM DUAL;

-- 예상 SQL (LLM이 생성):
-- SELECT C2 as movie_title
-- FROM TBL_001
-- WHERE C4 >= 9.0;

-- 질문 2: 복잡한 조건
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '1990년대에 개봉한 드라마 장르 영화의 평균 평점은?',
  action => 'runsql'
) as result FROM DUAL;

-- 예상 SQL:
-- SELECT AVG(C4) as avg_rating
-- FROM TBL_001
-- WHERE C3 BETWEEN DATE '1990-01-01' AND DATE '1999-12-31'
--   AND C5 = 'Drama';
```

#### Step 6: 주석 효과 비교

```sql
-- 생성된 SQL 비교
SELECT 
  'Without Comments' as scenario,
  DBMS_CLOUD_AI.GENERATE(
    prompt => '가장 높은 평점의 영화는?',
    profile_name => 'PROFILE_NO_COMMENTS',
    action => 'showsql'
  ) as generated_sql
FROM DUAL
UNION ALL
SELECT 
  'With Comments' as scenario,
  DBMS_CLOUD_AI.GENERATE(
    prompt => '가장 높은 평점의 영화는?',
    profile_name => 'PROFILE_WITH_COMMENTS',
    action => 'showsql'
  ) as generated_sql
FROM DUAL;
```

### 3.3 고급 주석 전략

#### 비즈니스 규칙을 주석에 포함

```sql
-- 단순한 설명
COMMENT ON COLUMN SALES.AMOUNT IS 'Sale amount';

-- ✅ 비즈니스 규칙 포함
COMMENT ON COLUMN SALES.AMOUNT IS 
'Total sale amount in USD. Excludes tax and shipping. Negative values indicate refunds.';

-- ✅ 관계 설명
COMMENT ON COLUMN ORDERS.CUSTOMER_ID IS 
'Foreign key to CUSTOMERS.ID. Links order to customer who placed it.';

-- ✅ 계산 로직 설명
COMMENT ON COLUMN EMPLOYEES.ANNUAL_SALARY IS 
'Annual gross salary in USD. Calculate monthly: ANNUAL_SALARY / 12';
```

#### 코드 값 및 열거형 설명

```sql
-- ✅ 가능한 값 나열
COMMENT ON COLUMN ORDERS.STATUS IS 
'Order status: PENDING (awaiting payment), CONFIRMED (paid), SHIPPED (in transit), DELIVERED (completed), CANCELLED';

-- ✅ 약어 설명
COMMENT ON COLUMN EMPLOYEES.DEPT_CODE IS 
'Department code: HR (Human Resources), IT (Information Technology), FIN (Finance), MKT (Marketing), OPS (Operations)';
```

#### 날짜/시간 필드 주석

```sql
COMMENT ON COLUMN LOGS.CREATED_AT IS 
'Record creation timestamp in UTC timezone. Format: YYYY-MM-DD HH24:MI:SS';

COMMENT ON COLUMN PROJECTS.DUE_DATE IS 
'Project deadline date (business days only, excludes weekends and holidays)';
```

### 3.4 주석 품질 체크리스트

프로파일 생성 전에 다음을 확인하세요:

```sql
-- 주석 현황 확인
SELECT 
  table_name,
  column_name,
  CASE 
    WHEN comments IS NULL THEN '❌ 주석 없음'
    WHEN LENGTH(comments) < 10 THEN '⚠️ 주석 너무 짧음'
    ELSE '✅ 양호'
  END as comment_status,
  comments
FROM USER_COL_COMMENTS
WHERE table_name IN ('TBL_001', 'CUSTOMERS', 'ORDERS')
ORDER BY table_name, column_name;
```

#### 주석 작성 가이드라인

| 요소 | 포함할 내용 | 예시 |
|------|------------|------|
| **설명** | 컬럼의 비즈니스적 의미 | "고객이 주문을 생성한 날짜" |
| **데이터 타입** | 단위, 포맷, 범위 | "USD 단위, 소수점 2자리" |
| **관계** | 다른 테이블과의 연결 | "CUSTOMERS.ID를 참조하는 외래키" |
| **제약사항** | 비즈니스 규칙, 유효 값 | "0-100 사이 값, NULL은 미평가" |
| **계산** | 파생 컬럼의 계산 방식 | "PRICE * QUANTITY - DISCOUNT" |

---

## 4. Select AI with RAG (검색 증강 생성)

### 4.1 RAG가 필요한 이유

#### 전통적인 AI의 한계

```
❌ 질문: "우리 회사의 2024년 출장 정책에 따르면 항공권 예약은 며칠 전에 해야 하나요?"

LLM 응답: "일반적으로 기업들은 7-14일 전 예약을 권장합니다..."
          ⚠️ 하지만 이것은 일반적인 답변일 뿐, 귀사의 실제 정책이 아닙니다!
```

**문제점:**
- LLM은 학습 데이터에 없는 기업 내부 문서를 모름
- 최신 정책 변경 사항 반영 불가
- 환각(Hallucination): 그럴듯하지만 틀린 답변 생성

#### RAG (Retrieval Augmented Generation) 해결책

[cite_start]Select AI RAG는 기업의 비공개 데이터(문서, 매뉴얼, 사규 등)를 벡터화하여 저장하고, 사용자의 질문 시 관련 내용을 검색(Retrieval)하여 답변을 생성합니다[cite: 512].

```
✅ 질문: "우리 회사의 2024년 출장 정책에 따르면 항공권 예약은 며칠 전에 해야 하나요?"

1. 벡터 DB에서 "출장 정책", "항공권 예약"과 관련된 문서 청크 검색
2. 검색된 실제 회사 문서를 LLM 프롬프트에 포함
3. LLM이 실제 문서 기반으로 답변 생성

AI 응답: "귀사의 2024년 출장 정책(7페이지)에 따르면, 
          국내선은 3영업일 전, 국제선은 14일 전까지 예약해야 합니다.
          
          출처: 2024_Travel_Policy.pdf, 7페이지"
```

#### RAG 아키텍처

```
┌──────────────────────────────────────────────────────────┐
│ 1. 문서 준비 단계 (한 번만 수행)                            │
└──────────────────────────────────────────────────────────┘
                        │
        ┌───────────────▼────────────────┐
        │  Object Storage                 │
        │  📄 policy.pdf                  │
        │  📄 manual.docx                 │
        │  📄 handbook.txt                │
        └───────────────┬────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │  DBMS_CLOUD_AI.CREATE_VECTOR_INDEX    │
        │  • 문서 로드                           │
        │  • 청킹 (Chunking)                     │
        │  • 임베딩 생성 (Embedding)             │
        │  • 벡터 DB 저장                        │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────┐
        │  Vector Database                │
        │  [0.234, 0.891, -0.432, ...]   │
        │  [0.123, -0.234, 0.567, ...]   │
        └────────────────┬───────────────┘

┌──────────────────────────────────────────────────────────┐
│ 2. 쿼리 실행 단계 (사용자 질문마다)                         │
└──────────────────────────────────────────────────────────┘
                        │
        사용자 질문: "출장비 한도는?"
                        │
                        ▼
        ┌───────────────────────────────┐
        │  질문을 벡터로 변환              │
        │  [0.221, 0.876, -0.401, ...]  │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  유사도 검색 (Similarity)       │
        │  가장 관련성 높은 청크 Top-K    │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌────────────────────────────────┐
        │  LLM에 전달                     │
        │  프롬프트 = 질문 + 검색된 문서  │
        └────────────────┬───────────────┘
                        │
                        ▼
                답변 + 출처 정보
```

[cite: 527-528] **자동화된 파이프라인:** 문서 청킹(Chunking), 임베딩 생성, 벡터 저장, 검색, 프롬프트 증강의 전 과정을 Select AI가 자동화합니다.

### 4.2 RAG 실습: 기업 문서 검색 시스템 구축

#### 사전 준비: Object Storage 설정

**Step 1: OCI Object Storage Bucket 생성**

```
1. OCI Console → Storage → Buckets
2. Create Bucket
   - Name: company-documents
   - Storage Tier: Standard
   - Public Access: Disabled
```

**Step 2: 문서 업로드**

샘플 문서를 준비하여 버킷에 업로드:
- `hr_policy_2024.pdf` - HR 정책
- `travel_guidelines.txt` - 출장 가이드라인
- `security_handbook.docx` - 보안 매뉴얼

**Step 3: OCI Credential 생성**

```sql
-- API Key 기반 인증
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'OCI_CRED',
    username => 'ocid1.user.oc1..aaaaaaa...',  -- User OCID
    password => '-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBg...
-----END PRIVATE KEY-----'  -- API Private Key
  );
END;
/
```

#### 벡터 인덱스 생성

[cite: 2692-2702] **주요 속성:** 벡터 DB 제공자(`vector_db_provider`), 저장 위치(`location`), 임베딩 모델 프로파일, 청크 사이즈(`chunk_size`), 갱신 주기(`refresh_rate`) 등을 설정합니다.

```sql
BEGIN
  DBMS_CLOUD_AI.CREATE_VECTOR_INDEX(
    index_name => 'COMPANY_DOCS_INDEX',
    attributes => JSON_OBJECT(
      -- 벡터 DB 설정
      'vector_db_provider' VALUE 'oracle',
      'vector_table_name' VALUE 'COMPANY_DOCS_VECTORS',
      
      -- 문서 소스
      'location' VALUE 'https://objectstorage.us-ashburn-1.oraclecloud.com/n/[namespace]/b/company-documents/o/',
      'credential_name' VALUE 'OCI_CRED',
      'object_name' VALUE '*.pdf,*.txt,*.docx',  -- 모든 지원 문서
      
      -- 임베딩 모델
      'profile_name' VALUE 'EMBEDDING_PROFILE',
      'embedding_model' VALUE 'cohere.embed-multilingual-v3.0',  -- 다국어 지원
      
      -- 청킹 설정
      'chunk_size' VALUE 1000,        -- 청크당 1000자
      'chunk_overlap' VALUE 200,      -- 청크 간 200자 중복
      
      -- 메타데이터
      'metadata' VALUE JSON_OBJECT(
        'department' VALUE 'HR',
        'year' VALUE '2024'
      ),
      
      -- 갱신 주기
      'refresh_rate' VALUE 'DAILY',   -- 매일 자동 갱신
      'refresh_time' VALUE '02:00:00' -- 새벽 2시
    )
  );
END;
/
```

#### 임베딩 프로파일 생성

```sql
-- 임베딩 전용 프로파일
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'EMBEDDING_PROFILE',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'credential_name' VALUE 'OCI_CRED',
      'model' VALUE 'cohere.embed-multilingual-v3.0',
      'embedding_dimension' VALUE 1024
    )
  );
END;
/
```

#### RAG 프로파일 생성

```sql
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'RAG_PROFILE',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'credential_name' VALUE 'OCI_CRED',
      'model' VALUE 'cohere.command-r-plus',
      
      -- RAG 설정
      'rag_index_name' VALUE 'COMPANY_DOCS_INDEX',
      'rag_enabled' VALUE 'true',
      'top_k' VALUE 5,  -- 가장 관련성 높은 5개 청크 검색
      
      -- 정형 데이터 (선택사항)
      'object_list' VALUE JSON_ARRAY(
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'EMPLOYEES')
      )
    )
  );
  
  -- 프로파일 활성화
  DBMS_CLOUD_AI.SET_PROFILE('RAG_PROFILE');
END;
/
```

#### 벡터 인덱스 상태 확인

```sql
-- 인덱스 생성 진행 상황 확인
SELECT 
  index_name,
  status,
  total_documents,
  total_chunks,
  last_refresh_date,
  next_refresh_date
FROM USER_CLOUD_AI_VECTOR_INDEXES
WHERE index_name = 'COMPANY_DOCS_INDEX';
```

### 4.3 RAG 활용: 문서 기반 질의응답

#### narrate 액션 사용

[cite: 639-641] **활용:** `narrate` 액션을 사용하면 벡터 스토어에서 검색된 내용을 바탕으로 답변하며, 답변의 근거가 된 소스 문서 목록도 함께 제공합니다.

```sql
-- 질문 1: 단순 정책 조회
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '연차 휴가는 몇 일까지 사용할 수 있나요?',
  action => 'narrate'
) as answer FROM DUAL;

-- 예상 출력:
-- "직원은 연간 15일의 연차 휴가를 사용할 수 있으며, 
--  미사용 휴가는 최대 5일까지 다음 해로 이월 가능합니다.
--  
--  출처: hr_policy_2024.pdf (3페이지)"
```

#### 복잡한 질문

```sql
-- 질문 2: 조건부 정책
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '해외 출장 시 비즈니스 클래스 이용이 가능한 경우는?',
  action => 'narrate'
) as answer FROM DUAL;

-- 질문 3: 비교/계산
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '국내 출장과 해외 출장의 식비 지원 한도 차이는 얼마인가요?',
  action => 'narrate'
) as answer FROM DUAL;
```

#### 정형 + 비정형 데이터 통합 질의

```sql
-- EMPLOYEES 테이블과 문서를 함께 활용
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => 'IT 부서의 John Smith의 직급에서 승인 가능한 최대 구매 금액은?',
  action => 'narrate'
) as answer FROM DUAL;

-- Select AI가 수행하는 작업:
-- 1. EMPLOYEES 테이블에서 John Smith의 직급 조회 (예: Manager)
-- 2. 벡터 DB에서 "Manager 승인 권한" 관련 문서 검색
-- 3. 두 정보를 통합하여 답변 생성
```

### 4.4 고급 RAG 기능

#### 출처 추적 (Citation)

```sql
-- 답변과 함께 출처 정보 확인
SELECT 
  response.answer,
  response.citations
FROM (
  SELECT DBMS_CLOUD_AI.GENERATE(
    prompt => '보안 인식 교육은 얼마나 자주 받아야 하나요?',
    action => 'narrate',
    return_citations => 'true'  -- 출처 정보 포함
  ) as response
  FROM DUAL
);

-- 출력 예시:
-- ANSWER: "모든 직원은 분기별로 보안 인식 교육을 이수해야 합니다..."
-- CITATIONS: 
--   [
--     {"document": "security_handbook.docx", "page": 12, "score": 0.92},
--     {"document": "hr_policy_2024.pdf", "page": 45, "score": 0.87}
--   ]
```

#### 메타데이터 필터링

```sql
-- 특정 부서 문서만 검색
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '재택근무 정책은?',
  action => 'narrate',
  attributes => JSON_OBJECT(
    'metadata_filter' VALUE JSON_OBJECT(
      'department' VALUE 'HR',
      'year' VALUE '2024'
    )
  )
) FROM DUAL;
```

#### 하이브리드 검색 (키워드 + 시맨틱)

```sql
-- 벡터 검색과 키워드 검색 병행
BEGIN
  DBMS_CLOUD_AI.CREATE_VECTOR_INDEX(
    index_name => 'HYBRID_INDEX',
    attributes => JSON_OBJECT(
      'vector_db_provider' VALUE 'oracle',
      'search_mode' VALUE 'hybrid',  -- 하이브리드 모드
      'keyword_weight' VALUE 0.3,    -- 키워드 가중치 30%
      'semantic_weight' VALUE 0.7,   -- 시맨틱 가중치 70%
      'location' VALUE '...',
      'chunk_size' VALUE 1000
    )
  );
END;
/
```

### 4.5 RAG 인덱스 관리

#### 수동 갱신

```sql
-- 새 문서 추가 후 즉시 인덱스 갱신
BEGIN
  DBMS_CLOUD_AI.REFRESH_VECTOR_INDEX(
    index_name => 'COMPANY_DOCS_INDEX'
  );
END;
/
```

#### 인덱스 삭제

```sql
BEGIN
  DBMS_CLOUD_AI.DROP_VECTOR_INDEX(
    index_name => 'COMPANY_DOCS_INDEX'
  );
END;
/
```

#### 통계 및 모니터링

```sql
-- 인덱스 사용 통계
SELECT 
  query_date,
  total_queries,
  avg_latency_ms,
  avg_relevance_score
FROM USER_CLOUD_AI_RAG_STATS
WHERE index_name = 'COMPANY_DOCS_INDEX'
  AND query_date >= SYSDATE - 7
ORDER BY query_date DESC;

-- 가장 많이 검색된 청크
SELECT 
  chunk_id,
  document_name,
  chunk_text,
  retrieval_count,
  avg_relevance_score
FROM USER_CLOUD_AI_VECTOR_CHUNKS
WHERE index_name = 'COMPANY_DOCS_INDEX'
ORDER BY retrieval_count DESC
FETCH FIRST 10 ROWS ONLY;
```

### 4.6 RAG 최적화 팁

#### 청킹 전략

| 문서 유형 | 권장 Chunk Size | Overlap | 이유 |
|-----------|----------------|---------|------|
| 정책 문서 | 800-1200자 | 150-250자 | 문단 단위로 완전한 문맥 유지 |
| FAQ | 200-400자 | 50자 | 질문-답변 쌍이 하나의 청크 |
| 기술 매뉴얼 | 1000-1500자 | 300자 | 절차나 단계가 분리되지 않도록 |
| 법률 문서 | 600-1000자 | 200자 | 조항 단위 검색 가능 |

#### 임베딩 모델 선택

```sql
-- 다국어 문서: Cohere Multilingual
'embedding_model' VALUE 'cohere.embed-multilingual-v3.0'

-- 영어 전용, 고성능: OpenAI
'embedding_model' VALUE 'text-embedding-3-large'

-- 비용 최적화: Cohere English
'embedding_model' VALUE 'cohere.embed-english-v3.0'
```

#### 검색 품질 향상

```sql
-- Top-K 조정
'top_k' VALUE 3   -- 답변이 너무 길거나 관련 없는 내용 포함 시
'top_k' VALUE 10  -- 답변에 정보가 부족하거나 출처가 필요할 때

-- 유사도 임계값 설정
'similarity_threshold' VALUE 0.7  -- 0.7 이상인 청크만 사용
```

---

## 5. 보안 및 거버넌스: Real Application Security (RAS)

### 5.1 기존 보안 모델의 한계

#### 전통적인 3-Tier 애플리케이션의 문제

```
┌──────────────────────┐
│   웹 애플리케이션       │
│                       │
│  Alice (HR Manager)   │ ─┐
│  Bob (IT Staff)       │  │  모든 사용자가
│  Carol (Finance)      │  ├─ 동일한 DB 계정 사용
│  David (IT Manager)   │  │  (예: APP_USER)
│  ...                  │ ─┘
└───────────┬───────────┘
            │
            ▼
┌────────────────────────┐
│      Database          │
│  연결: APP_USER        │  ❌ 누가 쿼리했는지
│                        │     알 수 없음!
│  SELECT * FROM         │
│  EMPLOYEES...          │  ❌ 모든 사용자가
└────────────────────────┘     같은 권한!
```

**문제점:**
1. **사용자 식별 불가**: DB는 실제 사용자(Alice, Bob)를 모르고 APP_USER만 인식
2. **감사 추적 어려움**: 누가 민감한 데이터를 조회했는지 추적 불가
3. **세밀한 권한 제어 불가**: 애플리케이션 코드에서 권한 로직 구현 (에러 발생 가능)
4. **데이터 유출 위험**: APP_USER 계정 탈취 시 모든 데이터 노출

[cite: 1534-1544] **Real Application Security (RAS)**는 애플리케이션 사용자를 DB 레벨에서 식별하고 보안을 적용하여 이 문제를 해결합니다.

### 5.2 RAS 아키텍처

#### RAS가 적용된 Select AI

```
┌──────────────────────┐
│   Select AI 사용자     │
│                       │
│  Alice (HR Manager)   │ ─→ RAS Principal: ALICE
│  Bob (IT Staff)       │ ─→ RAS Principal: BOB
│  Carol (Finance)      │ ─→ RAS Principal: CAROL
│  David (IT Manager)   │ ─→ RAS Principal: DAVID
└───────────┬───────────┘
            │
            ▼
┌────────────────────────────────────────┐
│         Select AI + RAS                │
│                                        │
│  질문: "급여 정보를 보여줘"             │
│    ↓                                   │
│  1. 사용자 식별: DAVID                  │
│  2. 권한 확인: IT_MANAGER_ROLE         │
│  3. Data Realm 적용                    │
│  4. SQL 생성 with WHERE 조건            │
│    WHERE department = 'IT'             │
│    AND (employee_id = 'DAVID'          │
│         OR role = 'MANAGER')           │
└────────────────────────────────────────┘
```

### 5.3 RAS의 3가지 보안 차원

[cite: 1621, 1702, 1622-1623] Select AI와 결합 시 RAS는 다음 요소를 통해 강력한 데이터 거버넌스를 제공합니다:

#### 1. Principals (주체) - "누가?"

```sql
-- 애플리케이션 사용자 생성
BEGIN
  SYS.XS_PRINCIPAL.CREATE_USER(
    name => 'ALICE',
    schema => 'ADMIN'  -- 실제 DB 스키마
  );
  
  SYS.XS_PRINCIPAL.CREATE_USER(
    name => 'BOB',
    schema => 'ADMIN'
  );
  
  SYS.XS_PRINCIPAL.CREATE_USER(
    name => 'DAVID',
    schema => 'ADMIN'
  );
END;
/

-- 역할(Role) 생성
BEGIN
  SYS.XS_PRINCIPAL.CREATE_ROLE(
    name => 'HR_ROLE',
    enabled => TRUE
  );
  
  SYS.XS_PRINCIPAL.CREATE_ROLE(
    name => 'IT_STAFF_ROLE',
    enabled => TRUE
  );
  
  SYS.XS_PRINCIPAL.CREATE_ROLE(
    name => 'IT_MANAGER_ROLE',
    enabled => TRUE
  );
END;
/

-- 사용자에게 역할 부여
BEGIN
  SYS.XS_PRINCIPAL.GRANT_ROLES(
    user => 'ALICE',
    role => 'HR_ROLE'
  );
  
  SYS.XS_PRINCIPAL.GRANT_ROLES(
    user => 'BOB',
    role => 'IT_STAFF_ROLE'
  );
  
  SYS.XS_PRINCIPAL.GRANT_ROLES(
    user => 'DAVID',
    role => 'IT_MANAGER_ROLE'
  );
END;
/
```

#### 2. Application Privileges (권한) - "무엇을?"

```sql
-- 권한 정의 생성
BEGIN
  SYS.XS_SECURITY_CLASS.CREATE_SECURITY_CLASS(
    name => 'HR_SEC_CLASS',
    description => 'HR data security classification'
  );
END;
/

-- 개별 권한 정의
BEGIN
  -- 급여 조회 권한
  SYS.XS_SECURITY_CLASS.ADD_PRIVILEGES(
    sec_class => 'HR_SEC_CLASS',
    priv_list => XS$PRIVILEGE_LIST(
      XS$PRIVILEGE('VIEW_SALARY', 'View employee salary'),
      XS$PRIVILEGE('VIEW_PERSONAL_INFO', 'View personal information'),
      XS$PRIVILEGE('MODIFY_SALARY', 'Modify employee salary')
    )
  );
END;
/

-- 역할에 권한 부여
BEGIN
  -- HR은 모든 권한
  SYS.XS_ACL.GRANT_PRIVILEGE(
    acl => 'HR_ACL',
    principal => 'HR_ROLE',
    privilege => 'VIEW_SALARY'
  );
  
  SYS.XS_ACL.GRANT_PRIVILEGE(
    acl => 'HR_ACL',
    principal => 'HR_ROLE',
    privilege => 'MODIFY_SALARY'
  );
  
  -- IT Manager는 자기 부서만 조회
  SYS.XS_ACL.GRANT_PRIVILEGE(
    acl => 'IT_MANAGER_ACL',
    principal => 'IT_MANAGER_ROLE',
    privilege => 'VIEW_SALARY'
  );
  
  -- IT Staff는 자신의 정보만 조회
  SYS.XS_ACL.GRANT_PRIVILEGE(
    acl => 'IT_STAFF_ACL',
    principal => 'IT_STAFF_ROLE',
    privilege => 'VIEW_PERSONAL_INFO'
  );
END;
/
```

#### 3. Data Realm (데이터 영역) - "어떤 데이터?"

```sql
-- Data Security Policy 생성
BEGIN
  SYS.XS_DATA_SECURITY.CREATE_POLICY(
    name => 'EMPLOYEE_DATA_POLICY',
    description => 'Policy for employee data access'
  );
END;
/

-- Data Realm 생성: HR은 모든 직원 데이터
BEGIN
  SYS.XS_DATA_SECURITY.CREATE_DATA_REALM(
    realm_name => 'ALL_EMPLOYEES_REALM',
    description => 'All employee records',
    realm_type => XS_DATA_SECURITY.QUERY_REALM,
    realm_sql => 'TRUE'  -- 조건 없음 = 모든 데이터
  );
END;
/

-- Data Realm: IT Manager는 IT 부서만
BEGIN
  SYS.XS_DATA_SECURITY.CREATE_DATA_REALM(
    realm_name => 'IT_DEPT_REALM',
    description => 'IT department employees only',
    realm_type => XS_DATA_SECURITY.QUERY_REALM,
    realm_sql => 'DEPARTMENT_ID = ''IT'''
  );
END;
/

-- Data Realm: IT Staff는 자신만
BEGIN
  SYS.XS_DATA_SECURITY.CREATE_DATA_REALM(
    realm_name => 'OWN_DATA_REALM',
    description => 'Own employee record only',
    realm_type => XS_DATA_SECURITY.QUERY_REALM,
    realm_sql => 'EMPLOYEE_ID = SYS_CONTEXT(''XS_SESSION'', ''USERNAME'')'
  );
END;
/
```

### 5.4 HR 시나리오 실습

#### 환경 설정

**Step 1: 테스트 테이블 생성**

```sql
-- 직원 정보 테이블
CREATE TABLE EMPLOYEES (
  EMPLOYEE_ID VARCHAR2(50) PRIMARY KEY,
  FIRST_NAME VARCHAR2(50),
  LAST_NAME VARCHAR2(50),
  EMAIL VARCHAR2(100),
  DEPARTMENT_ID VARCHAR2(20),
  JOB_TITLE VARCHAR2(100),
  SALARY NUMBER(10,2),
  HIRE_DATE DATE,
  MANAGER_ID VARCHAR2(50)
);

-- 샘플 데이터 입력
INSERT INTO EMPLOYEES VALUES ('ALICE', 'Alice', 'Johnson', 'alice@company.com', 'HR', 'HR Manager', 95000, DATE '2015-03-15', NULL);
INSERT INTO EMPLOYEES VALUES ('BOB', 'Bob', 'Smith', 'bob@company.com', 'IT', 'Software Engineer', 85000, DATE '2018-07-01', 'DAVID');
INSERT INTO EMPLOYEES VALUES ('CAROL', 'Carol', 'Williams', 'carol@company.com', 'FINANCE', 'Financial Analyst', 78000, DATE '2019-01-20', NULL);
INSERT INTO EMPLOYEES VALUES ('DAVID', 'David', 'Brown', 'david@company.com', 'IT', 'IT Manager', 105000, DATE '2014-09-10', NULL);
INSERT INTO EMPLOYEES VALUES ('EVE', 'Eve', 'Davis', 'eve@company.com', 'IT', 'DevOps Engineer', 90000, DATE '2017-11-05', 'DAVID');
INSERT INTO EMPLOYEES VALUES ('FRANK', 'Frank', 'Miller', 'frank@company.com', 'IT', 'QA Engineer', 75000, DATE '2020-02-14', 'DAVID');
COMMIT;
```

**Step 2: RAS ACL 생성 및 적용**

[cite: 1835-1839, 1868-1872]

```sql
-- ACL 생성
BEGIN
  -- HR 전체 접근 ACL
  SYS.XS_ACL.CREATE_ACL(
    name => 'HR_FULL_ACCESS_ACL',
    description => 'Full access for HR role',
    ace_list => XS$ACE_LIST(
      XS$ACE_TYPE(
        privilege_list => XS$NAME_LIST('VIEW_SALARY', 'VIEW_PERSONAL_INFO'),
        principal_name => 'HR_ROLE',
        granted => TRUE
      )
    )
  );
  
  -- IT Manager 부서 접근 ACL
  SYS.XS_ACL.CREATE_ACL(
    name => 'IT_MANAGER_ACL',
    description => 'IT department access for IT managers',
    ace_list => XS$ACE_LIST(
      XS$ACE_TYPE(
        privilege_list => XS$NAME_LIST('VIEW_SALARY', 'VIEW_PERSONAL_INFO'),
        principal_name => 'IT_MANAGER_ROLE',
        granted => TRUE
      )
    )
  );
  
  -- IT Staff 자기 정보만 ACL
  SYS.XS_ACL.CREATE_ACL(
    name => 'IT_STAFF_OWN_ACL',
    description => 'Own data only for IT staff',
    ace_list => XS$ACE_LIST(
      XS$ACE_TYPE(
        privilege_list => XS$NAME_LIST('VIEW_PERSONAL_INFO'),
        principal_name => 'IT_STAFF_ROLE',
        granted => TRUE
      )
    )
  );
END;
/
```

**Step 3: Data Security Policy 적용**

```sql
BEGIN
  -- Policy에 ACL과 Realm 연결
  
  -- HR Role: 모든 데이터 + 모든 권한
  SYS.XS_DATA_SECURITY.APPLY_OBJECT_POLICY(
    policy => 'EMPLOYEE_DATA_POLICY',
    schema => 'ADMIN',
    object => 'EMPLOYEES',
    acl => 'HR_FULL_ACCESS_ACL',
    data_realm => 'ALL_EMPLOYEES_REALM'
  );
  
  -- IT Manager Role: IT 부서 데이터만
  SYS.XS_DATA_SECURITY.APPLY_OBJECT_POLICY(
    policy => 'EMPLOYEE_DATA_POLICY',
    schema => 'ADMIN',
    object => 'EMPLOYEES',
    acl => 'IT_MANAGER_ACL',
    data_realm => 'IT_DEPT_REALM'
  );
  
  -- IT Staff Role: 자신의 데이터만
  SYS.XS_DATA_SECURITY.APPLY_OBJECT_POLICY(
    policy => 'EMPLOYEE_DATA_POLICY',
    schema => 'ADMIN',
    object => 'EMPLOYEES',
    acl => 'IT_STAFF_OWN_ACL',
    data_realm => 'OWN_DATA_REALM'
  );
END;
/

-- Policy 활성화
BEGIN
  SYS.XS_DATA_SECURITY.ENABLE_POLICY(
    policy => 'EMPLOYEE_DATA_POLICY'
  );
END;
/
```

#### 테스트 시나리오

**시나리오 1: Alice (HR Manager) - 모든 직원 조회 가능**

```sql
-- Alice로 연결
BEGIN
  XS_SESSION.CREATE_SESSION(
    username => 'ALICE',
    packages => NULL
  );
END;
/

-- Select AI 질문
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '모든 직원의 급여를 보여줘',
  action => 'runsql'
) FROM DUAL;

-- 예상 결과: 6명 모두 표시
-- ALICE   95000
-- BOB     85000
-- CAROL   78000
-- DAVID   105000
-- EVE     90000
-- FRANK   75000
```

**시나리오 2: David (IT Manager) - IT 부서만 조회 가능**

```sql
-- David로 연결
BEGIN
  XS_SESSION.DESTROY_SESSION();
  XS_SESSION.CREATE_SESSION(
    username => 'DAVID',
    packages => NULL
  );
END;
/

-- Select AI 질문
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '팀원들의 급여를 보여줘',
  action => 'runsql'
) FROM DUAL;

-- 예상 결과: IT 부서 4명만 표시
-- DAVID   105000
-- BOB     85000
-- EVE     90000
-- FRANK   75000

-- HR 부서 조회 시도
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => 'Alice의 급여는?',
  action => 'runsql'
) FROM DUAL;

-- 예상 결과: 데이터 없음 (RAS가 자동으로 필터링)
```

**시나리오 3: Bob (IT Staff) - 자신의 정보만 조회 가능**

```sql
-- Bob으로 연결
BEGIN
  XS_SESSION.DESTROY_SESSION();
  XS_SESSION.CREATE_SESSION(
    username => 'BOB',
    packages => NULL
  );
END;
/

-- 자신의 급여 조회
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '내 급여는 얼마야?',
  action => 'runsql'
) FROM DUAL;

-- 예상 결과: 자신의 정보만
-- BOB     85000

-- 다른 직원 조회 시도
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => 'David의 급여는?',
  action => 'runsql'
) FROM DUAL;

-- 예상 결과: 데이터 없음 (VIEW_SALARY 권한 없음)
```

### 5.5 RAS와 Select AI 통합 이점

#### 자동 보안 적용

```
일반 SQL:
사용자가 직접 WHERE 조건 작성 필요
❌ WHERE department = 'IT' AND employee_id = 'BOB'
   (개발자가 잊어버리면 보안 위반!)

Select AI + RAS:
✅ RAS가 자동으로 보안 조건 추가
   사용자는 "내 정보 보여줘"라고만 질문
   → Select AI가 SQL 생성
   → RAS가 자동으로 WHERE employee_id = 'BOB' 추가
```

#### 감사 추적

```sql
-- 누가, 언제, 무엇을 조회했는지 추적
SELECT 
  xs_session_user as user_name,
  sql_text,
  execution_time,
  rows_returned
FROM DBA_CLOUD_AI_AUDIT_TRAIL
WHERE table_name = 'EMPLOYEES'
  AND action = 'SELECT'
  AND execution_time >= SYSDATE - 1
ORDER BY execution_time DESC;
```

### 5.6 고급 RAS 패턴

#### 컬럼 레벨 보안 (Column Masking)

```sql
-- 급여 정보는 HR과 Manager만, 일반 직원은 마스킹
BEGIN
  SYS.XS_DATA_SECURITY.CREATE_DATA_REALM(
    realm_name => 'SALARY_MASKED_REALM',
    description => 'Mask salary for non-privileged users',
    realm_type => XS_DATA_SECURITY.COLUMN_REALM,
    column_list => XS$LIST('SALARY'),
    realm_sql => 'CASE 
                    WHEN SYS_CONTEXT(''XS_SESSION'', ''USERNAME'') 
                         IN (SELECT employee_id FROM employees WHERE job_title LIKE ''%Manager%'')
                    THEN SALARY 
                    ELSE NULL 
                  END'
  );
END;
/
```

#### 시간 기반 접근 제어

```sql
-- 업무 시간에만 조회 가능
BEGIN
  SYS.XS_DATA_SECURITY.CREATE_DATA_REALM(
    realm_name => 'BUSINESS_HOURS_REALM',
    description => 'Access only during business hours',
    realm_type => XS_DATA_SECURITY.QUERY_REALM,
    realm_sql => 'TO_CHAR(SYSDATE, ''HH24'') BETWEEN ''09'' AND ''18'' 
                  AND TO_CHAR(SYSDATE, ''DY'') NOT IN (''SAT'', ''SUN'')'
  );
END;
/
```

#### 동적 권한 위임

```sql
-- Manager가 휴가 중일 때 대리자에게 권한 위임
BEGIN
  SYS.XS_PRINCIPAL.CREATE_DYNAMIC_ROLE(
    name => 'DELEGATED_MANAGER_ROLE',
    role_expr => 'SELECT ''IT_MANAGER_ROLE'' 
                  FROM employee_delegation 
                  WHERE delegated_to = SYS_CONTEXT(''XS_SESSION'', ''USERNAME'')
                    AND start_date <= SYSDATE 
                    AND end_date >= SYSDATE'
  );
END;
/
```

---

## 6. 엔터프라이즈 통합 및 확장

### 6.1 Oracle E-Business Suite (EBS) 통합
Select AI는 Oracle EBS 12.2와 통합되어 자연어 쿼리 기능을 제공할 수 있습니다.
* [cite_start]**아키텍처:** APEX UI 프론트엔드를 통해 사용자의 질문을 받고, ADB의 Select AI가 이를 SQL로 변환한 뒤, EBS 데이터베이스(XX_NLQ 스키마)에서 쿼리를 실행합니다 [cite: 758-762].
* [cite_start]**보안:** EBS의 보안 설정과 VPD(Virtual Private Database) 정책을 준수하여 쿼리가 실행됩니다[cite: 762].

### 6.2 MySQL Database 연결 핸즈온

#### 6.2.1 MySQL 연결 개요

**사용 사례:**
- 레거시 애플리케이션이 MySQL에 데이터 저장
- Oracle ADB로 마이그레이션 없이 자연어로 데이터 조회
- MySQL과 ADB의 데이터를 연합 쿼리로 통합 분석

#### 6.2.2 사전 준비: MySQL 서버 설정

**MySQL 인스턴스 준비 (AWS RDS MySQL 예시)**

```sql
-- MySQL 서버에 접속하여 테스트 데이터베이스 생성
CREATE DATABASE ecommerce;
USE ecommerce;

-- 제품 테이블 생성
CREATE TABLE products (
  product_id INT PRIMARY KEY AUTO_INCREMENT,
  product_name VARCHAR(200),
  category VARCHAR(100),
  price DECIMAL(10,2),
  stock_quantity INT,
  supplier_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 주문 테이블 생성
CREATE TABLE orders (
  order_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  order_date DATE,
  total_amount DECIMAL(10,2),
  status VARCHAR(50),
  shipping_address TEXT
);

-- 주문 상세 테이블
CREATE TABLE order_items (
  item_id INT PRIMARY KEY AUTO_INCREMENT,
  order_id INT,
  product_id INT,
  quantity INT,
  unit_price DECIMAL(10,2),
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 샘플 데이터 입력
INSERT INTO products (product_name, category, price, stock_quantity, supplier_id) VALUES
('Laptop Pro 15', 'Electronics', 1299.99, 45, 101),
('Wireless Mouse', 'Electronics', 29.99, 250, 101),
('Office Chair', 'Furniture', 249.99, 30, 102),
('Standing Desk', 'Furniture', 599.99, 15, 102),
('USB-C Hub', 'Electronics', 49.99, 120, 103),
('Monitor 27inch', 'Electronics', 399.99, 60, 101),
('Desk Lamp LED', 'Furniture', 39.99, 80, 102),
('Keyboard Mechanical', 'Electronics', 149.99, 95, 103);

INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
(1001, '2024-11-01', 1329.98, 'Delivered'),
(1002, '2024-11-03', 649.98, 'Shipped'),
(1003, '2024-11-05', 1899.97, 'Processing'),
(1001, '2024-11-10', 79.98, 'Delivered'),
(1004, '2024-11-15', 249.99, 'Pending');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1299.99),
(1, 2, 1, 29.99),
(2, 4, 1, 599.99),
(2, 3, 1, 49.99),
(3, 1, 1, 1299.99),
(3, 6, 1, 399.99),
(3, 8, 1, 149.99);

-- 원격 접속을 위한 사용자 생성
CREATE USER 'adb_user'@'%' IDENTIFIED BY 'SecurePassword123!';
GRANT SELECT ON ecommerce.* TO 'adb_user'@'%';
FLUSH PRIVILEGES;
```

**MySQL 보안 그룹 설정 (AWS 예시)**
- Inbound Rules에 ADB의 Public IP 추가
- Port: 3306
- Source: ADB NAT Gateway IP 또는 0.0.0.0/0 (테스트용)

#### 6.2.3 ADB에서 MySQL 연결 설정

**Step 1: MySQL JDBC Driver 확인**

Oracle Autonomous Database는 MySQL JDBC 드라이버를 내장하고 있습니다. 별도 설치 불필요.

**Step 2: MySQL 연결 Credential 생성**

```sql
-- MySQL 접속 정보를 저장하는 Credential 생성
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'MYSQL_CRED',
    username => 'adb_user',
    password => 'SecurePassword123!'
  );
END;
/

-- Credential 확인
SELECT credential_name, username, enabled
FROM USER_CREDENTIALS
WHERE credential_name = 'MYSQL_CRED';
```

**Step 3: Database Link 생성**

```sql
-- MySQL 데이터베이스로의 Database Link 생성
BEGIN
  DBMS_CLOUD_ADMIN.CREATE_DATABASE_LINK(
    db_link_name => 'MYSQL_ECOMMERCE_LINK',
    hostname => 'mysql-instance.c9akciq32.us-east-1.rds.amazonaws.com',
    port => '3306',
    service_name => 'ecommerce',
    ssl_server_cert_dn => NULL,
    credential_name => 'MYSQL_CRED',
    directory_name => NULL
  );
END;
/

-- Database Link 확인
SELECT db_link, host, username, created
FROM USER_DB_LINKS
WHERE db_link = 'MYSQL_ECOMMERCE_LINK';
```

**Step 4: 연결 테스트**

```sql
-- MySQL 테이블 조회 테스트
SELECT * 
FROM products@MYSQL_ECOMMERCE_LINK
WHERE ROWNUM <= 5;

-- 카운트 확인
SELECT COUNT(*) as total_products
FROM products@MYSQL_ECOMMERCE_LINK;

SELECT COUNT(*) as total_orders
FROM orders@MYSQL_ECOMMERCE_LINK;
```

#### 6.2.4 Select AI 프로파일 생성 (MySQL 포함)

**ADB의 로컬 테이블 준비**

```sql
-- ADB에 고객 정보 테이블 생성 (Oracle에 저장)
CREATE TABLE customers (
  customer_id NUMBER PRIMARY KEY,
  first_name VARCHAR2(50),
  last_name VARCHAR2(50),
  email VARCHAR2(100),
  phone VARCHAR2(20),
  customer_segment VARCHAR2(20),
  registration_date DATE
);

-- 샘플 고객 데이터
INSERT INTO customers VALUES (1001, 'John', 'Doe', 'john.doe@email.com', '555-0101', 'Premium', DATE '2023-05-15');
INSERT INTO customers VALUES (1002, 'Jane', 'Smith', 'jane.smith@email.com', '555-0102', 'Standard', DATE '2023-08-20');
INSERT INTO customers VALUES (1003, 'Robert', 'Johnson', 'robert.j@email.com', '555-0103', 'Premium', DATE '2023-03-10');
INSERT INTO customers VALUES (1004, 'Emily', 'Williams', 'emily.w@email.com', '555-0104', 'Standard', DATE '2024-01-05');
COMMIT;
```

**MySQL 테이블을 포함한 AI 프로파일 생성**

```sql
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'MYSQL_FEDERATED_PROFILE',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'credential_name' VALUE 'OCI_CRED',
      'model' VALUE 'cohere.command-r-plus',
      'comments' VALUE 'true',
      
      -- 오라클 로컬 테이블과 MySQL 원격 테이블 모두 포함
      'object_list' VALUE JSON_ARRAY(
        -- ADB 로컬 테이블
        JSON_OBJECT(
          'owner' VALUE 'ADMIN',
          'name' VALUE 'CUSTOMERS'
        ),
        -- MySQL 원격 테이블들 (Database Link 사용)
        JSON_OBJECT(
          'owner' VALUE 'ADMIN',
          'name' VALUE 'PRODUCTS@MYSQL_ECOMMERCE_LINK'
        ),
        JSON_OBJECT(
          'owner' VALUE 'ADMIN',
          'name' VALUE 'ORDERS@MYSQL_ECOMMERCE_LINK'
        ),
        JSON_OBJECT(
          'owner' VALUE 'ADMIN',
          'name' VALUE 'ORDER_ITEMS@MYSQL_ECOMMERCE_LINK'
        )
      )
    )
  );
  
  -- 프로파일 활성화
  DBMS_CLOUD_AI.SET_PROFILE('MYSQL_FEDERATED_PROFILE');
END;
/
```

**테이블 주석 추가 (정확도 향상)**

```sql
-- ADB 로컬 테이블 주석
COMMENT ON TABLE customers IS 
'Customer master data including contact information and segmentation';

COMMENT ON COLUMN customers.customer_segment IS 
'Customer tier: Premium (high-value), Standard (regular), or Trial';

-- MySQL 테이블은 MySQL에서 주석 추가
-- (또는 ADB에서 Synonym 생성 후 주석 추가 가능)
```

#### 6.2.5 연합 쿼리 실습

**질문 1: MySQL 테이블만 조회**

```sql
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '재고가 50개 미만인 제품과 재고 수량을 보여줘',
  action => 'runsql'
) FROM DUAL;

-- 예상 생성 SQL:
-- SELECT product_name, stock_quantity
-- FROM products@MYSQL_ECOMMERCE_LINK
-- WHERE stock_quantity < 50
-- ORDER BY stock_quantity;
```

**질문 2: Oracle + MySQL 연합 쿼리**

```sql
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => 'Premium 고객들의 총 주문 금액과 주문 건수를 보여줘',
  action => 'runsql'
) FROM DUAL;

-- 예상 생성 SQL (Oracle + MySQL 조인):
-- SELECT 
--   c.first_name || ' ' || c.last_name as customer_name,
--   c.customer_segment,
--   COUNT(o.order_id) as order_count,
--   SUM(o.total_amount) as total_spent
-- FROM customers c
-- JOIN orders@MYSQL_ECOMMERCE_LINK o ON c.customer_id = o.customer_id
-- WHERE c.customer_segment = 'Premium'
-- GROUP BY c.first_name, c.last_name, c.customer_segment
-- ORDER BY total_spent DESC;
```

**질문 3: 복잡한 3-Way 조인**

```sql
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => 'John Doe 고객이 구매한 제품 목록과 각 제품의 수량을 보여줘',
  action => 'runsql'
) FROM DUAL;

-- 예상 생성 SQL:
-- SELECT 
--   p.product_name,
--   p.category,
--   oi.quantity,
--   oi.unit_price,
--   o.order_date
-- FROM customers c
-- JOIN orders@MYSQL_ECOMMERCE_LINK o ON c.customer_id = o.customer_id
-- JOIN order_items@MYSQL_ECOMMERCE_LINK oi ON o.order_id = oi.order_id
-- JOIN products@MYSQL_ECOMMERCE_LINK p ON oi.product_id = p.product_id
-- WHERE c.first_name = 'John' AND c.last_name = 'Doe'
-- ORDER BY o.order_date DESC;
```

**질문 4: 집계 및 분석**

```sql
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '카테고리별 매출 상위 3개와 각 카테고리의 총 판매액을 보여줘',
  action => 'runsql'
) FROM DUAL;

-- 대화형으로 이어서 질문
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '그 중에서 Premium 고객의 구매만 보여줘',
  action => 'runsql'
) FROM DUAL;
```

#### 6.2.6 성능 최적화

**원격 테이블 캐싱**

```sql
-- 자주 조회되는 MySQL 테이블을 ADB에 캐시
CREATE MATERIALIZED VIEW products_cache
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT * FROM products@MYSQL_ECOMMERCE_LINK;

-- 캐시된 뷰를 프로파일에 추가
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'MYSQL_OPTIMIZED_PROFILE',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'credential_name' VALUE 'OCI_CRED',
      'object_list' VALUE JSON_ARRAY(
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'CUSTOMERS'),
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'PRODUCTS_CACHE'),
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'ORDERS@MYSQL_ECOMMERCE_LINK')
      )
    )
  );
END;
/

-- 정기적으로 캐시 갱신
BEGIN
  DBMS_MVIEW.REFRESH('PRODUCTS_CACHE');
END;
/
```

**쿼리 힌트 활용**

```sql
-- 대량 조인 시 드라이빙 테이블 지정
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '모든 주문 내역을 고객 정보와 함께 보여줘',
  action => 'showsql'
) FROM DUAL;

-- 생성된 SQL에 힌트 추가 (필요시)
SELECT /*+ USE_HASH(c o) LEADING(c) */ 
  c.customer_id,
  c.first_name,
  o.order_id,
  o.total_amount
FROM customers c
JOIN orders@MYSQL_ECOMMERCE_LINK o ON c.customer_id = o.customer_id;
```

### 6.3 Apache Iceberg 테이블 쿼리 핸즈온

#### 6.3.1 Iceberg 개요

[cite: 2945] Select AI는 데이터 레이크의 표준 포맷인 Apache Iceberg 테이블에 대한 쿼리를 지원합니다.

**Iceberg의 장점:**
- 대규모 데이터 레이크에서 ACID 트랜잭션 지원
- 스키마 진화 (Schema Evolution)
- 파티션 진화 (Partition Evolution)
- 타임 트래블 (Time Travel) 쿼리
- AWS S3, Azure ADLS, GCS 등 다양한 스토리지 지원

#### 6.3.2 Iceberg 지원 모델

[cite: 3006, 3009] Select AI는 두 가지 방식으로 Iceberg 테이블을 지원합니다:

| 방식 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **Catalog-Managed** | AWS Glue, Polaris, Unity Catalog 사용 | 메타데이터 자동 관리, 실시간 스키마 업데이트 | Catalog 서비스 필요 |
| **Direct-Metadata** | metadata.json 파일 직접 참조 | Catalog 불필요, 간단한 설정 | 스냅샷 시점 고정, 수동 업데이트 |

[cite: 2978-2979] **제약 사항:** 
- 현재는 읽기 전용(Query-only)
- 파티션된 테이블 미지원
- Row-level update(Merge-on-Read) 미지원

#### 6.3.3 방법 1: AWS Glue Catalog를 사용한 Iceberg 연결

**사전 준비: AWS Glue에 Iceberg 테이블 생성**

```python
# AWS Glue 또는 Spark에서 Iceberg 테이블 생성 (예시)
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Create Iceberg Table") \
    .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue_catalog.warehouse", "s3://my-data-lake/warehouse/") \
    .config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
    .getOrCreate()

# 웹 애플리케이스 로그 데이터
df = spark.read.parquet("s3://source-data/web-logs/")

df.writeTo("glue_catalog.analytics.web_events") \
    .using("iceberg") \
    .partitionedBy("event_date") \
    .create()
```

**Step 1: AWS Glue 접근을 위한 Credential 생성**

```sql
-- AWS Access Key 방식
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'AWS_GLUE_CRED',
    username => 'AKIAIOSFODNN7EXAMPLE',  -- AWS Access Key ID
    password => 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'  -- AWS Secret Key
  );
END;
/

-- 또는 IAM Role 사용 (권장)
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'AWS_GLUE_CRED',
    username => 'OCI$RESOURCE_PRINCIPAL'
  );
END;
/
```

**Step 2: Iceberg External Table 생성 (Glue Catalog 방식)**

```sql
-- AWS Glue Catalog의 Iceberg 테이블을 ADB에 External Table로 매핑
BEGIN
  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name => 'WEB_EVENTS_ICEBERG',
    credential_name => 'AWS_GLUE_CRED',
    format => JSON_OBJECT(
      'type' VALUE 'iceberg',
      'catalog_type' VALUE 'glue',
      'catalog_name' VALUE 'glue_catalog',
      'catalog_database' VALUE 'analytics',
      'catalog_table' VALUE 'web_events',
      'region' VALUE 'us-east-1'
    ),
    column_list => 'event_id NUMBER,
                    user_id NUMBER,
                    event_type VARCHAR2(50),
                    page_url VARCHAR2(500),
                    event_timestamp TIMESTAMP,
                    session_id VARCHAR2(100),
                    device_type VARCHAR2(50),
                    event_date DATE'
  );
END;
/
```

**Step 3: Iceberg 테이블 쿼리 테스트**

```sql
-- 직접 SQL로 조회
SELECT event_type, COUNT(*) as event_count
FROM WEB_EVENTS_ICEBERG
WHERE event_date >= DATE '2024-11-01'
GROUP BY event_type
ORDER BY event_count DESC;

-- 특정 사용자의 행동 추적
SELECT 
  event_timestamp,
  event_type,
  page_url,
  device_type
FROM WEB_EVENTS_ICEBERG
WHERE user_id = 12345
ORDER BY event_timestamp;
```

#### 6.3.4 방법 2: Direct Metadata를 사용한 Iceberg 연결

**Step 1: Iceberg 메타데이터 파일 위치 확인**

Iceberg 테이블의 메타데이터는 다음 경로에 저장됩니다:
```
s3://my-data-lake/warehouse/analytics/web_events/metadata/
  ├── v1.metadata.json
  ├── v2.metadata.json
  └── v3.metadata.json  ← 최신 버전
```

**Step 2: Direct Metadata 방식으로 External Table 생성**

```sql
BEGIN
  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name => 'WEB_EVENTS_SNAPSHOT',
    credential_name => 'AWS_GLUE_CRED',
    format => JSON_OBJECT(
      'type' VALUE 'iceberg',
      'metadata_location' VALUE 's3://my-data-lake/warehouse/analytics/web_events/metadata/v3.metadata.json'
    ),
    column_list => 'event_id NUMBER,
                    user_id NUMBER,
                    event_type VARCHAR2(50),
                    page_url VARCHAR2(500),
                    event_timestamp TIMESTAMP,
                    session_id VARCHAR2(100),
                    device_type VARCHAR2(50),
                    event_date DATE'
  );
END;
/
```

**Step 3: Time Travel 쿼리 (특정 스냅샷 조회)**

```sql
-- 이전 스냅샷 조회 (v2.metadata.json)
BEGIN
  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name => 'WEB_EVENTS_YESTERDAY',
    credential_name => 'AWS_GLUE_CRED',
    format => JSON_OBJECT(
      'type' VALUE 'iceberg',
      'metadata_location' VALUE 's3://my-data-lake/warehouse/analytics/web_events/metadata/v2.metadata.json'
    ),
    column_list => '...'
  );
END;
/

-- 두 스냅샷 비교
SELECT 'Current' as snapshot, COUNT(*) as row_count FROM WEB_EVENTS_SNAPSHOT
UNION ALL
SELECT 'Yesterday' as snapshot, COUNT(*) as row_count FROM WEB_EVENTS_YESTERDAY;
```

#### 6.3.5 Select AI with Iceberg

**Iceberg 테이블을 포함한 프로파일 생성**

```sql
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'ICEBERG_ANALYTICS_PROFILE',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'credential_name' VALUE 'OCI_CRED',
      'model' VALUE 'cohere.command-r-plus',
      'comments' VALUE 'true',
      
      'object_list' VALUE JSON_ARRAY(
        -- ADB 로컬 테이블
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'CUSTOMERS'),
        -- MySQL 테이블
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'ORDERS@MYSQL_ECOMMERCE_LINK'),
        -- Iceberg 테이블
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'WEB_EVENTS_ICEBERG')
      )
    )
  );
  
  DBMS_CLOUD_AI.SET_PROFILE('ICEBERG_ANALYTICS_PROFILE');
END;
/
```

**테이블 주석 추가**

```sql
COMMENT ON TABLE WEB_EVENTS_ICEBERG IS 
'Web application user behavior events stored in Iceberg format in S3 data lake';

COMMENT ON COLUMN WEB_EVENTS_ICEBERG.event_type IS 
'Type of event: page_view, click, form_submit, purchase, logout';

COMMENT ON COLUMN WEB_EVENTS_ICEBERG.device_type IS 
'Device category: desktop, mobile, tablet';
```

#### 6.3.6 3-Way 연합 쿼리: Oracle + MySQL + Iceberg

**시나리오: 고객의 웹 행동과 구매 패턴 분석**

```sql
-- 질문 1: 웹사이트 방문 후 실제 구매한 고객 비율
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '지난 7일간 웹사이트를 방문한 고객 중 실제로 구매한 고객의 비율은?',
  action => 'runsql'
) FROM DUAL;

-- 예상 생성 SQL:
-- WITH visitors AS (
--   SELECT DISTINCT user_id as customer_id
--   FROM WEB_EVENTS_ICEBERG
--   WHERE event_date >= SYSDATE - 7
-- ),
-- purchasers AS (
--   SELECT DISTINCT customer_id
--   FROM orders@MYSQL_ECOMMERCE_LINK
--   WHERE order_date >= SYSDATE - 7
-- )
-- SELECT 
--   COUNT(DISTINCT v.customer_id) as total_visitors,
--   COUNT(DISTINCT p.customer_id) as purchasers,
--   ROUND(COUNT(DISTINCT p.customer_id) * 100.0 / COUNT(DISTINCT v.customer_id), 2) as conversion_rate
-- FROM visitors v
-- LEFT JOIN purchasers p ON v.customer_id = p.customer_id;
```

**질문 2: 고객 세그먼트별 웹 행동 분석**

```sql
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => 'Premium 고객과 Standard 고객의 평균 페이지 뷰 수를 비교해줘',
  action => 'runsql'
) FROM DUAL;

-- 예상 생성 SQL:
-- SELECT 
--   c.customer_segment,
--   COUNT(w.event_id) as total_page_views,
--   COUNT(DISTINCT w.session_id) as total_sessions,
--   ROUND(COUNT(w.event_id) * 1.0 / COUNT(DISTINCT w.session_id), 2) as avg_pages_per_session
-- FROM customers c
-- JOIN WEB_EVENTS_ICEBERG w ON c.customer_id = w.user_id
-- WHERE w.event_type = 'page_view'
--   AND w.event_date >= SYSDATE - 30
-- GROUP BY c.customer_segment;
```

**질문 3: 제품 조회 후 구매 전환율**

```sql
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '제품 페이지를 본 고객 중 해당 제품을 실제로 구매한 비율을 제품별로 보여줘',
  action => 'runsql'
) FROM DUAL;

-- 복잡한 3-Way 조인:
-- Oracle CUSTOMERS + Iceberg WEB_EVENTS + MySQL ORDERS/ORDER_ITEMS
```

**질문 4: 실시간 대시보드 쿼리**

```sql
-- 대화형 질문
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '현재 온라인 상태인 고객 수는? (최근 10분 이내 활동)',
  action => 'runsql'
) FROM DUAL;

-- 이어서 질문
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '그 중에서 장바구니에 상품을 담은 고객은 몇 명이야?',
  action => 'runsql'
) FROM DUAL;

-- 계속 질문
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '장바구니 총액 상위 5명의 고객 정보를 보여줘',
  action => 'runsql'
) FROM DUAL;
```

#### 6.3.7 Iceberg 테이블 관리

**메타데이터 새로고침 (Direct Metadata 방식)**

```sql
-- 새로운 스냅샷이 생성되면 External Table 재생성
BEGIN
  DBMS_CLOUD.DROP_EXTERNAL_TABLE(
    table_name => 'WEB_EVENTS_ICEBERG'
  );
  
  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name => 'WEB_EVENTS_ICEBERG',
    credential_name => 'AWS_GLUE_CRED',
    format => JSON_OBJECT(
      'type' VALUE 'iceberg',
      'metadata_location' VALUE 's3://my-data-lake/warehouse/analytics/web_events/metadata/v4.metadata.json'  -- 새 버전
    ),
    column_list => '...'
  );
END;
/
```

**Catalog-Managed 방식은 자동 업데이트**

```sql
-- Glue Catalog 방식은 항상 최신 스냅샷 참조
-- 별도 새로고침 불필요
SELECT COUNT(*) FROM WEB_EVENTS_ICEBERG;  -- 항상 최신 데이터
```

**스키마 확인**

```sql
-- Iceberg 테이블 스키마 확인
SELECT column_name, data_type, data_length
FROM USER_TAB_COLUMNS
WHERE table_name = 'WEB_EVENTS_ICEBERG'
ORDER BY column_id;
```

### 6.4 통합 시나리오: 전사 데이터 분석

#### 실전 비즈니스 쿼리

**시나리오:** 전자상거래 기업의 CMO가 마케팅 캠페인 효과를 분석

```sql
-- CMO: "지난 달 신규 가입 고객들의 첫 구매까지 걸린 평균 시간과 
--       첫 구매 금액을 고객 유입 채널별로 보여줘"

SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '지난 달 신규 가입 고객들의 첫 구매까지 걸린 평균 시간과 첫 구매 금액을 고객 유입 채널별로 보여줘',
  profile_name => 'ICEBERG_ANALYTICS_PROFILE',
  action => 'runsql'
) FROM DUAL;

-- Select AI가 생성하는 복잡한 쿼리:
-- 1. CUSTOMERS (Oracle) - 신규 가입 고객 필터링
-- 2. WEB_EVENTS_ICEBERG - 유입 채널 정보 추출
-- 3. ORDERS@MYSQL_ECOMMERCE_LINK - 첫 구매 정보
-- 위 3개 데이터 소스를 조인하여 분석
```

**연속 질문으로 드릴다운**

```sql
-- 후속 질문 1
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '가장 전환율이 높은 채널의 상위 10개 제품은 뭐야?',
  action => 'runsql'
) FROM DUAL;

-- 후속 질문 2
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '해당 제품들의 현재 재고 상황은?',
  action => 'runsql'
) FROM DUAL;

-- 후속 질문 3
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '재고가 부족한 제품이 있으면 공급업체 정보도 같이 보여줘',
  action => 'runsql'
) FROM DUAL;
```

### 6.5 모니터링 및 문제 해결

#### Database Link 상태 확인

```sql
-- 활성 Database Link 조회
SELECT 
  db_link,
  host,
  username,
  created
FROM USER_DB_LINKS;

-- Database Link 연결 테스트
SELECT 
  'MySQL Connection' as test_name,
  CASE 
    WHEN COUNT(*) > 0 THEN 'Success'
    ELSE 'Failed'
  END as status
FROM products@MYSQL_ECOMMERCE_LINK
WHERE ROWNUM <= 1;
```

#### External Table (Iceberg) 상태 확인

```sql
-- External Table 정보
SELECT 
  table_name,
  type_name,
  default_directory_name,
  access_parameters
FROM USER_EXTERNAL_TABLES
WHERE table_name LIKE '%ICEBERG%';

-- Iceberg 테이블 읽기 테스트
SELECT COUNT(*) FROM WEB_EVENTS_ICEBERG WHERE ROWNUM <= 10;
```

#### 성능 모니터링

```sql
-- 원격 쿼리 실행 통계
SELECT 
  sql_text,
  executions,
  avg_elapsed_time / 1000000 as avg_seconds,
  buffer_gets,
  disk_reads
FROM V$SQL
WHERE sql_text LIKE '%@MYSQL_ECOMMERCE_LINK%'
ORDER BY avg_elapsed_time DESC;
```

---

## 7. 핸즈온 실습 가이드

### 7.1 실습 1: 기본 Proxy Database 설정

**목표:** MySQL 데이터베이스를 ADB에 연결하고 Select AI로 자연어 쿼리

**소요 시간:** 30분

**단계:**
1. ✅ MySQL RDS 인스턴스 생성 및 샘플 데이터 로드
2. ✅ ADB에서 Database Link 생성
3. ✅ Select AI 프로파일 설정
4. ✅ 자연어 쿼리 테스트

**체크리스트:**
- [ ] MySQL 테이블 직접 조회 성공
- [ ] Database Link 연결 확인
- [ ] Select AI 프로파일 생성 완료
- [ ] 자연어 질문으로 데이터 조회 성공

### 7.2 실습 2: Iceberg 데이터 레이크 연결

**목표:** S3의 Iceberg 테이블을 ADB에서 쿼리

**소요 시간:** 45분

**단계:**
1. ✅ AWS Glue에 Iceberg 테이블 생성 (또는 기존 테이블 사용)
2. ✅ ADB에서 External Table 생성
3. ✅ Iceberg 테이블 쿼리 테스트
4. ✅ Select AI 프로파일에 Iceberg 테이블 추가

**체크리스트:**
- [ ] AWS Glue Catalog 접근 성공
- [ ] Iceberg 메타데이터 읽기 성공
- [ ] External Table 쿼리 작동
- [ ] Select AI로 Iceberg 데이터 조회 가능

### 7.3 실습 3: 연합 쿼리 마스터

**목표:** Oracle + MySQL + Iceberg 3-Way 조인 쿼리 실행

**소요 시간:** 60분

**단계:**
1. ✅ 세 데이터 소스 모두 프로파일에 등록
2. ✅ 각 테이블에 의미있는 주석 추가
3. ✅ 단순 조인 쿼리 테스트
4. ✅ 복잡한 비즈니스 쿼리 실행
5. ✅ 대화형 질문으로 드릴다운 분석

**체크리스트:**
- [ ] 3개 데이터 소스 동시 조회 성공
- [ ] 조인 쿼리 자동 생성 확인
- [ ] 집계 및 그룹화 쿼리 작동
- [ ] 대화 문맥 유지되며 연속 질문 가능

### 7.4 실습 4: 성능 최적화

**목표:** 대규모 데이터 조회 시 응답 속도 개선

**소요 시간:** 30분

**기법:**
- Materialized View로 원격 테이블 캐싱
- 쿼리 힌트 활용
- 인덱스 전략
- 파티션 활용

**체크리스트:**
- [ ] 캐시 적용 전후 성능 비교
- [ ] 실행 계획 분석 완료
- [ ] 최적화된 프로파일 생성

---

## 8. DBMS_CLOUD_AI 패키지 핵심 레퍼런스

[cite: 1973-1977] Select AI 기능을 제어하는 주요 서브프로그램 요약입니다.

### 8.1 주요 서브프로그램

| 서브프로그램 | 설명 | 주요 사용 사례 |
| :--- | :--- | :--- |
| **CREATE_PROFILE** | [cite: 1980] LLM 제공자, 모델, 대상 테이블 등을 지정하여 AI 프로파일 생성 | 새로운 데이터 소스 연결, 모델 변경 |
| **SET_PROFILE** | [cite: 2015] 현재 세션에서 사용할 AI 프로파일 활성화 | 프로파일 전환, 세션 설정 |
| **GENERATE** | [cite: 2011] AI에게 작업을 요청하는 핵심 함수. `runsql`, `showsql`, `narrate`, `chat`, `summarize` 등의 액션 수행 | 모든 자연어 쿼리 |
| **CREATE_VECTOR_INDEX** | [cite: 2059] 비정형 데이터를 벡터화하여 인덱스 생성 (RAG용) | 문서 검색, RAG 구현 |
| **FEEDBACK** | [cite: 2000] AI가 생성한 쿼리에 대해 긍정/부정 피드백을 제공하여 정확도 개선 | 쿼리 품질 개선 |
| **GENERATE_SYNTHETIC_DATA** | [cite: 2049] 개발/테스트용 가상 데이터를 생성 | 테스트 데이터 생성 |
| **SUMMARIZE** | [cite: 2043] 긴 텍스트 내용을 요약 (문단 또는 리스트 형태) | 리포트 요약, 텍스트 압축 |

### 8.2 GENERATE 함수 상세

#### 기본 문법

```sql
DBMS_CLOUD_AI.GENERATE(
  prompt         IN VARCHAR2,
  profile_name   IN VARCHAR2 DEFAULT NULL,
  action         IN VARCHAR2 DEFAULT 'runsql',
  conversation_id IN NUMBER DEFAULT NULL,
  return_citations IN BOOLEAN DEFAULT FALSE
) RETURN CLOB;
```

#### 액션 타입

| 액션 | 설명 | 반환값 | 사용 예 |
|------|------|--------|---------|
| **runsql** | SQL 생성 및 실행, 결과 반환 | 쿼리 결과 (JSON) | 데이터 조회 |
| **showsql** | SQL만 생성하여 반환 (실행 안 함) | SQL 문자열 | SQL 검증, 학습 |
| **narrate** | RAG 기반 자연어 답변 생성 | 텍스트 답변 + 출처 | 문서 검색 질의응답 |
| **chat** | 일반 대화 (데이터 조회 없음) | 텍스트 응답 | 일반 질문, 도움말 |
| **summarize** | 텍스트 요약 | 요약문 | 긴 텍스트 압축 |

#### 실습 예제

```sql
-- 예제 1: SQL 생성 및 실행
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '판매량 상위 10개 제품과 판매액을 보여줘',
  action => 'runsql'
) FROM DUAL;

-- 예제 2: SQL만 확인 (실행 안 함)
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '지난 달 신규 고객 수는?',
  action => 'showsql'
) FROM DUAL;

-- 예제 3: RAG 질의응답
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '연차 사용 규정은?',
  action => 'narrate',
  return_citations => TRUE
) FROM DUAL;

-- 예제 4: 대화 모드
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => 'Select AI가 뭐야?',
  action => 'chat'
) FROM DUAL;

-- 예제 5: 텍스트 요약
SELECT DBMS_CLOUD_AI.SUMMARIZE(
  data => 'Long text content here...',
  format => 'paragraph'  -- 또는 'list'
) FROM DUAL;
```

### 8.3 대화 관리 함수

```sql
-- 대화 생성
DECLARE
  v_conv_id NUMBER;
BEGIN
  v_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION(
    profile_name => 'MY_PROFILE',
    description => 'Q4 Sales Analysis',
    attributes => JSON_OBJECT('retention_days' VALUE 30)
  );
  DBMS_OUTPUT.PUT_LINE('Conversation ID: ' || v_conv_id);
END;
/

-- 대화 ID 설정
BEGIN
  DBMS_CLOUD_AI.SET_CONVERSATION_ID(conversation_id => 12345);
END;
/

-- 현재 대화 ID 확인
SELECT DBMS_CLOUD_AI.GET_CONVERSATION_ID() FROM DUAL;

-- 대화 컨텍스트 초기화
BEGIN
  DBMS_CLOUD_AI.CLEAR_CONVERSATION_ID();
END;
/

-- 대화 삭제
BEGIN
  DBMS_CLOUD_AI.DROP_CONVERSATION(conversation_id => 12345);
END;
/
```

### 8.4 프로파일 관리

```sql
-- 프로파일 목록 조회
SELECT 
  profile_name,
  status,
  created_date,
  modified_date
FROM USER_CLOUD_AI_PROFILES
ORDER BY created_date DESC;

-- 프로파일 상세 확인
SELECT 
  profile_name,
  attributes
FROM USER_CLOUD_AI_PROFILES
WHERE profile_name = 'MY_PROFILE';

-- 프로파일 수정
BEGIN
  DBMS_CLOUD_AI.DROP_PROFILE(
    profile_name => 'OLD_PROFILE'
  );
  
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'NEW_PROFILE',
    attributes => '...'
  );
END;
/

-- 현재 활성 프로파일 확인
SELECT SYS_CONTEXT('CLOUD_AI', 'PROFILE_NAME') as current_profile
FROM DUAL;
```

### 8.5 피드백 및 학습

```sql
-- 긍정 피드백 (쿼리가 정확함)
BEGIN
  DBMS_CLOUD_AI.FEEDBACK(
    feedback_type => 'positive',
    prompt => '판매량 상위 10개 제품',
    generated_sql => 'SELECT product_name, sales FROM ...',
    comments => '완벽한 쿼리입니다'
  );
END;
/

-- 부정 피드백 (쿼리 수정 필요)
BEGIN
  DBMS_CLOUD_AI.FEEDBACK(
    feedback_type => 'negative',
    prompt => '지난 주 매출',
    generated_sql => 'SELECT * FROM sales WHERE ...',
    correct_sql => 'SELECT SUM(amount) FROM sales WHERE week = ...',
    comments => '집계 함수를 사용해야 합니다'
  );
END;
/

-- 피드백 이력 조회
SELECT 
  feedback_date,
  feedback_type,
  prompt,
  generated_sql,
  comments
FROM USER_CLOUD_AI_FEEDBACK
ORDER BY feedback_date DESC
FETCH FIRST 10 ROWS ONLY;
```

---

## 9. 트러블슈팅 및 FAQ

### 9.1 일반적인 오류 및 해결 방법

#### 오류 1: Database Link 연결 실패

```
ORA-02019: connection description for remote database not found
```

**원인:**
- Database Link 이름 오타
- 원격 데이터베이스 접근 불가 (네트워크, 방화벽)
- Credential 오류

**해결책:**

```sql
-- 1. Database Link 존재 확인
SELECT db_link FROM USER_DB_LINKS;

-- 2. 연결 테스트
SELECT * FROM DUAL@MYSQL_ECOMMERCE_LINK;

-- 3. Credential 재생성
BEGIN
  DBMS_CLOUD.DROP_CREDENTIAL('MYSQL_CRED');
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'MYSQL_CRED',
    username => 'correct_username',
    password => 'correct_password'
  );
END;
/

-- 4. Database Link 재생성
BEGIN
  DBMS_CLOUD_ADMIN.DROP_DATABASE_LINK('MYSQL_ECOMMERCE_LINK');
  DBMS_CLOUD_ADMIN.CREATE_DATABASE_LINK(
    db_link_name => 'MYSQL_ECOMMERCE_LINK',
    hostname => 'correct-hostname.rds.amazonaws.com',
    port => '3306',
    service_name => 'ecommerce',
    credential_name => 'MYSQL_CRED'
  );
END;
/
```

#### 오류 2: Iceberg External Table 읽기 실패

```
ORA-29913: error in executing ODCIEXTTABLEOPEN callout
```

**원인:**
- S3 접근 권한 부족
- Iceberg metadata.json 경로 오류
- Credential 만료 또는 잘못됨

**해결책:**

```sql
-- 1. Credential 확인
SELECT credential_name, username, enabled
FROM USER_CREDENTIALS
WHERE credential_name = 'AWS_GLUE_CRED';

-- 2. S3 접근 테스트
SELECT * 
FROM DBMS_CLOUD.LIST_OBJECTS(
  credential_name => 'AWS_GLUE_CRED',
  location_uri => 's3://my-data-lake/warehouse/'
);

-- 3. External Table 재생성
BEGIN
  DBMS_CLOUD.DROP_EXTERNAL_TABLE('WEB_EVENTS_ICEBERG');
  
  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name => 'WEB_EVENTS_ICEBERG',
    credential_name => 'AWS_GLUE_CRED',
    format => JSON_OBJECT(
      'type' VALUE 'iceberg',
      'metadata_location' VALUE 's3://my-data-lake/warehouse/analytics/web_events/metadata/v3.metadata.json'
    ),
    column_list => '...'
  );
END;
/
```

#### 오류 3: Select AI가 잘못된 SQL 생성

**증상:**
- LLM이 존재하지 않는 컬럼 참조
- 잘못된 조인 조건
- 부적절한 집계 함수 사용

**해결책:**

```sql
-- 1. 테이블과 컬럼에 상세한 주석 추가
COMMENT ON TABLE products IS 
'Product catalog with inventory tracking. Primary key: product_id. 
Foreign keys: supplier_id references suppliers(id)';

COMMENT ON COLUMN products.price IS 
'Unit price in USD. Always positive. Use for revenue calculations';

-- 2. 프로파일에 comments 옵션 활성화
BEGIN
  DBMS_CLOUD_AI.DROP_PROFILE('MY_PROFILE');
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'MY_PROFILE',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'comments' VALUE 'true',  -- 중요!
      'object_list' VALUE JSON_ARRAY(...)
    )
  );
END;
/

-- 3. 부정 피드백 제공
BEGIN
  DBMS_CLOUD_AI.FEEDBACK(
    feedback_type => 'negative',
    prompt => '판매량이 높은 제품',
    generated_sql => 'SELECT * FROM products WHERE sales > 100',  -- 잘못된 쿼리
    correct_sql => 'SELECT product_name, SUM(quantity) as total_sales 
                    FROM order_items GROUP BY product_name 
                    ORDER BY total_sales DESC',
    comments => 'sales 컬럼은 없습니다. order_items 테이블의 quantity를 집계해야 합니다'
  );
END;
/
```

### 9.2 성능 최적화

#### 느린 원격 쿼리

**문제:** MySQL이나 Iceberg 테이블 조회 시 응답 속도가 느림

**해결책:**

```sql
-- 1. Materialized View로 자주 사용하는 데이터 캐시
CREATE MATERIALIZED VIEW products_mv
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT * FROM products@MYSQL_ECOMMERCE_LINK;

-- 2. 스케줄러로 주기적 갱신
BEGIN
  DBMS_SCHEDULER.CREATE_JOB(
    job_name => 'REFRESH_PRODUCTS_MV',
    job_type => 'PLSQL_BLOCK',
    job_action => 'BEGIN DBMS_MVIEW.REFRESH(''PRODUCTS_MV''); END;',
    start_date => SYSTIMESTAMP,
    repeat_interval => 'FREQ=HOURLY; INTERVAL=1',
    enabled => TRUE
  );
END;
/

-- 3. 프로파일에 캐시된 뷰 사용
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'OPTIMIZED_PROFILE',
    attributes => JSON_OBJECT(
      'object_list' VALUE JSON_ARRAY(
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'PRODUCTS_MV')  -- 원본 대신 MV 사용
      )
    )
  );
END;
/
```

#### 대량 데이터 조인 최적화

```sql
-- 실행 계획 확인
EXPLAIN PLAN FOR
SELECT c.customer_name, o.order_date, o.total_amount
FROM customers c
JOIN orders@MYSQL_ECOMMERCE_LINK o ON c.customer_id = o.customer_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

-- 힌트 사용하여 최적화
SELECT /*+ USE_HASH(c o) LEADING(c) */ 
  c.customer_name, 
  o.order_date, 
  o.total_amount
FROM customers c
JOIN orders@MYSQL_ECOMMERCE_LINK o ON c.customer_id = o.customer_id;
```

### 9.3 FAQ

**Q1: Select AI는 어떤 LLM을 지원하나요?**

A: 다음 LLM 제공자를 지원합니다:
- OCI Generative AI: Cohere Command, Meta Llama
- OpenAI: GPT-4, GPT-3.5
- Azure OpenAI
- Google Vertex AI: PaLM, Gemini
- Anthropic Claude (via 3rd party integration)

**Q2: 무료 티어에서 Select AI를 사용할 수 있나요?**

A: Oracle Autonomous Database Always Free 티어에서 Select AI 기능을 사용할 수 있습니다. 단, LLM API 호출에 대한 비용은 별도로 발생합니다.

**Q3: 데이터베이스 외부로 데이터가 전송되나요?**

A: 네. Select AI는 LLM에게 다음을 전송합니다:
- 사용자의 자연어 질문
- 데이터베이스 스키마 정보 (테이블명, 컬럼명, 주석)
- 생성된 SQL 쿼리
- (선택적) 쿼리 결과 샘플

**실제 데이터**는 기본적으로 전송되지 않지만, `narrate`나 `chat` 액션 사용 시 일부 데이터가 포함될 수 있습니다.

**Q4: 민감한 데이터를 보호하려면?**

A: 다음 방법을 권장합니다:
1. RAS를 사용하여 row-level security 적용
2. 민감한 컬럼은 프로파일의 `object_list`에서 제외
3. VPD(Virtual Private Database) 정책 적용
4. 프라이빗 LLM 엔드포인트 사용 (OCI 내부)

**Q5: 한국어 질문이 가능한가요?**

A: 네. 대부분의 최신 LLM은 한국어를 지원합니다. 다음 모델 추천:
- Cohere Command R+ (다국어 우수)
- GPT-4
- Claude 3

단, 테이블/컬럼 이름과 주석은 영어로 작성하는 것을 권장합니다.

**Q6: 연합 쿼리의 성능은 어떤가요?**

A: 성능은 다음 요소에 영향을 받습니다:
- 원격 데이터베이스의 네트워크 지연시간
- 조인되는 데이터 볼륨
- 원격 DB의 인덱스 상태

최적화 방법:
- 자주 사용하는 데이터는 Materialized View로 캐시
- 필터 조건을 원격 DB에 푸시다운
- 대량 조인은 ETL로 전환 고려

**Q7: Select AI 사용량을 모니터링하려면?**

```sql
-- 사용 통계 조회
SELECT 
  prompt_date,
  COUNT(*) as query_count,
  AVG(execution_time_ms) as avg_response_time,
  COUNT(DISTINCT user_id) as unique_users
FROM USER_CLOUD_AI_USAGE_STATS
WHERE prompt_date >= SYSDATE - 7
GROUP BY prompt_date
ORDER BY prompt_date DESC;

-- 비용 추정 (LLM API 호출 기준)
SELECT 
  SUM(input_tokens) as total_input_tokens,
  SUM(output_tokens) as total_output_tokens,
  SUM(input_tokens) * 0.000015 + SUM(output_tokens) * 0.00002 as estimated_cost_usd
FROM USER_CLOUD_AI_LLM_CALLS
WHERE call_date >= TRUNC(SYSDATE, 'MM');  -- 이번 달
```

---

## 10. 참고 자료 및 다음 단계

### 10.1 공식 문서

- [Oracle Select AI Documentation](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/select-ai-overview.html)
- [DBMS_CLOUD_AI Package Reference](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/dbms-cloud-ai.html)
- [Apache Iceberg Documentation](https://iceberg.apache.org/)
- [OCI Generative AI Service](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)

### 10.2 샘플 코드 및 튜토리얼

- Oracle LiveLabs: Select AI Workshops
- GitHub: Oracle Database Examples
- OCI Code Samples Repository

### 10.3 커뮤니티

- Oracle AI & Data Science Forum
- Oracle Cloud Infrastructure Community
- Stack Overflow: [oracle-select-ai] 태그

### 10.4 다음 학습 주제

완료한 핸즈온을 바탕으로 다음 단계를 진행하세요:

1. **고급 RAG 구현**
   - 하이브리드 검색 (Dense + Sparse)
   - Re-ranking 전략
   - Multi-hop 질문 처리

2. **프로덕션 배포**
   - REST API 래퍼 구축
   - 캐싱 전략
   - 사용량 모니터링 대시보드

3. **AI Agent 구축**
   - Select AI + LangChain 통합
   - 자동화된 데이터 분석 파이프라인
   - Slack/Teams 챗봇 통합

4. **엔터프라이즈 거버넌스**
   - RAS 정책 설계
   - 감사 로그 분석
   - 비용 최적화 전략

### 10.5 실습 완료 체크리스트

모든 핸즈온을 완료하셨나요? 다음 항목을 확인해보세요:

#### 기본 기능
- [ ] Select AI 프로파일 생성 및 활성화
- [ ] 자연어 질문으로 데이터 조회 성공
- [ ] `runsql`, `showsql`, `narrate` 액션 사용
- [ ] 대화형 쿼리 (Conversation) 테스트

#### 연합 쿼리
- [ ] MySQL Database Link 생성
- [ ] Iceberg External Table 연결
- [ ] Oracle + MySQL 2-Way 조인 쿼리
- [ ] Oracle + MySQL + Iceberg 3-Way 조인 쿼리

#### 고급 기능
- [ ] RAG 벡터 인덱스 생성
- [ ] 문서 기반 질의응답 테스트
- [ ] RAS 보안 정책 구현
- [ ] 메타데이터 주석으로 정확도 개선

#### 최적화
- [ ] Materialized View로 성능 개선
- [ ] 쿼리 피드백 제공
- [ ] 사용량 모니터링 설정

---

## 부록 A: 치트 시트

### 빠른 참조 - 자주 사용하는 명령어

```sql
-- ========================================
-- 프로파일 관리
-- ========================================

-- 프로파일 생성
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'MY_PROFILE',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'credential_name' VALUE 'OCI_CRED',
      'model' VALUE 'cohere.command-r-plus',
      'comments' VALUE 'true',
      'object_list' VALUE JSON_ARRAY(
        JSON_OBJECT('owner' VALUE 'ADMIN', 'name' VALUE 'TABLE_NAME')
      )
    )
  );
END;
/

-- 프로파일 활성화
EXEC DBMS_CLOUD_AI.SET_PROFILE('MY_PROFILE');

-- 프로파일 삭제
EXEC DBMS_CLOUD_AI.DROP_PROFILE('MY_PROFILE');

-- ========================================
-- 쿼리 실행
-- ========================================

-- SQL 실행하여 결과 반환
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '질문',
  action => 'runsql'
) FROM DUAL;

-- SQL만 확인 (실행 안 함)
SELECT DBMS_CLOUD_AI.GENERATE(
  prompt => '질문',
  action => 'showsql'
) FROM DUAL;

-- ========================================
-- Database Link (MySQL/PostgreSQL)
-- ========================================

-- Credential 생성
EXEC DBMS_CLOUD.CREATE_CREDENTIAL('DB_CRED', 'username', 'password');

-- Database Link 생성
EXEC DBMS_CLOUD_ADMIN.CREATE_DATABASE_LINK(
  db_link_name => 'REMOTE_DB',
  hostname => 'host.example.com',
  port => '3306',
  service_name => 'database_name',
  credential_name => 'DB_CRED'
);

-- ========================================
-- Iceberg External Table
-- ========================================

BEGIN
  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name => 'ICEBERG_TABLE',
    credential_name => 'AWS_CRED',
    format => JSON_OBJECT(
      'type' VALUE 'iceberg',
      'metadata_location' VALUE 's3://bucket/path/metadata.json'
    ),
    column_list => '...'
  );
END;
/

-- ========================================
-- 대화 관리
-- ========================================

-- 대화 시작
v_conv_id := DBMS_CLOUD_AI.CREATE_CONVERSATION(profile_name => 'MY_PROFILE');

-- 대화 설정
EXEC DBMS_CLOUD_AI.SET_CONVERSATION_ID(v_conv_id);

-- 대화 초기화
EXEC DBMS_CLOUD_AI.CLEAR_CONVERSATION_ID();

-- ========================================
-- 모니터링
-- ========================================

-- 활성 프로파일
SELECT SYS_CONTEXT('CLOUD_AI', 'PROFILE_NAME') FROM DUAL;

-- 사용 통계
SELECT * FROM USER_CLOUD_AI_USAGE_STATS;

-- Database Link 목록
SELECT * FROM USER_DB_LINKS;

-- External Table 목록
SELECT * FROM USER_EXTERNAL_TABLES;
```

---

**축하합니다! 🎉**

Oracle Select AI with Proxy Database 핸즈온을 완료하셨습니다. 이제 여러분은:
- ✅ 여러 데이터베이스를 통합하여 자연어로 조회할 수 있습니다
- ✅ 데이터 레이크(Iceberg)와 관계형 DB를 동시에 쿼리할 수 있습니다
- ✅ RAG를 활용하여 문서와 데이터를 통합 분석할 수 있습니다
- ✅ 엔터프라이즈급 보안과 거버넌스를 구현할 수 있습니다

질문이나 피드백이 있으시면 Oracle AI Community에 공유해주세요!