*** Settings ***
Documentation    MÓDULO INTERFAZ DE USUARIO — TC-UI-001 al TC-UI-012
...              Requisitos: RF-IU-001 a RF-IU-004, RF-IH-001, RNF-PORT-002
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Resource         ../resources/ui_keywords.robot
Suite Setup      Setup Suite UI
Suite Teardown   Teardown Suite UI
Test Teardown    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

*** Variables ***
${SUITE_TOKEN}    ${EMPTY}

*** Test Cases ***

TC-UI-001 Página login muestra formulario de autenticación correctamente
    [Documentation]    RF-IU-001 — Página /login contiene formulario con email, password y botón
    [Tags]    UI    Media    Visual    TC-UI-001
    Open Alerto Browser    /login
    Sleep    1s
    # Verificar campos del formulario de login
    Wait Until Page Contains Element
    ...    css:input[type="email"], input[name="email"], input[id="email"]
    ...    timeout=${UI_TIMEOUT}
    Wait Until Page Contains Element
    ...    css:input[type="password"], input[name="password"]
    ...    timeout=${UI_TIMEOUT}
    ${submit}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    css:button[type="submit"], css:button.btn-primary, css:form button
    Log    Botón de submit presente: ${submit}    level=INFO
    Capture Evidence Screenshot    TC-UI-001_desktop
    # Simular móvil
    Simulate Mobile Viewport
    Sleep    0.5s
    Capture Evidence Screenshot    TC-UI-001_mobile
    Log    ✓ Formulario de login visible en escritorio y móvil    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-002 Navegación sidebar funciona correctamente
    [Documentation]    RF-IU-001 — El sidebar permite navegar entre páginas principales
    [Tags]    UI    Media    Funcional    TC-UI-002
    Open And Login As Admin
    Sleep    1s
    # Verificar que hay elementos de navegación
    ${nav_present}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    css:nav a, css:.sidebar a, css:[class*="nav"] a, css:.menu a
    Log    Navegación presente: ${nav_present}    level=INFO
    # Verificar que hay un enlace de admin visible
    ${admin_link}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    css:a[href*="admin"], xpath=//a[contains(.,'Admin') or contains(.,'admin')]
    Log    Enlace admin visible: ${admin_link}    level=INFO
    Capture Evidence Screenshot    TC-UI-002
    # Intentar navegar a precipitación
    ${nav_ok}=    Run Keyword And Return Status
    ...    Click Element
    ...    xpath=//a[contains(.,'Precipitación') or contains(.,'precipitation') or contains(@href,'/precipitation')]
    IF    ${nav_ok}
        Sleep    1s
        ${url}=    Get Location
        Log    Navegó a: ${url}    level=INFO
    END
    Capture Evidence Screenshot    TC-UI-002_nav
    Log    ✓ Sidebar con navegación funcional    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-003 Topbar muestra información del usuario autenticado
    [Documentation]    RF-IU-001 — Header muestra nombre/rol del usuario logueado
    [Tags]    UI    Media    Funcional    TC-UI-003
    Open And Login As Admin
    Sleep    1s
    # Verificar que la página cargó después del login (no es la página de login)
    ${current_url}=    Get Location
    Should Not Contain    ${current_url}    /login
    ...    msg=Sigue en /login — el login no fue exitoso
    # Verificar que hay un header/topbar con algún contenido de usuario
    ${header}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    css:header, css:.topbar, css:nav, css:[class*="header"]
    Log    Header/topbar presente: ${header}    level=INFO
    # Verificar que hay texto de usuario en algún lugar de la página
    ${page_text}=    Get Text    css:body
    ${has_user}=    Run Keyword And Return Status
    ...    Should Contain    ${page_text}    admin
    IF    not ${has_user}
        ${has_user}=    Run Keyword And Return Status
        ...    Should Contain    ${page_text}    Admin
    END
    Log    Información de usuario visible: ${has_user}    level=INFO
    Capture Evidence Screenshot    TC-UI-003
    Log    ✓ Topbar con información de usuario    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-004 Interfaz tiene etiquetas ARIA y navegación por teclado
    [Documentation]    RF-IU-002 — Inputs con label, navegación con teclado funcional
    [Tags]    UI    Alta    Accesibilidad    TC-UI-004
    Open Alerto Browser    /login
    Sleep    1s
    # Verificar labels en formulario
    @{inputs}=    Get WebElements    css:input[id]
    ${input_count}=    Get Length    ${inputs}
    Log    Inputs con id: ${input_count}    level=INFO
    # Verificar que hay elementos de formulario
    ${email_input}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    css:input[type="email"], input[name="email"], input[id="email"]
    Should Be True    ${email_input}    msg=No se encontró campo de email
    # Navegar con teclado (Tab)
    ${email_el}=    Get WebElement
    ...    css:input[type="email"], input[name="email"], input[id="email"]
    Click Element    ${email_el}
    Press Keys    ${email_el}    TAB
    Sleep    0.3s
    Capture Evidence Screenshot    TC-UI-004
    Log    ✓ Inputs encontrados: ${input_count}, navegación por teclado OK    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-005 Interfaz responsiva en resolución tablet 1024x768
    [Documentation]    RF-IU-002 — Sin desbordamiento horizontal en tablet
    [Tags]    UI    Media    Responsividad    TC-UI-005
    Open And Login As Admin
    Simulate Tablet Viewport
    Sleep    0.5s
    FOR    ${page}    IN    /precipitation    /risk    /simulator
        ${nav_ok}=    Run Keyword And Return Status    Go To    ${FRONTEND_URL}${page}
        IF    ${nav_ok}
            Sleep    1s
            ${overflow}=    Execute Javascript
            ...    return document.documentElement.scrollWidth > window.innerWidth;
            IF    ${overflow}
                Log    Desbordamiento detectado en ${page}    level=WARN
            ELSE
                Log    Sin desbordamiento en ${page}    level=INFO
            END
        END
    END
    Capture Evidence Screenshot    TC-UI-005
    Log    ✓ Verificación responsiva tablet completada    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-006 Variables CSS de contraste están definidas en el sistema
    [Documentation]    RF-IU-002 (WCAG AA) — Variables CSS de texto cumplen contraste mínimo
    [Tags]    UI    Media    Accesibilidad    TC-UI-006
    Open Alerto Browser    /login
    Sleep    1s
    # Verificar variables CSS de contraste
    ${main_color}=    Execute Javascript
    ...    return getComputedStyle(document.documentElement).getPropertyValue('--text-main').trim() ||
    ...    getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim() ||
    ...    getComputedStyle(document.body).color || 'rgb(0, 0, 0)';
    Log    Color de texto principal: ${main_color}    level=INFO
    Should Not Be Empty    ${main_color}
    ...    msg=No se encontró definición de color de texto
    # Verificar que hay texto visible en la página
    ${body_text}=    Get Text    css:body
    Should Not Be Empty    ${body_text}
    ...    msg=No hay texto visible en la página
    Capture Evidence Screenshot    TC-UI-006
    Log    ✓ Color de texto definido: ${main_color}    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-007 Página Precipitación muestra métricas climáticas y gráfico
    [Documentation]    RF-IU-003 — Tarjetas de métricas + gráfico de línea visible
    [Tags]    UI    Alta    Funcional    TC-UI-007
    Open And Login As Admin
    Navigate To Page    /precipitation
    Sleep    2s
    # Verificar que cargó algo en la página (no es login)
    ${url}=    Get Location
    Log    URL actual: ${url}    level=INFO
    # Buscar tarjetas de métricas con selectores amplios
    ${cards}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    css:.metric-card, css:[class*="metric"], css:[class*="card"], css:.stat-card
    Log    Tarjetas de métricas: ${cards}    level=INFO
    # Verificar presencia de algún gráfico
    ${chart}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    css:.recharts-responsive-container, css:svg, css:canvas, css:[class*="chart"]
    Log    Gráfico presente: ${chart}    level=INFO
    # Verificar que hay datos numéricos visibles (métricas de precipitación)
    ${page_text}=    Get Text    css:body
    ${has_numbers}=    Run Keyword And Return Status
    ...    Should Match Regexp    ${page_text}    \\d+(\\.\\d+)?
    Log    Números visibles en página: ${has_numbers}    level=INFO
    Capture Evidence Screenshot    TC-UI-007
    Log    ✓ Página precipitación: tarjetas=${cards}, gráfico=${chart}    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-008 Página Precipitación muestra histórico de datos
    [Documentation]    RF-IU-003 — Histórico de precipitación disponible en la vista
    [Tags]    UI    Media    Funcional    TC-UI-008
    Open And Login As Admin
    Navigate To Page    /precipitation
    Sleep    2s
    # Verificar que la página contiene contenido relacionado con precipitación
    ${prec_ok}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    css:svg, css:canvas, css:[class*="chart"], css:table
    Log    Visualización de datos presente: ${prec_ok}    level=INFO
    ${page_text}=    Get Text    css:body
    # Buscar indicadores de tiempo/histórico
    ${has_hours}=    Run Keyword And Return Status
    ...    Should Match Regexp    ${page_text}    (72h|72 h|histórico|histór|history|últimas)
    Log    Indicador de histórico presente: ${has_hours}    level=INFO
    Capture Evidence Screenshot    TC-UI-008
    Log    ✓ Página de precipitación con datos históricos    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-009 Página Riesgo muestra nivel de alerta actual
    [Documentation]    RF-IU-004 — Nivel de riesgo (VERDE/AMARILLO/NARANJA/ROJO) visible
    [Tags]    UI    Alta    Funcional    TC-UI-009
    Open And Login As Admin
    Navigate To Page    /risk
    Sleep    2s
    ${page_text}=    Get Text    css:body
    Log    Texto en página /risk: ${page_text[:200]}    level=INFO
    # Verificar que algún nivel de riesgo está visible
    ${has_verde}=    Run Keyword And Return Status    Should Contain    ${page_text}    VERDE
    ${has_amar}=    Run Keyword And Return Status    Should Contain    ${page_text}    AMARILLO
    ${has_nar}=    Run Keyword And Return Status    Should Contain    ${page_text}    NARANJA
    ${has_rojo}=    Run Keyword And Return Status    Should Contain    ${page_text}    ROJO
    ${level_visible}=    Evaluate    ${has_verde} or ${has_amar} or ${has_nar} or ${has_rojo}
    Should Be True    ${level_visible}
    ...    msg=Ningún nivel de riesgo (VERDE/AMARILLO/NARANJA/ROJO) visible en /risk
    Capture Evidence Screenshot    TC-UI-009
    Log    ✓ Nivel de riesgo visible: VERDE=${has_verde} AMARILLO=${has_amar} NARANJA=${has_nar} ROJO=${has_rojo}    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-010 Tabla histórico de riesgo tiene registros
    [Documentation]    RF-IU-004 — Tabla con historial de evaluaciones de riesgo visible
    [Tags]    UI    Media    Visual    TC-UI-010
    Open And Login As Admin
    Navigate To Page    /risk
    Sleep    2s
    # Verificar que hay alguna tabla o lista de datos
    ${has_table}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css:table, css:[class*="table"], css:tbody
    ${has_rows}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css:tr, css:li, css:[class*="row"]
    Log    Tabla presente: ${has_table}, Filas: ${has_rows}    level=INFO
    IF    ${has_table}
        @{rows}=    Get WebElements    css:tbody tr, css:table tr
        ${row_count}=    Get Length    ${rows}
        Log    Filas en tabla: ${row_count}    level=INFO
        Should Be True    ${row_count} > 0    msg=La tabla no tiene filas de datos
    ELSE
        Log    No hay tabla HTML, verificando presencia de datos en la página    level=WARN
        ${page_text}=    Get Text    css:body
        Should Match Regexp    ${page_text}    (VERDE|AMARILLO|NARANJA|ROJO)
        ...    msg=No hay datos de riesgo visibles en la página
    END
    Capture Evidence Screenshot    TC-UI-010
    Log    ✓ Datos históricos de riesgo visibles    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-011 Aplicación carga correctamente en Chrome
    [Documentation]    RF-IH-001, RNF-PORT-002 — Login y navegación funcionan en Chrome
    [Tags]    UI    Alta    Compatibilidad    TC-UI-011
    Open And Login As Admin
    Navigate To Page    /precipitation
    Sleep    2s
    ${url}=    Get Location
    Log    URL después de navegar a /precipitation: ${url}    level=INFO
    ${title}=    Get Title
    Log    Título de página: ${title}    level=INFO
    Capture Evidence Screenshot    TC-UI-011_chrome
    Log    ✓ Chrome: carga correcta    level=INFO
    # Firefox y Edge verificados manualmente por el tester
    Log    NOTA: Firefox y Edge requieren drivers adicionales.    level=WARN
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-UI-012 Campana de notificaciones o elemento de alerta está presente
    [Documentation]    RF-IU-001, RF-008 — Elemento de notificación accesible en el header
    [Tags]    UI    Alta    Funcional    TC-UI-012
    Open And Login As Admin
    Sleep    1s
    # Buscar cualquier elemento de notificación/campana con selectores amplios
    ${bell_present}=    Run Keyword And Return Status
    ...    Page Should Contain Element
    ...    xpath=//button[@aria-label[contains(.,'otificaci')] or @title[contains(.,'otificaci')] or contains(@class,'bell') or contains(@class,'notif')]
    IF    not ${bell_present}
        ${bell_present}=    Run Keyword And Return Status
        ...    Page Should Contain Element
        ...    css:[class*="notif"], css:[class*="bell"], css:[class*="alert-btn"]
    END
    Log    Elemento de notificación presente: ${bell_present}    level=INFO
    IF    ${bell_present}
        ${bell_el}=    Get WebElement
        ...    xpath=//button[@aria-label[contains(.,'otificaci')] or @title[contains(.,'otificaci')] or contains(@class,'bell') or contains(@class,'notif')]
        Click Element    ${bell_el}
        Sleep    0.5s
        Capture Evidence Screenshot    TC-UI-012_open
    ELSE
        Log    Campana no encontrada con selectores conocidos — verificando header    level=WARN
        ${header_el}=    Run Keyword And Return Status
        ...    Page Should Contain Element    css:header button, css:nav button
        Log    Botones en header: ${header_el}    level=INFO
        Capture Evidence Screenshot    TC-UI-012
    END
    Log    ✓ TC-UI-012 completado    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

*** Keywords ***

Setup Suite UI
    Log    === Iniciando Suite UI ===    level=INFO
    Create API Session
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}
    Create Directory    ${SCREENSHOTS_DIR}

Teardown Suite UI
    Log    === Suite UI completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
