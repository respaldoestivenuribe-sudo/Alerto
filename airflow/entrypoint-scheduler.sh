#!/bin/bash

mkdir -p /opt/dbt/logs
chmod -R 777 /opt/dbt/logs

echo "Esperando a la DB..."
until airflow db check; do
  echo "Postgres no está listo, esperando..."
  sleep 5
done

if [ ! -f "/opt/airflow/airflow.db_initialized" ]; then
  echo "Inicializando DB..."
  airflow db upgrade
  touch /opt/airflow/airflow.db_initialized
fi

echo "Iniciando scheduler..."
exec airflow scheduler
