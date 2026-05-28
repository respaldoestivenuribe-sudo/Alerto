FROM apache/airflow:2.9.0

USER root
COPY entrypoint-scheduler.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

USER root
ENTRYPOINT ["/entrypoint.sh"]