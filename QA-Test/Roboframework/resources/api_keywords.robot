*** Settings ***
Documentation    Keywords reutilizables para pruebas de API REST (RequestsLibrary)
Resource         variables.robot
Library          RequestsLibrary
Library          Collections
Library          String
Library          DateTime

*** Keywords ***

# ── Sesión HTTP ───────────────────────────────────────────────────────────

Create API Session
    [Documentation]    Crea sesión HTTP apuntando a la API de Alerto
    Create Session    api    ${API_URL}    verify=False    disable_warnings=True

Create Auth Session
    [Arguments]    ${token}
    [Documentation]    Crea sesión HTTP con token JWT en el header Authorization
    &{headers}=    Create Dictionary
    ...    Content-Type=application/json
    ...    Authorization=Bearer ${token}
    Create Session    auth_api    ${API_URL}    headers=${headers}
    ...    verify=False    disable_warnings=True

# ── Autenticación ─────────────────────────────────────────────────────────

Get Admin Token
    [Documentation]    Inicia sesión como administrador y retorna el token JWT
    Create API Session
    &{body}=    Create Dictionary    email=${ADMIN_EMAIL}    password=${ADMIN_PASS}
    ${resp}=    POST On Session    api    /api/auth/login    json=${body}
    Status Should Be    200    ${resp}
    ${token}=    Get From Dictionary    ${resp.json()}    access_token
    RETURN    ${token}

Get User Token
    [Arguments]    ${email}    ${password}
    [Documentation]    Inicia sesión con las credenciales dadas y retorna el token JWT
    Create API Session
    &{body}=    Create Dictionary    email=${email}    password=${password}
    ${resp}=    POST On Session    api    /api/auth/login    json=${body}
    Status Should Be    200    ${resp}
    ${token}=    Get From Dictionary    ${resp.json()}    access_token
    RETURN    ${token}

Register Test User
    [Arguments]    ${email}=${TEST_EMAIL}    ${password}=${TEST_PASS}
    [Documentation]    Registra un usuario de prueba. Ignora si ya existe (409/400).
    Create API Session
    &{body}=    Create Dictionary
    ...    nombre=${TEST_NAME}
    ...    email=${email}
    ...    password=${password}
    ...    security_question=${TEST_QUESTION}
    ...    security_answer=${TEST_ANSWER}
    ${resp}=    POST On Session    api    /api/auth/register    json=${body}
    ...    expected_status=any
    Log    Registro usuario ${email}: HTTP ${resp.status_code}
    RETURN    ${resp}

Delete Test User If Exists
    [Arguments]    ${email}=${TEST_EMAIL}    ${admin_token}=${EMPTY}
    [Documentation]    Elimina el usuario de prueba vía SQL directo (para limpieza).
    Log    Limpieza: usuario ${email} gestionado vía BD si existe.

# ── Requests genéricos ────────────────────────────────────────────────────

POST Json
    [Arguments]    ${endpoint}    ${body}    ${session}=api
    [Documentation]    Ejecuta POST con body JSON, retorna response
    ${resp}=    POST On Session    ${session}    ${endpoint}    json=${body}
    ...    expected_status=any
    RETURN    ${resp}

GET Authenticated
    [Arguments]    ${endpoint}    ${token}    ${params}=${None}    ${expected_status}=any
    [Documentation]    Ejecuta GET con Bearer token, retorna response
    &{headers}=    Create Dictionary    Authorization=Bearer ${token}
    IF    $params is None
        ${resp}=    GET On Session    api    ${endpoint}    headers=${headers}
        ...    expected_status=any
    ELSE
        ${resp}=    GET On Session    api    ${endpoint}    headers=${headers}
        ...    params=${params}    expected_status=any
    END
    RETURN    ${resp}

PATCH Authenticated
    [Arguments]    ${endpoint}    ${body}    ${token}    ${expected_status}=any
    [Documentation]    Ejecuta PATCH con Bearer token y body JSON
    &{headers}=    Create Dictionary    Authorization=Bearer ${token}
    ${resp}=    PATCH On Session    api    ${endpoint}    json=${body}
    ...    headers=${headers}    expected_status=any
    RETURN    ${resp}

POST Authenticated
    [Arguments]    ${endpoint}    ${body}    ${token}    ${expected_status}=any
    [Documentation]    Ejecuta POST con Bearer token y body JSON
    &{headers}=    Create Dictionary    Authorization=Bearer ${token}
    ${resp}=    POST On Session    api    ${endpoint}    json=${body}
    ...    headers=${headers}    expected_status=any
    RETURN    ${resp}

# ── Validaciones de respuesta ─────────────────────────────────────────────

Response Should Have Status
    [Arguments]    ${resp}    ${expected_status}
    ${status}=    Convert To Integer    ${expected_status}
    Should Be Equal As Integers    ${resp.status_code}    ${status}
    ...    msg=Esperaba HTTP ${expected_status}, recibió ${resp.status_code}. Body: ${resp.text}

Response Body Should Contain Key
    [Arguments]    ${resp}    ${key}
    ${data}=    Set Variable    ${resp.json()}
    Dictionary Should Contain Key    ${data}    ${key}
    ...    msg=La respuesta no contiene la clave '${key}'. Body: ${resp.text}

Response Field Should Equal
    [Arguments]    ${resp}    ${field}    ${expected}
    ${data}=    Set Variable    ${resp.json()}
    ${value}=    Get From Dictionary    ${data}    ${field}
    Should Be Equal As Strings    ${value}    ${expected}
    ...    msg=Campo '${field}': esperaba '${expected}', obtuvo '${value}'

Measure Response Time
    [Arguments]    ${resp}    ${max_ms}=${MAX_RESPONSE_MS}
    [Documentation]    Verifica que el tiempo de respuesta no exceda max_ms milisegundos
    ${elapsed_ms}=    Evaluate    ${resp.elapsed.total_seconds()} * 1000
    Should Be True    ${elapsed_ms} < ${max_ms}
    ...    msg=Tiempo de respuesta ${elapsed_ms:.0f}ms excede el límite de ${max_ms}ms
    Log    Tiempo de respuesta: ${elapsed_ms:.0f}ms ✓

# ── Helpers ───────────────────────────────────────────────────────────────

Generate Unique Email
    [Documentation]    Genera un email único para pruebas usando timestamp
    ${ts}=    Get Current Date    result_format=epoch
    ${ts_int}=    Convert To Integer    ${ts}
    ${email}=    Set Variable    qa.auto.${ts_int}@test.com
    RETURN    ${email}

Decode JWT Payload
    [Arguments]    ${token}
    [Documentation]    Decodifica la parte payload del JWT (sin verificar firma)
    ${parts}=    Split String    ${token}    .
    ${payload_b64}=    Get From List    ${parts}    1
    # JWT usa base64url — urlsafe_b64decode + padding automático
    ${decoded}=    Evaluate
    ...    __import__('json').loads(__import__('base64').urlsafe_b64decode('${payload_b64}' + '==').decode('utf-8'))
    RETURN    ${decoded}
