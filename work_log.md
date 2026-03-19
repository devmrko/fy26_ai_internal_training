# Work Log

## 2026-03-17

- 프로젝트 git 상태 확인 (로컬과 remote 동기화 완료 확인)
- `work_log.md` 파일 생성
- `1회차/adb_select_ai/README.md` 점검 및 개선
  - 목차(TOC), 대상 독자, 실습 흐름 요약, 프로젝트 파일 구조 섹션 추가
  - Windows powershell 명령 오타 수정
  - 코드 블록 언어 지정 (sql, bash, python) 일괄 추가
  - 반복되는 `uv init` / `uv add` 안내 정리
  - `.env` 설정 안내 보강 (예시 값, DSN 확인 방법)
  - `comments: false` 비일관성 안내 Tip 추가
  - 트러블슈팅 섹션(부록) 추가
- `2회차/adb_select_ai_agent/README.md` 점검 및 개선
  - 대상 독자, 실습 흐름 요약, 프로젝트 파일 구조 섹션 추가
  - PL/SQL Tool 함수명 불일치 수정 (`generate_return_auth` → `generate_return`)
  - Step 1.3 네트워크 ACL 코드에서 누락된 `BEGIN` 추가
  - `{query}` 플레이스홀더 필수 사항을 주석→경고 박스로 승격
  - 테스트 코드의 하드코딩된 conversation_id를 변수화 및 안내 추가
  - 개인 이메일 주소 → 플레이스홀더로 교체
  - 잘못된 Step 참조 수정 (Step 11.3 → Step 7.3)
  - Python Streamlit 앱 실행 가이드(부록) 추가
  - 트러블슈팅 섹션(부록) 추가
- `2회차/proxy_database/README.md` 점검 및 개선
  - 문서 개요, 대상 독자, 실습 흐름 요약, 프로젝트 파일 구조 섹션 추가
  - 목차에 부록(Streamlit, 트러블슈팅) 항목 추가
  - 오타 수정 ("나눠저" → "나뉘어")
  - Credential 이름 불일치 수정 (`AWS_ICEBERG_CRED` → `AWS_GLUE_CRED`)
  - 하드코딩된 AWS 엔드포인트/비밀번호 → 플레이스홀더로 교체
  - 질문 번호 점프 수정 (1→3→5 → 1→2→3)
  - Python Streamlit 앱 실행 가이드(부록) 추가
  - 트러블슈팅 섹션(부록) 추가 (DB Link, Select AI, Iceberg, Streamlit)

### 2차 점검 (3개 문서 교차 검증)

- `1회차/adb_select_ai/README.md` 2차 점검
  - `"comments": false` → `"comments": true` 수정 (Resource Principal / API Key 모두)
  - `mcp_server.py` docstring의 `NORTHWIND_AI3` → `NORTHWIND_AI` 일괄 수정
- `2회차/adb_select_ai_agent/README.md` 2차 점검
  - DROP_TOOL 예외 처리 PL/SQL 문법 수정 (EXCEPTION 키워드 위치)
  - 테스트 6.2 하드코딩된 conversation_id → 변수화 (`l_conv_id`) 및 교체 안내 추가
  - WebSearch CREATE_AGENT 구문 수정 (`profile_name` 직접 파라미터 → `attributes` JSON 방식)
  - OpenAI Credential 비밀번호 빈 값 → 플레이스홀더로 교체
  - RAG Tool의 하드코딩된 OCI 값(location_uri, compartment_id) → 플레이스홀더로 교체
  - Step 1.3 ACL "선택사항"에 "Step 7.3 필수" 경고 추가
- `2회차/proxy_database/README.md` 2차 점검
  - `.env.example` 파일 신규 생성
  - 예제 3(시계열 분석)에 누락된 `SET_PROFILE` 추가
  - `comments => 'true'` 표현 → 정확한 JSON 속성 표기로 수정

### 3차 점검 (실행 차단 이슈 집중)

- `1회차/adb_select_ai/README.md` 3차 점검
  - 프로파일 이름 대소문자 수정: `northwind_ai` → `NORTHWIND_AI`
  - README 내 MCP 서버 코드 docstring `NORTHWIND_AI3` → `NORTHWIND_AI` (3곳)
  - Cursor MCP 설정의 하드코딩된 개인 경로 → 플레이스홀더로 교체
- `2회차/adb_select_ai_agent/README.md` 3차 점검
  - `generate_return` 함수 테스트 코드 누락된 `/` 종결자 추가
  - `WEBSEARCH_PROFILE` CREATE_PROFILE 뒤 누락된 `/` 종결자 추가
- `2회차/proxy_database/README.md` 3차 점검
  - PostgreSQL db_type 대소문자 수정: `POSTGRES` → `postgres`
  - PostgreSQL port 타입 수정: 문자열 `'5432'` → 숫자 `5432`
  - SELECT AI 문 따옴표 누락 일괄 수정 (~20곳): `SELECT AI 질문` → `SELECT AI '질문'`
