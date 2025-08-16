import os
from datetime import datetime

from airflow.exceptions import AirflowException
from airflow.providers.ssh.hooks.ssh import SSHHook

from airflow.decorators import dag, task


def run_dbt_command(command: str):
    ssh_hook = SSHHook(ssh_conn_id=os.environ.get("SSH_CONN_ID"))

    try:
        with ssh_hook.get_conn() as ssh_client:
            env_exports = " ".join([
                f"export {key}='{value}';"
                for key, value in {
                    "DBT_PROFILES_DIR": "/usr/app/profiles",
                    "DBT_TARGET": os.environ.get("DBT_TARGET"),
                    "LOCAL_ANALYTICS_GCP_PROJECT_ID": os.environ.get("LOCAL_ANALYTICS_GCP_PROJECT_ID"),
                    "LOCAL_ANALYTICS_GCP_LOCATION": os.environ.get("LOCAL_ANALYTICS_GCP_LOCATION"),
                    "LOCAL_GOOGLE_APPLICATION_CREDENTIALS": "/" + os.environ.get("LOCAL_GOOGLE_APPLICATION_CREDENTIALS"),
                    "LOCAL_ANALYTICS_GCP_DEFAULT_DATASET": os.environ.get("LOCAL_ANALYTICS_GCP_DEFAULT_DATASET"),
                    "PROD_ANALYTICS_GCP_PROJECT_ID": os.environ.get("PROD_ANALYTICS_GCP_PROJECT_ID"),
                    "PROD_ANALYTICS_GCP_LOCATION": os.environ.get("PROD_ANALYTICS_GCP_LOCATION"),
                    "PROD_GOOGLE_APPLICATION_CREDENTIALS": "/" + os.environ.get("PROD_GOOGLE_APPLICATION_CREDENTIALS"),
                    "PROD_ANALYTICS_GCP_DEFAULT_DATASET": os.environ.get("PROD_ANALYTICS_GCP_DEFAULT_DATASET"),
                }.items() if value is not None
            ])

            full_command = f"{env_exports} cd /usr/app && {command}"
            stdin, stdout, stderr = ssh_client.exec_command(full_command)

            exit_status = stdout.channel.recv_exit_status()

            output = stdout.read().decode().strip()
            error_output = stderr.read().decode().strip()

            print(f"[DBT OUTPUT]\n{output}")
            print(f"[DBT STDERR]\n{error_output}")

            if exit_status != 0:
                raise AirflowException(
                    f"DBT command failed with exit code {exit_status}\n"
                    f"Command: {full_command}\n"
                    f"STDERR:\n{error_output}\n"
                    f"STDOUT:\n{output}"
                )

            return output

    except Exception as e:
        raise AirflowException(f"SSH command failed: {str(e)}")


@dag(
    dag_id="dbt",
    start_date=datetime(2025, 8, 5),
    schedule=None,
    catchup=False,
    tags=["transform"],
)
def pipeline():
    @task()
    def dbt_deps():
        return run_dbt_command("dbt deps")

    @task()
    def dbt_run():
        return run_dbt_command("dbt run")

    @task()
    def dbt_test():
        return run_dbt_command("dbt test")

    dbt_deps() >> dbt_run() >> dbt_test()


dag = pipeline()
