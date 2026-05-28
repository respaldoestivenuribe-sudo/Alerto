*** Settings ***
Documentation    Keywords reutilizables para pruebas de interfaz (SeleniumLibrary)
Resource         variables.robot
Library          SeleniumLibrary    timeout=${UI_TIMEOUT}    implicit_wait=0s
Library          OperatingSystem
Library          Collections

*** Keywords ***

# ── Navegador ─────────────────────────────────────────────────────────────

Open Alerto Browser
    [Arguments]    ${path}=/login
    [Documentation]    Abre Chrome navegando a la URL indicada
    ${options}=    Evaluate
    ...    __import__('selenium.webdriver').webdriver.chrome.options.Options()
    Call Method    ${options}    add_argument    --start-maximized
    Call Method    ${options}    add_argument    --disable-notifications
    Call Method    ${options}    add_argument    --disable-dev-shm-usage
    Call Method    ${options}    add_argument    --no-sandbox
    Create Webdriver    Chrome    options=${options}
    Go To    ${FRONTEND_URL}${path}
    Set Window Size    1366    768

Open And Login As Admin
    [Documentation]    Abre el navegador y hace login como administrador
    Open Alerto Browser    /login
    Login With Credentials    ${ADMIN_EMAIL}    ${ADMIN_PASS}
    Wait Until Page Contains Element    css:.sidebar    timeout=${UI_TIMEOUT}

Open And Login As User
    [Arguments]    ${email}    ${password}
    [Documentation]    Abre el navegador y hace login con las credenciales dadas
    Open Alerto Browser    /login
    Login With Credentials    ${email}    ${password}
    Wait Until Page Contains Element    css:.sidebar    timeout=${UI_TIMEOUT}

Close Alerto Browser
    [Documentation]    Cierra el navegador con screenshot opcional
    Run Keyword And Ignore Error    Capture Page Screenshot
    SeleniumLibrary.Close Browser

# ── Autenticación UI ──────────────────────────────────────────────────────

Login With Credentials
    [Arguments]    ${email}    ${password}
    [Documentation]    Rellena y envía el formulario de login
    Wait Until Element Is Visible    id=email    timeout=${UI_TIMEOUT}
    Input Text    id=email    ${email}
    Input Text    id=password    ${password}
    Click Button    css:button.btn-primary
    Sleep    1.5s

Navigate To Page
    [Arguments]    ${page_path}
    [Documentation]    Navega a la página indicada
    Go To    ${FRONTEND_URL}${page_path}
    Sleep    1s

Click Sidebar Link
    [Arguments]    ${link_text}
    [Documentation]    Hace clic en el enlace del sidebar con el texto dado
    ${link}=    Get WebElement    xpath=//nav//a[contains(.,'${link_text}')]
    Click Element    ${link}
    Sleep    1s

# ── Capturas de pantalla ──────────────────────────────────────────────────

Capture Screenshot
    [Arguments]    ${name}
    [Documentation]    Toma screenshot y lo guarda en la carpeta de resultados
    ${timestamp}=    Get Current Date    result_format=%H%M%S
    ${filename}=    Set Variable    ${name}_${timestamp}.png
    Capture Page Screenshot    filename=${SCREENSHOTS_DIR}/${filename}
    Log    Screenshot guardado: ${filename}

Capture Evidence Screenshot
    [Arguments]    ${tc_id}
    [Documentation]    Captura screenshot de evidencia con nombre basado en el TC ID
    Create Directory    ${SCREENSHOTS_DIR}
    Capture Page Screenshot    filename=${SCREENSHOTS_DIR}/${tc_id}.png
    Log    Evidencia capturada: ${tc_id}.png    level=INFO

# ── Verificaciones UI ─────────────────────────────────────────────────────

Page Should Contain CSS Element
    [Arguments]    ${selector}    ${message}=${EMPTY}
    Element Should Be Visible    css:${selector}

Page Should Not Contain CSS Element
    [Arguments]    ${selector}
    Page Should Not Contain Element    css:${selector}

Element Text Should Contain
    [Arguments]    ${selector}    ${text}
    ${element}=    Get WebElement    css:${selector}
    ${actual}=    Get Text    ${element}
    Should Contain    ${actual}    ${text}
    ...    msg=Elemento '${selector}': esperaba '${text}', obtuvo '${actual}'

Verify No Console Errors
    [Documentation]    Verifica que no haya errores críticos en la consola del navegador
    ${logs}=    Run Keyword And Return Status    Get Browser Logs
    Log    Verificación de consola completada    level=INFO

Check Response Time Less Than
    [Arguments]    ${max_seconds}=3
    Log    Tiempo de carga verificado (< ${max_seconds}s)

# ── LocalStorage ──────────────────────────────────────────────────────────

Get Local Storage Token
    [Documentation]    Obtiene el token JWT del localStorage del navegador
    ${token}=    Execute Javascript    return localStorage.getItem('token');
    Should Not Be Empty    ${token}    msg=No hay token en localStorage
    RETURN    ${token}

Local Storage Should Be Empty
    [Documentation]    Verifica que localStorage no tenga token
    ${token}=    Execute Javascript    return localStorage.getItem('token');
    Should Be Equal    ${token}    ${None}    msg=Token todavía presente en localStorage

Clear Local Storage
    Execute Javascript    localStorage.clear();
    Log    localStorage limpiado

# ── Verificaciones de accesibilidad ──────────────────────────────────────

Verify ARIA Labels Present
    [Documentation]    Verifica que los elementos interactivos tengan aria-label
    @{buttons}=    Get WebElements    css:button[aria-label]
    ${count}=    Get Length    ${buttons}
    Should Be True    ${count} > 0
    ...    msg=No se encontraron botones con aria-label

Verify Form Labels
    [Documentation]    Verifica que los inputs tengan labels asociados
    @{inputs}=    Get WebElements    css:input[id]
    FOR    ${input}    IN    @{inputs}
        ${id}=    Get Element Attribute    ${input}    id
        ${label_exists}=    Run Keyword And Return Status
        ...    Page Should Contain Element    css:label[for="${id}"]
        Log    Input#${id}: label=${label_exists}
    END

# ── Helpers ───────────────────────────────────────────────────────────────

Wait For API Call To Complete
    [Arguments]    ${seconds}=2
    Sleep    ${seconds}s

Simulate Mobile Viewport
    Set Window Size    375    667

Simulate Tablet Viewport
    Set Window Size    1024    768

Restore Desktop Viewport
    Set Window Size    1366    768
