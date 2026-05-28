FROM python:3.11-slim

ENV DBT_PROFILES_DIR=/dbt

WORKDIR /dbt

RUN pip install --no-cache-dir dbt-postgres

COPY dbt/ .

RUN printf '#!/bin/sh\nset -e\necho "Instalando paquetes dbt..."\ndbt deps --project-dir /dbt --profiles-dir /dbt\nexec "$@"\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["tail", "-f", "/dev/null"]
