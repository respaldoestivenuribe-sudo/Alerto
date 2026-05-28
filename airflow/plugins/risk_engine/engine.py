import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def _build_precipitation_system():
    """Etapa 1: precip_1h + precip_3h + intensidad_actual → nivel_lluvia (0–1)"""

    precip_1h_uni    = np.arange(0, 51,   0.5)
    precip_3h_uni    = np.arange(0, 91,   0.5)
    intensidad_uni   = np.arange(0, 41,   0.5)
    nivel_lluvia_uni = np.arange(0, 1.01, 0.01)

    precip_1h    = ctrl.Antecedent(precip_1h_uni,    'precip_1h')
    precip_3h    = ctrl.Antecedent(precip_3h_uni,    'precip_3h')
    intensidad   = ctrl.Antecedent(intensidad_uni,   'intensidad_actual')
    nivel_lluvia = ctrl.Consequent(nivel_lluvia_uni, 'nivel_lluvia')

    precip_1h['baja']     = fuzz.trapmf(precip_1h.universe, [0,  0,  5,  10])
    precip_1h['moderada'] = fuzz.trimf( precip_1h.universe, [8,  16, 25])
    precip_1h['alta']     = fuzz.trimf( precip_1h.universe, [20, 30, 40])
    precip_1h['extrema']  = fuzz.trapmf(precip_1h.universe, [35, 45, 50, 50])

    precip_3h['baja']     = fuzz.trapmf(precip_3h.universe, [0,  0,  10, 20])
    precip_3h['moderada'] = fuzz.trimf( precip_3h.universe, [15, 30, 45])
    precip_3h['alta']     = fuzz.trimf( precip_3h.universe, [40, 55, 70])
    precip_3h['extrema']  = fuzz.trapmf(precip_3h.universe, [60, 75, 90, 90])

    intensidad['debil']      = fuzz.trapmf(intensidad.universe, [0,  0,  2.5, 5])
    intensidad['moderada']   = fuzz.trimf( intensidad.universe, [4,  9.5, 15])
    intensidad['fuerte']     = fuzz.trimf( intensidad.universe, [12, 21,  30])
    intensidad['torrencial'] = fuzz.trapmf(intensidad.universe, [25, 32,  40, 40])

    nivel_lluvia['bajo']  = fuzz.trapmf(nivel_lluvia.universe, [0,   0,   0.2, 0.4])
    nivel_lluvia['medio'] = fuzz.trimf( nivel_lluvia.universe, [0.3, 0.5, 0.7])
    nivel_lluvia['alto']  = fuzz.trapmf(nivel_lluvia.universe, [0.6, 0.8, 1.0, 1.0])

    rules = [
        ctrl.Rule(precip_1h['extrema'] | precip_3h['extrema'] | intensidad['torrencial'], nivel_lluvia['alto']),
        ctrl.Rule(precip_1h['alta']    | intensidad['fuerte'],                             nivel_lluvia['alto']),
        ctrl.Rule(precip_1h['moderada'] & (precip_3h['moderada'] | precip_3h['alta']),    nivel_lluvia['medio']),
        ctrl.Rule(intensidad['moderada'] & precip_1h['moderada'],                          nivel_lluvia['medio']),
        ctrl.Rule(precip_1h['baja'] & precip_3h['baja'] & intensidad['debil'],            nivel_lluvia['bajo']),
        ctrl.Rule(precip_1h['baja'] & intensidad['debil'],                                 nivel_lluvia['bajo']),
    ]

    return ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))


