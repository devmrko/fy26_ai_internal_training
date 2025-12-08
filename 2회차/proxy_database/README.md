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

### 6.2 Apache Iceberg 테이블 쿼리
[cite_start]Select AI는 데이터 레이크의 표준 포맷인 Apache Iceberg 테이블에 대한 쿼리를 지원합니다[cite: 2945].
* **지원 모델:**
    * [cite_start]**Catalog-Managed:** AWS Glue, Snowflake Polaris, Databricks Unity Catalog 등을 통해 메타데이터를 관리[cite: 3006].
    * [cite_start]**Direct-Metadata:** `metadata.json` 파일을 직접 지정하여 쿼리 (스냅샷 방식)[cite: 3009].
* [cite_start]**제약 사항:** 현재는 읽기 전용(Query-only)이며, 파티션된 테이블이나 Row-level update(Merge-on-Read)는 지원되지 않습니다 [cite: 2978-2979].

---

## 7. DBMS_CLOUD_AI 패키지 핵심 레퍼런스

[cite_start]Select AI 기능을 제어하는 주요 서브프로그램 요약입니다 [cite: 1973-1977].

| 서브프로그램 | 설명 |
| :--- | :--- |
| **CREATE_PROFILE** | [cite_start]LLM 제공자, 모델, 대상 테이블 등을 지정하여 AI 프로파일 생성[cite: 1980]. |
| **SET_PROFILE** | [cite_start]현재 세션에서 사용할 AI 프로파일 활성화[cite: 2015]. |
| **GENERATE** | AI에게 작업을 요청하는 핵심 함수. [cite_start]`runsql`, `showsql`, `narrate`, `chat`, `summarize` 등의 액션 수행[cite: 2011]. |
| **CREATE_VECTOR_INDEX** | [cite_start]비정형 데이터를 벡터화하여 인덱스 생성 (RAG용)[cite: 2059]. |
| **FEEDBACK** | [cite_start]AI가 생성한 쿼리에 대해 긍정/부정 피드백을 제공하여 정확도 개선[cite: 2000]. |
| **GENERATE_SYNTHETIC_DATA** | [cite_start]개발/테스트용 가상 데이터를 생성[cite: 2049]. |
| **SUMMARIZE** | [cite_start]긴 텍스트 내용을 요약 (문단 또는 리스트 형태)[cite: 2043]. |