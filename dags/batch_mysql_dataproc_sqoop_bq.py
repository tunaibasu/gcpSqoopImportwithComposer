from datetime import datetime, timedelta
from airflow import models
from airflow import DAG
from airflow.contrib.operators.dataproc_operator import DataprocClusterCreateOperator
from airflow.contrib.operators.dataproc_operator import DataprocClusterDeleteOperator
from airflow.contrib.operators.dataproc_operator import DataprocHadoopOperator
from airflow import models
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.bigquery_operator import (
    BigQueryOperator,
)
from airflow.contrib.operators.bigquery_check_operator import BigQueryCheckOperator
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.contrib.hooks.bigquery_hook import BigQueryHook
from airflow.contrib.operators.gcs_to_gcs import (
    GoogleCloudStorageToGoogleCloudStorageOperator,
)
from airflow.contrib.operators import bigquery_operator

BUCKET = "gs://taxi-trips-exalted-tape-316818"
BUCKET_WO_NS="taxi-trips-exalted-tape-316818"
instance_name = "mysql-taxi-trip"
project_id = "exalted-tape-316818"
dataset="taxi_trips"
region="us-central1"

DEFAULT_DAG_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.utcnow(),
    'email_on_failure': False,
    'email_on_retry': False,
    'project_id': project_id, 
    'schedule_interval': "@once",
    'region':'us-central1'
}


with DAG('sqoop_pipeline',
         default_args=DEFAULT_DAG_ARGS) as dag:  # Here we are using dag as context.

    create_cluster = DataprocClusterCreateOperator(
        task_id='create_sqoop_cluster',
        cluster_name="my-dp-cluster",
        master_machine_type='n1-standard-1',
        worker_machine_type='n1-standard-2',
        init_actions_uris=["gs://dataproc-initialization-actions/cloud-sql-proxy/cloud-sql-proxy.sh"],
        num_workers=2,
        region='us-central1',
        zone='us-central1-a',
        service_account_scopes=["https://www.googleapis.com/auth/sqlservice.admin"],
        properties={"hive:hive.metastore.warehouse.dir":BUCKET+"/hive-warehouse"},
        metadata={"additional-cloud-sql-instances":project_id+":"+region+":"+instance_name+"=tcp:3307","enable-cloud-sql-hive-metastore":"false"},
        image_version="1.2"
    )

    sqoop_inc_import = BashOperator(
	    task_id= 'sqoop_db_import',
	    bash_command="bash /home/airflow/gcs/plugins/submit_dataproc.sh my-dp-cluster",
	    dag=dag
	)

    bq_load_taxi_trips = GoogleCloudStorageToBigQueryOperator(
        task_id = "bq_load_taxi_trips",
        bucket=BUCKET_WO_NS,
        source_objects=["mysql_output/*.avro"],  
        destination_project_dataset_table=dataset+".chicago_taxi_trips",        
        autodetect=True,
        source_format="AVRO",
        create_disposition="CREATE_IF_NEEDED",
        skip_leading_rows=0,
        write_disposition="WRITE_APPEND",
        max_bad_records=0   
    )

    delete_cluster = DataprocClusterDeleteOperator(
        task_id='delete_dataproc_cluster',
        cluster_name="my-dp-cluster",
        region='us-central1',
        project_id=project_id
        #trigger_rule=TriggerRule.ALL_DONE
    )
    create_cluster.dag = dag
    create_cluster.set_downstream(sqoop_inc_import)
    sqoop_inc_import.set_downstream(bq_load_taxi_trips)
    bq_load_taxi_trips.set_downstream(delete_cluster)
 