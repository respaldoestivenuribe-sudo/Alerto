FROM python:3.11-slim

  WORKDIR /dbt

  RUN pip install dbt-postgres

  RUN printf '#!/bin/bash\nset -e\necho "Instalando paquetes dbt..."\ndbt deps --project-dir /dbt --profiles-dir /dbt\nexec "$@"\n' > /entrypoint.sh && chmod +x /entrypoint.sh

  COPY . .

  ENTRYPOINT ["/entrypoint.sh"]
  CMD ["tail", "-f", "/dev/null"]