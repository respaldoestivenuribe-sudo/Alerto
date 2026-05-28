*** Settings ***
Documentation    MÓDULO SIMULADOR — TC-SIM-001 al TC-SIM-003
...              Requisito: RF-002
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Library          Collections
Suite Setup      Setup Suite SIM
Suite Teardown   Teardown Suite SIM

*** Variables ***
${SUITE_TOKEN}    ${EMPTY}

*** Test Cases ***

TC-SIM-001 Simulador valida que precip 3h es mayor o igual a precip 1h
    [Documentation]    RF-002 — precip_3h < precip_1h debe retornar HTTP 422
    [Tags]    SIM    Media    Funcional    TC-SIM-001
    &{body}=    Create Dictionary    precip_1h=${20}    precip_3h=${10}    humedad=${50}
    ${resp}=    POST Authenticated    /api/simulate    ${body}    ${SUITE_TOKEN}
    Response Should Have Status    ${resp}    422
    Log    ✓ HTTP 422 para precip_3h (10) < precip_1h (20)    level=INFO

TC-SIM-002 Simulación exitosa dispara el pipeline y genera resultado
    [Documentation]    RF-002 — POST /api/simulate con valores válidos retorna 200 y dispara DAG
    [Tags]    SIM    Alta    Funcional    Integración    TC-SIM-002
    &{body}=    Create Dictionary    precip_1h=${10}    precip_3h=${20}    humedad=${70}
    ${resp}=    POST Authenticated    /api/simulate    ${body}    ${SUITE_TOKEN}
    Should Be True    ${resp.status_code} in [200, 202]
    ...    msg=Simulación falló: HTTP ${resp.status_code}. Body: ${resp.text}
    Response Body Should Contain Key    ${resp}    message
    ${msg}=    Get From Dictionary    ${resp.json()}    message
    Should Not Be Empty    ${msg}
    Log    ✓ Simulación AMARILLO disparada: ${msg}    level=INFO

TC-SIM-003 Simulador rechaza valores fuera del rango permitido
    [Documentation]    RF-002 — Valores > máximo deben retornar HTTP 422 con detalle
    [Tags]    SIM    Media    Funcional    TC-SIM-003
    &{body}=    Create Dictionary    precip_1h=${200}    precip_3h=${300}    humedad=${150}
    ${resp}=    POST Authenticated    /api/simulate    ${body}    ${SUITE_TOKEN}
    Response Should Have Status    ${resp}    422
    ${detail}=    Set Variable    ${resp.json()}
    Log    Detalle de validación: ${detail}    level=INFO
    Log    ✓ HTTP 422 con errores de validación para valores fuera de rango    level=INFO

*** Keywords ***

Setup Suite SIM
    Log    === Iniciando Suite SIM ===    level=INFO
    Create API Session
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}

Teardown Suite SIM
    Log    === Suite SIM completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
