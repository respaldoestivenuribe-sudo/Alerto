# Despliegue en Railway

Este repo funciona como monorepo. Para Railway, crea cada servicio apuntando al
mismo repositorio, con `Root Directory` en `/`, y configura el `Config File Path`
segun esta tabla.

| Servicio en Railway | Config File Path | Publico |
| --- | --- | --- |
| `backend` | `/railway/backend.json` | Opcional |
| `frontend` | `/railway/frontend.json` | Si |
| `airflow-webserver` | `/railway/airflow-webserver.json` | Opcional |
| `airflow-scheduler` | `/railway/airflow-scheduler.json` | No |
| `dbt` | `/railway/dbt.json` | No, opcional |
| `Postgres` | Plantilla PostgreSQL de Railway | No |

El servicio `dbt` es opcional porque las imagenes de Airflow ya copian el
proyecto `dbt/` y ejecutan dbt desde los DAGs.

## Variables

Si el servicio de base de datos no se llama `Postgres`, cambia ese nombre en las
referencias.

### backend

```env
PORT=8000
DATABASE_URL=${{Postgres.DATABASE_URL}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
POSTGRES_DB=${{Postgres.PGDATABASE}}
JWT_SECRET=<secret-largo>
AIRFLOW_URL=http://${{airflow-webserver.RAILWAY_PRIVATE_DOMAIN}}:${{airflow-webserver.PORT}}
AIRFLOW_USER=admin
AIRFLOW_PASS=admin
CORS_ORIGINS=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
```

### frontend

```env
PORT=3000
BACKEND_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}
```

### airflow-webserver

```env
PORT=8080
DATABASE_URL=${{Postgres.DATABASE_URL}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
POSTGRES_DB=${{Postgres.PGDATABASE}}
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=${{Postgres.DATABASE_URL}}
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__FERNET_KEY=<fernet-key-valida>
AIRFLOW__WEBSERVER__SECRET_KEY=<secret-largo>
AIRFLOW__API__AUTH_BACKENDS=airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session
```

### airflow-scheduler

Usa las mismas variables de `airflow-webserver`, excepto `PORT`.

### dbt

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
POSTGRES_DB=${{Postgres.PGDATABASE}}
```

## Orden recomendado

1. Crea `Postgres`.
2. Crea `backend`, `airflow-webserver` y `airflow-scheduler`.
3. Crea `frontend`.
4. Genera dominio publico para `frontend`.
5. Si usas `CORS_ORIGINS` con el dominio del frontend, redeploya `backend`
   despues de generar el dominio.

Para generar una `AIRFLOW__CORE__FERNET_KEY` valida:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
