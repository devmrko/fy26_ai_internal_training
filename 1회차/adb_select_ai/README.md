## Oracle Autonomous AI Database: Select AI 교육 과정

#### 문서 개요:
- 본 교육 자료는 Oracle Autonomous AI Database(ADB)의 Select AI 기능을 활용하여, 데이터베이스와 자연어로 상호작용하는 방법을 포괄적으로 다룹니다.
- 기본적인 Text-to-SQL 기능부터 Conversation(대화형 컨텍스트), Synthetic Data(가상 데이터 생성), Summarization(요약), Translation(번역) 등 Select AI의 다양한 고급 기능을 Northwind 데이터셋과 Python SDK를 활용해 실습합니다.
- 또한, 최신 MCP (Model Context Protocol) 기술을 적용하여 Cursor나 VS Code 같은 IDE에서 Select AI를 직접 호출하는 AI 에이전트 서버를 구축하는 방법까지 포함합니다.

### [1부] Oracle Autonomous AI Database: Select AI & RAG 기술 소개

##### 1. Select AI란 무엇인가?
Select AI는 Oracle Autonomous AI Database(ADB)에 내장된 AI 기능으로, 사용자가 복잡한 SQL 쿼리 작성법을 모르더라도 자연어(Natural Language)로 데이터베이스와 대화하듯 데이터를 조회하고 분석할 수 있게 해줍니다.

###### 1.1 핵심 가치 (Value Proposition)
- 생산성 향상: 개발자나 데이터 분석가는 반복적인 SQL 작성 시간을 단축하고, 비즈니스 로직과 데이터 해석에 집중할 수 있습니다.
- 데이터 접근성 민주화: SQL을 모르는 마케터, 경영진, 현업 담당자도 "지난달 매출 추이 보여줘"와 같은 질문으로 즉시 데이터를 확인할 수 있습니다.
- SaaS형 AI 통합: 별도의 AI 인프라(벡터 DB, 랭체인 서버 등)를 구축할 필요 없이, ADB 내장 패키지만으로 LLM 기능을 활용할 수 있습니다.

###### 1.2 작동 원리 (Text-to-SQL)
Select AI는 사용자의 질문을 해석하고 이를 데이터베이스 명령어로 변환하는 미들웨어 역할을 수행합니다.

1. 프롬프트 전송: 사용자가 자연어로 질문을 입력합니다.
2. 메타데이터 활용: ADB는 데이터베이스 스키마 정보(테이블 명, 컬럼 명, 데이터 타입, 주석 등)를 LLM에 컨텍스트로 제공합니다.
3. SQL 생성 (Generation): LLM은 질문의 의도와 스키마 정보를 결합하여 실행 가능한 SQL 쿼리를 생성합니다.
4. 쿼리 실행 및 반환: ADB는 생성된 SQL을 실행하고, 그 결과를 사용자에게 반환하거나 자연어로 요약하여 설명합니다.

##### 2. Structured RAG (정형 데이터 검색 증강 생성)
일반적으로 RAG (Retrieval Augmented Generation)는 벡터 데이터베이스를 활용하여 매뉴얼이나 규정집 같은 비정형 텍스트 문서를 검색하는 기술로 알려져 있습니다. 하지만 Select AI는 "데이터베이스 자체를 지식 저장소로 활용하는 RAG"를 구현합니다.

###### 2.1 개념 비교
- Unstructured RAG (비정형 RAG):
  - 소스: PDF, HTML, 텍스트 파일 등.
  - 방식: 문서를 벡터로 변환(Embedding)하여 저장하고, 질문과 유사한 벡터를 찾아(Similarity Search) 답변 생성.
  - 용도: "A 제품의 반품 규정이 뭐야?" 같은 문서 기반 질의.
- Structured RAG (정형 RAG - Select AI):
  - 소스: 관계형 데이터베이스 테이블 (Rows & Columns).
  - 방식: 질문을 SQL로 변환하여 정확한 데이터를 조회(Retrieval)하고, 이를 바탕으로 답변 생성.
  - 용도: "작년 3분기 동부 지역 매출 총합은?" 같은 수치/집계 기반 질의.

###### 2.2 왜 Structured RAG인가?
LLM은 계산에 약하고 사실이 아닌 정보를 지어내는 환각(Hallucination) 현상이 있습니다. 비즈니스 데이터 분석에서 숫자가 틀리는 것은 치명적입니다. Select AI는 "데이터 조회는 DB가(SQL), 답변 생성은 LLM이" 담당하는 구조를 통해 정확한 수치 데이터와 유려한 자연어 답변을 동시에 제공합니다.

##### 3. Select AI의 주요 고급 기능 (Advanced Features)
 Select AI는 단순한 데이터 조회(Text-to-SQL)를 넘어, 엔터프라이즈급 AI 애플리케이션 개발에 필요한 다양한 고급 기능을 제공합니다.

###### 3.1 Select AI Conversations (대화형 컨텍스트)
- 개요: Conversations 기능은 사용자와 시스템 간의 상호 작용을 대화(Dialogue) 형태로 관리합니다. 단발성 질문이 아니라, 사용자가 제공한 일련의 자연어 프롬프트를 저장하고 관리하여 LLM 상호 작용을 위한 장기 기억(Long-term Memory)을 지원합니다.
- 특징:
  - 문맥 유지: 이전 질문과 답변의 내용을 기억하여 후속 질문 시 문맥을 파악합니다.
  - 이력 관리: 대화 세션별로 이력을 관리하여 사용자가 과거 대화 내용을 참조하거나 이어서 진행할 수 있습니다.
- 예시:
  1. User: "가장 많이 팔린 제품이 뭐야?"
  2. System: "가장 많이 팔린 제품은 'Chai'입니다."
  3. User: "그 제품의 재고는 얼마나 남았어?" ('그 제품'이 'Chai'임을 인식하고 답변)

###### 3.2 Select AI with RAG (검색 증강 생성)
- 개요: Select AI의 RAG 기능은 사용자의 자연어 프롬프트를 벡터 스토어(Vector Store)에서 검색한 관련 콘텐츠로 증강(Augment)합니다. DBMS_CLOUD_AI 패키지를 사용하여 벡터 인덱스를 생성하고 관리하며, 의미론적 유사성(Semantic Similarity) 검색을 수행합니다.

- 작동 방식:
  1. 임베딩 생성: 사용자의 질문을 벡터 임베딩 모델을 통해 벡터로 변환합니다.
  2. 유사도 검색: 변환된 벡터를 사용하여 벡터 스토어(Oracle AI Vector Search 등)에서 가장 관련성이 높은 콘텐츠를 검색합니다.
  3. 프롬프트 증강: 검색된 콘텐츠를 원본 질문과 함께 LLM에 전달합니다.
  4. 답변 생성: LLM은 증강된 정보를 바탕으로 더 정확하고 구체적인 답변을 생성합니다.
- 장점:
  - 환각 감소: LLM이 학습하지 않은 최신 데이터나 사내 비공개 정보를 근거로 답변하므로 거짓 정보를 생성할 확률이 줄어듭니다.
  - 관련성 향상: 사용자의 질문 의도와 의미적으로 가장 가까운 정보를 찾아 답변하므로 답변의 품질이 높아집니다.

###### 3.3 Synthetic Data Generation (가상 데이터 생성)
- 개요: 실제 데이터와 유사한 통계적 특성과 구조를 가진 가상 데이터(Synthetic Data)를 생성하는 기능입니다. 랜덤 생성기, 알고리즘, 통계 모델, 그리고 LLM을 복합적으로 활용하여 데이터를 시뮬레이션합니다.

- 활용 사례:
  - 개발 및 테스트: 민감한 실제 데이터를 사용하지 않고도 애플리케이션 기능을 테스트하고 디버깅할 수 있습니다.
  - 데이터 증강: 머신러닝 모델 학습을 위해 데이터 양이 부족할 때 데이터를 늘리는 용도로 사용 가능합니다.
  - 데모 구축: 실제 고객 정보 없이도 현실감 있는 데모 환경을 구성할 수 있습니다.

###### 3.4 Feedback (피드백 루프)
- 개요: Feedback 기능은 사용자가 LLM이 생성한 SQL 쿼리의 정확성에 대해 피드백을 제공할 수 있게 합니다.

- 특징:
  - 정확도 향상: 사용자가 "이 질문에는 이 SQL을 써야 해"라고 정답을 알려주거나 부정적인 피드백을 제공하면, 시스템은 이를 학습하여 다음 번 유사한 질문에 더 정확한 쿼리를 생성하도록 개선됩니다.
  - 사용자 참여: 도메인 전문가가 직접 AI의 학습 과정에 참여하여 특정 비즈니스 로직에 맞는 쿼리를 생성하도록 유도할 수 있습니다.

###### 3.5 Generate a Summary (요약)
- 개요: Select AI는 데이터베이스 내의 텍스트나 외부 파일 등 대용량 텍스트(일반적으로 최대 1GB 지원)를 요약하여 핵심 인사이트를 추출하는 기능을 제공합니다. 지정된 AI 프로파일의 LLM을 사용하여 요약을 수행합니다.

- 주요 옵션:
  - 형식 제어: 요약 결과를 단락(Paragraph) 형태나 글머리 기호(Bullet points) 목록 등으로 지정할 수 있습니다.
  - 추출 수준(Extractiveness): 요약이 원본 문구와 얼마나 가깝게 유지될지를 제어할 수 있습니다.

- 사용 방법:
  - SQL 명령줄: SELECT AI summarize <텍스트>
  - 함수 사용: DBMS_CLOUD_AI.GENERATE 함수에 action => 'summarize' 파라미터 사용

###### 3.6 Translate (번역)
- 개요: OCI Translation 서비스(OCI Language) 또는 생성형 AI를 활용하여 텍스트를 원하는 언어로 번역하는 기능입니다. 30개 이상의 언어를 지원하며, SQL 쿼리 내에서 직접 AI 기반 번역을 수행할 수 있어 애플리케이션 개발을 단순화합니다.

- 장점:
  - 다국어 지원: 글로벌 비즈니스 환경에서 언어 장벽 없이 데이터를 조회하고 이해할 수 있습니다.
  - 자동 변환: DBMS_CLOUD_AI.GENERATE 또는 NARRATE 사용 시 출력 결과를 사용자가 선호하는 언어로 자동 변환하여 제공합니다.

- 사용 방법:
  - SQL 명령줄: SELECT AI translate <텍스트>
  - 함수 사용: DBMS_CLOUD_AI.TRANSLATE 함수 또는 DBMS_CLOUD_AI.GENERATE 함수에 action => 'translate' 파라미터 사용

### [2부] 핸즈온 실습 환경 구성 및 SQL/PLSQL 활용
- 문서 개요: 본 문서는 실습에 필요한 Northwind 샘플 데이터를 ADB에 구축하고, SQL Worksheet 환경에서 Select AI 프로파일을 설정하여 자연어 질의를 테스트하는 과정을 다룹니다. 또한, 가상 데이터 생성 및 AI 피드백 기능을 SQL 환경에서 직접 수행하는 심화 실습을 포함합니다.

