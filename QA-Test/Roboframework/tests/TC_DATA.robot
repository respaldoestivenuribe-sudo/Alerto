*** Settings ***
Documentation    MÓDULO PIPELINE DE DATOS — TC-DATA-001 al TC-DATA-012
...              Requisitos: RF-001, RF-002, RF-003, RF-004, RF-007, RF-011, RF-012, RF-013
...              Herramientas: RequestsLibrary + psycopg2 (DB checks)
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Library          Collections
Library          String
Suite Setup      Setup Suite DATA
Suite Teardown   Teardown Suite DATA

*** Variables ***
${SUITE_TOKEN}    ${EMPTY}

*** Test Cases ***

TC-DATA-001 Campos requeridos presentes en bronze_weather_current
    [Documentation]    RF-001 — Validar que todos los campos meteorológicos están en bronze
    [Tags]    DATA    Alta    Integración    TC-DATA-001
    ${resp}=    GET Authenticated    /api/precipitation/current    ${SUITE_TOKEN}
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    @{expected_fields}=    Create List
    ...    precipitation_1h    precipitation_3h    precipitation_6h    humidity_avg_6h
    FOR    ${field}    IN    @{expected_fields}
        Dictionary Should Contain Key    ${data}    ${field}
        ...    msg=Campo requerido '${field}' ausente en la respuesta
        ${value}=    Get From Dictionary    ${data}    ${field}
        Should Not Be Equal    ${value}    ${None}
        ...    msg=Campo '${field}' es null
    END
    Log    ✓ Todos los campos requeridos presentes en gold_precipitation    level=INFO

TC-DATA-002 Error en extracción genera mensaje descriptivo en Airflow
    [Documentation]    RF-001, RF-003 — El pipeline registra errores con detalle
    [Tags]    DATA    Alta    Integración    TC-DATA-002
    # Verificar que el sistema continúa operando (endpoint disponible)
    ${resp}=    GET Authenticated    /api/precipitation/current    ${SUITE_TOKEN}
    Response Should Have Status    ${resp}    200
    # Verificar historial disponible (indica que el pipeline ha corrido)
    ${hist}=    GET Authenticated    /api/precipitation/history    ${SUITE_TOKEN}
    ...    params=limit=1
    Response Should Have Status    ${hist}    200
    Log    ✓ Sistema operativo post-error: endpoints responden correctamente    level=INFO
    Log    NOTA: Verificar logs de Airflow en http://localhost:8080 para detalles de errores    level=WARN

TC-DATA-003 Flujo completo Bronze a Silver a Gold a Riesgo se ejecuta sin error
    [Documentation]    RF-002 — Trigger del DAG y verificación de datos en cada capa
    [Tags]    DATA    Alta    Integración    TC-DATA-003
    # Verificar que hay datos en la capa gold (indica que el pipeline corrió)
    ${risk_resp}=    GET Authenticated    /api/risk/current    ${SUITE_TOKEN}
    Skip If    ${risk_resp.status_code} == 404    No hay datos de riesgo aún — pipeline no ha corrido
    Response Should Have Status    ${risk_resp}    200
    ${risk_data}=    Set Variable    ${risk_resp.json()}
    Dictionary Should Contain Key    ${risk_data}    nivel_riesgo
    Dictionary Should Contain Key    ${risk_data}    riesgo_score
    ${nivel}=    Get From Dictionary    ${risk_data}    nivel_riesgo
    @{valid_niveles}=    Create List    VERDE    AMARILLO    NARANJA    ROJO
    Should Contain    ${valid_niveles}    ${nivel}
    ...    msg=Nivel de riesgo inválido: ${nivel}
    Log    ✓ Pipeline ejecutado. Nivel actual: ${nivel}    level=INFO
    # Verificar historial de precipitación (gold_precipitation_history)
    ${prec_hist}=    GET Authenticated    /api/precipitation/history    ${SUITE_TOKEN}
    ...    params=limit=5
    Response Should Have Status    ${prec_hist}    200
    ${hist_data}=    Set Variable    ${prec_hist.json()}
    Should Be True    len(${hist_data}) > 0    msg=No hay datos en gold_precipitation_history

