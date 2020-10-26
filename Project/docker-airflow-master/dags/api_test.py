import airflow
import pandas as pd
import requests
import boto3
import json
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator



default_args = {
    'owner': 'Uche',
    'depends_on_past': False,
    'start_date': datetime(2020, 9, 23),
    'email_on_failure': False,
    'email_on_retry': False,
    #'retries': 1,
    #'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG(dag_id = 'api_call', default_args=default_args,catchup = False)

def fetch_list(**context):
	list = pd.read_excel("/usr/local/list/fetch_list.xlsx", skiprows = 0)
	list_json = list.to_json(orient = 'values')
	context['ti'].xcom_push(key = 'user_id', value = list_json)
	
	print('I am okay')
	
def failed_api(*items, **context):
	#set failed list id to 1 to indicate a failed api list was created & write failed list to text file
	context['ti'].xcom_push(key = 'failed_list_id', value = 1)
	
	now = datetime.now()
	date_time = now.strftime("%m_%d_%Y_%H_%M_%S")
	txt_loc ="/usr/local/list/failed_apis_"+date_time+".txt"
	
	with open(txt_loc, 'w+') as f:
		f.writelines(str(items).strip('[]'))
	return
			
		

def check_apilist(**context):
	failed_list = []
	success_list = []
	recieved_value = context['ti'].xcom_pull(key = 'user_id')
	rec_value = json.loads(recieved_value)
	for list in rec_value:
		query_item = list[0]
		app_id = list[1]
		app_key = list[2]
		url = 'https://trackapi.nutritionix.com/v2/search/instant?query='
		request_url = url + str(query_item)
		str_app_id = str(app_id)
		str_app_key = str(app_key)
		response = requests.get(request_url, headers={'x-app-id':str_app_id, 'x-app-key':str_app_key})
		status_check = response.status_code
		if status_check == 200:
			success_list.append(query_item)
		else:
			failed_list.append(query_item)
			
	if len(failed_list) > 0 and len(success_list) == 0:
		failed_api(failed_list, **context)
		
 

				
	
 

fetch_api_list = PythonOperator(task_id = 'api_list', python_callable = fetch_list, provide_context = True, dag=dag)

recieve_api_list = PythonOperator(task_id = 'check_list', python_callable = check_apilist, provide_context = True, dag=dag)



fetch_api_list >> recieve_api_list