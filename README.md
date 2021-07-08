# Pipeline built on GCP with the below services:
## Google Clous SQL : Create a manager MySQL DB and load it with Chicago Taxi Trips public data
## Google Dataproc : Spin up a cluster and submit SQOOP job to unload the data from Cloud SQL to write to a GCS bucket
## Google BigQuery: Load the data from GCS to BQ for further analysis
## All these are automated through a Cloud Composer airflow DAG which provisions these services and at the end deletes the Dataproc cluster too
