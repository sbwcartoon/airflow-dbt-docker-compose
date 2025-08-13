# Airflow for Airflow + DBT

### PostgresHook의 postgres_conn_id는 상위 폴더의 .env에 정의함

- .env에서 "AIRFLOW_CONN_"를 prefix로 가지는 값(ex. .env에 AIRFLOW_CONN_ABC라는 키가 있을 때 postgres_conn_id는 "ABC")
- 상위 폴더에서 docker compose를 실행할 때 운영 환경에 따라 .env를 선택함

### package dependency

- pandas 버전 설정
  - apache-airflow-core 패키지가 의존성을 가지는 sqlalchemy는 버전이 2.0보다 낮아야
    하는데, [pandas 버전 2.2.0부터 sqlalchemy 2.0 이상을 요구함](https://pandas.pydata.org/docs/whatsnew/v2.2.0.html#increased-minimum-versions-for-dependencies)
  - 따라서 pandas의 버전은 2.2.0보다 낮게 설정함
- paramiko 버전 설정
  - ssh 연결을 위한 패키지
  - airflow에서는 SSHHook을 사용하는데 paramiko의 DSSKey를 사용함. 그런데 paramiko의 최신 버전은 대신 RSAKey를 사용하므로 오류가 발생함
  - 대신 paramiko에서 DSSKey를 사용하는 버전은 2.x이므로 3보다 작게 설정함

---

## 참고

### paramiko 관련 경고

- 사용하는 paramiko 버전이 최신이 아니므로 ssh 사용 시 경고가 발생할 수 있음
- 해당 경고는 본 프로젝트가 docker compose로 airflow, dbt 환경이 함께 실행되고 ssh로 연동되는 특수한 상황임을 고려하여 별도 조치하지 않음