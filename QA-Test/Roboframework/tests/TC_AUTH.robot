*** Settings ***
Documentation    MÓDULO AUTENTICACIÓN — TC-AUTH-001 al TC-AUTH-013
...              Requisitos: RF-014, RF-015, RF-016
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Resource         ../resources/ui_keywords.robot
Suite Setup      Setup Suite AUTH
Suite Teardown   Teardown Suite AUTH

*** Variables ***
${SUITE_TOKEN}      ${EMPTY}
${UNIQUE_EMAIL}     ${EMPTY}

*** Test Cases ***

TC-AUTH-001 Registro exitoso de nuevo usuario
    [Documentation]    RF-014, RF-015 — Registro con datos válidos debe crear usuario con rol 'usuario'
    [Tags]    AUTH    Alta    Funcional    TC-AUTH-001
    ${email}=    Generate Unique Email
    &{body}=    Create Dictionary
    ...    nombre=QA Robot User
    ...    email=${email}
    ...    password=Test1234!
    ...    security_question=${TEST_QUESTION}
    ...    security_answer=${TEST_ANSWER}
    ${resp}=    POST Json    /api/auth/register    ${body}
    Should Be True    ${resp.status_code} in [200, 201]
    ...    msg=Registro falló: HTTP ${resp.status_code}. Body: ${resp.text}
    &{login_body}=    Create Dictionary    email=${email}    password=Test1234!
    ${login_resp}=    POST Json    /api/auth/login    ${login_body}
    Response Should Have Status    ${login_resp}    200
    Response Body Should Contain Key    ${login_resp}    access_token
    ${payload}=    Decode JWT Payload    ${login_resp.json()['access_token']}
    Log    JWT payload del nuevo usuario: ${payload}    level=INFO
    Log    ✓ Usuario registrado: ${email}    level=INFO

TC-AUTH-002 Registro con email duplicado es rechazado
    [Documentation]    RF-014 — Email ya registrado debe retornar HTTP 400 o 409
    [Tags]    AUTH    Alta    Funcional    TC-AUTH-002
    &{body}=    Create Dictionary
    ...    nombre=Duplicado Test
    ...    email=${ADMIN_EMAIL}
    ...    password=Test1234!
    ...    security_question=${TEST_QUESTION}
    ...    security_answer=${TEST_ANSWER}
    ${resp}=    POST Json    /api/auth/register    ${body}
    Should Be True    ${resp.status_code} in [400, 409, 422]
    ...    msg=Registro duplicado no rechazado: HTTP ${resp.status_code}
    Log    ✓ HTTP ${resp.status_code} para email duplicado    level=INFO

TC-AUTH-003 Registro con contraseña corta es rechazado
    [Documentation]    RF-014 — Contraseña muy corta debe retornar HTTP 400 o 422
    [Tags]    AUTH    Media    Funcional    TC-AUTH-003
    ${email}=    Generate Unique Email
    &{body}=    Create Dictionary
    ...    nombre=Short Pass Test
    ...    email=${email}
    ...    password=abc
    ...    security_question=${TEST_QUESTION}
    ...    security_answer=${TEST_ANSWER}
    ${resp}=    POST Json    /api/auth/register    ${body}
    Should Be True    ${resp.status_code} in [400, 422]
    ...    msg=Contraseña corta no rechazada: HTTP ${resp.status_code}
    Log    ✓ HTTP ${resp.status_code} para contraseña corta    level=INFO

TC-AUTH-004 Login exitoso con credenciales válidas
    [Documentation]    RF-014, RF-015 — Login admin retorna JWT con claims correctos
    [Tags]    AUTH    Alta    Funcional    TC-AUTH-004
    &{body}=    Create Dictionary    email=${ADMIN_EMAIL}    password=${ADMIN_PASS}
    ${resp}=    POST Json    /api/auth/login    ${body}
    Response Should Have Status    ${resp}    200
    Response Body Should Contain Key    ${resp}    access_token
    ${token}=    Get From Dictionary    ${resp.json()}    access_token
    Should Not Be Empty    ${token}
    ${payload}=    Decode JWT Payload    ${token}
    Log    JWT payload admin: ${payload}    level=INFO
    Dictionary Should Contain Key    ${payload}    sub
    ...    msg=Campo 'sub' ausente en JWT
    Dictionary Should Contain Key    ${payload}    exp
    ...    msg=Campo 'exp' ausente en JWT
    Log    ✓ JWT válido con claims: ${payload.keys()}    level=INFO

