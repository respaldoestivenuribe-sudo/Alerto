import os
import requests
from sqlalchemy.orm import Session
from app.repositories.simulate_repository import SimulateRepository

AIRFLOW_URL  = os.getenv("AIRFLOW_URL",  "http://airflow-webserver:8080")
AIRFLOW_USER = os.getenv("AIRFLOW_USER", "admin")
AIRFLOW_PASS = os.getenv("AIRFLOW_PASS", "admin")


class SimulateService:

    def __init__(self, db: Session):
        self.repository = SimulateRepository(db)

    def run(self, precip_1h: float, precip_3h: float, humedad: float) -> dict:
        self.repository.insert_bronze(precip_1h, precip_3h, humedad)
        self._trigger_airflow()
        return {
            "status": "ok",
            "message": "Simulación iniciada. El pipeline está procesando los datos."
        }

    def _trigger_airflow(self):
        url      = f"{AIRFLOW_URL}/api/v1/dags/simulate_pipeline/dagRuns"
        response = requests.post(
            url,
            json={"conf": {}},
            auth=(AIRFLOW_USER, AIRFLOW_PASS),
            timeout=10,
        )
        if response.status_code not in (200, 201):
            raise Exception(
                f"Error al disparar Airflow: {response.status_code} — {response.text}"
            )