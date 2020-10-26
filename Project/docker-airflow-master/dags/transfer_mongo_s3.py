import airflow
from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.sensors import S3KeySensor
from airflow.operators import BashOperator


default_args = {
    'owner': 'Uche',
    'depends_on_past': False,
    'start_date': datetime(2020, 9, 4),
    'email_on_failure': False,
    'email_on_retry': False,
    #'retries': 1,
    #'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG(dag_id = 'mongo_to_s3_dag', default_args=default_args, schedule_interval=timedelta(days=1),catchup = False)

t_s3filetest = S3KeySensor(task_id='s3_file_test', poke_interval=0, timeout=30, soft_fail=False, bucket_key='sparktest/content.json/*.json', wildcard_match = True, aws_conn_id='aws', bucket_name='awsbuc01', dag=dag)

t_spark = SparkSubmitOperator(task_id='docker_spark', depends_on_past=False, application='/usr/local/spark_files/basicsubmit.py', trigger_rule='all_failed', conn_id='spark_local', dag = dag)

t_finished = BashOperator(task_id='task3', depends_on_past=False, bash_command='echo Job finished', trigger_rule='all_done', dag=dag)

t_spark.set_upstream(t_s3filetest)
t_finished.set_upstream(t_spark)
t_finished.set_upstream(t_s3filetest)