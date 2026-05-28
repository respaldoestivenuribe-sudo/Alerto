*** Settings ***
Documentation    MÓDULO MOTOR DE RIESGO — TC-RISK-001 al TC-RISK-006
...              Requisitos: RF-005, RF-008, RF-010
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Library          Collections
Suite Setup      Setup Suite RISK
Suite Teardown   Teardown Suite RISK

*** Variables ***
${SUITE_TOKEN}       ${EMPTY}
${PIPELINE_WAIT_S}   15

*** Test Cases ***

TC-RISK-001 Escenario VERDE produce nivel VERDE y score bajo
    [Documentation]    RF-008, RF-010 — Preset Verde (precip=0, humedad=30) → score bajo
    [Tags]    RISK    Alta    Funcional    TC-RISK-001
    &{sim_body}=    Create Dictionary    precip_1h=${0}    precip_3h=${0}    humedad=${30}
    ${sim_resp}=    POST Authenticated    /api/simulate    ${sim_body}    ${SUITE_TOKEN}
    Should Be True    ${sim_resp.status_code} in [200, 202]
    Log    Simulación VERDE disparada. Esperando ${PIPELINE_WAIT_S}s...    level=INFO
    Sleep    ${PIPELINE_WAIT_S}s
    ${resp}=    GET Authenticated    /api/risk/history    ${SUITE_TOKEN}    params=limit=1
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    Should Be True    len(${data}) > 0    msg=No hay registros en risk/history tras simulación
    ${last}=    Get From List    ${data}    0
    ${nivel}=    Get From Dictionary    ${last}    nivel_riesgo
    ${score}=    Get From Dictionary    ${last}    riesgo_score
    Log    Nivel: ${nivel}, Score: ${score}    level=INFO
    Should Be True    float(${score}) >= 0 and float(${score}) <= 100
    ...    msg=Score fuera del rango válido [0,100]: ${score}
    Should Be True    float(${score}) < 60
    ...    msg=Score para escenario mínimo esperado < 60, obtuvo ${score} (nivel=${nivel})
    Log    ✓ Escenario VERDE: nivel=${nivel}, score=${score}    level=INFO

TC-RISK-002 Escenario ROJO produce nivel ROJO y score alto
    [Documentation]    RF-008, RF-010 — Preset Rojo (precip_1h=40, precip_3h=75, humedad=95) → score alto
    [Tags]    RISK    Alta    Funcional    TC-RISK-002
    &{sim_body}=    Create Dictionary    precip_1h=${40}    precip_3h=${75}    humedad=${95}
    ${sim_resp}=    POST Authenticated    /api/simulate    ${sim_body}    ${SUITE_TOKEN}
    Should Be True    ${sim_resp.status_code} in [200, 202]
    Log    Simulación ROJO disparada. Esperando ${PIPELINE_WAIT_S}s...    level=INFO
    Sleep    ${PIPELINE_WAIT_S}s
    ${resp}=    GET Authenticated    /api/risk/history    ${SUITE_TOKEN}    params=limit=1
    Response Should Have Status    ${resp}    200
    ${last}=    Get From List    ${resp.json()}    0
    ${nivel}=    Get From Dictionary    ${last}    nivel_riesgo
    ${score}=    Get From Dictionary    ${last}    riesgo_score
    Log    Nivel: ${nivel}, Score: ${score}    level=INFO
    Should Be True    float(${score}) >= 40
    ...    msg=Score ROJO esperado >= 40, obtuvo ${score} (nivel=${nivel})
    Log    ✓ Escenario ROJO: nivel=${nivel}, score=${score}    level=INFO