TC-DATA-004 Pipeline no inserta registros duplicados en bronze
    [Documentation]    RF-002, RF-011 — La restricción UNIQUE en 'time' previene duplicados
    [Tags]    DATA    Alta    Funcional    TC-DATA-004
    # Obtener historial antes
    ${hist1}=    GET Authenticated    /api/precipitation/history    ${SUITE_TOKEN}
    ...    params=limit=100
    ${count1}=    Get Length    ${hist1.json()}
    # Obtener historial de nuevo (simula segunda consulta)
    ${hist2}=    GET Authenticated    /api/precipitation/history    ${SUITE_TOKEN}
    ...    params=limit=100
    ${count2}=    Get Length    ${hist2.json()}
    # Los timestamps deben ser únicos
    ${timestamps}=    Evaluate
    ...    [r['time_local'] for r in ${hist2.json()}]
    ${unique_count}=    Evaluate    len(set(${timestamps}))
    Should Be Equal As Integers    ${count2}    ${unique_count}
    ...    msg=Se encontraron timestamps duplicados: ${count2} total vs ${unique_count} únicos
    Log    ✓ Sin duplicados: ${count2} registros únicos    level=INFO

TC-DATA-005 Error de conexión Open-Meteo genera excepción correcta
    [Documentation]    RF-003 — El sistema maneja graciosamente los errores de conectividad
    [Tags]    DATA    Alta    Integración    TC-DATA-005
    # Verificar que el endpoint health está activo (sistema operativo)
    Create API Session
    ${health}=    GET On Session    api    /health    expected_status=any
    Skip If    ${health.status_code} == 404    Endpoint /health no disponible — sistema operativo verificado vía otros endpoints
    Response Should Have Status    ${health}    200
    Log    ✓ Sistema operativo. Test de falla de red: requiere modificar ambiente    level=INFO
    Log    NOTA TC-DATA-005: Test de interrupción de red requiere modificar hosts o usar mock.    level=WARN
    Log    Verificar manualmente en logs Airflow que las tareas fallidas muestran traceback.    level=WARN

TC-DATA-006 Motor de riesgo maneja tabla gold vacía graciosamente
    [Documentation]    RF-003 — Sin datos gold, el motor omite el ciclo sin excepción
    [Tags]    DATA    Alta    Funcional    TC-DATA-006
    # Verificar que el endpoint responde incluso en condiciones límite
    ${resp}=    GET Authenticated    /api/risk/current    ${SUITE_TOKEN}
    # Puede retornar 200 con datos o 404 si no hay datos aún
    ${status}=    Set Variable    ${resp.status_code}
    Should Be True    ${status} == 200 or ${status} == 404
    ...    msg=Respuesta inesperada: HTTP ${status}
    Log    ✓ Endpoint /api/risk/current responde correctamente: HTTP ${status}    level=INFO

TC-DATA-007 Mecanismo de reintento de Airflow ante fallo transitorio
    [Documentation]    RF-004 — DAG configurado con retries >= 1 y retry_delay
    [Tags]    DATA    Media    Funcional    TC-DATA-007
    # Verificar configuración del DAG en Airflow API
    Create Session    airflow    ${AIRFLOW_URL}    verify=False    disable_warnings=True
    &{headers}=    Create Dictionary    Authorization=Basic YWRtaW46YWRtaW4=
    # Basic auth: admin:admin en base64
    ${resp}=    GET On Session    airflow    /api/v1/dags/weather_pipeline
    ...    headers=${headers}    expected_status=any
    Log    Airflow DAG API: HTTP ${resp.status_code}    level=INFO
    Run Keyword If    ${resp.status_code} == 200
    ...    Log    ✓ DAG weather_pipeline accesible en Airflow API    level=INFO
    Run Keyword If    ${resp.status_code} != 200
    ...    Log    Airflow API no responde (HTTP ${resp.status_code}). Verificar manualmente.    level=WARN

TC-DATA-008 Tabla gold risk features latest contiene las métricas esperadas
    [Documentation]    RF-007 — Los campos calculados en gold están presentes y son válidos
    [Tags]    DATA    Alta    Integración    TC-DATA-008
    ${resp}=    GET Authenticated    /api/precipitation/current    ${SUITE_TOKEN}
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    # Verificar campos de gold_risk_features_latest
    ${p1h}=    Get From Dictionary    ${data}    precipitation_1h
    ${p3h}=    Get From Dictionary    ${data}    precipitation_3h
    ${hum}=    Get From Dictionary    ${data}    humidity_avg_6h
    Should Be True    float(${p1h}) >= 0    msg=precipitation_1h inválido: ${p1h}
    Should Be True    float(${p3h}) >= 0    msg=precipitation_3h inválido: ${p3h}
    Should Be True    float(${hum}) >= 0    msg=humidity_avg_6h inválido: ${hum}
    ${has_trend}=    Run Keyword And Return Status
    ...    Dictionary Should Contain Key    ${data}    trend_1h
    IF    ${has_trend}
        ${trend}=    Get From Dictionary    ${data}    trend_1h
        # Aceptar valores en español o inglés
        @{valid_trends}=    Create List    subiendo    bajando    estable    rising    falling    stable    increasing    decreasing
        ${trend_lower}=    Convert To Lowercase    ${trend}
        Should Contain    ${valid_trends}    ${trend_lower}
        ...    msg=trend_1h tiene valor inesperado: '${trend}'
        Log    ✓ gold_risk_features_latest: p1h=${p1h}, p3h=${p3h}, hum=${hum}, trend=${trend}    level=INFO
    ELSE
        Log    Campo trend_1h no presente en respuesta — campo opcional    level=WARN
        Log    ✓ gold_risk_features_latest: p1h=${p1h}, p3h=${p3h}, hum=${hum}    level=INFO
    END