##### 1. 사전 준비 사항 (Prerequisites)
실습을 시작하기 전 다음 사항을 확인하세요.
  1. OCI 계정: 유료 또는 트라이얼 계정.
  2. ADB 인스턴스: 19c 이상 (26ai 권장), 워크로드 유형(ADW/ATP) 무관.
  3. OCI GenAI 리전: US Midwest (Chicago), Frankfurt, London 등 GenAI 서비스가 활성화된 리전.
  4. 권한 설정: ADB 인스턴스가 Resource Principal 또는 API key 를 설정하는 것으로 GenAI 서비스를 호출할 수 있어야 합니다.

##### 2. 스키마 생성 및 데이터 로드 (Northwind)
- [작업 위치] OCI 콘솔 > Autonomous AI Database > Database Actions > SQL (ADMIN 계정으로 접속)

###### 2.1 사용자 생성 및 권한 부여
Northwind 데이터를 저장할 별도의 사용자를 생성합니다.
```
-- 사용자 생성
CREATE USER NORTHWIND IDENTIFIED BY "Welcome12345#";
```
```
-- 기본 권한 부여
GRANT CREATE SESSION TO NORTHWIND;
GRANT CONNECT, RESOURCE, DWROLE TO NORTHWIND;
GRANT UNLIMITED TABLESPACE TO NORTHWIND;
```
```
-- Select AI 및 클라우드 기능 사용 권한 부여
GRANT EXECUTE ON DBMS_CLOUD TO NORTHWIND;
GRANT EXECUTE ON DBMS_CLOUD_AI TO NORTHWIND;
```
```
-- sql id 검색을 위한 권한 부여
GRANT READ ON SYS.V_$MAPPED_SQL TO NORTHWIND;
GRANT READ ON SYS.V_$SESSION TO NORTHWIND;
```
```
-- Enabling User Access to Database Actions” 절차, SQL worksheet 접속을 위해 필요
BEGIN
  ords_admin.enable_schema(
    p_enabled           => TRUE,
    p_schema            => 'NORTHWIND',
    p_url_mapping_type  => 'BASE_PATH',
    p_url_mapping_pattern => 'northwind',
    p_auto_rest_auth    => NULL
  );
  COMMIT;
END;
```
```
-- 외부 네트워크(AI API) 접속 권한 (API Key 방식 사용 시 필수), * 대신 domain 주소 지정 가능(openai 등 을 위한 설정)
BEGIN
  DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
    host => '*',
    ace  => xs$ace_type(privilege_list => xs$name_list('http'),
                        principal_name => 'NORTHWIND',
                        principal_type => xs_acl.ptype_db)
  );
END;
/
```

