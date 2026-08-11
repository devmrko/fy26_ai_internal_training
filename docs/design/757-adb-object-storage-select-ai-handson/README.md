# 설계서: 신규 ADB·Object Storage·Select AI 교육 Hands-on

> Redmine: #757
>
> 공개 범위: GitHub Public Repository

## 목적

빈 Oracle Autonomous AI Database 26ai에서 다음 흐름을 소형 데이터로 재현하는 교육 모듈을
제공한다.

1. ADB와 실습 스키마 준비
2. Resource Principal로 Object Storage ORC 접근
3. External Table과 타입 정규화 소비 뷰 생성
4. Select AI Profile과 승인 객체 구성
5. Vector Few-shot 검색과 게임/도메인 대상 결정
6. 생성 SQL의 실제 실행과 의미 검증

## 공개 안전 기준

- 고객명, 실제 게임명, bucket URI, OCID, 계정, 암호, Token, Wallet, private key를 포함하지 않는다.
- 실습자는 `.env.example`의 placeholder를 자기 환경에서만 치환한다.
- 대용량 전체 scan 대신 한 날짜의 작은 ORC 객체 2개를 사용한다.
- SQL 예시는 `GAME_USER_MST`, `GAME_BIZ_USER_TXN`이라는 일반 이름을 사용한다.

## 구조

```text
3회차/adb_object_storage_select_ai/
├── README.md
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── execution-result.md
│   └── troubleshooting.md
└── sql/
    ├── 01_bootstrap.sql
    ├── 02_external_tables.sql
    ├── 03_verify.sql
    ├── 04_select_ai_profile.sql
    └── 05_vector_fewshot.sql
```

## 완료 기준

- 처음 보는 실습자가 큰 흐름부터 SQL 실행 순서까지 따라갈 수 있다.
- 각 스크립트의 실행 계정, 입력값, 결과, 실패 판별 기준이 명시된다.
- Mermaid 아키텍처와 sequence diagram이 렌더링된다.
- 공개 저장소 secret scan과 Markdown link 검사를 통과한다.
