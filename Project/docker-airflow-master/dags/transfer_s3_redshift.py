import airflow
from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.glue import AwsGlueJobOperator
from airflow.operators.sensors import S3KeySensor
from airflow.operators import BashOperator


default_args = {
    'owner': 'Uche',
    'depends_on_past': False,
    'start_date': datetime(2020, 9, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    #'retries': 1,
    #'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG(dag_id = 's3_to_redshift', default_args=default_args, schedule_interval=timedelta(days=1),catchup = False)

t_s3filetest = S3KeySensor(task_id='s3_file_test', poke_interval=0, timeout=30, bucket_key='sparktest2/content/*snappy.parquet', wildcard_match = True, aws_conn_id='aws_id', bucket_name='awsbuc01', dag=dag)

t_glue_job = AwsGlueJobOperator(task_id= 'glue_task', job_name="Newtransferjob", script_location="s3://aws-glue-scripts-499365594194-us-east-2/root/Newtransferjob", concurrent_run_limit=None, script_args=None, num_of_dpus = 2, retry_limit=2, aws_conn_id='aws_id', region_name='us-east-2', s3_bucket= 'awsbuc01', iam_role_name = 'AWSGlueServiceRole-newrole4', dag = dag)

t_finished = BashOperator(task_id='task3', depends_on_past=False, bash_command='echo Job finished', dag=dag)

t_s3filetest >> t_glue_job >> t_finished