###### 2.2 테이블 생성 및 데이터 로드 (SQL 변환 완료)
주의: 반드시 ADMIN에서 로그아웃하고, 방금 생성한 NORTHWIND 사용자로 로그인하여 실행하세요. (비밀번호: Welcome12345#)

```
-- 1. Categories 테이블 생성
CREATE TABLE CATEGORIES (
    CATEGORY_ID NUMBER PRIMARY KEY,
    CATEGORY_NAME VARCHAR2(15),
    DESCRIPTION VARCHAR2(300)
);

COMMENT ON TABLE CATEGORIES IS
'Product categories. Each category groups similar types of products. Used to classify products in the PRODUCTS table.';

COMMENT ON COLUMN CATEGORIES.CATEGORY_ID IS 'Primary key. Unique identifier for each product category.';
COMMENT ON COLUMN CATEGORIES.CATEGORY_NAME IS 'Name of the category (e.g., Beverages, Condiments).';
COMMENT ON COLUMN CATEGORIES.DESCRIPTION IS 'Optional description of the category.';

```
```
-- 2. Customers 테이블 생성
CREATE TABLE CUSTOMERS (
    CUSTOMER_ID VARCHAR2(5) PRIMARY KEY,
    COMPANY_NAME VARCHAR2(40),
    CONTACT_NAME VARCHAR2(30),
    CONTACT_TITLE VARCHAR2(30),
    ADDRESS VARCHAR2(60),
    CITY VARCHAR2(15),
    REGION VARCHAR2(15),
    POSTAL_CODE VARCHAR2(10),
    COUNTRY VARCHAR2(15),
    PHONE VARCHAR2(24),
    FAX VARCHAR2(24)
);

COMMENT ON TABLE CUSTOMERS IS
'List of customers who place orders. Linked to ORDERS table through CUSTOMER_ID.';

COMMENT ON COLUMN CUSTOMERS.CUSTOMER_ID IS 'Primary key. Unique code for each customer.';
COMMENT ON COLUMN CUSTOMERS.COMPANY_NAME IS 'Customer company name.';
COMMENT ON COLUMN CUSTOMERS.CONTACT_NAME IS 'Main contact person at the customer company.';
COMMENT ON COLUMN CUSTOMERS.CONTACT_TITLE IS 'Job title of the contact person.';
COMMENT ON COLUMN CUSTOMERS.ADDRESS IS 'Customer address.';
COMMENT ON COLUMN CUSTOMERS.CITY IS 'City of the customer.';
COMMENT ON COLUMN CUSTOMERS.REGION IS 'Region/state of the customer.';
COMMENT ON COLUMN CUSTOMERS.POSTAL_CODE IS 'Postal/ZIP code.';
COMMENT ON COLUMN CUSTOMERS.COUNTRY IS 'Country of the customer.';
COMMENT ON COLUMN CUSTOMERS.PHONE IS 'Customer phone number.';
COMMENT ON COLUMN CUSTOMERS.FAX IS 'Customer fax number.';

```
```
-- 3. Products 테이블 생성
CREATE TABLE PRODUCTS (
    PRODUCT_ID NUMBER PRIMARY KEY,
    PRODUCT_NAME VARCHAR2(40),
    SUPPLIER_ID NUMBER,
    CATEGORY_ID NUMBER,
    QUANTITY_PER_UNIT VARCHAR2(20),
    UNIT_PRICE NUMBER(10, 2),
    UNITS_IN_STOCK NUMBER,
    UNITS_ON_ORDER NUMBER,
    REORDER_LEVEL NUMBER,
    DISCONTINUED NUMBER(1),
    FOREIGN KEY (CATEGORY_ID) REFERENCES CATEGORIES(CATEGORY_ID)
);

COMMENT ON TABLE PRODUCTS IS
'Products available for sale. Linked to CATEGORIES via CATEGORY_ID and to ORDER_DETAILS via PRODUCT_ID.';

COMMENT ON COLUMN PRODUCTS.PRODUCT_ID IS 'Primary key. Unique identifier for each product.';
COMMENT ON COLUMN PRODUCTS.PRODUCT_NAME IS 'Name of the product.';
COMMENT ON COLUMN PRODUCTS.SUPPLIER_ID IS 'Identifier for the supplier (not defined in this schema).';
COMMENT ON COLUMN PRODUCTS.CATEGORY_ID IS 'Foreign key referencing CATEGORIES(CATEGORY_ID). Indicates the product category.';
COMMENT ON COLUMN PRODUCTS.QUANTITY_PER_UNIT IS 'Description of quantity per unit (e.g., 24 - 12 oz bottles).';
COMMENT ON COLUMN PRODUCTS.UNIT_PRICE IS 'Price per unit of the product.';
COMMENT ON COLUMN PRODUCTS.UNITS_IN_STOCK IS 'Current inventory level.';
COMMENT ON COLUMN PRODUCTS.UNITS_ON_ORDER IS 'Units ordered but not yet received.';
COMMENT ON COLUMN PRODUCTS.REORDER_LEVEL IS 'Minimum stock level before reorder is required.';
COMMENT ON COLUMN PRODUCTS.DISCONTINUED IS 'Whether the product is discontinued (0 = no, 1 = yes).';

```
```
-- 4. Orders 테이블 생성
CREATE TABLE ORDERS (
    ORDER_ID NUMBER PRIMARY KEY,
    CUSTOMER_ID VARCHAR2(5),
    EMPLOYEE_ID NUMBER,
    ORDER_DATE DATE,
    REQUIRED_DATE DATE,
    SHIPPED_DATE DATE,
    SHIP_VIA NUMBER,
    FREIGHT NUMBER(10, 2),
    SHIP_NAME VARCHAR2(40),
    SHIP_ADDRESS VARCHAR2(60),
    SHIP_CITY VARCHAR2(15),
    SHIP_REGION VARCHAR2(15),
    SHIP_POSTAL_CODE VARCHAR2(10),
    SHIP_COUNTRY VARCHAR2(15),
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMERS(CUSTOMER_ID)
);

COMMENT ON TABLE ORDERS IS
'Customer orders. Each order may contain multiple products through ORDER_DETAILS.';

COMMENT ON COLUMN ORDERS.ORDER_ID IS 'Primary key. Unique identifier for each order.';
COMMENT ON COLUMN ORDERS.CUSTOMER_ID IS 'Foreign key referencing CUSTOMERS(CUSTOMER_ID). Identifies the customer who placed the order.';
COMMENT ON COLUMN ORDERS.EMPLOYEE_ID IS 'Employee handling the order (not defined in this schema).';
COMMENT ON COLUMN ORDERS.ORDER_DATE IS 'Date when the order was placed.';
COMMENT ON COLUMN ORDERS.REQUIRED_DATE IS 'Date when the order is required.';
COMMENT ON COLUMN ORDERS.SHIPPED_DATE IS 'Date when the order was shipped.';
COMMENT ON COLUMN ORDERS.SHIP_VIA IS 'Shipping method identifier.';
COMMENT ON COLUMN ORDERS.FREIGHT IS 'Shipping cost.';
COMMENT ON COLUMN ORDERS.SHIP_NAME IS 'Name of the shipping contact/';
COMMENT ON COLUMN ORDERS.SHIP_ADDRESS IS 'Shipping address.';
COMMENT ON COLUMN ORDERS.SHIP_CITY IS 'Shipping city.';
COMMENT ON COLUMN ORDERS.SHIP_REGION IS 'Shipping region/state.';
COMMENT ON COLUMN ORDERS.SHIP_POSTAL_CODE IS 'Shipping ZIP/postal code.';
COMMENT ON COLUMN ORDERS.SHIP_COUNTRY IS 'Shipping country.';

```
```
-- 5. Order Details 테이블 생성
CREATE TABLE ORDER_DETAILS (
    ORDER_ID NUMBER,
    PRODUCT_ID NUMBER,
    UNIT_PRICE NUMBER(10, 2),
    QUANTITY NUMBER,
    DISCOUNT NUMBER(4, 2),
    PRIMARY KEY (ORDER_ID, PRODUCT_ID),
    FOREIGN KEY (ORDER_ID) REFERENCES ORDERS(ORDER_ID),
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID)
);

COMMENT ON TABLE ORDER_DETAILS IS
'Line items of each order. Links ORDERS and PRODUCTS. Stores quantity, price, and discount for each product in an order.';

COMMENT ON COLUMN ORDER_DETAILS.ORDER_ID IS 'Foreign key referencing ORDERS(ORDER_ID). Identifies the order.';
COMMENT ON COLUMN ORDER_DETAILS.PRODUCT_ID IS 'Foreign key referencing PRODUCTS(PRODUCT_ID). Identifies the product.';
COMMENT ON COLUMN ORDER_DETAILS.UNIT_PRICE IS 'Unit price at the time of order (may differ from current price).';
COMMENT ON COLUMN ORDER_DETAILS.QUANTITY IS 'Quantity of the product ordered.';
COMMENT ON COLUMN ORDER_DETAILS.DISCOUNT IS 'Discount applied (0 to 1).';

```
```
-- 6. 데이터 입력 (샘플 데이터)
-- Categories (전체 8개 카테고리)
INSERT INTO CATEGORIES VALUES (1, 'Beverages', 'Soft drinks, coffees, teas, beers, and ales');
INSERT INTO CATEGORIES VALUES (2, 'Condiments', 'Sweet and savory sauces, relishes, spreads, and seasonings');
INSERT INTO CATEGORIES VALUES (3, 'Confections', 'Desserts, candies, and sweet breads');
INSERT INTO CATEGORIES VALUES (4, 'Dairy Products', 'Cheeses');
INSERT INTO CATEGORIES VALUES (5, 'Grains/Cereals', 'Breads, crackers, pasta, and cereal');
INSERT INTO CATEGORIES VALUES (6, 'Meat/Poultry', 'Prepared meats');
INSERT INTO CATEGORIES VALUES (7, 'Produce', 'Dried fruit and bean curd');
INSERT INTO CATEGORIES VALUES (8, 'Seafood', 'Seaweed and fish');

-- Customers (샘플 고객 추가)
INSERT INTO CUSTOMERS VALUES ('ALFKI', 'Alfreds Futterkiste', 'Maria Anders', 'Sales Representative', 'Obere Str. 57', 'Berlin', NULL, '12209', 'Germany', '030-0074321', '030-0076545');
INSERT INTO CUSTOMERS VALUES ('ANATR', 'Ana Trujillo Emparedados y helados', 'Ana Trujillo', 'Owner', 'Avda. de la Constitución 2222', 'México D.F.', NULL, '05021', 'Mexico', '(5) 555-4729', '(5) 555-3745');
INSERT INTO CUSTOMERS VALUES ('ANTON', 'Antonio Moreno Taquería', 'Antonio Moreno', 'Owner', 'Mataderos 2312', 'México D.F.', NULL, '05023', 'Mexico', '(5) 555-3932', NULL);
INSERT INTO CUSTOMERS VALUES ('AROUT', 'Around the Horn', 'Thomas Hardy', 'Sales Representative', '120 Hanover Sq.', 'London', NULL, 'WA1 1DP', 'UK', '(171) 555-7788', '(171) 555-6750');
INSERT INTO CUSTOMERS VALUES ('BERGS', 'Berglunds snabbköp', 'Christina Berglund', 'Order Administrator', 'Berguvsvägen 8', 'Luleå', NULL, 'S-958 22', 'Sweden', '0921-12 34 65', '0921-12 34 67');

-- Products (더 많은 제품 추가)
INSERT INTO PRODUCTS VALUES (1, 'Chai', 1, 1, '10 boxes x 20 bags', 18.00, 39, 0, 10, 0);
INSERT INTO PRODUCTS VALUES (2, 'Chang', 1, 1, '24 - 12 oz bottles', 19.00, 17, 40, 25, 0);
INSERT INTO PRODUCTS VALUES (3, 'Aniseed Syrup', 1, 2, '12 - 550 ml bottles', 10.00, 13, 70, 25, 0);
INSERT INTO PRODUCTS VALUES (4, 'Chef Anton''s Cajun Seasoning', 2, 2, '48 - 6 oz jars', 22.00, 53, 0, 0, 0);
INSERT INTO PRODUCTS VALUES (5, 'Chef Anton''s Gumbo Mix', 2, 2, '36 boxes', 21.35, 0, 0, 0, 1);
INSERT INTO PRODUCTS VALUES (6, 'Grandma''s Boysenberry Spread', 2, 2, '12 - 8 oz jars', 25.00, 120, 0, 25, 0);
INSERT INTO PRODUCTS VALUES (7, 'Uncle Bob''s Organic Dried Pears', 2, 7, '12 - 1 lb pkgs.', 30.00, 15, 0, 10, 0);
INSERT INTO PRODUCTS VALUES (8, 'Northwoods Cranberry Sauce', 2, 2, '12 - 12 oz jars', 40.00, 6, 0, 0, 0);
INSERT INTO PRODUCTS VALUES (9, 'Mishi Kobe Niku', 2, 6, '18 - 500 g pkgs.', 97.00, 29, 0, 0, 1);
INSERT INTO PRODUCTS VALUES (10, 'Ikura', 2, 8, '12 - 200 ml jars', 31.00, 31, 0, 0, 0);

-- Orders (더 많은 주문 추가)
INSERT INTO ORDERS VALUES (10248, 'ALFKI', 5, TO_DATE('1996-07-04', 'YYYY-MM-DD'), TO_DATE('1996-08-01', 'YYYY-MM-DD'), TO_DATE('1996-07-16', 'YYYY-MM-DD'), 3, 32.38, 'Alfreds Futterkiste', 'Obere Str. 57', 'Berlin', NULL, '12209', 'Germany');
INSERT INTO ORDERS VALUES (10249, 'ANATR', 6, TO_DATE('1996-07-05', 'YYYY-MM-DD'), TO_DATE('1996-08-16', 'YYYY-MM-DD'), TO_DATE('1996-07-10', 'YYYY-MM-DD'), 1, 11.61, 'Ana Trujillo Emparedados', 'Avda. de la Constitución 2222', 'México D.F.', NULL, '05021', 'Mexico');
INSERT INTO ORDERS VALUES (10250, 'AROUT', 4, TO_DATE('1996-07-08', 'YYYY-MM-DD'), TO_DATE('1996-08-05', 'YYYY-MM-DD'), TO_DATE('1996-07-12', 'YYYY-MM-DD'), 2, 65.83, 'Around the Horn', '120 Hanover Sq.', 'London', NULL, 'WA1 1DP', 'UK');
INSERT INTO ORDERS VALUES (10251, 'BERGS', 3, TO_DATE('1996-07-08', 'YYYY-MM-DD'), TO_DATE('1996-08-05', 'YYYY-MM-DD'), TO_DATE('1996-07-15', 'YYYY-MM-DD'), 1, 41.34, 'Berglunds snabbköp', 'Berguvsvägen 8', 'Luleå', NULL, 'S-958 22', 'Sweden');

-- Order Details (주문 상세 추가)
INSERT INTO ORDER_DETAILS VALUES (10248, 1, 14.00, 12, 0.0);
INSERT INTO ORDER_DETAILS VALUES (10248, 2, 9.80, 10, 0.0);
INSERT INTO ORDER_DETAILS VALUES (10248, 3, 34.80, 5, 0.0);
INSERT INTO ORDER_DETAILS VALUES (10249, 4, 18.60, 9, 0.0);
INSERT INTO ORDER_DETAILS VALUES (10249, 5, 42.40, 40, 0.0);
INSERT INTO ORDER_DETAILS VALUES (10250, 1, 18.00, 10, 0.0);
INSERT INTO ORDER_DETAILS VALUES (10250, 6, 25.00, 35, 0.15);
INSERT INTO ORDER_DETAILS VALUES (10250, 7, 30.00, 15, 0.0);
INSERT INTO ORDER_DETAILS VALUES (10251, 8, 40.00, 20, 0.05);
INSERT INTO ORDER_DETAILS VALUES (10251, 9, 97.00, 40, 0.05);

COMMIT;
```

##### 3. 인증 설정 및 메타데이터 보강

###### 3.1 인증 설정 (사용 목적에 따라 선택)

**인증 방식 선택 가이드:**
| 방식 | 장점 | 단점 | 권장 대상 |
|------|------|------|-----------|
| Resource Principal | API Key 불필요, 가장 안전 | OCI 리소스에서만 사용 가능 | 프로덕션 환경 |
| API Key | 로컬/외부에서도 사용 가능 | Key 관리 필요 | 개발/테스트 환경 |
| OpenAI/타사 | 다양한 LLM 사용 | 외부 서비스 의존 | 특정 모델 필요 시 |

**Case A-1: OCI GenAI (Resource Principal - 프로덕션 권장)**
API Key 관리 없이 IAM 권한으로 인증하는 가장 안전한 방식입니다.

**1단계: Dynamic Group 생성 (OCI 콘솔)**
  - 메뉴: Identity & Security > Dynamic Groups
  - Create Dynamic Group 클릭
  - Name: `ADB_Dynamic_Group`
  - Matching Rule: ADB 인스턴스가 속한 구획(Compartment)의 모든 DB를 포함
    ```
    ALL {resource.type = 'autonomousdatabase', resource.compartment.id = '<Your_Compartment_OCID>'}
    ```

**2단계: Policy 설정 (OCI 콘솔)**
  - 메뉴: Identity & Security > Policies
  - Create Policy 클릭
  - Name: `Allow_ADB_Access_GenAI`
  - Statement: 위에서 만든 Dynamic Group이 GenAI 제품군을 사용할 수 있도록 허용
    ```
    Allow dynamic-group ADB_Dynamic_Group to manage generative-ai-family in compartment <Your_Compartment_Name>
    ```

**3단계: Resource Principal 사용**
  - Resource Principal은 **별도의 credential 생성이 필요 없습니다**
  - Oracle ADB는 `OCI$RESOURCE_PRINCIPAL`이라는 예약된 이름을 자동으로 인식합니다
  - Dynamic Group과 Policy 설정만 완료하면 바로 사용 가능

**주의사항:**
- `OCI$RESOURCE_PRINCIPAL`은 Oracle이 예약한 특별한 이름 ($ 기호 포함)
- DBMS_CLOUD.CREATE_CREDENTIAL로 생성하지 않음
- OCI 리소스(ADB) 내부에서만 작동
- Dynamic Group과 Policy가 올바르게 설정되어 있어야 함
```
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'GENAI_RP_CRED',
    username        => 'OCI$RESOURCE_PRINCIPAL',
    password        => 'NULL'
  );
END;
```

**Case A-2: OCI GenAI (API Key 방식 - Private Key 사용)**
특정 OCI 사용자 계정의 API Key를 사용하여 인증합니다. 로컬 개발 환경에서 주로 사용됩니다. 
  - 준비:
    - OCI 콘솔 > 사용자 설정 > API Keys > Add API Key.
    - Private Key 다운로드 (.pem 파일).
    - 설정 정보 확인 (Tenancy OCID, User OCID, Fingerprint).
```
BEGIN
  DBMS_CLOUD.DROP_CREDENTIAL('OCI_KEY_CRED');
END;
/

BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'OCI_KEY_CRED',
    user_ocid       => 'ocid1.user.oc1..aaaa...',  -- 사용자 OCID
    tenancy_ocid    => 'ocid1.tenancy.oc1..aaaa...',  -- 테넌시 OCID
    private_key     => 'MIIEEpQIBAAKCAQEA...',  -- .pem 파일 내용 전체
    fingerprint     => '12:34:56:78:90:ab:cd:ef...'  -- 핑거프린트
  );
END;
/
```

**생성 확인:**
```sql
SELECT credential_name, username 
FROM user_credentials 
WHERE credential_name = 'OCI_KEY_CRED';
```

**Case B: 타사 AI (OpenAI, Azure OpenAI 등)**
OCI GenAI 대신 OpenAI나 다른 제공자의 모델을 사용하고 싶을 때 선택합니다.

**OpenAI 예시:**
1. OpenAI 웹사이트(https://platform.openai.com)에서 API Key 발급
2. Credential 생성:

```sql
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'OPENAI_CRED',
    username        => 'OPENAI',  -- 고정값
    password        => 'sk-proj-...'  -- 실제 OpenAI API Key
  );
END;
/
```

###### 3.2 메타데이터(Comment) 보강 (Annotation 활용)
LLM이 테이블과 컬럼의 의미를 더 정확하게 파악할 수 있도록 JSON 형태의 Annotation을 포함한 코멘트를 추가합니다.

- 테이블 레벨: 데이터의 성격 정의
```
COMMENT ON TABLE PRODUCTS IS '{"comment": "판매 상품 마스터 정보", "annotation": {"description": "회사가 취급하는 모든 상품의 가격, 재고, 공급업체 정보를 포함함"}}';
COMMENT ON TABLE ORDERS IS '{"comment": "고객 주문 헤더", "annotation": {"description": "고객이 생성한 주문의 기본 정보. 배송지 및 주문 날짜 포함"}}';
```

- 컬럼 레벨: 비즈니스 로직 및 제약사항 가이드
```
COMMENT ON COLUMN PRODUCTS.UNITS_IN_STOCK IS '{"comment": "재고 수량", "annotation": {"meaning": "현재 창고에 물리적으로 존재하는 수량"}}';
COMMENT ON COLUMN PRODUCTS.UNITS_ON_ORDER IS '{"comment": "입고 예정 수량", "annotation": {"meaning": "공급업체에 발주하여 도착 예정인 수량"}}';
COMMENT ON COLUMN PRODUCTS.UNIT_PRICE IS '{"comment": "단가", "annotation": {"currency": "USD", "description": "할인이 적용되지 않은 개별 상품의 기본 판매 가격"}}';
```

###### 3.3 AI 프로파일 생성

주의: 생성 시 object_list에 필요한 테이블을 지정하고, comments 속성을 true로 설정하면 위에서 작성한 annotation 주석이 LLM에 전달됩니다.

**프로파일 삭제 (선택사항)**
```sql
BEGIN
    DBMS_CLOUD_AI.DROP_PROFILE(
        profile_name => 'NORTHWIND_AI',
        force        => TRUE
    );
END;
/
```

**방법 1: Resource Principal 사용 (프로덕션 권장)**
```sql
BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'NORTHWIND_AI',
        attributes   => '{
            "provider": "oci",
            "model": "meta.llama-4-maverick-17b-128e-instruct-fp8",
            "credential_name": "OCI$RESOURCE_PRINCIPAL",
            "comments": false,
            "object_list": [
                {"owner": "NORTHWIND", "name": "CATEGORIES"},
                {"owner": "NORTHWIND", "name": "PRODUCTS"},
                {"owner": "NORTHWIND", "name": "CUSTOMERS"},
                {"owner": "NORTHWIND", "name": "ORDERS"},
                {"owner": "NORTHWIND", "name": "ORDER_DETAILS"}
            ]
        }'
    );
END;
/
```

**참고:** `OCI$RESOURCE_PRINCIPAL`은 $ 기호가 포함된 Oracle의 예약 credential 이름입니다.

**방법 2: API Key 사용**
```sql
BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'NORTHWIND_AI',
        attributes   => '{
            "provider": "oci",
            "model": "meta.llama-4-maverick-17b-128e-instruct-fp8",
            "credential_name": "OCI_KEY_CRED",
            "comments": false,
            "object_list": [
                {"owner": "NORTHWIND", "name": "CATEGORIES"},
                {"owner": "NORTHWIND", "name": "PRODUCTS"},
                {"owner": "NORTHWIND", "name": "CUSTOMERS"},
                {"owner": "NORTHWIND", "name": "ORDERS"},
                {"owner": "NORTHWIND", "name": "ORDER_DETAILS"}
            ]
        }'
    );
END;
/
```

**주요 파라미터:**
- `provider`: "oci" (OCI GenAI) 또는 "openai" (OpenAI) 선택
- `model`: 사용할 모델 지정
  - `meta.llama-4-maverick-17b-128e-instruct-fp8`: Llama 4 모델 (권장)
  - `cohere.command-r-plus`: Cohere Command R+ 모델
  - `meta.llama-3.1-405b-instruct`: Llama 3.1 405B 모델
- `credential_name`: 인증 방식 지정
  - `OCI$RESOURCE_PRINCIPAL`: Resource Principal 사용 (프로덕션) - **$ 기호 포함 주의**
  - `OCI_KEY_CRED`: API Key 사용 (개발/테스트)
- `comments`: true로 설정하면 테이블/컬럼 annotation 주석을 LLM에 전달
- `object_list`: Select AI가 접근할 수 있는 테이블 목록

**프로파일 확인:**
```sql
-- 생성된 프로파일 목록 확인
SELECT profile_name, status, created
FROM user_cloud_ai_profiles;

-- 프로파일 상세 속성 확인
SELECT attribute_name, attribute_value
FROM user_cloud_ai_profile_attributes
WHERE profile_name = 'NORTHWIND_AI'
ORDER BY attribute_name;
```

**예상 결과:**
```
ATTRIBUTE_NAME      ATTRIBUTE_VALUE
------------------- --------------------------------------------------
comments            false
credential_name     OCI$RESOURCE_PRINCIPAL (또는 OCI_KEY_CRED)
model               meta.llama-4-maverick-17b-128e-instruct-fp8
object_list         [{"owner":"NORTHWIND","name":"CATEGORIES"}...]
provider            oci
```

**중요:** Resource Principal 사용 시 credential_name에 **`OCI$RESOURCE_PRINCIPAL`** ($ 기호 포함)이 표시됩니다.

##### 4. 자연어 질의 테스트 (SQL Worksheet)

```
-- 1. 프로파일 활성화
EXEC DBMS_CLOUD_AI.SET_PROFILE('northwind_ai');
```

```
-- 2. 단순 조회
SELECT AI 'What is the product with the most stock?';
```

```
-- 3. 집계 및 분석
SELECT AI 'What is the total sales amount for the "Beverages" category?';
```

```
-- 4. 쿼리 검증 (생성된 SQL 확인)
SELECT AI showsql 'What is the total sales amount for the "Beverages" category?';
```

##### 5. 고급 기능 실습 (Advanced SQL Features)
Python SDK 없이도 SQL(PL/SQL)만으로 Select AI의 고급 기능들을 사용할 수 있습니다.

###### 5.1 Synthetic Data Generation (가상 데이터 생성)
- 개발 및 테스트 목적으로 실제 데이터 패턴을 학습한 가상 데이터를 생성합니다.

- 시나리오: PRODUCTS 테이블에 가상 물품 1개를 추가합니다.

```
BEGIN
  DBMS_CLOUD_AI.GENERATE_SYNTHETIC_DATA(
    profile_name => 'NORTHWIND_AI',
    object_name  => 'PRODUCTS',
    owner_name   => 'NORTHWIND',
    record_count => 1,
    user_prompt  => 'Generate realistic grocery products'
  );
END;
```
```
-- 생성된 데이터 확인
SELECT * FROM products;
```

###### 5.2 Feedback (피드백 제공)
- LLM이 생성한 SQL이 부정확할 경우, 사용자가 올바른 SQL이나 힌트를 제공하여 AI를 학습시킬 수 있습니다.

- 시나리오: 사용자가 "총 매출"을 물어봤을 때 AI가 Freight(운임)까지 포함하여 계산했다고 가정합니다. 이를 수정하는 피드백을 제공합니다.

  1. 부정확한 질문 실행 및 SQL ID 확인
```
-- 질문 실행 (showsql로 쿼리 확인)
EXEC DBMS_CLOUD_AI.SET_PROFILE('NORTHWIND_AI');
SELECT AI showsql "What is the product with the most stock?"
```
```
SELECT 
    p."PRODUCT_ID" AS "PRODUCT_ID"
    , p."PRODUCT_NAME" AS "PRODUCT_NAME"
    , p."UNITS_IN_STOCK" AS "UNITS_IN_STOCK" 
FROM "NORTHWIND"."PRODUCTS" p 
ORDER BY p."UNITS_IN_STOCK" DESC FETCH FIRST 1 ROW ONLY
```
2. 피드백 등록 (PL/SQL) DBMS_CLOUD_AI.ADD_FEEDBACK을 사용하여 올바른 계산식을 알려줍니다.
```
-- 실행한 sql_id 검색
SELECT sql_id, sql_text, translation_timestamp
FROM v$mapped_sql
WHERE sql_text LIKE '%SELECT AI%'
ORDER BY translation_timestamp DESC
FETCH FIRST 5 ROWS ONLY;
```
참고: 피드백이 등록되면 Select AI는 다음 번 유사한 질문이 들어올 때 이 피드백을 참고하여 SQL을 생성합니다.
```
BEGIN
  DBMS_CLOUD_AI.FEEDBACK(
    profile_name     => 'NORTHWIND_AI',
    sql_id         => '5hxp7tj5fuj5r',
    feedback_type    => 'negative',
    response         => 'SELECT product_name FROM NORTHWIND.PRODUCTS ORDER BY UNITS_IN_STOCK DESC FETCH FIRST 1 ROW ONLY',
    feedback_content => 'because this query is much simpler',
    operation        => 'add'
  );
END;
/
```
**중요: 캐시 무효화**
Select AI는 성능 향상을 위해 쿼리 결과를 캐싱합니다. 피드백을 적용한 후 새로운 SQL을 생성하려면 질문을 약간 변경하거나 주석을 추가하여 캐시를 우회해야 합니다. (아래는 timestamp 값 추가)

```sql
-- 방법 1: 타임스탬프 주석 추가
EXEC DBMS_CLOUD_AI.SET_PROFILE('NORTHWIND_AI');
SELECT AI showsql "What is the product with the most stock?" --202512022028;
```
```
SELECT p."PRODUCT_NAME" AS "Product Name" 
FROM "NORTHWIND"."PRODUCTS" p 
ORDER BY p."UNITS_IN_STOCK" DESC 
FETCH FIRST 1 ROW ONLY
```

### [3부] Python 개발 및 Select AI 고급 기능 실습
Python SDK(select_ai)를 활용하여 애플리케이션 레벨에서 Select AI를 제어하고, 대화형 컨텍스트(Conversation), 가상 데이터 생성(Synthetic Data) 등 고급 기능을 구현하는 방법을 다룹니다. 또한 Streamlit을 활용하여 간단한 GUI 기반의 AI 챗봇을 만드는 방법도 포함합니다.

##### 1. Python 개발 환경
  - 주요 라이브러리 소개
    본 실습에서는 다음 두 가지 핵심 라이브러리를 사용합니다.
    - oracledb: Oracle Database와 Python을 연결해주는 드라이버입니다. SQL 실행, 트랜잭션 관리 등 데이터베이스와의 기본적인 통신을 담당합니다. select_ai는 내부적으로 이 라이브러리를 사용하여 DB와 통신합니다.
    - select_ai: Oracle Autonomous AI Database의 DBMS_CLOUD_AI 패키지를 Python에서 쉽게 사용할 수 있도록 감싸둔(Wrapper) SDK입니다. 복잡한 PL/SQL 호출 없이 Python 객체와 메서드로 AI 기능을 제어할 수 있게 해줍니다.

###### 1.1 설치 및 기본 연결
로컬 PC나 OCI Cloud Shell에서 진행합니다.

- 패키지 설치(uv 패키지 매니저 설치):
  - MacOS / Linux:
`curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows:
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex`
https://visualstudio.microsoft.com/ko/visual-cpp-build-tools/ 설치 "Desktop development with with C++" workload 설치 필요

- 사용 할 라이브러리 설치
```
uv init
uv add dotenv select_ai oracledb streamlit
```
- Wallet을 이용한 연결
  - 사전 준비:
    1. OCI 콘솔의 ADB 상세 페이지에서 DB Connection 클릭.
    2. Download Wallet을 클릭하여 zip 파일을 다운로드합니다.
    3. 다운로드한 파일의 압축을 풀고 경로를 기억해둡니다. (예: /Users/me/wallet_adb)
    4. select_ai.connect 함수에 wallet_location 파라미터를 추가하여 연결합니다.

- .env 에서 아래 항목에 해당하는 정보를 저장하여 이 정보를 아래 python code에서 활용하도록 합니다.
```
WALLET_DIR=
DB_USER=
DB_PASSWORD=
DB_DSN=
WALLET_PASSWORD=
```

```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 지갑 경로 설정 (압축 푼 폴더의 전체 경로)
WALLET_DIR = os.getenv("WALLET_DIR")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

# 필수 환경 변수 체크
if not WALLET_DIR:
    raise ValueError("WALLET_DIR environment variable is not set. Please create a .env file with required variables.")
if not DB_USER:
    raise ValueError("DB_USER environment variable is not set.")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is not set.")
if not DB_DSN:
    raise ValueError("DB_DSN environment variable is not set.")
if not WALLET_PASSWORD:
    raise ValueError("WALLET_PASSWORD environment variable is not set.")

# TNS_ADMIN 설정 (oracledb 모듈이 로드되기 전에 반드시 설정)
os.environ['TNS_ADMIN'] = WALLET_DIR

# 이제 select_ai를 import (TNS_ADMIN이 설정된 후)
import select_ai

# 연결 시도
select_ai.connect(
    user=DB_USER,
    password=DB_PASSWORD,  # 실제 비밀번호로 변경
    dsn=DB_DSN,  # tnsnames.ora 파일 안의 서비스 별칭
    wallet_location=WALLET_DIR,
    wallet_password=WALLET_PASSWORD  # 지갑 다운로드 시 설정한 비밀번호
)
print("✓ Connected securely using Wallet")
```

위 코드를 `db_conn.py` 파일로 저장한 후 실행:

```bash
uv init
uv add dotenv select_ai
uv run db_conn.py
```

##### 2. Select AI 프로파일 로드 및 테스트
PL/SQL에서 생성한 프로파일을 Python 객체로 불러와 기본 동작을 확인합니다.

###### 2.1 기본 연결 및 프로파일 사용

```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 지갑 경로 설정 (압축 푼 폴더의 전체 경로)
WALLET_DIR = os.getenv("WALLET_DIR")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

# 필수 환경 변수 체크
if not WALLET_DIR:
    raise ValueError("WALLET_DIR environment variable is not set. Please create a .env file with required variables.")
if not DB_USER:
    raise ValueError("DB_USER environment variable is not set.")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is not set.")
if not DB_DSN:
    raise ValueError("DB_DSN environment variable is not set.")
if not WALLET_PASSWORD:
    raise ValueError("WALLET_PASSWORD environment variable is not set.")

# TNS_ADMIN 설정 (oracledb 모듈이 로드되기 전에 반드시 설정)
os.environ['TNS_ADMIN'] = WALLET_DIR

# 이제 select_ai를 import (TNS_ADMIN이 설정된 후)
import select_ai

# 연결 시도
select_ai.connect(
    user=DB_USER,
    password=DB_PASSWORD,  # 실제 비밀번호로 변경
    dsn=DB_DSN,  # tnsnames.ora 파일 안의 서비스 별칭
    wallet_location=WALLET_DIR,
    wallet_password=WALLET_PASSWORD  # 지갑 다운로드 시 설정한 비밀번호
)
print("Connected securely using Wallet")

# 프로파일 로드
profile = select_ai.Profile(profile_name="NORTHWIND_AI")
print("✓ Profile loaded")

# 자연어 질의 테스트
question = "What is the product with the most stock?"
print(f"\nQuestion: {question}")

# 방법 1: narrate() - 결과와 설명을 자연어로 반환
response = profile.narrate(question)
print(f"Answer: {response}")

# 방법 2: generate() - SQL만 생성
sql = profile.generate(f"showsql {question}")
print(f"\nGenerated SQL:\n{sql}")

# 방법 3: chat() - 일반 대화
info = profile.chat("Tell me about the Northwind database structure")
print(f"\nDatabase Info: {info}")
```

###### 2.2 실행 파일 생성 (test_connection.py)
위 코드를 `test_connection.py` 파일로 저장하고 실행:

```bash
uv init
uv add dotenv select_ai
uv run test_connection.py
```

##### 3. 고급 기능 실습

###### 3.1 Conversations (대화형 컨텍스트)
단발성 질문이 아닌, 문맥을 기억하는 대화 세션을 구현합니다.

```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 지갑 경로 설정 (압축 푼 폴더의 전체 경로)
WALLET_DIR = os.getenv("WALLET_DIR")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

# 필수 환경 변수 체크
if not WALLET_DIR:
    raise ValueError("WALLET_DIR environment variable is not set. Please create a .env file with required variables.")
if not DB_USER:
    raise ValueError("DB_USER environment variable is not set.")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is not set.")
if not DB_DSN:
    raise ValueError("DB_DSN environment variable is not set.")
if not WALLET_PASSWORD:
    raise ValueError("WALLET_PASSWORD environment variable is not set.")

# TNS_ADMIN 설정 (oracledb 모듈이 로드되기 전에 반드시 설정)
os.environ['TNS_ADMIN'] = WALLET_DIR

# 이제 select_ai를 import (TNS_ADMIN이 설정된 후)
import select_ai

# 연결 시도
select_ai.connect(
    user=DB_USER,
    password=DB_PASSWORD,  # 실제 비밀번호로 변경
    dsn=DB_DSN,  # tnsnames.ora 파일 안의 서비스 별칭
    wallet_location=WALLET_DIR,
    wallet_password=WALLET_PASSWORD  # 지갑 다운로드 시 설정한 비밀번호
)
print("Connected securely using Wallet")

from select_ai import Conversation, ConversationAttributes

# 프로파일 로드
profile = select_ai.Profile(profile_name="NORTHWIND_AI")

# 1. 대화 세션 메타데이터 정의
conv_attr = ConversationAttributes(
    title="재고 분석 세션",
    description="Northwind 제품 재고 현황 및 발주 필요성 분석"
)

# 2. 대화 객체 생성 및 등록
conversation = Conversation(attributes=conv_attr)
conv_id = conversation.create()
print(f"대화 생성 완료 - 세션 ID: {conv_id}\n")

# 3. 대화 시작 (narrate로 데이터 조회 → chat으로 의견 교환)
print("=== 시나리오: narrate()로 DB 조회, chat()으로 LLM 의견 수렴 ===\n")

with profile.chat_session(conversation=conversation) as session:
    
    # ==========================================
    # 단계 1: narrate()로 실제 데이터 조회
    # ==========================================
    print("=" * 60)
    print("단계 1: narrate()로 DB에서 실제 데이터 조회")
    print("=" * 60)
    
    print("\n[DB 쿼리] Beverages 카테고리 제품 재고 조회 중...")
    db_query = "List all products in the Beverages category with their unit price, units in stock, and units on order"
    beverages_data = profile.narrate(db_query)
    print(f"\n📊 데이터베이스 조회 결과:\n{beverages_data}\n")
    
    # ==========================================
    # 단계 2: chat()으로 LLM 분석 및 의견 받기
    # ==========================================
    print("=" * 60)
    print("단계 2: chat()으로 LLM에게 데이터 분석 요청")
    print("=" * 60)
    
    print("\n[사용자] 재고 데이터 분석 요청...")
    analysis_request = f"""다음 Beverages 재고 데이터를 간단히 분석해주세요:

{beverages_data}

가장 우려되는 제품과 이유, 그리고 개선 방안을 3-4문장으로 요약해주세요."""
    
    analysis = session.chat(analysis_request)
    print(f"\n🤖 LLM 분석:\n{analysis}\n")
    
    # ==========================================
    # 단계 3: 추가 질문 (대화 맥락 유지)
    # ==========================================
    print("=" * 60)
    print("단계 3: 대화 맥락을 유지하며 추가 질문")
    print("=" * 60)
    
    print("\n[사용자] 우선순위 질문...")
    priority_question = session.chat("가장 먼저 재주문해야 할 제품을 1-2개만 간단히 추천해주세요.")
    print(f"\n🤖 LLM 답변:\n{priority_question}\n")

print("=" * 60)
print("✓ 대화 완료")
print("=" * 60)
print("\n💡 요약:")
print("  1. narrate() → DB에서 실제 재고 데이터 조회")
print("  2. chat() → LLM에게 데이터 분석 및 의견 요청")
print("  3. chat() → 대화 맥락 유지하며 추가 질문")
print("\n✨ narrate()는 팩트(데이터), chat()은 인사이트(분석)를 제공합니다!")
```

위 코드를 `chat.py` 파일로 저장하고 실행:

```bash
uv init
uv add dotenv select_ai
uv run chat.py
```

**주요 특징:**
- `chat_session()`: 컨텍스트 매니저로 대화 세션 관리
- 이전 질문과 답변을 자동으로 기억
- "그 중에서", "그걸"과 같은 대명사 참조 가능
- 세션 ID로 대화 이력 추적 가능

###### 3.2 Synthetic Data Generation (가상 데이터 생성)
개발 및 테스트를 위해 CUSTOMERS 테이블에 그럴듯한 가상 데이터를 생성해 넣습니다.

```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 지갑 경로 설정 (압축 푼 폴더의 전체 경로)
WALLET_DIR = os.getenv("WALLET_DIR")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

# 필수 환경 변수 체크
if not WALLET_DIR:
    raise ValueError("WALLET_DIR environment variable is not set. Please create a .env file with required variables.")
if not DB_USER:
    raise ValueError("DB_USER environment variable is not set.")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is not set.")
if not DB_DSN:
    raise ValueError("DB_DSN environment variable is not set.")
if not WALLET_PASSWORD:
    raise ValueError("WALLET_PASSWORD environment variable is not set.")

# TNS_ADMIN 설정 (oracledb 모듈이 로드되기 전에 반드시 설정)
os.environ['TNS_ADMIN'] = WALLET_DIR

# 이제 select_ai를 import (TNS_ADMIN이 설정된 후)
import select_ai

# 연결 시도
select_ai.connect(
    user=DB_USER,
    password=DB_PASSWORD,  # 실제 비밀번호로 변경
    dsn=DB_DSN,  # tnsnames.ora 파일 안의 서비스 별칭
    wallet_location=WALLET_DIR,
    wallet_password=WALLET_PASSWORD  # 지갑 다운로드 시 설정한 비밀번호
)
print("Connected securely using Wallet")

from select_ai import SyntheticDataAttributes, SyntheticDataParams

profile = select_ai.Profile(profile_name="NORTHWIND_AI")

print("\n=== Synthetic Data 생성 테스트 ===\n")

# 가상 데이터 생성 파라미터 설정
syn_params = SyntheticDataParams(
    sample_rows=5,      # 기존 데이터 5건을 샘플링하여 패턴 학습
    priority="HIGH"     # 생성 우선순위
)

syn_attr = SyntheticDataAttributes(
    object_name="CUSTOMERS",
    owner_name="NORTHWIND",
    record_count=3,     # 3개의 가상 고객 생성
    user_prompt="Generate realistic customer data for a European food trading company. Include diverse countries and contact information.",
    params=syn_params
)

print("가상 데이터 생성 중...")
try:
    profile.generate_synthetic_data(synthetic_data_attributes=syn_attr)
    print("생성 완료!\n")
    
    # 결과 확인
    print("최근 추가된 고객 3명:")
    result = profile.run_sql(
        "SELECT CUSTOMER_ID, COMPANY_NAME, CONTACT_NAME, CITY, COUNTRY "
        "FROM CUSTOMERS "
        "ORDER BY CUSTOMER_ID DESC "
    )
    print(result)
    
except Exception as e:
    print(f"✗ 실패: {e}")
    import traceback
    traceback.print_exc()
```

```bash
uv init
uv add dotenv select_ai
uv run synthetic_data.py
```

**주요 파라미터 설명:**
- `sample_rows`: 패턴 학습에 사용할 기존 데이터 행 수
- `record_count`: 생성할 가상 데이터 건수
- `user_prompt`: LLM에게 제공하는 데이터 생성 지침
- `priority`: 생성 작업 우선순위 (LOW, MEDIUM, HIGH)

###### 3.3 Summarization & Translate (요약 및 번역)
데이터베이스 내의 텍스트나 외부 텍스트를 요약하고 번역합니다.

```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 지갑 경로 설정 (압축 푼 폴더의 전체 경로)
WALLET_DIR = os.getenv("WALLET_DIR")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

# 필수 환경 변수 체크
if not WALLET_DIR:
    raise ValueError("WALLET_DIR environment variable is not set. Please create a .env file with required variables.")
if not DB_USER:
    raise ValueError("DB_USER environment variable is not set.")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is not set.")
if not DB_DSN:
    raise ValueError("DB_DSN environment variable is not set.")
if not WALLET_PASSWORD:
    raise ValueError("WALLET_PASSWORD environment variable is not set.")

# TNS_ADMIN 설정 (oracledb 모듈이 로드되기 전에 반드시 설정)
os.environ['TNS_ADMIN'] = WALLET_DIR

# 이제 select_ai를 import (TNS_ADMIN이 설정된 후)
import select_ai

# 연결 시도
select_ai.connect(
    user=DB_USER,
    password=DB_PASSWORD,  # 실제 비밀번호로 변경
    dsn=DB_DSN,  # tnsnames.ora 파일 안의 서비스 별칭
    wallet_location=WALLET_DIR,
    wallet_password=WALLET_PASSWORD  # 지갑 다운로드 시 설정한 비밀번호
)
print("Connected securely using Wallet")

from select_ai import SyntheticDataAttributes, SyntheticDataParams 

profile = select_ai.Profile(profile_name="NORTHWIND_AI")

print("\n=== 요약 및 번역 테스트 ===\n")

# 테스트용 긴 텍스트
long_text = """
Chai is a flavored tea beverage made by brewing black tea with a mixture of aromatic 
spices and herbs. Originating in India, the beverage has gained worldwide popularity, 
becoming a feature in many coffee and tea houses. Traditional chai is made with loose-leaf 
black tea, milk, water, and a combination of spices such as cardamom, ginger, cinnamon, 
cloves, and black pepper. The blend of spices varies by region and personal preference.
"""

# 1. 요약 (Summarize)
print("원문 요약 중...")
try:
    summary = profile.summarize(content=long_text)
    print(f"✓ 요약 완료:\n{summary}\n")
except Exception as e:
    print(f"✗ 요약 실패: {e}\n")
    summary = long_text  # 실패 시 원문 사용

# 2. 번역 (Translate) - chat 메서드 사용 (권장)
# 참고: Python SDK의 Action enum에는 TRANSLATE가 없습니다.
# 사용 가능한 Actions: RUNSQL, SHOWSQL, EXPLAINSQL, NARRATE, CHAT, SHOWPROMPT, FEEDBACK, SUMMARIZE
print("한국어로 번역 중...")
try:
    translation = profile.chat(
        f"다음 영문을 자연스러운 한국어로 번역해주세요:\n\n{summary}"
    )
    print(f"✓ 번역 완료:\n{translation}\n")
except Exception as e:
    print(f"✗ 번역 실패: {e}\n")
```

```bash
uv init
uv add dotenv select_ai
uv run summarize.py
```

**사용 가능한 메서드:**
- `profile.summarize(content=텍스트)`: 텍스트 요약
- `profile.chat(질문)`: 자유 대화 (번역, 설명 등)
 
##### 4. [Bonus] Streamlit을 활용한 AI Chatbot GUI 구축
터미널 환경을 넘어, 사용자가 웹 브라우저에서 편리하게 DB와 대화할 수 있는 간단한 GUI 애플리케이션을 만들어 봅니다.

- app.py 파일 생성
다음 코드를 복사하여 app.py 파일로 저장합니다.

```python
"""
Northwind Data Assistant - Oracle Select AI Chatbot
Simple, modular, and easy to read
"""

import os
from dotenv import load_dotenv

# ⚠️ 중요: TNS_ADMIN을 oracledb/select_ai 임포트 전에 설정해야 함!

# .env 파일 로드
load_dotenv()

# 지갑 경로 설정 (압축 푼 폴더의 전체 경로)
WALLET_DIR = os.getenv("WALLET_DIR")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

# 필수 환경 변수 체크
if not WALLET_DIR:
    raise ValueError("WALLET_DIR environment variable is not set. Please create a .env file with required variables.")
if not DB_USER:
    raise ValueError("DB_USER environment variable is not set.")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is not set.")
if not DB_DSN:
    raise ValueError("DB_DSN environment variable is not set.")
if not WALLET_PASSWORD:
    raise ValueError("WALLET_PASSWORD environment variable is not set.")

# TNS_ADMIN 설정 (oracledb 모듈이 로드되기 전에 반드시 설정)
os.environ['TNS_ADMIN'] = WALLET_DIR
print(f"✓ TNS_ADMIN 설정됨: {WALLET_DIR}")
print(f"✓ DB_DSN: {DB_DSN}")

# 이제 다른 모듈들을 import (TNS_ADMIN이 설정된 후)
import streamlit as st
import pandas as pd
import oracledb
import select_ai

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def connect_to_database():
    """Connect to Oracle database"""
    try:
        if not select_ai.is_connected():
            select_ai.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN,
                wallet_location=WALLET_DIR,
                wallet_password=WALLET_PASSWORD
            )
            print("✓ 데이터베이스 연결 성공!")
        return True, None
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False, str(e)


@st.cache_resource
def get_ai_profile(profile_name):
    """Get AI profile object (cached)"""
    try:
        return select_ai.Profile(profile_name=profile_name)
    except Exception as e:
        st.error(f"Failed to load profile: {e}")
        return None


def get_sql_for_question(question, profile_name):
    """Generate SQL from natural language question"""
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            config_dir=WALLET_DIR,
            wallet_location=WALLET_DIR,
            wallet_password=WALLET_PASSWORD
        )
        cursor = conn.cursor()
        
        # Set AI profile
        cursor.execute(f"""
            BEGIN
                DBMS_CLOUD_AI.SET_PROFILE(profile_name => '{profile_name}');
            END;
        """)
        conn.commit()
        
        # Get SQL
        cursor.execute(f"SELECT AI showsql {question}")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result[0] if result and result[0] else None
    except Exception as e:
        st.error(f"SQL generation failed: {e}")
        return None


def execute_sql(sql):
    """Execute SQL and return results as DataFrame"""
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            config_dir=WALLET_DIR,
            wallet_location=WALLET_DIR,
            wallet_password=WALLET_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        cursor.close()
        conn.close()
        
        if rows and columns:
            return pd.DataFrame(rows, columns=columns)
        return None
    except Exception as e:
        st.error(f"SQL execution failed: {e}")
        return None


# ============================================================================
# AI RESPONSE FUNCTIONS
# ============================================================================

def chat_mode(profile, question):
    """Chat mode: General conversation"""
    response = profile.chat(question)
    st.markdown(response)
    return {"content": response}


def narrate_mode(profile, question, profile_name, show_sql):
    """Narrate mode: Results + explanation with optional SQL display"""
    # Show SQL if requested
    sql = None
    if show_sql:
        with st.spinner("Generating SQL..."):
            sql = get_sql_for_question(question, profile_name)
            if sql:
                st.code(sql, language="sql")
    
    # Get narration
    with st.spinner("Getting results and explanation..."):
        response = profile.narrate(question)
        st.markdown(response)
    
    return {"content": response, "sql": sql}


def sql_only_mode(question, profile_name):
    """SQL Only mode: Just generate and show SQL"""
    with st.spinner("Generating SQL..."):
        sql = get_sql_for_question(question, profile_name)
        
        if sql:
            st.markdown("**Generated SQL:**")
            st.code(sql, language="sql")
            
            # Add execute button
            if st.button("🚀 Execute SQL"):
                with st.spinner("Executing..."):
                    df = execute_sql(sql)
                    if df is not None:
                        st.success(f"✅ {len(df)} rows returned")
                        st.dataframe(df, use_container_width=True)
            
            return {"content": "**Generated SQL:**", "sql": sql}
        else:
            st.error("Failed to generate SQL")
            return {"content": "Failed to generate SQL"}


def runsql_mode(question, profile_name, show_sql, show_table):
    """RunSQL mode: Execute query and show results"""
    with st.spinner("Generating and executing SQL..."):
        # Get SQL
        sql = get_sql_for_question(question, profile_name)
        
        if not sql:
            st.error("Failed to generate SQL")
            return {"content": "Failed to generate SQL"}
        
        # Show SQL if requested
        if show_sql:
            st.code(sql, language="sql")
        
        # Execute SQL
        df = execute_sql(sql)
        
        if df is not None:
            st.markdown(f"**Results: {len(df)} rows**")
            
            if show_table:
                st.dataframe(df, use_container_width=True)
            else:
                st.write(df)
            
            return {
                "content": f"**Results: {len(df)} rows**",
                "sql": sql,
                "dataframe": df
            }
        else:
            st.info("No results found")
            return {"content": "No results", "sql": sql}


# ============================================================================
# UI COMPONENTS
# ============================================================================

def setup_page():
    """Configure page settings"""
    st.set_page_config(
        page_title="Northwind Data Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Northwind Data Assistant")
    st.markdown("*Ask questions about your data in natural language*")


def setup_sidebar():
    """Setup sidebar with settings and options"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Connection status
        st.subheader("🔌 Database")
        
        # Ensure connection on every run
        success, error = connect_to_database()
        
        if success:
            st.success("✅ Connected")
        else:
            st.error("❌ Failed to connect")
            if error:
                st.error(error)
            st.stop()
        
        # AI Profile
        st.subheader("🎯 AI Profile")
        
        # Get available profiles from database
        try:
            profile_objects = select_ai.Profile.list()
            if profile_objects:
                # Extract profile names from profile objects
                available_profiles = [p.profile_name for p in profile_objects]
            else:
                st.warning("⚠️ No profiles found in database")
                available_profiles = ["NORTHWIND_AI"]  # fallback
            
            profile = st.selectbox(
                "Select Profile",
                available_profiles,
                help="Select an AI profile configured in your database"
            )
        except Exception as e:
            st.warning(f"⚠️ Could not fetch profiles: {e}")
            profile = st.selectbox(
                "Select Profile",
                ["NORTHWIND_AI"],
                help="Using default profile"
            )
        
        # Query Mode
        st.subheader("💬 Mode")
        mode = st.radio(
            "Query Mode",
            ["Chat", "Narrate", "SQL Only", "RunSQL"],
            index=1,
            help="Narrate mode is recommended for most queries"
        )
        
        # Display Options
        st.subheader("🔧 Display")
        show_sql = st.checkbox("Show SQL", value=True)
        show_table = st.checkbox("Show as Table", value=True)
        
        # Sample Questions
        st.subheader("💡 Examples")
        st.markdown("""
        **Try asking:**
        - 가장 비싼 제품 5개는?
        - 재고가 10개 미만인 제품은?
        - 1997년 총 매출은?
        - 고객별 주문 횟수는?
        """)
        
        # Clear history
        st.divider()
        if st.button("🔄 Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        return profile, mode, show_sql, show_table


def display_chat_history(show_sql, show_table):
    """Display previous chat messages"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                # Display SQL if available
                if show_sql and "sql" in msg and msg.get("sql"):
                    st.code(msg["sql"], language="sql")
                
                # Display DataFrame if available
                if show_table and "dataframe" in msg:
                    df = msg.get("dataframe")
                    if df is not None and isinstance(df, pd.DataFrame):
                        st.dataframe(df, use_container_width=True)
                
                # Display content
                if "content" in msg and msg.get("content"):
                    st.markdown(msg["content"])


def process_user_input(prompt, profile_name, mode, show_sql, show_table):
    """Process user question and generate response"""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response
    with st.chat_message("assistant"):
        profile = get_ai_profile(profile_name)
        if not profile:
            return
        
        try:
            # Route to appropriate mode
            if mode == "Chat":
                response_data = chat_mode(profile, prompt)
            elif mode == "Narrate":
                response_data = narrate_mode(profile, prompt, profile_name, show_sql)
            elif mode == "SQL Only":
                response_data = sql_only_mode(prompt, profile_name)
            elif mode == "RunSQL":
                response_data = runsql_mode(prompt, profile_name, show_sql, show_table)
            else:
                response_data = {"content": "Unknown mode"}
            
            # Save to history
            response_data["role"] = "assistant"
            st.session_state.messages.append(response_data)
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.exception(e)


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application logic"""
    # Setup
    setup_page()
    profile_name, mode, show_sql, show_table = setup_sidebar()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hello! Ask me anything about the Northwind database."
        })
    
    # Display chat history
    display_chat_history(show_sql, show_table)
    
    # Handle user input
    if prompt := st.chat_input("Ask a question (e.g., 가장 비싼 제품 5개는?)"):
        process_user_input(prompt, profile_name, mode, show_sql, show_table)
    
    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "<small>Powered by Oracle Select AI</small>"
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()

```

- 애플리케이션 실행
터미널에서 다음 명령어를 실행합니다.
```
streamlit run app.py
or
uv run streamlit run app.py
```

- 결과 확인
브라우저가 열리면 사이드바에 DB 접속 정보를 입력하고 Connect를 누른 뒤, 채팅창에 "가장 재고가 많은 제품은?"과 같이 질문해 봅니다.


### [4부] MCP 서버 구축 및 IDE 연동 가이드
Python 패키지 매니저인 uv와 MCP 서버 구축 프레임워크인 fastmcp를 사용하여, Oracle Autonomous AI Database의 Select AI 기능을 제공하는 MCP(Model Context Protocol) 서버를 구축하는 방법을 상세히 다룹니다. 구축된 서버는 Cursor나 VS Code와 같은 AI 기반 IDE에 연동되어, 사용가 채팅창에서 데이터베이스와 직접 대화하며 사용할 수 있는 환경을 제공합니다.

##### 1. uv 패키지 매니저 설치
  - uv란?
    - uv는 Rust로 작성된 초고속 Python 패키지 및 프로젝트 관리자입니다. 기존의 pip, poetry, virtualenv 등을 대체할 수 있으며, 의존성 해결 속도가 매우 빠르고 가상 환경 관리가 간편합니다.
  - uv 설치
    - 운영체제에 맞는 설치 명령어를 실행합니다.
      MacOS / Linux:
`curl -LsSf https://astral.sh/uv/install.sh | sh`
      Windows:
`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
    - 설치 후 터미널을 재시작하고 버전을 확인합니다.
`uv --version`

##### 2.1 프로젝트 초기화

```
# 프로젝트 디렉토리 생성
mkdir oracle-select-ai-mcp
cd oracle-select-ai-mcp
```
```
# uv 프로젝트 초기화 (가상환경 자동 생성)
uv init
```
이 명령은 .python-version, pyproject.toml, uv.lock 파일 등을 생성하여 프로젝트 환경을 구성합니다.

##### 2.2 의존성 라이브러리 추가
MCP 서버 구축과 Oracle DB 연결에 필요한 패키지를 추가합니다.

```
# fastmcp: MCP 서버를 쉽게 만드는 프레임워크
# select_ai: Oracle Select AI Python SDK
# oracledb: Oracle DB 드라이버
uv add fastmcp select_ai oracledb
uv add 명령은 패키지를 설치하고 pyproject.toml에 의존성을 자동으로 기록합니다.
```

##### 3. MCP 서버 구현 (mcp_server.py)
fastmcp를 사용하여 Select AI의 핵심 기능(자연어 질의, 피드백)을 도구(Tool)로 노출하는 서버 코드를 작성합니다.
프로젝트 루트에 mcp_server.py 파일을 생성하고 다음 코드를 작성합니다.

```python
"""
Oracle Select AI MCP Server
Simple interface to query Oracle database using natural language
"""

import os
from dotenv import load_dotenv

# ============================================================================
# CONFIGURATION - 환경 변수 사용 (보안)
# ============================================================================
# .env 파일 로드
load_dotenv()

WALLET_DIR = os.getenv("WALLET_DIR")

DB_USER = os.getenv("DB_USER", "NORTHWIND")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

DEFAULT_PROFILE = os.getenv("AI_PROFILE", "NORTHWIND_AI")

# 필수 환경 변수 체크
if not all([WALLET_DIR, DB_PASSWORD, DB_DSN, WALLET_PASSWORD]):
    raise ValueError(
        "Required environment variables not set: "
        "WALLET_DIR, DB_PASSWORD, DB_DSN, WALLET_PASSWORD"
    )

# Set TNS_ADMIN before any database operations (MUST be before select_ai import)
os.environ['TNS_ADMIN'] = WALLET_DIR

# Now import select_ai and fastmcp AFTER setting TNS_ADMIN
from fastmcp import FastMCP
import select_ai

# Create MCP server
mcp = FastMCP("Oracle Select AI")

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

def ensure_connection():
    """Ensure database is connected (reconnect if needed)"""
    try:
        if not select_ai.is_connected():
            select_ai.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN,
                wallet_location=WALLET_DIR,
                wallet_password=WALLET_PASSWORD
            )
        return True
    except Exception as e:
        import sys, traceback
        print(f"❌ Connection error: {e}", file=sys.stderr, flush=True)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
        return False


def get_profile(profile_name: str):
    """Get AI profile object"""
    try:
        return select_ai.Profile(profile_name=profile_name)
    except Exception as e:
        raise Exception(f"Failed to load profile '{profile_name}': {e}")


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
def ask_database(
    question: str,
    profile_name: str = DEFAULT_PROFILE
) -> str:
    """
    Ask a question about the Northwind database in natural language.
    Returns results with explanation.
    
    Examples:
    - "What are the top 5 most expensive products?"
    - "Show me total sales for 1997"
    - "Which employee has the most orders?"
    
    Args:
        question: Natural language question about the data
        profile_name: AI profile to use (default: NORTHWIND_AI3)
    
    Returns:
        Natural language explanation of the query results
    """
    try:
        # Ensure connected
        if not ensure_connection():
            return "Error: Could not connect to database"
        
        # Get profile and execute
        profile = get_profile(profile_name)
        response = profile.narrate(question)
        
        return response
    
    except Exception as e:
        import sys, traceback
        error_msg = f"Error: {str(e)}"
        print(f"❌ [ask_database] {error_msg}\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        return error_msg


@mcp.tool()
def generate_sql(
    question: str,
    profile_name: str = DEFAULT_PROFILE
) -> str:
    """
    Generate SQL code from natural language without executing it.
    Use this when you just want to see the SQL query.
    
    Examples:
    - "Generate SQL to find top selling products"
    - "Show me the SQL for customer orders"
    
    Args:
        question: Natural language description of what you want to query
        profile_name: AI profile to use (default: NORTHWIND_AI3)
    
    Returns:
        SQL query as a string
    """
    try:
        # Ensure connected
        if not ensure_connection():
            return "Error: Could not connect to database"
        
        # Get profile and generate SQL
        profile = get_profile(profile_name)
        sql = profile.generate(f"showsql {question}")
        
        return str(sql)
    
    except Exception as e:
        import sys, traceback
        error_msg = f"Error: {str(e)}"
        print(f"❌ [generate_sql] {error_msg}\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        return error_msg


@mcp.tool()
def chat_with_ai(
    message: str,
    profile_name: str = DEFAULT_PROFILE
) -> str:
    """
    Have a general conversation with the AI about the database.
    Use this for questions about the database schema, concepts, or general help.
    
    Examples:
    - "What tables are in the Northwind database?"
    - "What is the Northwind database about?"
    - "How do I find customer information?"
    
    Args:
        message: Your question or message
        profile_name: AI profile to use (default: NORTHWIND_AI3)
    
    Returns:
        AI's response
    """
    try:
        # Ensure connected
        if not ensure_connection():
            return "Error: Could not connect to database"
        
        # Get profile and chat
        profile = get_profile(profile_name)
        response = profile.chat(message)
        
        return response
    
    except Exception as e:
        import sys, traceback
        error_msg = f"Error: {str(e)}"
        print(f"❌ [chat_with_ai] {error_msg}\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        return error_msg




# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    # Start MCP server
    # This will be called by Cursor/Claude Desktop
    import sys
    print("="*80, file=sys.stderr, flush=True)
    print("Starting Oracle Select AI MCP Server...", file=sys.stderr, flush=True)
    print(f"✓ .env file loaded from: {os.getcwd()}", file=sys.stderr, flush=True)
    print(f"✓ Wallet directory: {WALLET_DIR}", file=sys.stderr, flush=True)
    print(f"✓ Database DSN: {DB_DSN}", file=sys.stderr, flush=True)
    print(f"✓ Database user: {DB_USER}", file=sys.stderr, flush=True)
    print(f"✓ Default AI profile: {DEFAULT_PROFILE}", file=sys.stderr, flush=True)
    print(f"✓ Available tools: ask_database, generate_sql, chat_with_ai", file=sys.stderr, flush=True)
    print("="*80, file=sys.stderr, flush=True)
    
    mcp.run()

```

#### 4. 환경 변수 설정
MCP 서버 실행 전에 필요한 환경 변수를 설정합니다.
.env 설정이 되어있으면 추가로 할 필요는 없습니다.

#### 5. IDE 연동 설정
구축한 MCP 서버를 IDE에 등록하여 AI 어시스턴트가 이 도구를 인식하고 사용할 수 있게 합니다.

##### 5.1 Cursor 연동 (MCP 설정 파일)
Cursor는 설정 파일을 통해 MCP 서버를 등록합니다.

**설정 파일 위치:**
Mac: Cmd + , (커맨드 + 쉼표)
Windows: Ctrl + ,

**설정 파일 내용 (`mcp.json`):** 설정 화면에서 Cmd(Ctrl) + shift + P 입력 후 MCP tool 추가를 선택하고 아래 내요을 입력(directory는 각자 상황에 맞춰야 합니다.)

```json
{
  "mcpServers": {
    "oracle-select-ai": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/joungminko/devkit/fy26_ai_internal_training/1회차/adb_select_ai",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

**주의사항:**
- `--directory`: MCP 서버 프로젝트의 절대 경로 (pyproject.toml이 있는 디렉토리)
- `env`: 환경 변수를 직접 설정 (선택사항, .env 파일이 있다면 생략 가능)
- `uv` 경로 확인: 터미널에서 `which uv` (Mac/Linux) 또는 `where.exe uv` (Windows) 실행

**Cursor 재시작:**
설정 파일을 저장한 후 Cursor를 완전히 종료하고 다시 시작합니다.

Cursor에서 MCP 서버 리로드 방법:
커맨드 팔레트 열기 (Cmd+Shift+P)
"MCP: Restart Servers" 또는 "Developer: Reload Window" 입력

#### 6. MCP 서버 등록 및 통신 방식

##### 6.1 MCP Tool 등록 방법

MCP(Model Context Protocol) 서버를 Cursor에 등록하려면 설정 파일을 생성해야 합니다.

**설정 파일 구조 설명:**
- `mcpServers`: MCP 서버들의 컨테이너 객체
- `oracle-select-ai`: 서버 식별자 (임의로 지정 가능)
- `command`: 실행할 명령어 (uv, python, node 등)
- `args`: 명령어에 전달할 인자 배열
  - `--directory`: 프로젝트 디렉토리 (절대 경로)
  - `run`: uv의 실행 명령
  - `mcp_server.py`: 실행할 파일명

**주의사항:**
1. `--directory`는 **절대 경로**로 지정해야 합니다
2. 해당 디렉토리에 `.env` 파일이 있어야 합니다 (환경 변수 로드용)
3. `pyproject.toml`이 있는 디렉토리를 지정해야 합니다
4. 설정 변경 후 Cursor를 재시작하거나 MCP 서버를 리로드해야 합니다

**MCP 서버 리로드:**
- `Cmd+Shift+P` (Mac) 또는 `Ctrl+Shift+P` (Windows)
- "MCP: Restart Servers" 입력 및 실행

##### 6.2 STDIO 통신 방식

MCP는 **STDIO(Standard Input/Output)** 방식으로 통신합니다. 이는 프로세스 간 통신(IPC)의 가장 간단한 형태입니다.

**통신 구조:**
```
┌─────────────┐         STDIN          ┌─────────────┐
│             │  ─────────────────────> │             │
│   Cursor    │    JSON-RPC 요청        │ MCP Server  │
│    IDE      │                         │  (Python)   │
│             │  <───────────────────── │             │
└─────────────┘         STDOUT         └─────────────┘
                      JSON-RPC 응답
```

**작동 원리:**

1. **Cursor → MCP Server (STDIN):**
   - Cursor가 JSON-RPC 형식의 요청을 MCP 서버의 **표준 입력(stdin)**으로 전송
   - 예: `{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "ask_database", "arguments": {"question": "..."}}}`

2. **MCP Server → Cursor (STDOUT):**
   - MCP 서버가 JSON-RPC 형식의 응답을 **표준 출력(stdout)**으로 반환
   - 예: `{"jsonrpc": "2.0", "result": "재고가 가장 많은 제품은..."}`

3. **에러 로그 (STDERR):**
   - 디버깅 메시지나 에러는 **표준 에러(stderr)**로 출력
   - stdout은 JSON-RPC 통신 전용으로 유지해야 함

**중요한 규칙:**
- ✅ **STDOUT**: JSON-RPC 메시지만 출력 (프로토콜 통신용)
- ✅ **STDERR**: 디버그 로그, 에러 메시지 출력 (개발자용)
- ❌ **STDOUT에 일반 텍스트 출력 금지**: JSON 파싱 오류 발생

**올바른 로깅 예시:**
```python
import sys

# ✅ 올바른 방법: stderr 사용
print("Debug: Connecting to database...", file=sys.stderr, flush=True)

# ❌ 잘못된 방법: stdout 사용 (JSON-RPC 깨짐)
print("Debug: Connecting to database...")
```

##### 6.4 로컬 테스트

IDE 연동 전에 로컬에서 MCP 서버를 테스트할 수 있습니다:

```bash
# 프로젝트 디렉토리로 이동
cd /Users/joungminko/devkit/fy26_ai_internal_training/1회차/adb_select_ai

# MCP 서버 실행
uv run mcp_server.py
```

**예상 출력 (STDERR):**
```
================================================================================
Starting Oracle Select AI MCP Server...
✓ Database: jtc0w11kmdnyykbj_low
✓ Profile: NORTHWIND_AI
================================================================================

                        ▄▀▀ ▄▀█ █▀▀ ▀█▀ █▀▄▀█ █▀▀ █▀█
                        █▀  █▀█ ▄▄█  █  █ ▀ █ █▄▄ █▀▀

                             FastMCP 2.13.3

                 🖥  Server name: Oracle Select AI
                 📦 Transport:   STDIO
```

서버가 정상 실행되면 stdin에서 JSON-RPC 메시지를 대기합니다. `Ctrl+C`로 종료할 수 있습니다.

MCP tool을 서버처럼 직접 실행해서 사용하는 구조는 아니고, Cursor와 같은 MCP 클라이언트 환경이 MCP manifest(tool 선언 정보)를 기반으로 tool discovery를 먼저 수행한 뒤, tool에 정의된 정보를 기반으로 사용자의 요청에 따라 필요하다고 판단한 시점에 stdio 기반 JSON-RPC 포맷의 메시지로 해당 tool을 invoke(호출) 하는 구조입니다.
이때 모든 요청과 응답은 jsonrpc, id, method, params, result 필드를 가지는 표준 JSON-RPC 2.0 포맷으로 stdin/stdout을 통해 로컬 프로세스 간에 직접 전달됩니다.
MCP 클라이언트가 선언정보에 따라 직접 호출함으로 미리 실행하지 않아도 됩니다.

##### 6.5 IDE 채팅창에서 사용

**시나리오 1: 데이터 조회 (ask_database)**
```
사용자:
"Northwind 데이터베이스에서 재고가 가장 많은 제품 5개를 알려줘"

AI (내부 동작):
- MCP Tool 호출: ask_database("재고가 가장 많은 제품 5개")
- DB 쿼리 실행 및 결과 반환

AI 응답:
"재고가 가장 많은 제품 5개는 다음과 같습니다:

1. Grandma's Boysenberry Spread - 120개
2. Organic Apples - 100개
3. Chef Anton's Cajun Seasoning - 53개
4. Chai - 39개
5. Ikura - 31개"
```

**시나리오 2: SQL 생성 (generate_sql)**
```
사용자:
"1996년 7월에 주문한 고객들의 총 주문 금액을 계산하는 SQL을 만들어줘"

AI (내부 동작):
- MCP Tool 호출: generate_sql("1996년 7월 총 주문 금액")
- SQL 생성 (실행하지 않음)

AI 응답:
"다음 SQL 쿼리를 사용하시면 됩니다:

SELECT 
    c.COMPANY_NAME,
    COUNT(o.ORDER_ID) as ORDER_COUNT,
    SUM(od.UNIT_PRICE * od.QUANTITY * (1 - od.DISCOUNT)) as TOTAL_AMOUNT
FROM CUSTOMERS c
JOIN ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
JOIN ORDER_DETAILS od ON o.ORDER_ID = od.ORDER_ID
WHERE o.ORDER_DATE >= TO_DATE('1996-07-01', 'YYYY-MM-DD')
  AND o.ORDER_DATE < TO_DATE('1996-08-01', 'YYYY-MM-DD')
GROUP BY c.COMPANY_NAME
ORDER BY TOTAL_AMOUNT DESC;"
```

**시나리오 3: 데이터베이스 구조 질문 (chat_with_ai)**
```
사용자:
"Northwind 데이터베이스의 주요 테이블 구조를 설명해줘"

AI (내부 동작):
- MCP Tool 호출: chat_with_ai("주요 테이블 구조 설명")
- LLM과 대화 (DB 조회 없음)

AI 응답:
"Northwind 데이터베이스는 다음 5개의 주요 테이블로 구성되어 있습니다:

1. CATEGORIES: 제품 카테고리 정보 (음료, 조미료, 유제품 등)
2. CUSTOMERS: 고객 정보 (회사명, 연락처, 주소)
3. PRODUCTS: 제품 정보 (가격, 재고, 카테고리)
4. ORDERS: 주문 헤더 (주문일, 배송정보)
5. ORDER_DETAILS: 주문 상세 (제품별 수량, 가격, 할인)

주문은 ORDERS와 ORDER_DETAILS로 분리되어 있으며,
외래키로 연결되어 정규화된 구조를 갖추고 있습니다."
```
