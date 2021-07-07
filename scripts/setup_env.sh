
# Setting environment variables
echo Insert your Google Cloud project ID ...
read PROJECT
DATASET=taxi_trips1

# Create BigQuery dataset
gcloud config set project  $PROJECT
gcloud alpha bq datasets create $DATASET \
--description "A dataset that has Chicago City Taxi Trips details populated through DAG; an Apache Airflow data pipeline ran on Cloud Composer."
echo Created $PROJECT.$DATASET

# Create bucket
gsutil mb -l EU gs://taxi-trips-$PROJECT
echo Created gs://taxi-trips-$PROJECT

# Copy data to bucket
gsutil cp -r ../data/ gs://taxi-trips-$PROJECT/data

## Create Cloud Composer
echo Insert the service account to deploy your Cloud Composer environment ...
read SERVICE_ACCOUNT
echo Deploying a Cloud Composer environment on the default network ... This will most likely take longer than 20 minutes ...
gcloud composer environments create subhajit-sqoop-omposer \
--location us-central1 \
--node-count 3 \
--zone us-central1-a \
--machine-type n1-standard-1 \
--disk-size 20 \
--oauth-scopes https://www.googleapis.com/auth/cloud-platform 
--service-account $SERVICE_ACCOUNT \
--tags development \
--image-version composer-1.16.1-airflow-1.10.15 \
--python-version 3 \
--cloud-sql-machine-type db-n1-standard-2 \
--network default \
--web-server-allow-all \
--env-variables environment=development