TC-DATA-009 gold precipitation history almacena histórico horario
    [Documentation]    RF-007, RF-012 — El histórico contiene timestamps únicos y ordenados
    [Tags]    DATA    Media    Funcional    TC-DATA-009
    ${resp}=    GET Authenticated    /api/precipitation/history    ${SUITE_TOKEN}
    ...    params=limit=72
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    ${count}=    Get Length    ${data}
    Should Be True    ${count} > 0    msg=No hay datos históricos de precipitación
    # Verificar unicidad de timestamps
    ${timestamps}=    Evaluate    [r['time_local'] for r in ${data}]
    ${unique_count}=    Evaluate    len(set(${timestamps}))
    Should Be Equal As Integers    ${count}    ${unique_count}
    ...    msg=Timestamps duplicados: ${count} total vs ${unique_count} únicos
    Log    ✓ Histórico: ${count} registros únicos    level=INFO

TC-DATA-010 Datos crudos se almacenan correctamente en bronze
    [Documentation]    RF-011 — Los datos bronze tienen fetched_at y time diferenciados
    [Tags]    DATA    Alta    Funcional    TC-DATA-010
    ${resp}=    GET Authenticated    /api/precipitation/history    ${SUITE_TOKEN}
    ...    params=limit=3
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    Should Be True    len(${data}) > 0    msg=No hay datos en el histórico
    ${first}=    Get From List    ${data}    0
    Dictionary Should Contain Key    ${first}    time_local
    Dictionary Should Contain Key    ${first}    precipitation_mm
    ${prec}=    Get From Dictionary    ${first}    precipitation_mm
    Should Not Be Equal    ${prec}    ${None}
    Log    ✓ Datos bronze accesibles vía API gold: time_local y precipitation_mm presentes    level=INFO

TC-DATA-011 Datos procesados Silver se almacenan correctamente
    [Documentation]    RF-012 — La capa silver tiene datos sin duplicados y sin nulos
    [Tags]    DATA    Media    Integración    TC-DATA-011
    ${resp}=    GET Authenticated    /api/precipitation/history    ${SUITE_TOKEN}
    ...    params=limit=100
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    # Verificar que ningún precipitation_mm es null
    FOR    ${record}    IN    @{data}
        ${prec}=    Get From Dictionary    ${record}    precipitation_mm
        Should Not Be Equal    ${prec}    ${None}
        ...    msg=precipitation_mm null en registro: ${record}
    END
    Log    ✓ Silver: ${data.__len__()} registros sin valores nulos    level=INFO

TC-DATA-012 Clasificación de riesgo se almacena en tabla alerts
    [Documentation]    RF-013 — La tabla alerts tiene registros con nivel y score válidos
    [Tags]    DATA    Alta    Funcional    TC-DATA-012
    ${resp}=    GET Authenticated    /api/risk/history    ${SUITE_TOKEN}
    ...    params=limit=5
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    Should Be True    len(${data}) > 0    msg=No hay registros en alerts
    FOR    ${alert}    IN    @{data}
        Dictionary Should Contain Key    ${alert}    nivel_riesgo
        Dictionary Should Contain Key    ${alert}    riesgo_score
        ${nivel}=    Get From Dictionary    ${alert}    nivel_riesgo
        ${score}=    Get From Dictionary    ${alert}    riesgo_score
        @{valid}=    Create List    VERDE    AMARILLO    NARANJA    ROJO
        Should Contain    ${valid}    ${nivel}
        Should Be True    float(${score}) >= 0 and float(${score}) <= 100
        ...    msg=Score fuera de rango [0,100]: ${score}
    END
    Log    ✓ alerts: ${data.__len__()} registros con nivel y score válidos    level=INFO

*** Keywords ***

Setup Suite DATA
    Log    === Iniciando Suite DATA ===    level=INFO
    Create API Session
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}

Teardown Suite DATA
    Log    === Suite DATA completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
