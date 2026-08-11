# 참고 실증 결과

이 문서의 수치는 교육 설계 검증용 소형 실행 사례이며 운영 성능 보장을 의미하지 않습니다.

| 단계 | 결과 |
|---|---|
| ADB 26ai Developer tier 생성 | 약 3분 이내 `AVAILABLE` |
| Wallet `ADMIN` / 업무 스키마 접속 | PASS / PASS |
| Resource Principal 단일 객체 GET | PASS |
| External Table | 9개 생성 PASS |
| 실제 sample | 8개 읽기 PASS, 대형 1개 metadata only |
| 소비 뷰 날짜 계약 | `VARCHAR2 → DATE` PASS |
| 일별 사용자 집계 | 약 1~2초 |
| 일별 사업 사용자 집계 | 약 7~8초 |
| Select AI provider/profile | PASS |
| 기본 NL2SQL 의미 판정 | 불필요 조건으로 FAIL |
| Vector 예제 검색 | PASS |
| Few-shot 유도 SQL과 실행 | PASS |

핵심 관찰은 “SQL 문자열 생성 성공”이 최종 성공이 아니라는 점입니다. 실제 사례에서는 기본
NL2SQL이 질문에 없는 cohort 조건을 추가했습니다. 검증 예제를 문맥으로 제공하자 올바른
`AU_FLAG`, `EXPT_USER_YN`, `COUNT(DISTINCT GUID)` 조건으로 교정됐습니다.

또한 교정된 SQL도 첫 실행에서 날짜 타입 불일치로 실패했습니다. External Table의 Hive 날짜를
소비 뷰에서 DATE로 정규화한 뒤 같은 SQL이 성공했습니다. 따라서 의미 정책과 데이터 타입 계약을
각각 검증해야 합니다.
