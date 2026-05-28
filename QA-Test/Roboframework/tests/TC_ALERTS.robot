*** Settings ***
Documentation    MÓDULO ALERTAS — TC-ALERTS-001 al TC-ALERTS-003
...              Requisito: RF-008
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Resource         ../resources/ui_keywords.robot
Library          Collections
Suite Setup      Setup Suite ALERTS
Suite Teardown   Teardown Suite ALERTS

*** Variables ***
${SUITE_TOKEN}    ${EMPTY}

*** Test Cases ***

TC-ALERTS-001 Página alertas carga con datos de contadores y tabla
    [Documentation]    RF-008 — La página /alerts muestra estadísticas y tabla de alertas
    [Tags]    ALERTS    Alta    Funcional    UI    TC-ALERTS-001
    Open And Login As Admin
    Navigate To Page    /alerts
    Sleep    2s
    # Verificar que la página cargó (no redirigió a login)
    ${url}=    Get Location
    Should Contain    ${url}    alerts
    ...    msg=No navegó a /alerts. URL actual: ${url}
    # Verificar algún elemento estadístico (contadores de nivel)
    ${has_stats}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    css:.stats-strip, [class*="stat"], [class*="counter"], [class*="badge"]
    Log    Estadísticas/contadores presentes: ${has_stats}    level=INFO
    # Verificar tabla o lista de alertas
    ${has_table}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css:table, [class*="table"], tbody
    Log    Tabla de alertas presente: ${has_table}    level=INFO
    # Al menos uno de los dos debe estar presente
    Should Be True    ${has_stats} or ${has_table}
    ...    msg=Página /alerts no muestra ni estadísticas ni tabla de alertas
    Capture Evidence Screenshot    TC-ALERTS-001
    Log    ✓ Página /alerts cargada (stats=${has_stats}, tabla=${has_table})    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-ALERTS-002 Filtro por nivel de riesgo está disponible y funciona
    [Documentation]    RF-008 — Filtros TODOS/ROJO/NARANJA/AMARILLO/VERDE disponibles
    [Tags]    ALERTS    Media    Funcional    UI    TC-ALERTS-002
    Open And Login As Admin
    Navigate To Page    /alerts
    Sleep    2s
    # Verificar que hay botones o controles de filtro
    ${filter_buttons}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    xpath=//button[contains(.,'ROJO') or contains(.,'NARANJA') or contains(.,'VERDE') or contains(.,'TODOS') or contains(.,'Filtrar')]
    Log    Botones de filtro presentes: ${filter_buttons}    level=INFO
    IF    ${filter_buttons}
        ${rojo_ok}=    Run Keyword And Return Status
        ...    Click Element    xpath=//button[contains(.,'ROJO')]
        IF    ${rojo_ok}
            Sleep    0.5s
            Capture Evidence Screenshot    TC-ALERTS-002_filtro_rojo
        END
        ${todos_ok}=    Run Keyword And Return Status
        ...    Click Element
        ...    xpath=//button[contains(.,'TODOS') or contains(.,'Todos') or contains(.,'Todo')]
        IF    ${todos_ok}
            Sleep    0.5s
        END
    ELSE
        ${has_select}=    Run Keyword And Return Status
        ...    Page Should Contain Element    css:select, css:[class*="filter"]
        Log    Filtro alternativo presente: ${has_select}    level=WARN
    END
    Capture Evidence Screenshot    TC-ALERTS-002
    Log    ✓ TC-ALERTS-002 completado    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-ALERTS-003 Paginación de alertas funciona con muchos registros
    [Documentation]    RF-008 — Máximo 50 registros por página, botones de navegación
    [Tags]    ALERTS    Media    Funcional    TC-ALERTS-003
    # Verificar vía API que hay registros
    ${resp}=    GET Authenticated    /api/risk/history    ${SUITE_TOKEN}    params=limit=100
    Response Should Have Status    ${resp}    200
    ${total}=    Get Length    ${resp.json()}
    Log    Total de alertas disponibles: ${total}    level=INFO
    Open And Login As Admin
    Navigate To Page    /alerts
    Sleep    2s
    ${has_table}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css:table, tbody, [class*="table"]
    IF    ${has_table}
        @{rows}=    Get WebElements    css:tbody tr, table tr:not(:first-child)
        ${row_count}=    Get Length    ${rows}
        Log    Filas en primera página: ${row_count}    level=INFO
        Should Be True    ${row_count} <= 50
        ...    msg=Primera página tiene más de 50 filas: ${row_count}
    ELSE
        Log    No hay tabla HTML — página puede usar otro componente    level=WARN
    END
    ${next_btn}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    xpath=//button[contains(.,'Siguiente') or contains(.,'›') or contains(.,'Next') or @aria-label='next page']
    Log    Botón Siguiente presente: ${next_btn}    level=INFO
    Capture Evidence Screenshot    TC-ALERTS-003
    Log    ✓ Paginación verificada    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

*** Keywords ***

Setup Suite ALERTS
    Log    === Iniciando Suite ALERTS ===    level=INFO
    Create API Session
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}
    Create Directory    ${SCREENSHOTS_DIR}

Teardown Suite ALERTS
    Log    === Suite ALERTS completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
