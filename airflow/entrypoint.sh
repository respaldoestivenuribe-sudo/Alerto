#!/bin/bash

mkdir -p /opt/dbt/logs
chmod -R 777 /opt/dbt/logs

echo "Esperando a Postgres..."
until airflow db check; do
  echo "Postgres no está listo, esperando..."
  sleep 5
done

if [ ! -f "/opt/airflow/airflow.db_initialized" ]; then
  echo "Inicializando DB..."
  airflow db upgrade

  echo "Creando usuario admin..."
  airflow users create \
    --username admin \
    --password admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@mail.com || true

  touch /opt/airflow/airflow.db_initialized
fi

rm -f /opt/airflow/airflow-webserver.pid
echo "Iniciando webserver..."
exec airflow webserver --host 0.0.0.0 --port "${PORT:-8080}"
