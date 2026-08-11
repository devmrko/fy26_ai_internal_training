# 트러블슈팅

실패하면 다음 실행 체인을 먼저 기록합니다.

1. Client가 명령을 읽었는가
2. OCI API 또는 DB 서버에 도달했는가
3. 서버가 실제 실행했는가
4. 정확한 HTTP/Oracle 오류와 결과는 무엇인가

| 증상 | 실행 단계 | 주요 원인 | 확인·조치 |
|---|---|---|---|
| ADB create HTTP 400 | OCI API 입력 검증 | tier별 compute/storage 필수값 | 현재 CLI help와 서비스 계약 확인 |
| Object not found/authorized | DB→Object Storage | Dynamic Group rule, bucket policy, token cache | ADB OCID 단일 rule, policy, RP 재활성화 확인 |
| `ORA-06564 DATA_PUMP_DIR` | DB External DDL | 스키마 DIRECTORY 권한 누락 | ADMIN이 READ/WRITE 최소 권한 부여 |
| `ORA-29913 / ORA-01861` | External fetch | Hive 날짜 문자열과 DATE literal 충돌 | 소비 뷰에서 명시적 TO_DATE |
| GenAI HTTP 404 | DB/CLI→GenAI | 현재 region에 모델 없음 | model catalogue 조회 후 runtime model 변경 |
| GenAI high load | DB→GenAI | provider 일시 부하 | 구성 실패로 오판하지 말고 제한적으로 재검증 |
| `SHOWSQL`은 성공하지만 오답 | LLM 생성 | 잘못된 집단·집계 의미 | Few-shot 정책, 실제 SQL 실행, 정답 판정 |

동일 명령을 반복하기 전에 실패한 단계가 바뀌는지 확인합니다. SQL이 서버에 전달되지 않았다면
DB 성능이나 데이터 크기 문제로 설명하지 않습니다.
