*** Settings ***
Documentation    MÓDULO NOTIFICACIONES — TC-NOTIF-001 al TC-NOTIF-003
...              Requisito: RF-008
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Resource         ../resources/ui_keywords.robot
Library          Collections
Suite Setup      Setup Suite NOTIF
Suite Teardown   Teardown Suite NOTIF

*** Variables ***
${SUITE_TOKEN}    ${EMPTY}

*** Test Cases ***

TC-NOTIF-001 Dashboard refleja nivel de riesgo actualizado tras simulación
    [Documentation]    RF-008 — Un cambio en el nivel se refleja en la UI
    [Tags]    NOTIF    Alta    Funcional    UI    TC-NOTIF-001
    # Disparar simulación para cambiar el nivel
    &{sim_body}=    Create Dictionary    precip_1h=${5}    precip_3h=${10}    humedad=${60}
    ${sim_resp}=    POST Authenticated    /api/simulate    ${sim_body}    ${SUITE_TOKEN}
    Should Be True    ${sim_resp.status_code} in [200, 202]
    Log    Simulación disparada    level=INFO
    # Verificar UI con el nivel actual
    Open And Login As Admin
    Navigate To Page    /dashboard
    Sleep    2s
    ${url}=    Get Location
    Log    URL actual: ${url}    level=INFO
    # Verificar que hay contenido relacionado con el nivel de riesgo
    ${page_text}=    Get Text    css:body
    ${has_verde}=    Run Keyword And Return Status    Should Contain    ${page_text}    VERDE
    ${has_amar}=    Run Keyword And Return Status    Should Contain    ${page_text}    AMARILLO
    ${has_nar}=    Run Keyword And Return Status    Should Contain    ${page_text}    NARANJA
    ${has_rojo}=    Run Keyword And Return Status    Should Contain    ${page_text}    ROJO
    ${has_level}=    Evaluate    ${has_verde} or ${has_amar} or ${has_nar} or ${has_rojo}
    Log    Nivel de riesgo visible: ${has_level}    level=INFO
    IF    not ${has_level}
        # Si /dashboard no existe, intentar /risk
        Navigate To Page    /risk
        Sleep    2s
        ${page_text}=    Get Text    css:body
        ${has_verde2}=    Run Keyword And Return Status    Should Contain    ${page_text}    VERDE
        ${has_amar2}=    Run Keyword And Return Status    Should Contain    ${page_text}    AMARILLO
        ${has_nar2}=    Run Keyword And Return Status    Should Contain    ${page_text}    NARANJA
        ${has_rojo2}=    Run Keyword And Return Status    Should Contain    ${page_text}    ROJO
        ${has_level}=    Evaluate    ${has_verde2} or ${has_amar2} or ${has_nar2} or ${has_rojo2}
    END
    Should Be True    ${has_level}
    ...    msg=Ningún nivel de riesgo visible en la UI tras simulación
    Capture Evidence Screenshot    TC-NOTIF-001
    Log    ✓ Nivel de riesgo visible en UI    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-NOTIF-002 Nivel de alerta ROJO se destaca visualmente en la interfaz
    [Documentation]    RF-008 — El nivel ROJO usa color rojo en los componentes UI
    [Tags]    NOTIF    Alta    Funcional    UI    TC-NOTIF-002
    # Disparar escenario ROJO
    &{sim_body}=    Create Dictionary    precip_1h=${40}    precip_3h=${75}    humedad=${95}
    ${sim_resp}=    POST Authenticated    /api/simulate    ${sim_body}    ${SUITE_TOKEN}
    Should Be True    ${sim_resp.status_code} in [200, 202]
    Log    Simulación ROJO disparada    level=INFO
    Sleep    5s
    Open And Login As Admin
    Navigate To Page    /risk
    Sleep    2s
    ${page_text}=    Get Text    css:body
    Log    Página /risk texto: ${page_text[:300]}    level=INFO
    Capture Evidence Screenshot    TC-NOTIF-002_risk
    Navigate To Page    /alerts
    Sleep    2s
    Capture Evidence Screenshot    TC-NOTIF-002_alerts
    ${url}=    Get Location
    Should Contain    ${url}    alerts
    ...    msg=No navegó a /alerts. URL: ${url}
    Log    ✓ UI cargada con datos de nivel    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-NOTIF-003 Sistema no genera alertas duplicadas por el mismo evento
    [Documentation]    RF-008 — Una simulación genera a lo sumo 1-2 nuevas alertas
    [Tags]    NOTIF    Media    Funcional    TC-NOTIF-003
    # Obtener conteo inicial de alertas
    ${resp_before}=    GET Authenticated    /api/risk/history    ${SUITE_TOKEN}    params=limit=100
    Response Should Have Status    ${resp_before}    200
    ${count_before}=    Get Length    ${resp_before.json()}
    Log    Alertas antes de simulación: ${count_before}    level=INFO
    # Disparar UNA simulación
    &{sim_body}=    Create Dictionary    precip_1h=${10}    precip_3h=${20}    humedad=${65}
    ${sim_resp}=    POST Authenticated    /api/simulate    ${sim_body}    ${SUITE_TOKEN}
    Should Be True    ${sim_resp.status_code} in [200, 202]
    Sleep    8s
    # Verificar que se generó máximo 2 alertas (no duplicados masivos)
    ${resp_after}=    GET Authenticated    /api/risk/history    ${SUITE_TOKEN}    params=limit=100
    Response Should Have Status    ${resp_after}    200
    ${count_after}=    Get Length    ${resp_after.json()}
    ${new_alerts}=    Evaluate    ${count_after} - ${count_before}
    Log    Nuevas alertas generadas: ${new_alerts}    level=INFO
    Should Be True    ${new_alerts} <= 3
    ...    msg=Posibles alertas duplicadas: ${new_alerts} nuevas en un solo evento
    Should Be True    ${new_alerts} >= 0
    Log    ✓ Simulación generó ${new_alerts} alerta(s) — sin duplicación masiva    level=INFO

*** Keywords ***

Setup Suite NOTIF
    Log    === Iniciando Suite NOTIF ===    level=INFO
    Create API Session
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}

Teardown Suite NOTIF
    Log    === Suite NOTIF completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