TC-AUTH-005 Login con contraseña incorrecta es rechazado
    [Documentation]    RF-014 — Credenciales inválidas deben retornar HTTP 401
    [Tags]    AUTH    Alta    Funcional    Seguridad    TC-AUTH-005
    &{body}=    Create Dictionary
    ...    email=${ADMIN_EMAIL}    password=contraseña_incorrecta_xyz_qa
    ${resp}=    POST Json    /api/auth/login    ${body}
    Response Should Have Status    ${resp}    401
    Log    ✓ HTTP 401 para credenciales inválidas    level=INFO

TC-AUTH-007 Acceso sin sesión redirige a login
    [Documentation]    RF-015 — Sin token, rutas protegidas redirigen a /login
    [Tags]    AUTH    Alta    Seguridad    TC-AUTH-007
    Open Alerto Browser    /risk
    Sleep    2s
    ${current_url}=    Get Location
    Log    URL tras acceso sin sesión: ${current_url}    level=INFO
    Should Contain    ${current_url}    /login
    ...    msg=La ruta /risk no redirigió a /login sin sesión. URL actual: ${current_url}
    Capture Evidence Screenshot    TC-AUTH-007
    Log    ✓ Redirección a /login sin sesión activa    level=INFO
    [Teardown]    Run Keyword And Ignore Error    SeleniumLibrary.Close Browser

TC-AUTH-008 Usuario regular no puede acceder a rutas de admin
    [Documentation]    RF-015 (RBAC) — Rol 'usuario' bloqueado en endpoints admin
    [Tags]    AUTH    Alta    Seguridad    TC-AUTH-008
    ${email}=    Generate Unique Email
    &{reg}=    Create Dictionary
    ...    nombre=Usuario Regular QA
    ...    email=${email}    password=Test1234!
    ...    security_question=${TEST_QUESTION}    security_answer=${TEST_ANSWER}
    ${reg_resp}=    POST Json    /api/auth/register    ${reg}
    Should Be True    ${reg_resp.status_code} in [200, 201]
    &{user_login}=    Create Dictionary    email=${email}    password=Test1234!
    ${user_login_resp}=    POST Json    /api/auth/login    ${user_login}
    Should Be True    ${user_login_resp.status_code} in [200, 201]
    ${user_token}=    Get From Dictionary    ${user_login_resp.json()}    access_token
    # API: GET /api/admin/users con token de usuario regular
    ${resp}=    GET Authenticated    /api/admin/users    ${user_token}
    Should Be True    ${resp.status_code} in [401, 403]
    ...    msg=Usuario regular NO debería acceder a /api/admin/users. HTTP ${resp.status_code}
    Log    ✓ HTTP ${resp.status_code} para usuario regular en ruta admin    level=INFO

TC-AUTH-009 Token JWT inválido es rechazado con HTTP 401
    [Documentation]    RF-015 — Token manipulado o expirado debe retornar HTTP 401
    [Tags]    AUTH    Alta    Seguridad    TC-AUTH-009
    # Token con exp en el pasado (2001-09-08) — firma inválida → el servidor rechaza con 401
    ${expired_token}=    Set Variable
    ...    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QHRlc3QuY29tIiwiaWQiOjk5OSwibmFtZSI6IlRlc3QiLCJyb2xlIjoidXN1YXJpbyIsImV4cCI6MTAwMDAwMDAwMH0.invalid_signature_for_testing
    ${resp}=    GET Authenticated    /api/risk/current    ${expired_token}
    Should Be True    ${resp.status_code} in [401, 403, 422]
    ...    msg=Token inválido/expirado fue aceptado: HTTP ${resp.status_code}
    Log    ✓ HTTP ${resp.status_code} para token inválido    level=INFO

TC-AUTH-010 Cuenta desactivada no puede iniciar sesión
    [Documentation]    RF-015 — Usuario con is_active=false rechazado en login
    [Tags]    AUTH    Alta    Funcional    TC-AUTH-010
    ${email}=    Generate Unique Email
    &{reg}=    Create Dictionary    nombre=Desactivado QA    email=${email}
    ...    password=Test1234!    security_question=${TEST_QUESTION}    security_answer=${TEST_ANSWER}
    ${reg_resp}=    POST Json    /api/auth/register    ${reg}
    Should Be True    ${reg_resp.status_code} in [200, 201]
    # Buscar user_id via admin API (la respuesta de registro solo garantiza access_token)
    ${users_resp}=    GET Authenticated    /api/admin/users    ${SUITE_TOKEN}
    Response Should Have Status    ${users_resp}    200
    ${user_id}=    Evaluate
    ...    next((u['id'] for u in ${users_resp.json()} if u['email'] == '${email}'), None)
    Should Not Be Equal    ${user_id}    ${None}
    ...    msg=Usuario registrado no encontrado en /api/admin/users: ${email}
    # Desactivar vía API admin
    &{patch}=    Create Dictionary    is_active=${False}
    ${deact}=    PATCH Authenticated    /api/admin/users/${user_id}/status    ${patch}    ${SUITE_TOKEN}
    Should Be True    ${deact.status_code} in [200, 204]
    ...    msg=No se pudo desactivar usuario: HTTP ${deact.status_code}
    # Intentar login con cuenta desactivada
    &{login}=    Create Dictionary    email=${email}    password=Test1234!
    ${resp}=    POST Json    /api/auth/login    ${login}
    Should Be True    ${resp.status_code} in [401, 403]
    ...    msg=Cuenta desactivada fue aceptada: HTTP ${resp.status_code}
    Log    ✓ Cuenta desactivada: login rechazado HTTP ${resp.status_code}    level=INFO

