# Select AI / Ask Oracle 최신 업데이트 체크리스트

확인일: 2026-05-28

이 문서는 OAPC 3차 교육에 바로 반영할 최신 변경점과, 시간이 부족하면 말로만 소개할 확장 주제를 분리한 운영 메모입니다. 본 핸즈온의 핵심 흐름은 `SQL Tool -> PL/SQL Tool -> Agent Team -> Ask Oracle(APEX)`로 유지합니다.

## 1. 26ai / 19c 기능 차이

Oracle의 2026-05 기준 Select AI 기능 매트릭스는 19c와 26ai 모두에서 Chat, NL2SQL, AI Agent, Summarization, Translation 같은 기본 기능을 제공하지만, 고급 기능은 26ai 쪽에 더 집중되어 있습니다.

| 구분 | 교육 반영 |
|------|-----------|
| 공통 설명 | Select AI는 AI 모델을 DB 안에 내장하는 것이 아니라, AI Profile로 외부/OCI LLM을 연결하는 프레임워크라고 설명합니다. |
| 19c에서도 가능한 축 | Chat, NL2SQL, AI Agent, Summarization, Translation 중심으로 설명합니다. |
| 26ai에서 강조할 축 | NL2SQL Feedback, Auto Object Selection, RAG/Vector Search를 최신 확장 기능으로 설명합니다. |
| 현장 실습 판단 | 실습 DB가 26ai가 아니거나 Vector Index 준비가 안 되어 있으면 RAG는 설명만 하고, SQL Tool/PLSQL Tool/Ask Oracle 중심으로 진행합니다. |

공식 참고:

```text
https://blogs.oracle.com/developers/select-ai-by-release-a-quick-guide-to-26ai-and-19c-capabilities
https://www.oracle.com/autonomous-database/select-ai/
```

## 2. DBMS_CLOUD_AI_AGENT Tool 최신 정리

`DBMS_CLOUD_AI_AGENT.CREATE_TOOL`은 커스텀 PL/SQL 함수/프로시저뿐 아니라 내장 Tool 타입을 지원합니다.

| Tool 타입 | 필수/주요 파라미터 | OAPC 적용 |
|-----------|--------------------|-----------|
| `SQL` | `tool_params.profile_name` | 본 실습의 `SQL_Analysis_Tool` |
| `RAG` | `tool_params.profile_name` | Vector Index 준비가 된 환경에서만 확장 실습 |
| `WEBSEARCH` | `tool_params.credential_name` | 시간 부족 시 개념만 소개. 외부 API credential 필요 |
| `NOTIFICATION` | `notification_type`, email/slack별 credential | Step 7 확장 예제로 유지 |
| Custom PL/SQL | `function`, `instruction` | 본 실습의 `Return_Auth_Generator` |

실무에서 기존 PL/SQL 프로시저가 여러 `OUT` 파라미터를 반환하면, 원본 프로시저를 바꾸기보다 wrapper function을 만들고 결과를 하나의 JSON payload로 반환하는 패턴이 권장됩니다. 본 교재의 RMA 예제는 단일 `VARCHAR2` 반환으로 단순화되어 있으나, 고객사 실제 프로시저를 연결할 때는 이 wrapper 패턴을 설명하면 좋습니다.

공식 참고:

```text
https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/dbms-cloud-ai-agent-package.html
https://blogs.oracle.com/machinelearning/how-to-reuse-multi-output-pl-sql-procedures-in-the-select-ai-agent-framework
```

## 3. Ask Oracle v4 반영

Ask Oracle은 Oracle DevRel이 제공하는 공식 APEX 샘플 앱입니다. 2026-05-28 기준 공식 GitHub 폴더에는 APEX export SQL, 설치 PDF, README가 있으며, 현재 export 파일명은 `ADB-AskOracle-Chatbot-2026-03-04.sql`입니다.

Ask Oracle v4의 데모 포인트:

| 기능 | 현장 데모 여부 |
|------|----------------|
| Chat | 선택. LLM 직접 대화 비교용 |
| NL2SQL | 필수. `TRAIN05_AI`로 Northwind 질의 |
| Explain SQL | 가능하면 시연 |
| Chart | 가능하면 시연. "막대 차트로 보여줘" 질문 사용 |
| AI Agent | 필수. `NORTHWIND_SUPPORT_TEAM`으로 RMA Tool 호출 |
| RAG | Vector Index가 없으면 설명만 |
| Audio generation | 시간 부족 시 생략 |
| Prompt/Profile/Agent details | Settings 화면에서 선택값 확인용 |

OAPC 강사용 설치 URL:

```text
https://yh0olybn5pqce4n-d8aukro81636mon0.adb.ap-seoul-1.oraclecloudapps.com/ords/r/oapc_demo/askoracle/home
```

공식 참고:

```text
https://blogs.oracle.com/machinelearning/try-the-new-ask-oracle-chatbot-powered-by-select-ai
https://github.com/oracle-devrel/oracle-autonomous-database-samples/tree/main/apex/Ask-Oracle
```

## 4. Autonomous AI Database MCP Server

MCP Server는 별도 Agent Tool 타입이 아니라, Select AI Agent로 만든 Tool을 MCP 호환 클라이언트에서 호출할 수 있게 노출하는 운영 방식입니다. Oracle 문서 기준으로 Autonomous AI Database 26ai와 19c에서 제공되며, 별도 고객 호스팅 MCP 서버를 직접 운영하지 않는 것이 장점입니다.

