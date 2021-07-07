#!/bin/bash
export CLUSTER_NAME=my-dp-cluster
export REGION=us-central1
export GCS_BUCKET=taxi-trips-exalted-tape-316818
export PROJECT_ID=exalted-tape-316818
export SQL_INSTANCE_NAME=mysql-taxi-trip
export PORT=3307
export DATABASE_NAME=taxi_trip
export DATABASE_USERNAME=root
export TABLE=taxi

gsutil ls gs://$GCS_BUCKET/mysql_output
if [[ $? -eq 0 ]];
then
    gsutil rm -rf gs://$GCS_BUCKET/mysql_output
fi
gcloud dataproc jobs submit hadoop --cluster=$CLUSTER_NAME \
 --region=$REGION --class=org.apache.sqoop.Sqoop \
 --jars=gs://$GCS_BUCKET/sqoop-1.4.7-hadoop260.jar,gs://$GCS_BUCKET/avro-tools-1.8.2.jar,file:///usr/share/java/mysql-connector-java-5.1.49.jar \
 -- import -Dmapreduce.job.user.classpath.first=true -Dmapreduce.job.classloader=true \
 --connect=jdbc:mysql://localhost:$PORT/$DATABASE_NAME --username=$DATABASE_USERNAME \
 --password-file=gs://$GCS_BUCKET/passwordFile.txt \
 --target-dir=gs://$GCS_BUCKET/mysql_output --table=$TABLE \
 --as-avrodatafile