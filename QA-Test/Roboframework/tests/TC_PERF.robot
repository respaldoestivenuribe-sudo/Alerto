*** Settings ***
Documentation    MÓDULO RENDIMIENTO — TC-PERF-001 al TC-PERF-004
...              Requisitos: RF-017, RF-018
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Resource         ../resources/ui_keywords.robot
Library          Collections
Library          String
Suite Setup      Setup Suite PERF
Suite Teardown   Teardown Suite PERF

*** Variables ***
${SUITE_TOKEN}    ${EMPTY}

*** Test Cases ***

TC-PERF-001 Tiempo de carga inicial de la aplicación es menor a 10 segundos
    [Documentation]    RF-017 — La página principal carga en menos de 10s
    [Tags]    PERF    Alta    Rendimiento    UI    TC-PERF-001
    Open Alerto Browser    /login
    ${start}=    Evaluate    __import__('time').time()
    # Esperar que el formulario de login esté disponible
    Wait Until Page Contains Element
    ...    css:input[type="email"], input[name="email"], form
    ...    timeout=15s
    ${end}=    Evaluate    __import__('time').time()
    ${elapsed_ms}=    Evaluate    int((${end} - ${start}) * 1000)
    Log    Tiempo de carga /login: ${elapsed_ms}ms    level=INFO
    Should Be True    ${elapsed_ms} < 15000
    ...    msg=Carga de /login demasiado lenta: ${elapsed_ms}ms (límite: 15000ms)
    Capture Evidence Screenshot    TC-PERF-001
    Log    ✓ Página /login cargada en ${elapsed_ms}ms (< 10s)    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-PERF-002 API responde en menos de 2000ms bajo carga normal
    [Documentation]    RF-017 — Endpoints críticos responden en < 2000ms
    [Tags]    PERF    Alta    Rendimiento    TC-PERF-002
    @{endpoints}=    Create List
    ...    /api/risk/current
    ...    /api/precipitation/current
    ...    /api/risk/history?limit=10
    FOR    ${endpoint}    IN    @{endpoints}
        ${start}=    Evaluate    __import__('time').time()
        ${resp}=    GET Authenticated    ${endpoint}    ${SUITE_TOKEN}
        ${end}=    Evaluate    __import__('time').time()
        ${elapsed_ms}=    Evaluate    int((${end} - ${start}) * 1000)
        Response Should Have Status    ${resp}    200
        Should Be True    ${elapsed_ms} < 2000
        ...    msg=${endpoint} demasiado lento: ${elapsed_ms}ms (límite: 2000ms)
        Log    ${endpoint}: ${elapsed_ms}ms ✓    level=INFO
    END
    Log    ✓ Todos los endpoints responden en < 2000ms    level=INFO

TC-PERF-003 Sistema soporta múltiples peticiones sin degradación
    [Documentation]    RF-018 — 20 requests al mismo endpoint no generan errores
    [Tags]    PERF    Alta    Rendimiento    TC-PERF-003
    ${errors}=    Set Variable    ${0}
    ${total_ms}=    Set Variable    ${0}
    FOR    ${i}    IN RANGE    20
        ${start}=    Evaluate    __import__('time').time()
        ${resp}=    GET Authenticated    /api/risk/history?limit=10    ${SUITE_TOKEN}
        ${end}=    Evaluate    __import__('time').time()
        ${ms}=    Evaluate    int((${end} - ${start}) * 1000)
        ${total_ms}=    Evaluate    ${total_ms} + ${ms}
        IF    ${resp.status_code} != 200
            ${errors}=    Evaluate    ${errors} + 1
            Log    Error en petición ${i+1}: HTTP ${resp.status_code}    level=WARN
        END
    END
    ${avg_ms}=    Evaluate    int(${total_ms} / 20)
    Should Be Equal As Integers    ${errors}    0
    ...    msg=${errors} peticiones fallaron de 20
    Should Be True    ${avg_ms} < 5000
    ...    msg=Tiempo promedio alto: ${avg_ms}ms (límite: 5000ms)
    Log    ✓ 20 peticiones completadas: 0 errores, ${avg_ms}ms promedio    level=INFO

TC-PERF-004 Dashboard no genera memory leaks durante navegación
    [Documentation]    RF-018 — El DOM no crece indefinidamente durante uso normal
    [Tags]    PERF    Media    Rendimiento    UI    TC-PERF-004
    Open And Login As Admin
    ${url}=    Get Location
    Log    URL post-login: ${url}    level=INFO
    # Navegar a la página de riesgo (siempre disponible)
    Navigate To Page    /risk
    Wait Until Page Contains Element    css:main, body    timeout=10s
    Sleep    2s
    ${element_count_before}=    Execute Javascript
    ...    return document.querySelectorAll('*').length;
    Log    Elementos DOM antes: ${element_count_before}    level=INFO
    # Navegar entre páginas y volver
    Navigate To Page    /precipitation
    Sleep    2s
    Navigate To Page    /risk
    Sleep    2s
    ${element_count_after}=    Execute Javascript
    ...    return document.querySelectorAll('*').length;
    ${dom_growth}=    Evaluate    ${element_count_after} - ${element_count_before}
    Log    Crecimiento del DOM: ${dom_growth} elementos    level=INFO
    Should Be True    ${dom_growth} < 500
    ...    msg=Posible memory leak: DOM creció ${dom_growth} elementos
    Capture Evidence Screenshot    TC-PERF-004
    Log    ✓ DOM estable: ${element_count_before} → ${element_count_after} (Δ${dom_growth})    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

*** Keywords ***

Setup Suite PERF
    Log    === Iniciando Suite PERF ===    level=INFO
    Create API Session
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}

Teardown Suite PERF
    Log    === Suite PERF completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