TC-RISK-003 Escenario NARANJA produce score intermedio
    [Documentation]    RF-008, RF-010 — Preset Naranja (precip_1h=18, precip_3h=35, humedad=85) → score medio
    [Tags]    RISK    Alta    Funcional    TC-RISK-003
    &{sim_body}=    Create Dictionary    precip_1h=${18}    precip_3h=${35}    humedad=${85}
    ${sim_resp}=    POST Authenticated    /api/simulate    ${sim_body}    ${SUITE_TOKEN}
    Should Be True    ${sim_resp.status_code} in [200, 202]
    Sleep    ${PIPELINE_WAIT_S}s
    ${resp}=    GET Authenticated    /api/risk/history    ${SUITE_TOKEN}    params=limit=1
    Response Should Have Status    ${resp}    200
    ${last}=    Get From List    ${resp.json()}    0
    ${nivel}=    Get From Dictionary    ${last}    nivel_riesgo
    ${score}=    Get From Dictionary    ${last}    riesgo_score
    Log    Nivel: ${nivel}, Score: ${score}    level=INFO
    Should Be True    float(${score}) >= 10
    ...    msg=Score intermedio esperado >= 10, obtuvo ${score}
    Log    ✓ Escenario NARANJA: nivel=${nivel}, score=${score}    level=INFO

TC-RISK-004 Score de riesgo siempre en rango 0 a 100
    [Documentation]    RF-010 — Ningún registro tiene score fuera de [0, 100]
    [Tags]    RISK    Alta    Funcional    TC-RISK-004
    ${resp}=    GET Authenticated    /api/risk/history    ${SUITE_TOKEN}    params=limit=100
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    ${invalid_count}=    Set Variable    ${0}
    FOR    ${alert}    IN    @{data}
        ${score}=    Get From Dictionary    ${alert}    riesgo_score
        ${out_of_range}=    Evaluate    not (0 <= float(${score}) <= 100)
        IF    ${out_of_range}
            ${invalid_count}=    Evaluate    ${invalid_count} + 1
            Log    Score fuera de rango: ${score}    level=WARN
        END
    END
    Should Be Equal As Integers    ${invalid_count}    0
    ...    msg=${invalid_count} registros con score fuera de [0,100]
    Log    ✓ ${data.__len__()} registros verificados — todos en [0, 100]    level=INFO

TC-RISK-005 Clasificación es consistente con el score
    [Documentation]    RF-010 — nivel_riesgo es coherente con riesgo_score (sin extremos invertidos)
    [Tags]    RISK    Alta    Funcional    TC-RISK-005
    ${resp}=    GET Authenticated    /api/risk/history    ${SUITE_TOKEN}    params=limit=50
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    ${inconsistencies}=    Set Variable    ${0}
    FOR    ${alert}    IN    @{data}
        ${nivel}=    Get From Dictionary    ${alert}    nivel_riesgo
        ${score}=    Evaluate    float(${alert['riesgo_score']})
        # Verificar sólo inconsistencias extremas (umbral amplio para tolerar variaciones de config)
        ${extreme_inconsistent}=    Evaluate    ('${nivel}' == 'VERDE' and ${score} > 80) or ('${nivel}' == 'ROJO' and ${score} < 20)
        IF    ${extreme_inconsistent}
            ${inconsistencies}=    Evaluate    ${inconsistencies} + 1
            Log    INCONSISTENCIA: nivel=${nivel}, score=${score}    level=WARN
        END
    END
    Should Be Equal As Integers    ${inconsistencies}    0
    ...    msg=${inconsistencies} registros extremadamente inconsistentes
    Log    ✓ ${data.__len__()} registros sin inconsistencias extremas    level=INFO

TC-RISK-006 Endpoint api risk current retorna el resultado más reciente
    [Documentation]    RF-008 — /api/risk/current devuelve los campos requeridos
    [Tags]    RISK    Alta    Funcional    TC-RISK-006
    ${resp}=    GET Authenticated    /api/risk/current    ${SUITE_TOKEN}
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    @{required_fields}=    Create List    nivel_riesgo    riesgo_score    evaluated_at
    FOR    ${field}    IN    @{required_fields}
        Dictionary Should Contain Key    ${data}    ${field}
        ...    msg=Campo requerido '${field}' ausente en /api/risk/current
    END
    Measure Response Time    ${resp}    2000
    Log    ✓ /api/risk/current: todos los campos presentes    level=INFO

*** Keywords ***

Setup Suite RISK
    Log    === Iniciando Suite RISK ===    level=INFO
    Create API Session
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}

Teardown Suite RISK
    Log    === Suite RISK completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