def _build_risk_system():
    """Etapa 2: nivel_lluvia + humedad_prom_6h → riesgo (0–100)"""

    nivel_lluvia_uni = np.arange(0, 1.01, 0.01)
    humedad_uni      = np.arange(0, 101,  1)
    riesgo_uni       = np.arange(0, 101,  1)

    nivel_lluvia = ctrl.Antecedent(nivel_lluvia_uni, 'nivel_lluvia')
    humedad      = ctrl.Antecedent(humedad_uni,      'humedad_prom_6h')
    riesgo       = ctrl.Consequent(riesgo_uni,       'riesgo', defuzzify_method='centroid')

    nivel_lluvia['bajo']  = fuzz.trapmf(nivel_lluvia.universe, [0,   0,   0.2, 0.4])
    nivel_lluvia['medio'] = fuzz.trimf( nivel_lluvia.universe, [0.3, 0.5, 0.7])
    nivel_lluvia['alto']  = fuzz.trapmf(nivel_lluvia.universe, [0.6, 0.8, 1.0, 1.0])

    humedad['seca']     = fuzz.trapmf(humedad.universe, [0,  0,  45, 60])
    humedad['humeda']   = fuzz.trimf( humedad.universe, [55, 67, 80])
    humedad['saturada'] = fuzz.trapmf(humedad.universe, [75, 87, 100, 100])

    riesgo['verde']    = fuzz.trapmf(riesgo.universe, [0,  0,  15, 25])
    riesgo['amarillo'] = fuzz.trimf( riesgo.universe, [20, 37, 50])
    riesgo['naranja']  = fuzz.trimf( riesgo.universe, [45, 62, 75])
    riesgo['rojo']     = fuzz.trapmf(riesgo.universe, [70, 87, 100, 100])

    rules = [
        ctrl.Rule(nivel_lluvia['alto']  & humedad['saturada'], riesgo['rojo']),
        ctrl.Rule(nivel_lluvia['alto']  & humedad['humeda'],   riesgo['naranja']),
        ctrl.Rule(nivel_lluvia['alto']  & humedad['seca'],     riesgo['amarillo']),
        ctrl.Rule(nivel_lluvia['medio'] & humedad['saturada'], riesgo['naranja']),
        ctrl.Rule(nivel_lluvia['medio'] & humedad['humeda'],   riesgo['amarillo']),
        ctrl.Rule(nivel_lluvia['medio'] & humedad['seca'],     riesgo['verde']),
        ctrl.Rule(nivel_lluvia['bajo']  & humedad['saturada'], riesgo['amarillo']),
        ctrl.Rule(nivel_lluvia['bajo']  & humedad['humeda'],   riesgo['verde']),
        ctrl.Rule(nivel_lluvia['bajo']  & humedad['seca'],     riesgo['verde']),
    ]

    return ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))


def calculate_risk(
    precip_1h: float,
    precip_3h: float,
    intensidad_actual: float,
    humedad_prom_6h: float,
) -> dict:

    sim1 = _build_precipitation_system()
    sim1.input['precip_1h']         = min(precip_1h,        50)
    sim1.input['precip_3h']         = min(precip_3h,        90)
    sim1.input['intensidad_actual'] = min(intensidad_actual, 40)
    sim1.compute()
    nivel_lluvia = float(sim1.output['nivel_lluvia'])

    sim2 = _build_risk_system()
    sim2.input['nivel_lluvia']    = nivel_lluvia
    sim2.input['humedad_prom_6h'] = min(humedad_prom_6h, 100)
    sim2.compute()
    riesgo_score = float(sim2.output['riesgo'])

    if riesgo_score < 25:
        nivel_riesgo = "VERDE"
    elif riesgo_score < 50:
        nivel_riesgo = "AMARILLO"
    elif riesgo_score < 75:
        nivel_riesgo = "NARANJA"
    else:
        nivel_riesgo = "ROJO"

    return {
        "nivel_lluvia": round(nivel_lluvia,  4),
        "riesgo_score": round(riesgo_score,  2),
        "nivel_riesgo": nivel_riesgo,
    }


if __name__ == "__main__":
    casos = [
        {"desc": "Sin lluvia, seco",         "p1":  0,  "p3":  0,  "i":  0,  "h": 30},
        {"desc": "Lluvia leve, húmedo",       "p1":  5,  "p3": 12,  "i":  3,  "h": 70},
        {"desc": "Lluvia moderada, saturado", "p1": 18,  "p3": 35,  "i": 14,  "h": 85},
        {"desc": "Lluvia extrema, saturado",  "p1": 40,  "p3": 75,  "i": 30,  "h": 95},
    ]

    for c in casos:
        r = calculate_risk(c["p1"], c["p3"], c["i"], c["h"])
        print(f"[{c['desc']}]")
        print(f"  nivel_lluvia : {r['nivel_lluvia']}")
        print(f"  riesgo_score : {r['riesgo_score']}")
        print(f"  nivel_riesgo : {r['nivel_riesgo']}")
        print()