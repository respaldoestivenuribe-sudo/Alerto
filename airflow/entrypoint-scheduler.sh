#!/bin/bash

mkdir -p /opt/dbt/logs
chmod -R 777 /opt/dbt/logs

echo "Esperando a la DB..."
until airflow db check; do
  echo "Postgres no está listo, esperando..."
  sleep 5
done

echo "Iniciando scheduler..."
exec airflow scheduler
