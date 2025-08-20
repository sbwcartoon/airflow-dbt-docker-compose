# DBT for Airflow + DBT

### 레이어 구성

- raw
  - 원본 데이터를 모델링하기 위한 base 레이어
  - 기존 db에 이미 존재하며, dbt에서는 데이터 형식이 적합한지 test만 가능(dbt test)
  - 원본 데이터와의 인터페이스 역할
- staging
  - raw 데이터를 표준화하고 정제하여 후속 모델에서 바로 사용할 수 있는 기본 레이어
  - 컬럼 명/데이터 유형 정리, 불필요 컬럼 제거, null 처리 등
  - 모델 명 prefix는 stg_
- intermediate
  - staging 레이어를 바탕으로 생성하는 중간 레이어
  - 데이터를 marts 레이어에서 쉽게 참조할 수 있는 형태로 가공
  - 여러 모델 조인, 비즈니스 로직 적용, 파생 컬럼 생성, 집계 등
  - 모델 명 prefix는 int_
- marts
  - intermediate 레이어를 바탕으로 최종 분석 및 BI 용도로 fact/dimension 테이블을 제공하는 레이어
  - 모델 명 prefix는 fact=fct_, dimension=dim_
- bi
  - marts 레이어를 기반으로 한 뷰 레이어(marts 레이어의 버전 변경에 대비)
  - 본 데이터를 활용하는 서비스(Looker Studio 등)와의 인터페이스 역할
  - 모델 명은 view_{marts의 fact 모델 명}. ex. fct_user_event_metrics => view_fct_user_event_metrics

### 스키마 설정

- dbt 작동 결과 데이터가 저장되는 기본 스키마는 dbt(profiles/profiles.yml에 정의함)
- dbt_project.yml에서 기본 스키마가 아닌 스키마로 설정 가능(설정하지 않을 경우 기본 스키마 사용)
- schema 명명 규칙
  - 기본 규칙은 {기본 스키마}_{변경할 스키마}. ex. 기본 스키마=dbt, 변경할 스키마=staging => dbt_staging
  - 본 프로젝트에서는 변경할 스키마 이름이 없다면 기본 스키마를 사용하고, 있다면 해당 값을 사용하도록 명명 규칙을 바꿈(generate_schema_name macro를 오버라이드함)

### schema.yml 생성 패키지 사용법

- 실제 db에 저장된 모델을 바탕으로 생성함(dbt run으로 해당 모델을 db에 생성 후 generate 가능)
- 생성 결과는 schema.yml이고, 모델(sql 파일)의 타입과 유효성 정의
- 생성 후 tests, description 등 내용 추가/수정 필요
- 자동 생성 예시(fct_user_event_metrics.sql 모델 예제)
  1. 모델이 ephemeral 설정이라 db에 실체를 저장하지 않는 경우, 사전에 모델을 view로 설정 변경 필요

  - 모델 파일(sql) 상단에 view로 설정: {{ config(materialized='view') }} 입력({{ config(materialized='ephemeral') }}가 있다면 대체)
  - ephemeral 모델은 db에 데이터를 생성하지 않으므로, 본 과정 완료 후 설정을 되돌리고 생성한 view를 삭제해야 함(drop view view_name;)

  2. 모델 생성
  > dbt run --select fct_user_event_metrics
  3. schema.yml generate(명령어를 실행한 경로에 schema.yml 생성)
  > dbt run-operation generate_model_yaml --args='{"model_names": ["fct_user_event_metrics"]}' --quiet > schema.yml

---

## 참고

- 본 프로젝트는 airflow(LocalExecutor 사용) + dbt를 docker compose로 구성한 프로젝트의 일부로서, 구성이 달라질 경우 ssh 관련 설정은 제거할 수 있음
- profiles.yml 구동 환경별 설정 정보를 담고 있어서 env 파일의 역할을 하나, 현재의 구성은 env를 사용하여 구동 환경을 선택하므로 .gitignore에 포함하지 않음