교육 반영:

| 구분 | 내용 |
|------|------|
| 핵심 메시지 | "오늘 만든 SQL/PLSQL Tool을 APEX뿐 아니라 MCP client에서도 쓸 수 있다"로 설명합니다. |
| 실습 포함 여부 | OAPC 3차 3시간 안에는 포함하지 않습니다. OCI tag/IAM, OAuth 또는 bearer token, client 설정까지 필요합니다. |
| 보안 주의 | MCP는 DB 사용자의 권한 범위 안에서 동작합니다. 최소 권한, VPD/RAS, 감사 정책을 먼저 설계해야 합니다. |
| 엔드포인트 형식 | `https://dataaccess.adb.{region-identifier}.oraclecloudapps.com/adb/mcp/v1/databases/{database-ocid}` |

공식 참고:

```text
https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/about-mcp-server.html
https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/use-mcp-server.html
https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/security.html
```

## 5. Pre-built AI Agents

Oracle은 Select AI Agent 기반의 pre-built agent 예제를 공개했습니다. OAPC 3차에서는 설치하지 않고, 파트너사가 고객 PoC로 확장할 때 참고할 "다음 단계"로 소개합니다.

대표 예:

| Agent | 활용 메시지 |
|-------|-------------|
| NL2SQL Data Retrieval Agent | Ask Oracle + NL2SQL 데모 이후 확장 방향 |
| Autonomous AI Database Provisioning Agent | OCI 운영 자동화 PoC |
| Database Inspect Agent | 스키마/객체 분석, 개발자 지원 |
| Insight Agent for Jira | 업무 시스템 연동 예 |
| Cloud Repository Connector Agent | GitHub/AWS CodeCommit/Azure Repos 연동 |
| OCI Object Storage / Vault / Network Load Balancer Agent | OCI 운영 자동화 예 |

공식 참고:

```text
https://blogs.oracle.com/machinelearning/announcing-oracle-select-ai-pre-built-ai-agents
https://www.oracle.com/autonomous-database/prebuilt-ai-agents/
```

## 6. Ask Oracle + VPD 보안 메시지

파트너 대상 교육에서는 "LLM이 SQL을 만들더라도 최종 실행 권한은 DB 보안 정책이 통제한다"는 메시지가 중요합니다. Oracle의 Ask Oracle + VPD 예제는 사용자별 지역 권한에 따라 같은 자연어 질문도 다른 결과가 나오도록 구성합니다.

OAPC 반영:

| 구분 | 내용 |
|------|------|
| 1분 설명 | Select AI는 SQL을 생성하지만, DB 실행 시 VPD/RAS/권한/마스킹 정책을 우회하지 않는 구조로 설계해야 합니다. |
| 고객 제안 포인트 | 영업/고객 데이터 데모에서는 계정별 row-level security를 같이 보여주면 신뢰도가 높습니다. |
| 현장 실습 | 이번 3차에서는 구현하지 않고 후속 Solution Day 후보로 둡니다. |

공식 참고:

```text
https://blogs.oracle.com/machinelearning/building-ai-apps-with-select-ai-and-virtual-private-database
```

## 7. Translation / Built-in Examples 확장 주제

2026-04 이후 자료 기준으로 Select AI Translate는 OCI 외에 Google, AWS, Azure 번역 provider 지원이 확대되었습니다. 또한 OML Notebooks의 built-in example template에는 Select AI SQL/Python 예제가 포함되어 있어, 수강생이 교육 후 자습할 수 있는 경로로 안내하기 좋습니다.

OAPC 반영:

| 주제 | 현장 처리 |
|------|-----------|
| Select AI Translate | 다국어 고객 응대/RAG 문서 정규화 사례로 짧게 언급 |
| OML Notebook built-in examples | "교육 이후 자습/PoC 템플릿"으로 안내 |
| Python API / connection pooling | 이번 SQL/APEX 중심 실습에서는 생략 |

공식 참고:

```text
https://blogs.oracle.com/machinelearning/expanding-oracle-autonomous-ai-database-select-ai-translate-with-google-aws-and-azure
https://blogs.oracle.com/developers/jumpstart-ai-projects-with-built-in-examples-on-autonomous-ai-database
```

## 8. OAPC 3차 진행 반영안

| 시간 | 내용 | 비고 |
|------|------|------|
| 0-10분 | 최신 업데이트 맵: 26ai/19c, Ask Oracle, MCP, Pre-built Agents | 이 문서 기준 |
| 10-65분 | SQL Tool + PL/SQL Tool + Task/Agent/Team 생성 | `OAPC_3rd_Field_Practice_Guide.md` 빠른 SQL |
| 65-85분 | SQL Worksheet에서 Agent 실행 검증 | 가장 비싼 제품, RMA 생성 |
| 85-115분 | Ask Oracle 공식 APEX 앱으로 NL2SQL/Chart/Agent Team 시연 | `TRAIN05_AI`, `NORTHWIND_SUPPORT_TEAM` |
| 115-135분 | 고객 제안 포인트: MCP, VPD, Pre-built Agents, RAG | 구현 대신 설계 방향 |
| 135-170분 | 수강생 환경 이슈 해결 및 반복 실습 | 계정별 `TRAINxx_AI` 확인 |
| 170-180분 | 정리/Q&A | Solution Day 후보 수집 |

