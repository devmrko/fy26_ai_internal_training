# Oracle Autonomous AI Database: Select AI 심화 기술 백서

## 1. Select AI 아키텍처와 "Sidecar" 모델

### 1.1 Sidecar(사이드카) 개념 및 필요성
기존 비즈니스 사용자는 SQL 기술 부족으로 인해 데이터 접근에 장벽이 있었습니다. Select AI는 **"AI Sidecar"** 모델을 통해 이 문제를 해결합니다.
* [cite_start]**개념:** Select AI Sidecar는 기존 데이터베이스와 함께 작동하는 Oracle Autonomous Database(ADB) 인스턴스(별도 또는 기존 인스턴스)를 사용하여 SQL 변환 및 연합 쿼리(Federated Query)를 오프로드(Offload)합니다[cite: 10].
* [cite_start]**역할:** 사용자의 자연어 질문을 해석하고, 연결된 여러 데이터 소스(온프레미스, 멀티 클라우드 등)에 대한 쿼리를 대신 수행합니다[cite: 11].
* [cite_start]**이점:** 복잡한 ETL 프로세스나 데이터 이동 없이, 비즈니스 사용자가 "지난달 재택근무 직원 수는?"과 같은 질문을 통해 즉각적인 인사이트를 얻을 수 있습니다 [cite: 8, 62-66].

### 1.2 연합 쿼리 (Federated Queries)
Select AI는 단순한 단일 DB 조회를 넘어, 이기종 데이터 소스 간의 연합 쿼리를 지원합니다.
* [cite_start]**작동 방식:** 예를 들어, "Acme Corp의 보류 중인 주문 보여줘"라는 질문에 대해 Google Cloud의 BigQuery에 있는 고객 데이터와 AWS Redshift의 주문 데이터를 조인하여 결과를 가져올 수 있습니다[cite: 52].
* [cite_start]**자동화:** Select AI는 조인, 데이터 위치 파악, 쿼리 최적화의 복잡성을 처리하므로 사용자는 데이터의 위치를 알 필요가 없습니다[cite: 53].
* [cite_start]**지원 데이터 소스:** Oracle Database, PostgreSQL, MySQL, SQL Server, Snowflake, MongoDB, AWS Redshift, Google BigQuery 등 다양한 소스를 지원합니다 [cite: 2830-2832].

---

## 2. 대화형 AI (Conversations) 및 문맥 유지

### 2.1 대화형 쿼리의 차별점
[cite_start]단발성 질문(Natural Language Query)과 달리, **Conversations** 기능은 이전 질문과 답변의 문맥을 기억하여 자연스러운 탐색을 가능하게 합니다 [cite: 129-131].
* **예시:**
    1.  "총 스트리밍 횟수는?"
    2.  "장르별로 나눠줘" (이전 질문의 '스트리밍 횟수'를 기억함)
    3.  [cite_start]"고객 세그먼트도 추가해줘" [cite: 135-137].

### 2.2 프로파일 설정 (conversations: true)
대화 기능을 활성화하려면 AI 프로파일 설정 시 `conversations` 속성을 `true`로 설정해야 합니다.

```sql
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE (
    profile_name => 'GENAI',
    attributes => '{"provider": "oci", 
                    "conversation": "true", 
                    "object_list": [...]}'
  );
END;
```
[cite_start][cite: 157-167, 1101-1106].

### 2.3 대화 관리 (API)
Select AI는 대화 세션을 관리하기 위한 전용 프로시저와 함수를 제공합니다.
* **`CREATE_CONVERSATION`**: 대화 세션을 생성하고 `conversation_id`를 반환합니다. [cite_start]`retention_days` 등의 속성을 설정할 수 있습니다[cite: 2539, 2546].
* [cite_start]**`SET_CONVERSATION_ID`**: 현재 세션에 특정 대화 ID를 설정하여 문맥을 이어갑니다[cite: 2573].
* [cite_start]**`GET_CONVERSATION_ID`**: 현재 세션에 활성화된 대화 ID를 확인합니다[cite: 2577].
* [cite_start]**`CLEAR_CONVERSATION_ID`**: 현재 세션에서 대화 설정을 해제하여 문맥 없는 질문으로 전환합니다[cite: 2582].
* [cite_start]**`DROP_CONVERSATION`**: 특정 대화 세션 및 관련 이력을 삭제합니다[cite: 2594].

