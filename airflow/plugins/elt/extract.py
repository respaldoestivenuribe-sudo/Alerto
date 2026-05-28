import requests as rq
from elt.config import OPEN_METEO_CURRENT_URL, OPEN_METEO_HOURLY_URL


class ExtractorBase:
    def __init__(self, source_name):
        self.source   = source_name
        self.raw_data = None

    def extract(self):
        raise NotImplementedError("El método extract debe ser implementado")


class OpenMeteoCurrentExtractor(ExtractorBase):
    def __init__(self):
        super().__init__("OpenMeteo-Current")
        self.url = OPEN_METEO_CURRENT_URL

    def extract(self):
        print(f"Iniciando extracción de {self.source}...")
        try:
            with rq.get(self.url, timeout=10) as response:
                response.raise_for_status()
                self.raw_data = response.json()
                print("Extracción current exitosa")
                return self.raw_data
        except rq.exceptions.RequestException as e:
            print(f"Error en {self.source}: {e}")
            raise


class OpenMeteoHourlyExtractor(ExtractorBase):
    def __init__(self):
        super().__init__("OpenMeteo-Hourly")
        self.url = OPEN_METEO_HOURLY_URL

    def extract(self):
        print(f"Iniciando extracción de {self.source}...")
        try:
            with rq.get(self.url, timeout=10) as response:
                response.raise_for_status()
                self.raw_data = response.json()
                print("Extracción hourly exitosa")
                return self.raw_data
        except rq.exceptions.RequestException as e:
            print(f"Error en {self.source}: {e}")
            raise