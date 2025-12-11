# Oracle Autonomous AI Database: Select AI 심화 - Sidecar & Heterogeneous(이기종) Database Connectivity 핸즈온 가이드

## 목차
1. [Select AI 아키텍처와 "Sidecar" 모델](#1-select-ai-아키텍처와-sidecar-모델)
2. [메타데이터 보강을 통한 정확도 향상](#2-메타데이터-보강을-통한-정확도-향상)
3. [엔터프라이즈 통합 및 확장](#3-엔터프라이즈-통합-및-확장)

---

## 시작하기 전에

### 사전 준비 사항
- Oracle Autonomous AI Database 인스턴스 (Always Free 또는 유료)
- SQL Developer, SQL*Plus, 또는 Database Actions 접속 환경
- OCI (Oracle Cloud Infrastructure) 계정 및 API Keys
- 선택사항: 외부 데이터베이스 (PostgreSQL, MySQL 등) 접속 정보

---

## 1. Select AI 아키텍처와 "Sidecar" 모델

### 1.1 Sidecar(사이드카) 개념 및 필요성

**비즈니스 문제:** 기존에 여러 디비로 나눠저 있어 데이터에 대한 통합 접근이나 AI 활용을 위해 매번 ETL이나 데이터 요청이나 해야 하는 번거로움이 있었습니다.

**해결책:** Select AI는 **"AI Sidecar"** 모델을 통해 흩어져 있는 데이터 베이스를 통합하여 AI에 활용하도록 도와줍니다.

#### Sidecar 모델이란?
마치 오토바이 옆에 붙어있는 사이드카처럼, 여러 데이터 소스를 ETL 없이 ADB에 붙여 AI 기능을 제공하는 논리 개념입니다.

**핵심 개념:**
* **개념:** Select AI Sidecar는 기존 데이터베이스와 함께 작동하는 Oracle Autonomous AI Database(ADB) 인스턴스를 사용하여 SQL 변환 및 연합 쿼리(Federated Query)를 실행 합니다.
* **역할:** 사용자의 자연어 질문을 해석하고, 연결된 여러 데이터 소스(온프레미스, 멀티 클라우드 등)에 대한 쿼리를 대신 수행합니다.
* **보안:** 완전히 관리되는 AI Sidecar 데이터베이스로 배포되어, 데이터 거버넌스를 위한 모든 데이터베이스 보안 기능(권한, 행 수준 보안, RAS)을 적용합니다.
* **이점:** 복잡한 ETL 프로세스나 데이터 이동 없이, 비즈니스 사용자가 SQL 기술 없이도 자연어 질문을 통해 인사이트를 얻을 수 있습니다.

### 1.2 연합 쿼리 (Federated Queries)

Select AI의 가장 강력한 기능 중 하나는 **여러 데이터베이스에 흩어진 데이터를 마치 하나의 데이터베이스처럼 조회**할 수 있다는 점입니다.

#### 작동 원리
* **작동 방식:** 예를 들어, "Acme Corp의 보류 중인 주문 보여줘"라는 질문에 대해 Google Cloud의 BigQuery에 있는 고객 데이터와 AWS Redshift의 주문 데이터를 조인하여 결과를 가져올 수 있습니다.
* **자동화:** Select AI는 조인, 데이터 위치 파악, 쿼리 최적화의 복잡성을 처리하므로 사용자는 데이터의 위치를 알 필요가 없습니다.

#### 지원 데이터 소스 (Oracle-Managed Heterogeneous Connectivity)

Select AI는 다음과 같은 다양한 데이터 소스를 지원합니다:

| 데이터베이스 타입 | db_type 값 | 기본 포트 |
|-----------------|-----------|---------|
| **Amazon Redshift** | awsredshift | 5439 |
| **Azure SQL / Synapse** | azure | 1433 |
| **Apache Cassandra** | cassandra | 9042 |
| **IBM Db2** | db2 | 25000/50000 |
| **Google Analytics** | google_analytics | 443 |
| **Google BigQuery** | google_bigquery | 443 |
| **Google Drive** | google_drive | 443 |
| **Apache Hive** | hive | 443 |
| **MongoDB** | mongodb | 27017 |
| **MySQL** | mysql | 3306 |
| **MySQL Community** | mysql_community | 3306 |
| **PostgreSQL** | postgres | 5432 |
| **Salesforce** | salesforce | 19937 |
| **ServiceNow** | servicenow | 443 |
| **Microsoft SharePoint** | sharepoint | 443 |
| **Snowflake** | snowflake | 443 |
| **YouTube** | youtube | 443 |

**중요 사항:**
- 모든 연결은 **읽기 전용(Query-only)** - UPDATE/INSERT/DELETE 불가
- Public endpoint는 SSL/TLS 필수
- Private endpoint는 TCP 프로토콜 사용 (SSL 선택사항)

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
-- NORTHWIND 사용자로 실행:
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

## 2. 메타데이터 보강을 통한 정확도 향상

### 2.1 LLM의 환각 방지와 Comments의 역할

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

---

## 3. 엔터프라이즈 통합 및 확장

### 3.1 MySQL Database 연결 핸즈온

#### 3.1.1 MySQL 연결 개요

**사용 사례:**
- 레거시 애플리케이션이 MySQL에 데이터 저장
- Oracle ADB로 마이그레이션 없이 자연어로 데이터 조회
- MySQL과 ADB의 데이터를 연합 쿼리로 통합 분석

---

#### 3.1.2 사전 준비: MySQL 서버 설정

이 섹션의 SQL 스크립트는 MySQL community Edition에서 작동합니다.

**MySQL 인스턴스 준비 (AWS RDS MySQL 또는 로컬 MySQL)**

```sql
-- Step 1: 데이터베이스 생성
CREATE DATABASE ecommerce_poc;
USE ecommerce_poc;

-- Step 2: 테이블 생성 (COMMENT 추가 - Select AI 정확도 향상!)

-- 1. Customers Table
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique identifier for the customer',
    full_name VARCHAR(100) NOT NULL COMMENT 'The first and last name of the customer',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT 'Customer email address used for login and notifications',
    signup_date DATE DEFAULT (CURRENT_DATE) COMMENT 'The date when the customer first registered',
    region VARCHAR(50) COMMENT 'Geographic region of the customer (e.g., NA, EMEA, APAC)'
) COMMENT='Stores customer profiles and demographic information';

-- 2. Products Table
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique identifier for the product',
    product_name VARCHAR(150) NOT NULL COMMENT 'Commercial name of the product',
    category VARCHAR(50) COMMENT 'Product category: Electronics, Clothing, Home, or Sports',
    price DECIMAL(10, 2) NOT NULL COMMENT 'Unit price of the product in USD',
    stock_quantity INT DEFAULT 0 COMMENT 'Current inventory level. If 0, product is out of stock'
) COMMENT='Catalog of available items for sale with pricing and inventory status';

-- 3. Orders Table
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique identifier for the order transaction',
    customer_id INT NOT NULL COMMENT 'Foreign key to the customers table',
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the order was placed',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT 'Total value of the order in USD including tax',
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'Order status: PENDING, SHIPPED, DELIVERED, or CANCELLED',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) COMMENT='Transaction history headers. Use this to calculate revenue or sales volume';

-- Step 3: 샘플 데이터 입력

-- Insert Customers
INSERT INTO customers (full_name, email, region, signup_date) VALUES 
('John Doe', 'john.doe@example.com', 'NA', '2023-01-15'),
('Jane Smith', 'jane.smith@example.com', 'EMEA', '2023-02-20'),
('Alice Kim', 'alice.kim@example.com', 'APAC', '2023-03-10'),
('Bob Johnson', 'bob.j@example.com', 'NA', '2023-05-05'),
('Charlie Lee', 'charlie.lee@example.com', 'APAC', '2023-06-15');

-- Insert Products
INSERT INTO products (product_name, category, price, stock_quantity) VALUES 
('Smartphone X', 'Electronics', 999.00, 50),
('Laptop Pro', 'Electronics', 1299.00, 30),
('Running Shoes', 'Clothing', 89.99, 100),
('Coffee Maker', 'Home', 45.50, 20),
('Yoga Mat', 'Sports', 25.00, 200),
('Gaming Mouse', 'Electronics', 59.99, 75);

-- Insert Orders
INSERT INTO orders (customer_id, total_amount, status, order_date) VALUES 
(1, 1088.99, 'DELIVERED', '2023-07-01 10:00:00'), -- John bought items
(2, 1299.00, 'SHIPPED', '2023-07-02 14:30:00'),   -- Jane bought Laptop
(3, 59.99, 'PENDING', '2023-07-03 09:15:00'),     -- Alice bought Mouse
(1, 25.00, 'DELIVERED', '2023-07-05 11:00:00'),   -- John bought Yoga Mat
(4, 45.50, 'CANCELLED', '2023-07-06 16:20:00'),   -- Bob cancelled
(3, 1299.00, 'DELIVERED', '2023-07-10 08:45:00'); -- Alice bought Laptop

```

---

**MySQL 네트워크 설정**

**AWS RDS MySQL 사용 시:**
1. **보안 그룹 설정**
   - Inbound Rules에 ADB의 Public IP 추가
   - Port: 3306
   - Source: ADB NAT Gateway IP 또는 0.0.0.0/0 (테스트용)

2. **Public 접근 활성화**
   - RDS 인스턴스의 "Publicly accessible" 옵션 활성화
   - 엔드포인트 확인: `your-instance.xxxxx.us-east-1.rds.amazonaws.com`

#### 3.1.3 ADB에서 MySQL 연결 설정

**Step 1: MySQL JDBC Driver 확인**

Oracle Autonomous AI Database는 MySQL JDBC 드라이버를 내장하고 있습니다. 별도 설치 불필요.

**Step 2: 사용자 권한 부여 (ADMIN 권한 필요)**

ADMIN이 아닌 사용자(예: NORTHWIND)가 MySQL Database Link를 생성하려면 다음 권한이 필요합니다:

```sql
-- ADMIN 권한으로 실행:

-- 1. Database Link 생성 권한
GRANT CREATE DATABASE LINK TO NORTHWIND;

-- 2. DBMS_CLOUD_ADMIN 패키지 실행 권한 (Database Link 생성에 필요)
GRANT EXECUTE ON DBMS_CLOUD_ADMIN TO NORTHWIND;

```

**💡 왜 이 권한들이 필요한가?**

1. **CREATE DATABASE LINK**
   - Database Link 객체를 생성할 수 있는 시스템 권한
   - 없으면 `ORA-01031: insufficient privileges` 오류 발생

2. **EXECUTE ON DBMS_CLOUD_ADMIN**
   - `DBMS_CLOUD_ADMIN.CREATE_DATABASE_LINK` 프로시저 실행 권한
   - Autonomous Database에서 외부 데이터베이스 연결에 필요
   - 없으면 `PLS-00201: identifier 'DBMS_CLOUD_ADMIN' must be declared` 오류 발생

**Step 3: MySQL 연결 Credential 생성**

```sql
-- NORTHWIND 사용자로 실행:
-- MySQL 접속 정보를 저장하는 Credential 생성
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'AWS_RDS_CRED',
    username        => 'admin',          -- Your AWS Master Username
    password        => '' -- Your AWS Master Password
  );
END;
/

```

**Step 4: Database Link 생성**

```sql
-- NORTHWIND 사용자로 실행:
-- MySQL 데이터베이스로의 Database Link 생성
BEGIN
  DBMS_CLOUD_ADMIN.CREATE_DATABASE_LINK(
    db_link_name => 'RDS_LINK',
    hostname     => 'database-1.czaaygccsncp.ap-northeast-2.rds.amazonaws.com',
    port         => 3306,
    service_name => '',
    credential_name => 'AWS_RDS_CRED',
    gateway_params  => JSON_OBJECT('db_type' value 'mysql_community')
  );
END;
/

```

**Step 5: 연결 테스트**

```sql
-- NORTHWIND 사용자로 실행:
-- 1. Customers 테이블 조회
SELECT * FROM "ecommerce_poc"."customers"@RDS_LINK
WHERE ROWNUM <= 5;

CREATE OR REPLACE VIEW view_rds_customers AS SELECT * FROM "ecommerce_poc"."customers"@RDS_LINK;
CREATE OR REPLACE VIEW view_rds_orders AS SELECT * FROM "ecommerce_poc"."orders"@RDS_LINK;
CREATE OR REPLACE VIEW view_rds_products AS SELECT * FROM "ecommerce_poc"."products"@RDS_LINK;

COMMENT ON TABLE view_rds_customers IS 'Stores customer profiles and demographic information';
COMMENT ON COLUMN view_rds_customers."region" IS 'Geographic region of the customer (e.g., NA, EMEA, APAC)';

```

#### 3.1.4 Select AI 프로파일 생성 (MySQL 포함)

**선택사항: ADB의 로컬 테이블 준비 (연합 쿼리 테스트용)**

MySQL에 이미 customers 테이블이 있지만, 연합 쿼리 데모를 위해 ADB에 추가 정보를 저장할 수 있습니다.

```sql
-- NORTHWIND 사용자로 실행:
-- ADB에 고객 등급 정보 테이블 생성 (Oracle에 저장)
CREATE TABLE customer_tiers (
  customer_id NUMBER PRIMARY KEY,
  tier_level VARCHAR2(20),  -- Gold, Silver, Bronze
  loyalty_points NUMBER,
  member_since DATE
);

-- 주석 추가 (Select AI 정확도 향상)
COMMENT ON TABLE customer_tiers IS 
'Customer loyalty tier information managed in Oracle ADB';

COMMENT ON COLUMN customer_tiers.tier_level IS 
'Loyalty tier: Gold (premium), Silver (regular), Bronze (new)';

COMMENT ON COLUMN customer_tiers.loyalty_points IS 
'Accumulated loyalty points for rewards program';

-- 샘플 데이터 (MySQL의 customer_id와 매칭)
INSERT INTO customer_tiers VALUES (1, 'Gold', 5000, DATE '2023-01-15');
INSERT INTO customer_tiers VALUES (2, 'Silver', 2500, DATE '2023-02-20');
INSERT INTO customer_tiers VALUES (3, 'Gold', 4500, DATE '2023-03-10');
INSERT INTO customer_tiers VALUES (4, 'Bronze', 500, DATE '2023-05-05');
INSERT INTO customer_tiers VALUES (5, 'Silver', 3000, DATE '2023-06-15');
COMMIT;

-- 데이터 확인
SELECT * FROM customer_tiers;
```

**MySQL 테이블을 포함한 AI 프로파일 생성**

```sql
-- NORTHWIND 사용자로 실행:
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
      profile_name => 'AWS_RDS_AI_PROFILE',
      attributes   => '{"provider": "oci", 
                        "model": "meta.llama-4-maverick-17b-128e-instruct-fp8",
                        "credential_name": "OCI_KEY_CRED",
                        "object_list": [
                            {"owner": "NORTHWIND", "name": "view_rds_customers"},
                            {"owner": "NORTHWIND", "name": "view_rds_orders"},
                            {"owner": "NORTHWIND", "name": "view_rds_products"},
                            {"owner": "NORTHWIND", "name": "customer_tiers"}
                        ]}'
  );
END;
  
  -- 프로파일 활성화
EXEC DBMS_CLOUD_AI.SET_PROFILE('AWS_RDS_AI_PROFILE');
/

```

**💡 중요: MySQL COMMENT 자동 활용**

MySQL에서 설정한 COMMENT는 Database Link를 통해 Select AI가 자동으로 읽어옵니다:
- ✅ `comments => 'true'` 설정만 하면 됨
- ✅ MySQL의 테이블/컬럼 COMMENT가 LLM 프롬프트에 포함됨
- ✅ 추가 설정 불필요!

**확인:**
```sql
-- NORTHWIND 사용자로 실행:
-- MySQL COMMENT가 잘 전달되는지 확인
EXEC DBMS_CLOUD_AI.SET_PROFILE('AWS_RDS_AI_PROFILE');
select ai 'orders 테이블의 status 컬럼에 가능한 값들은?';

```

#### 3.1.5 연합 쿼리 실습

**질문 1: MySQL 테이블만 조회 (SELECT AI 사용)**

```sql
-- NORTHWIND 사용자로 실행:
-- 재고 확인
EXEC DBMS_CLOUD_AI.SET_PROFILE('AWS_RDS_AI_PROFILE');
SELECT AI '재고가 50개 이하인 제품을 보여줘';
```

**질문 3: Oracle + MySQL 연합 쿼리 (customer_tiers 포함)**

```sql
-- NORTHWIND 사용자로 실행:
-- Gold 등급 고객의 주문 분석

EXEC DBMS_CLOUD_AI.SET_PROFILE('AWS_RDS_AI_PROFILE');
SELECT AI 'Gold 등급 고객들의 총 주문 금액은?';

```

**질문 5: 시계열 분석**

```sql
-- NORTHWIND 사용자로 실행:
-- 월별 매출 추이
SELECT AI 월별 총 매출액을 보여줘;

-- 고객 가입 추이
SELECT AI 월별 신규 가입 고객 수는?;
```

#### 3.1.6 성능 최적화

**원격 테이블 캐싱**

```sql
-- NORTHWIND 사용자로 실행:
-- 자주 조회되는 MySQL 테이블을 ADB에 캐시
CREATE MATERIALIZED VIEW products_cache
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT * FROM "ecommerce_poc"."products"@RDS_LINK;

-- 캐시된 뷰를 프로파일에 추가

BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
      profile_name => 'MYSQL_OPTIMIZED_PROFILE',
      attributes   => '{"provider": "oci", 
                        "model": "meta.llama-4-maverick-17b-128e-instruct-fp8",
                        "credential_name": "OCI_KEY_CRED",
                        "object_list": [
                            {"owner": "NORTHWIND", "name": "view_rds_customers"},
                            {"owner": "NORTHWIND", "name": "view_rds_orders"},
                            {"owner": "NORTHWIND", "name": "products_cache"},
                            {"owner": "NORTHWIND", "name": "customer_tiers"}
                        ]}'
  );
END;
  
/

-- 정기적으로 캐시 갱신
BEGIN
  DBMS_MVIEW.REFRESH('PRODUCTS_CACHE');
END;
/
```

---

### 3.2 PostgreSQL Database 연결 (MySQL Community Edition 대안) ✅

#### 3.2.1 PostgreSQL을 사용하는 이유

**🎯 이 섹션의 목표:**
- AWS RDS PostgreSQL 인스턴스 설정
- Oracle ADB에서 PostgreSQL Database Link 생성
- View를 통한 Select AI 통합
- 자연어 쿼리로 PostgreSQL 데이터 분석

---

#### 3.2.2 PostgreSQL 데이터베이스 준비

**AWS RDS PostgreSQL 인스턴스 생성**

```sql
-- PostgreSQL에 접속하여 데이터베이스 및 테이블 생성

-- 1. Customers Table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    signup_date DATE DEFAULT CURRENT_DATE,
    region VARCHAR(50)
);

-- PostgreSQL COMMENT 추가
COMMENT ON TABLE customers IS 
'Stores customer profiles and demographic information';
COMMENT ON COLUMN customers.customer_id IS 
'Unique identifier for the customer';
COMMENT ON COLUMN customers.full_name IS 
'The first and last name of the customer';
COMMENT ON COLUMN customers.email IS 
'Customer email address used for login and notifications';
COMMENT ON COLUMN customers.region IS 
'Geographic region of the customer (e.g., NA, EMEA, APAC)';

-- 2. Products Table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0
);

COMMENT ON TABLE products IS 
'Catalog of available items for sale with pricing and inventory status';
COMMENT ON COLUMN products.product_id IS 
'Unique identifier for the product';
COMMENT ON COLUMN products.price IS 
'Unit price of the product in USD';
COMMENT ON COLUMN products.stock_quantity IS 
'Current inventory level. If 0, product is out of stock';

-- 3. Orders Table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

COMMENT ON TABLE orders IS 
'Transaction history headers. Use this to calculate revenue or sales volume';
COMMENT ON COLUMN orders.total_amount IS 
'Total value of the order in USD including tax';
COMMENT ON COLUMN orders.status IS 
'Order status: PENDING, SHIPPED, DELIVERED, or CANCELLED';

-- Step 3: 샘플 데이터 입력

-- Insert Customers
INSERT INTO customers (full_name, email, region, signup_date) VALUES 
('John Doe', 'john.doe@example.com', 'NA', '2023-01-15'),
('Jane Smith', 'jane.smith@example.com', 'EMEA', '2023-02-20'),
('Alice Kim', 'alice.kim@example.com', 'APAC', '2023-03-10'),
('Bob Johnson', 'bob.j@example.com', 'NA', '2023-05-05'),
('Charlie Lee', 'charlie.lee@example.com', 'APAC', '2023-06-15');

-- Insert Products
INSERT INTO products (product_name, category, price, stock_quantity) VALUES 
('Smartphone X', 'Electronics', 999.00, 50),
('Laptop Pro', 'Electronics', 1299.00, 30),
('Running Shoes', 'Clothing', 89.99, 100),
('Coffee Maker', 'Home', 45.50, 20),
('Yoga Mat', 'Sports', 25.00, 200),
('Gaming Mouse', 'Electronics', 59.99, 75);

-- Insert Orders
INSERT INTO orders (customer_id, total_amount, status, order_date) VALUES 
(1, 1088.99, 'DELIVERED', '2023-07-01 10:00:00'),
(2, 1299.00, 'SHIPPED', '2023-07-02 14:30:00'),
(3, 59.99, 'PENDING', '2023-07-03 09:15:00'),
(1, 25.00, 'DELIVERED', '2023-07-05 11:00:00'),
(4, 45.50, 'CANCELLED', '2023-07-06 16:20:00'),
(5, 1299.00, 'DELIVERED', '2023-07-10 08:45:00');

-- Step 4: 데이터 확인
SELECT COUNT(*) as customer_count FROM customers;
SELECT COUNT(*) as product_count FROM products;
SELECT COUNT(*) as order_count FROM orders;

-- Step 5: 원격 접속을 위한 사용자 권한 (기본적으로 postgres 사용자 사용)
-- 이미 마스터 사용자(postgres)가 있으므로 추가 설정 불필요
-- 단, pg_hba.conf에서 외부 IP 접근 허용 필요 (AWS RDS는 보안그룹으로 관리)
```

**AWS RDS PostgreSQL 보안 그룹 설정**

AWS Console에서:
1. **RDS > Databases > 보안 그룹**
2. **Inbound Rules 추가:**
   - Type: PostgreSQL
   - Protocol: TCP
   - Port: 5432
   - Source: ADB NAT Gateway IP 또는 0.0.0.0/0 (테스트용)

---

#### 3.2.3 ADB에서 PostgreSQL 연결 설정

**Step 1: 사용자 권한 부여 (ADMIN 권한 필요)**

```sql
-- ADMIN 권한으로 실행:
GRANT CREATE DATABASE LINK TO NORTHWIND;
GRANT EXECUTE ON DBMS_CLOUD_ADMIN TO NORTHWIND;

```

**Step 2: PostgreSQL Credential 생성**

```sql
-- NORTHWIND 사용자로 실행:
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'AWS_RDS_POSTGRES_CRED',
    username        => 'postgres',          -- AWS RDS Master Username
    password        => ''   -- AWS RDS Master Password
  );
END;
/

```

**Step 3: PostgreSQL Database Link 생성**

```sql
-- NORTHWIND 사용자로 실행:
BEGIN
  DBMS_CLOUD_ADMIN.CREATE_DATABASE_LINK(
    db_link_name       => 'RDS_POSTGRES_LINK',
    hostname           => 'database-2.czaaygccsncp.ap-northeast-2.rds.amazonaws.com', -- Your RDS Endpoint
    port               => '5432',                -- PostgreSQL Default Port
    service_name       => 'postgres',            -- The PostgreSQL Database Name
    credential_name    => 'AWS_RDS_POSTGRES_CRED',
    ssl_server_cert_dn => NULL,                  -- Usually NULL for standard RDS
    private_target     => FALSE,
    gateway_params     => JSON_OBJECT('db_type' value 'POSTGRES')
  );
END;
/

```

**Step 4: 연결 테스트 (⚠️ 중요: 대소문자 이슈!)**

```sql
-- NORTHWIND 사용자로 실행:
SELECT * FROM "public"."customers"@RDS_POSTGRES_LINK;

-- 데이터 개수 확인
SELECT COUNT(*) FROM "public"."customers"@RDS_POSTGRES_LINK; 
SELECT COUNT(*) FROM "public"."products"@RDS_POSTGRES_LINK;  
SELECT COUNT(*) FROM "public"."orders"@RDS_POSTGRES_LINK;    
```

---

#### 3.2.4 View 생성

**Step 1: Local View 생성**

```sql
-- NORTHWIND 사용자로 실행:
-- 1. Customers View
CREATE OR REPLACE VIEW view_customers AS 
SELECT * FROM "public"."customers"@RDS_POSTGRES_LINK;

-- 2. Products View
CREATE OR REPLACE VIEW view_products AS 
SELECT * FROM "public"."products"@RDS_POSTGRES_LINK;

-- 3. Orders View
CREATE OR REPLACE VIEW view_orders AS 
SELECT * FROM "public"."orders"@RDS_POSTGRES_LINK;

```

**Step 2: Local View에 COMMENT 추가 (Select AI에 필수!)**

```sql
-- NORTHWIND 사용자로 실행:
-- Customers View 주석
COMMENT ON TABLE view_customers IS 
'Stores customer profiles and demographic information';
COMMENT ON COLUMN view_customers.customer_id IS 
'Unique identifier for the customer';
COMMENT ON COLUMN view_customers.full_name IS 
'The first and last name of the customer';
COMMENT ON COLUMN view_customers.email IS 
'Customer email address used for login and notifications';
COMMENT ON COLUMN view_customers.region IS 
'Geographic region of the customer (e.g., NA, EMEA, APAC)';

-- Products View 주석
COMMENT ON TABLE view_products IS 
'Catalog of available items for sale with pricing and inventory status';
COMMENT ON COLUMN view_products.product_id IS 
'Unique identifier for the product';
COMMENT ON COLUMN view_products.product_name IS 
'Commercial name of the product';
COMMENT ON COLUMN view_products.category IS 
'Product category: Electronics, Clothing, Home, or Sports';
COMMENT ON COLUMN view_products.price IS 
'Unit price of the product in USD';
COMMENT ON COLUMN view_products.stock_quantity IS 
'Current inventory level. If 0, product is out of stock';

-- Orders View 주석
COMMENT ON TABLE view_orders IS 
'Transaction history headers. Use this to calculate revenue or sales volume';
COMMENT ON COLUMN view_orders.order_id IS 
'Unique identifier for the order transaction';
COMMENT ON COLUMN view_orders.customer_id IS 
'Foreign key to the customers table';
COMMENT ON COLUMN view_orders.order_date IS 
'Timestamp when the order was placed';
COMMENT ON COLUMN view_orders.total_amount IS 
'Total value of the order in USD including tax';
COMMENT ON COLUMN view_orders.status IS 
'Order status: PENDING, SHIPPED, DELIVERED, or CANCELLED';

```

---

#### 3.2.5 Select AI 프로파일 생성

**Step 1: AI 프로파일 생성 (View 사용)**

```sql
-- NORTHWIND 사용자로 실행:
-- 기존 프로파일 삭제 (있다면)
BEGIN
  DBMS_CLOUD_AI.DROP_PROFILE('AWS_POSTGRES_AI_PROFILE', force => TRUE);
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

-- 새 프로파일 생성 (VIEW 이름 사용!)
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
      profile_name => 'AWS_POSTGRES_AI_PROFILE',
      attributes   => '{"provider": "oci", 
                        "model": "meta.llama-4-maverick-17b-128e-instruct-fp8",
                        "credential_name": "OCI_KEY_CRED",
                        "object_list": [
                            {"owner": "NORTHWIND", "name": "view_customers"},
                            {"owner": "NORTHWIND", "name": "view_orders"},
                            {"owner": "NORTHWIND", "name": "view_products"}
                        ]}'
  );
END;
/

-- 프로파일 활성화
EXEC DBMS_CLOUD_AI.SET_PROFILE('AWS_POSTGRES_AI_PROFILE');
/
```

---

#### 3.2.6 Select AI 쿼리 실행

**기본 쿼리:**

```sql
-- NORTHWIND 사용자로 실행:
-- 총 고객 수
EXEC DBMS_CLOUD_AI.SET_PROFILE('AWS_POSTGRES_AI_PROFILE');
SELECT AI show me the total number of customers;
```

---

### 3.3 Apache Iceberg 테이블 쿼리 핸즈온

#### 3.3.1 Iceberg 개요

Select AI는 데이터 레이크의 표준 포맷인 Apache Iceberg 테이블에 대한 쿼리를 지원합니다.

**Iceberg의 장점:**
- 대규모 데이터 레이크에서 ACID 트랜잭션 지원
- 스키마 진화 (Schema Evolution)
- 파티션 진화 (Partition Evolution)
- 타임 트래블 (Time Travel) 쿼리
- AWS S3, Azure ADLS, GCS 등 다양한 스토리지 지원

#### 3.3.2 Iceberg의 핵심 장점: 스키마 자동 감지

**Iceberg 다른점?**

일반 CSV나 Parquet 파일과 달리, Iceberg는 **메타데이터 파일에 스키마 정보를 포함**합니다:
- 컬럼 이름과 데이터 타입
- 파티션 정보
- 테이블 히스토리 (스냅샷)
- 데이터 파일 위치

**결과:** External Table 생성 시 **컬럼을 일일이 정의할 필요가 없습니다!**

#### 3.3.3 Iceberg 지원 모델

Select AI는 두 가지 방식으로 Iceberg 테이블을 지원합니다:

| 방식 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **Catalog-Managed** | AWS Glue, Polaris, Unity Catalog 사용 | 메타데이터 자동 관리, 실시간 스키마 업데이트 | Catalog 서비스 필요 |
| **Direct-Metadata** | metadata.json 파일 직접 참조 | Catalog 불필요, 간단한 설정 | 스냅샷 시점 고정, 수동 업데이트 |

**제약 사항 (중요!):** 
- 현재는 **읽기 전용(Query-only)** - INSERT, UPDATE, DELETE 불가
- **파티션된 Iceberg 테이블 미지원** - 비파티션 테이블만 가능
- **Row-level update (Merge-on-Read) 미지원** - delete 파일이 있으면 쿼리 실패
- **스키마 진화(Schema Evolution) 제한** - 스키마가 변경되면 External Table 재생성 필요
- **Time Travel 미지원** - 특정 스냅샷, 버전, 타임스탬프로 쿼리 불가

#### 3.3.4 방법 1: AWS Glue Catalog를 사용한 Iceberg 연결

**Step 1: AWS Glue 접근을 위한 Credential 생성**

```sql
-- NORTHWIND 사용자로 실행:
-- AWS Access Key 방식
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'AWS_GLUE_CRED',
    username => 'AKIAIOSFODNN7EXAMPLE',  -- AWS Access Key ID
    password => ''  -- AWS Secret Key
  );
END;
/

```

```sql
-- NORTHWIND 사용자로 실행:
BEGIN
  DBMS_CLOUD.CREATE_EXTERNAL_TABLE (
    table_name       => 'YELLOW_TRIPDATA_ICEBERG_EXT',
    credential_name  => 'AWS_ICEBERG_CRED',
    file_uri_list    => 'https://nyc-public-bucket.s3.ap-northeast-2.amazonaws.com/icebergdb-tables/yellow_tripdata_iceberg/metadata/00000-393dfa5e-431f-40a9-8241-1c869c03cbd7.metadata.json',
    format           => '{"access_protocol":{"protocol_type":"iceberg"}}'
  );
END;
/
```

**Step 1.5: Directory 권한 설정 (중요!)**

External Table 생성 시 `DATA_PUMP_DIR` 디렉토리에 대한 읽기/쓰기 권한이 필요합니다.

```sql
-- ADMIN 사용자가 아닌 경우 권한 부여 필요
-- ADMIN 권한으로 실행:
GRANT READ, WRITE ON DIRECTORY DATA_PUMP_DIR TO <your_username>;

-- 예: NORTHWIND 사용자에게 권한 부여
GRANT READ, WRITE ON DIRECTORY DATA_PUMP_DIR TO NORTHWIND;

```

**📌 왜 이 권한이 필요한가?**

1. **External Table 메타데이터 저장**
   - Oracle은 External Table의 메타데이터를 디렉토리에 임시로 저장합니다
   - Iceberg 스키마 정보를 읽고 파싱하는 동안 필요

2. **로그 파일 생성**
   - External Table 쿼리 실행 중 발생하는 로그를 기록
   - 오류 발생 시 디버깅에 필요한 정보 저장

3. **임시 파일 처리**
   - 복잡한 Iceberg 메타데이터 처리 시 임시 파일 사용
   - 대용량 데이터 처리를 위한 버퍼링

**⚠️ 주의사항:**
- ADMIN 계정으로 ADB를 사용한다면 이미 권한이 있으므로 불필요
- 별도 사용자 계정(예: NORTHWIND)을 생성한 경우 반드시 필요

```sql
-- NORTHWIND 사용자로 실행:
-- 스키마가 자동으로 생성되었는지 확인
DESC YELLOW_TRIPDATA_ICEBERG_EXT;

-- 19개 컬럼이 자동으로 감지됨!

-- 데이터 조회 테스트
SELECT * FROM YELLOW_TRIPDATA_ICEBERG_EXT WHERE ROWNUM <= 10;

```

**Step 3: VIEW를 사용한 접근**

External Table 대신 VIEW를 생성하여 comment 정보를 추가/보강할 수 있습니다.

```sql
-- NORTHWIND 사용자로 실행:
-- 방법 1: External Table을 먼저 생성한 후 View 생성
CREATE OR REPLACE VIEW NYC_TAXI_VIEW AS
SELECT 
  VENDORID,
  TPEP_PICKUP_DATETIME,
  TPEP_DROPOFF_DATETIME,
  PASSENGER_COUNT,
  TRIP_DISTANCE,
  RATECODEID,
  STORE_AND_FWD_FLAG,
  PULOCATIONID,
  DOLOCATIONID,
  PAYMENT_TYPE,
  FARE_AMOUNT,
  EXTRA,
  MTA_TAX,
  TIP_AMOUNT,
  TOLLS_AMOUNT,
  IMPROVEMENT_SURCHARGE,
  TOTAL_AMOUNT,
  CONGESTION_SURCHARGE,
  AIRPORT_FEE
FROM YELLOW_TRIPDATA_ICEBERG_EXT;

-- View에 상세한 주석 추가 (Select AI 정확도 대폭 향상)
COMMENT ON TABLE NYC_TAXI_VIEW IS 
'NYC Yellow Taxi trip data containing pickup/dropoff locations, fares, distances, and passenger information for data analysis and AI-powered queries';

COMMENT ON COLUMN NYC_TAXI_VIEW.VENDORID IS 
'Taxi company identifier: 1=Creative Mobile Technologies, 2=VeriFone Inc';

COMMENT ON COLUMN NYC_TAXI_VIEW.TPEP_PICKUP_DATETIME IS 
'Trip start date and time when meter was engaged';

COMMENT ON COLUMN NYC_TAXI_VIEW.TPEP_DROPOFF_DATETIME IS 
'Trip end date and time when meter was disengaged';

COMMENT ON COLUMN NYC_TAXI_VIEW.PASSENGER_COUNT IS 
'Number of passengers in the vehicle (driver entered value)';

COMMENT ON COLUMN NYC_TAXI_VIEW.TRIP_DISTANCE IS 
'Trip distance in miles recorded by taximeter';

COMMENT ON COLUMN NYC_TAXI_VIEW.RATECODEID IS 
'Rate code: 1=Standard rate, 2=JFK, 3=Newark, 4=Nassau/Westchester, 5=Negotiated fare, 6=Group ride';

COMMENT ON COLUMN NYC_TAXI_VIEW.STORE_AND_FWD_FLAG IS 
'Trip record held in memory before sending: Y=store and forward, N=not a store and forward trip';

COMMENT ON COLUMN NYC_TAXI_VIEW.PULOCATIONID IS 
'Pickup location ID corresponding to taxi zone where trip started';

COMMENT ON COLUMN NYC_TAXI_VIEW.DOLOCATIONID IS 
'Drop-off location ID corresponding to taxi zone where trip ended';

COMMENT ON COLUMN NYC_TAXI_VIEW.PAYMENT_TYPE IS 
'Payment method: 1=Credit card, 2=Cash, 3=No charge, 4=Dispute, 5=Unknown, 6=Voided trip';

COMMENT ON COLUMN NYC_TAXI_VIEW.FARE_AMOUNT IS 
'Base fare amount calculated by time and distance meter';

COMMENT ON COLUMN NYC_TAXI_VIEW.EXTRA IS 
'Extra charges: rush hour and overnight charges ($0.50 and $1.00)';

COMMENT ON COLUMN NYC_TAXI_VIEW.MTA_TAX IS 
'Metropolitan Transportation Authority tax ($0.50 automatically triggered)';

COMMENT ON COLUMN NYC_TAXI_VIEW.TIP_AMOUNT IS 
'Tip amount automatically populated for credit card payments, cash tips not included';

COMMENT ON COLUMN NYC_TAXI_VIEW.TOLLS_AMOUNT IS 
'Total amount of tolls paid during trip';

COMMENT ON COLUMN NYC_TAXI_VIEW.IMPROVEMENT_SURCHARGE IS 
'Improvement surcharge assessed on hailed trips ($0.30)';

COMMENT ON COLUMN NYC_TAXI_VIEW.TOTAL_AMOUNT IS 
'Total amount charged to passengers including all fees, taxes, and tips';

COMMENT ON COLUMN NYC_TAXI_VIEW.CONGESTION_SURCHARGE IS 
'Congestion surcharge for trips in Manhattan south of 96th Street ($2.50)';

COMMENT ON COLUMN NYC_TAXI_VIEW.AIRPORT_FEE IS 
'Airport fee for trips to/from LaGuardia or JFK airports ($1.25)';

-- View를 사용한 쿼리 
SELECT COUNT(*) as total_trips FROM NYC_TAXI_VIEW;

```

#### 3.3.5 Select AI with Iceberg

**Iceberg 테이블을 포함한 프로파일 생성**

```sql
-- NORTHWIND 사용자로 실행:
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'SIDECAR_AI_PROFILE',
    attributes   => '{
      "provider": "oci",
      "model": "meta.llama-4-maverick-17b-128e-instruct-fp8",
      "credential_name": "OCI_KEY_CRED",
      "object_list": [
        {"owner": "NORTHWIND", "name": "NYC_TAXI_VIEW"}
      ]
    }'
  );
END;
/
```

**실전 예제: NYC Taxi 데이터로 Select AI 쿼리**

NYC Yellow Taxi 데이터를 Select AI로 분석하는 예제입니다.

```sql
-- NORTHWIND 사용자로 실행:
BEGIN
    DBMS_CLOUD_AI.SET_PROFILE(profile_name => 'SIDECAR_AI_PROFILE');
END;
/
SELECT ai '신용카드로 결제된 건들의 평균 팁 금액을 알려줘';
```

**💡 더 간편한 방법: SELECT AI 구문 사용** ⭐

프로파일을 활성화한 후, `SELECT AI` 키워드로 더 간단하게 질문할 수 있습니다:

```sql
-- NORTHWIND 사용자로 실행:
-- SELECT AI 구문 사용 예제 (더 간편함!)

-- 기본 분석
SELECT AI 신용카드로 결제된 건들의 평균 팁 금액을 알려줘;
SELECT AI 총 택시 운행 건수는?;
SELECT AI 평균 택시 요금과 평균 이동 거리는?;

-- 결제 방식 분석
SELECT AI 결제 방식별로 건수와 평균 팁을 보여줘;
SELECT AI 신용카드와 현금 결제의 평균 팁 차이는?;

-- 시간 분석
SELECT AI 시간대별로 운행 건수를 보여줘;
SELECT AI 가장 바쁜 시간대는 언제야?;
SELECT AI 새벽 시간대(0-6시) 평균 요금은?;

-- 거리 및 요금 분석
SELECT AI 10마일 이상 장거리 운행의 평균 요금은?;
SELECT AI 5마일 미만 단거리 운행의 비율은?;

-- 승객 분석
SELECT AI 승객 수에 따른 평균 요금 차이를 보여줘;
SELECT AI 1인 승객과 여러 명 승객의 팁 비율 차이는?;

-- 위치 분석
SELECT AI 가장 많이 이용되는 픽업 위치 상위 5곳은?;
SELECT AI 공항 픽업 요금의 평균은?;

-- 비즈니스 인사이트
SELECT AI 수익성이 가장 높은 시간대와 거리 조합은?;
SELECT AI 평균 팁이 가장 높은 운행 조건은?;

-- 대화형 질문 (연속으로)
SELECT AI 가장 비싼 택시 요금은?;
-- 이어서
SELECT AI 그 운행의 이동 거리와 소요 시간도 보여줘;
-- 계속
SELECT AI 팁은 얼마였어?;
```