---

## 3. 메타데이터 보강을 통한 정확도 향상

### 3.1 LLM의 환각 방지와 Comments의 역할
테이블이나 컬럼 이름이 `TABLE1`, `C1`과 같이 모호할 경우 LLM은 SQL을 제대로 생성할 수 없습니다. [cite_start]Select AI는 데이터베이스의 **Comments(주석)**를 활용하여 LLM에게 스키마의 의미를 전달합니다 [cite: 311-313].

### 3.2 주석 활용 예시
모호한 컬럼명에 주석을 달아 AI가 이해할 수 있도록 합니다.
```sql
COMMENT ON TABLE table1 IS '영화 정보, 제목 및 개봉 연도 포함';
COMMENT ON COLUMN table1.c1 IS '영화 ID, 다른 테이블과 조인 시 사용';
```
[cite_start][cite: 319-322].
[cite_start]프로파일 생성 시 `"comments":"true"` 옵션을 주면, Select AI가 이 주석 정보를 LLM 프롬프트에 자동으로 포함시킵니다[cite: 350].

---

## 4. Select AI with RAG (검색 증강 생성)

### 4.1 정형 및 비정형 데이터의 결합
[cite_start]Select AI RAG는 기업의 비공개 데이터(문서, 매뉴얼, 사규 등)를 벡터화하여 저장하고, 사용자의 질문 시 관련 내용을 검색(Retrieval)하여 답변을 생성합니다[cite: 512].
* [cite_start]**자동화된 파이프라인:** 문서 청킹(Chunking), 임베딩 생성, 벡터 저장, 검색, 프롬프트 증강의 전 과정을 Select AI가 자동화합니다 [cite: 527-528].

### 4.2 벡터 인덱스 생성 및 활용
`DBMS_CLOUD_AI.CREATE_VECTOR_INDEX` 프로시저를 사용하여 Object Storage의 문서를 벡터 인덱스로 만듭니다.
* [cite_start]**주요 속성:** 벡터 DB 제공자(`vector_db_provider`), 저장 위치(`location`), 임베딩 모델 프로파일, 청크 사이즈(`chunk_size`), 갱신 주기(`refresh_rate`) 등을 설정합니다 [cite: 2692-2702].
* [cite_start]**활용:** `narrate` 액션을 사용하면 벡터 스토어에서 검색된 내용을 바탕으로 답변하며, 답변의 근거가 된 소스 문서 목록도 함께 제공합니다 [cite: 639-641].

---

## 5. 보안 및 거버넌스: Real Application Security (RAS)

### 5.1 RAS 개요
기존 데이터베이스 보안 모델은 애플리케이션 사용자(Application User)를 식별하지 못하고 단일 DB 계정(스키마)으로 접속하는 한계가 있었습니다. [cite_start]**Real Application Security (RAS)**는 애플리케이션 사용자를 DB 레벨에서 식별하고 보안을 적용합니다 [cite: 1534-1544].

### 5.2 RAS의 3가지 보안 차원
Select AI와 결합 시 RAS는 다음 요소를 통해 강력한 데이터 거버넌스를 제공합니다.
1.  [cite_start]**Principals (주체):** 애플리케이션 사용자 및 역할(Role)[cite: 1621].
2.  [cite_start]**Application Privileges (권한):** 특정 데이터에 대해 수행할 수 있는 작업(예: `VIEW_SALARY`)[cite: 1702].
3.  [cite_start]**Objects (객체/데이터):** ACL(접근 제어 목록)과 Data Realm(데이터 영역)을 통해 보호되는 실제 데이터 행(Row)과 열(Column) [cite: 1622-1623].

### 5.3 HR 시나리오 적용 예시
* **상황:** IT 부서의 David는 자신의 급여는 볼 수 있지만, 다른 IT 직원의 급여는 볼 수 없어야 함. [cite_start]HR 담당자 Susan은 모든 직원의 급여를 볼 수 있음 [cite: 1835-1839].
* [cite_start]**구현:** `EMP_ACL`, `IT_ACL`, `HR_ACL`을 생성하여 역할별로 접근 가능한 데이터 영역(Realm)과 컬럼(Salary)에 대한 권한을 세밀하게 제어합니다 [cite: 1868-1872]. Select AI는 이 보안 정책을 준수하여 쿼리를 생성하고 실행합니다.

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