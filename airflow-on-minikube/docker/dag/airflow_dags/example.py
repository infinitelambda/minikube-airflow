import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator

# args
DAG_NAME = 'local_log_dag'
start_date = datetime(year=2021, month=1, day=5, hour=1, minute=1)
catchup = False

# Airflow ENV variables
dag_schedule = Variable.get(DAG_NAME + "_schedule", "0 0/1 * * *")
secret_id = os.getenv("AWS_ACCESS_KEY_ID", None)
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", None)

# create example trigger command
ingest_cmd = "/usr/local/airflow/ci/launch_ingest.sh"
activate_venv = "source /usr/local/airflow/venv/bin/activate && "

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2019, 12, 10),
    "email": ["airflow@airflow"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

test_dag = DAG(
    DAG_NAME,
    schedule_interval=dag_schedule,
    start_date=start_date,
    catchup=catchup,
    default_args=default_args
)

dummy_task = DummyOperator(task_id='dummy_task', dag=test_dag)

# tasks
test_task = KubernetesPodOperator(namespace='development',
                                  image="localhost:5000/dag-img",
                                  image_pull_policy="Always",
                                  is_delete_operator_pod=False,  # we leave it false to make sure we get the logs
                                  name='copied_task',
                                  in_cluster=True,
                                  task_id="prin",
                                  cmds=["/bin/bash", "-c", activate_venv + ingest_cmd],
                                  startup_timeout_seconds=999,
                                  get_logs=True,
                                  default_args=default_args,
                                  env_vars={
                                  'AWS_ACCESS_KEY_ID': secret_id,
                                  'AWS_SECRET_ACCESS_KEY': secret_key}
                                  )

dummy_task.set_downstream(test_task)

dummy_task