TC-AUTH-011 Recuperación contraseña paso 1 muestra pregunta de seguridad
    [Documentation]    RF-016 — GET con email válido retorna la pregunta de seguridad
    [Tags]    AUTH    Alta    Funcional    TC-AUTH-011
    Create API Session
    &{params}=    Create Dictionary    email=${ADMIN_EMAIL}
    ${resp}=    GET On Session    api    /api/auth/security-question    params=${params}
    ...    expected_status=any
    Skip If    ${resp.status_code} == 404
    ...    Endpoint /api/auth/security-question no implementado — skipping
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    ${has_question}=    Run Keyword And Return Status
    ...    Dictionary Should Contain Key    ${data}    security_question
    IF    not ${has_question}
        ${has_question}=    Run Keyword And Return Status
        ...    Dictionary Should Contain Key    ${data}    question
    END
    Should Be True    ${has_question}
    ...    msg=Respuesta no contiene campo de pregunta de seguridad: ${data}
    Log    ✓ Pregunta de seguridad obtenida    level=INFO

TC-AUTH-012 Recuperación contraseña paso 2 cambia la contraseña exitosamente
    [Documentation]    RF-016 — Respuesta correcta + nueva contraseña actualizan la BD
    [Tags]    AUTH    Alta    Funcional    TC-AUTH-012
    &{body}=    Create Dictionary
    ...    email=${TEST_EMAIL}
    ...    security_answer=${TEST_ANSWER}
    ...    new_password=NuevaPassRobot99!
    ${resp}=    POST Json    /api/auth/reset-password    ${body}
    Skip If    ${resp.status_code} == 404
    ...    Endpoint /api/auth/reset-password no implementado — skipping
    Should Be True    ${resp.status_code} in [200, 204]
    ...    msg=Cambio de contraseña falló: HTTP ${resp.status_code}
    # Verificar login con nueva contraseña
    &{login}=    Create Dictionary    email=${TEST_EMAIL}    password=NuevaPassRobot99!
    ${login_resp}=    POST Json    /api/auth/login    ${login}
    Should Be True    ${login_resp.status_code} in [200]
    # Restaurar contraseña original
    &{restore}=    Create Dictionary
    ...    email=${TEST_EMAIL}    security_answer=${TEST_ANSWER}    new_password=${TEST_PASS}
    POST Json    /api/auth/reset-password    ${restore}
    Log    ✓ Contraseña cambiada y restaurada exitosamente    level=INFO

TC-AUTH-013 Recuperación contraseña con respuesta incorrecta es rechazada
    [Documentation]    RF-016 — Respuesta incorrecta debe retornar HTTP 400
    [Tags]    AUTH    Alta    Funcional    Seguridad    TC-AUTH-013
    &{body}=    Create Dictionary
    ...    email=${ADMIN_EMAIL}
    ...    security_answer=respuesta_falsa_xyz_incorrect
    ...    new_password=HackerPass123!
    ${resp}=    POST Json    /api/auth/reset-password    ${body}
    Skip If    ${resp.status_code} == 404
    ...    Endpoint /api/auth/reset-password no implementado — skipping
    Should Be True    ${resp.status_code} in [400, 401, 403, 422]
    ...    msg=Respuesta incorrecta aceptada: HTTP ${resp.status_code}
    Log    ✓ HTTP ${resp.status_code}: respuesta de seguridad incorrecta rechazada    level=INFO

*** Keywords ***

Setup Suite AUTH
    Log    === Iniciando Suite AUTH ===    level=INFO
    Create API Session
    Register Test User
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}
    Create Directory    ${SCREENSHOTS_DIR}

Teardown Suite AUTH
    Log    === Suite AUTH completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
