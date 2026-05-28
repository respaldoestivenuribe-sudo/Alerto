FROM apache/airflow:2.9.0

ENV DBT_PROFILES_DIR=/opt/dbt

USER root
COPY airflow/entrypoint-scheduler.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && mkdir -p /opt/airflow/dags /opt/airflow/plugins /opt/dbt \
    && chown -R airflow:0 /opt/airflow /opt/dbt \
    && chmod -R g+rwX /opt/airflow /opt/dbt

USER airflow
COPY airflow/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY --chown=airflow:0 airflow/dags /opt/airflow/dags
COPY --chown=airflow:0 airflow/plugins /opt/airflow/plugins
COPY --chown=airflow:0 dbt /opt/dbt

USER root
ENTRYPOINT ["/entrypoint.sh"]
