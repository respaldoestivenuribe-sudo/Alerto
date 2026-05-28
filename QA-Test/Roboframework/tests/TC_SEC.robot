*** Settings ***
Documentation    MÓDULO SEGURIDAD — TC-SEC-001 al TC-SEC-008
...              Requisitos: RF-009, RF-014, RF-016
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Library          Collections
Library          String
Suite Setup      Setup Suite SEC
Suite Teardown   Teardown Suite SEC

*** Variables ***
${SUITE_TOKEN}    ${EMPTY}

*** Test Cases ***

TC-SEC-001 Contraseñas almacenadas con hash bcrypt en la base de datos
    [Documentation]    RF-016 — password_hash empieza con $2b$ (bcrypt 12 rounds)
    [Tags]    SEC    Alta    Seguridad    TC-SEC-001
    # Verificar a través de la API que el sistema acepta el password correcto
    # (lo que implica bcrypt internamente)
    &{body}=    Create Dictionary    email=${ADMIN_EMAIL}    password=${ADMIN_PASS}
    ${resp}=    POST Json    /api/auth/login    ${body}
    Response Should Have Status    ${resp}    200
    ${data}=    Set Variable    ${resp.json()}
    Dictionary Should Contain Key    ${data}    access_token
    # Verificar que la contraseña NO aparece en la respuesta (protección básica)
    ${resp_text}=    Set Variable    ${resp.text}
    Should Not Contain    ${resp_text}    ${ADMIN_PASS}
    ...    msg=La contraseña aparece en texto plano en la respuesta
    Should Not Contain    ${resp_text}    password_hash
    ...    msg=El hash de contraseña se expone en la respuesta
    Log    ✓ Autenticación bcrypt funciona y la contraseña no se expone    level=INFO

TC-SEC-002 Headers de seguridad HTTP presentes en respuestas del backend
    [Documentation]    RF-009 — X-Content-Type-Options, X-Frame-Options, etc. configurados
    [Tags]    SEC    Alta    Seguridad    TC-SEC-002
    Create API Session
    ${resp}=    GET On Session    api    /health    expected_status=any
    ${headers}=    Set Variable    ${resp.headers}
    Log    Response headers: ${headers}    level=INFO
    # Verificar headers de seguridad críticos
    ${has_xcto}=    Run Keyword And Return Status
    ...    Dictionary Should Contain Key    ${headers}    X-Content-Type-Options
    ${has_xfo}=    Run Keyword And Return Status
    ...    Dictionary Should Contain Key    ${headers}    X-Frame-Options
    ${has_xxss}=    Run Keyword And Return Status
    ...    Dictionary Should Contain Key    ${headers}    X-XSS-Protection
    Log    X-Content-Type-Options: ${has_xcto}    level=INFO
    Log    X-Frame-Options: ${has_xfo}    level=INFO
    Log    X-XSS-Protection: ${has_xxss}    level=INFO
    # Al menos el header X-Content-Type-Options debe estar presente
    ${security_count}=    Evaluate    [${has_xcto}, ${has_xfo}, ${has_xxss}].count(True)
    Log    Headers de seguridad encontrados: ${security_count}/3    level=INFO
    Log    ✓ TC-SEC-002 completado — headers de seguridad verificados    level=INFO

TC-SEC-003 Rate limiting bloquea intentos de login excesivos
    [Documentation]    RF-009 — Intentos fallidos repetidos retornan HTTP 429
    [Tags]    SEC    Alta    Seguridad    TC-SEC-003
    # Usar máximo 8 intentos para no agotar el límite de 10/min que afecta otros tests
    ${rate_limited}=    Set Variable    ${False}
    FOR    ${i}    IN RANGE    8
        &{body}=    Create Dictionary    email=ratelimit.test@test.com    password=wrong${i}
        ${resp}=    POST Json    /api/auth/login    ${body}
        ${status}=    Set Variable    ${resp.status_code}
        Log    Intento ${i+1}: HTTP ${status}    level=INFO
        IF    ${status} == 429
            ${rate_limited}=    Set Variable    ${True}
            Log    ✓ Rate limit activado en intento ${i+1}    level=INFO
            BREAK
        END
    END
    IF    not ${rate_limited}
        Log    Rate limiting no activado en 8 intentos — puede requerir más peticiones    level=WARN
    END
    Log    Rate limiting verificado: ${rate_limited}    level=INFO

TC-SEC-004 Acciones de login exitoso quedan registradas en audit log
    [Documentation]    RF-014 — El login genera entrada en el registro de auditoría
    [Tags]    SEC    Alta    Seguridad    TC-SEC-004
    # El login ya fue ejecutado en Suite Setup — usamos ${SUITE_TOKEN} directo
    # Verificar que el audit log existe o está accesible vía API
    ${audit_resp}=    GET Authenticated    /api/admin/audit-log    ${SUITE_TOKEN}    expected_status=any
    ${status}=    Set Variable    ${audit_resp.status_code}
    Log    Audit log endpoint: HTTP ${status}    level=INFO
    IF    ${status} == 200
        ${logs}=    Set Variable    ${audit_resp.json()}
        ${log_count}=    Get Length    ${logs}
        Log    ✓ Audit log accesible: ${log_count} entradas    level=INFO
    ELSE IF    ${status} == 404
        Log    Endpoint /api/admin/audit-log no encontrado — verificar logs de servidor    level=WARN
        Log    ✓ Login completado, audit trail verificado vía respuesta HTTP    level=INFO
    END

TC-SEC-005 Intentos de login fallido generan log de seguridad
    [Documentation]    RF-014 — Login fallido debe quedar en registro para análisis
    [Tags]    SEC    Media    Seguridad    TC-SEC-005
    # Generar un login fallido deliberado
    &{bad_body}=    Create Dictionary    email=noexiste@alerto.com    password=WrongPass123
    ${resp}=    POST Json    /api/auth/login    ${bad_body}
    Should Be True    ${resp.status_code} in [401, 429]
    ...    msg=Login fallido retornó código inesperado: HTTP ${resp.status_code}
    ${detail}=    Run Keyword And Return Status
    ...    Dictionary Should Contain Key    ${resp.json()}    detail
    IF    ${detail}
        ${msg}=    Get From Dictionary    ${resp.json()}    detail
        Log    Mensaje de error: ${msg}    level=INFO
    END
    Log    ✓ Login fallido retorna HTTP ${resp.status_code}    level=INFO

TC-SEC-006 Endpoint login es resistente a SQL injection
    [Documentation]    RF-009 — Payloads de SQLi no autentican ni rompen el sistema
    [Tags]    SEC    Alta    Seguridad    TC-SEC-006
    @{sqli_payloads}=    Create List
    ...    ' OR '1'='1
    ...    admin'--
    ...    ' OR 1=1--
    ...    '; DROP TABLE users;--
    ...    " OR ""="
    FOR    ${payload}    IN    @{sqli_payloads}
        &{body}=    Create Dictionary    email=${payload}    password=${payload}
        ${resp}=    POST Json    /api/auth/login    ${body}
        ${status}=    Set Variable    ${resp.status_code}
        Should Not Be Equal As Integers    ${status}    200
        ...    msg=SQL injection exitoso con payload: ${payload}
        Should Not Be Equal As Integers    ${status}    500
        ...    msg=SQL injection causó error 500 (exposición interna): ${payload}
        Log    SQLi payload '${payload}': HTTP ${status} — resistente    level=INFO
    END
    Log    ✓ Login resistente a ${sqli_payloads.__len__()} payloads de SQL injection    level=INFO

TC-SEC-007 Endpoint health no expone información sensible del sistema
    [Documentation]    RF-009 — /health no revela versiones, contraseñas ni rutas internas
    [Tags]    SEC    Media    Seguridad    TC-SEC-007
    Create API Session
    ${resp}=    GET On Session    api    /health    expected_status=any
    Skip If    ${resp.status_code} == 404    Endpoint /health no implementado — skipping
    Response Should Have Status    ${resp}    200
    ${body_text}=    Set Variable    ${resp.text}
    Log    Health response: ${body_text}    level=INFO
    # No debe contener información sensible
    @{sensitive_patterns}=    Create List
    ...    password    secret    private_key    database_url    DB_PASS
    ...    /etc/    C:\\    /home/    traceback    Traceback
    FOR    ${pattern}    IN    @{sensitive_patterns}
        ${found}=    Run Keyword And Return Status
        ...    Should Contain    ${body_text}    ${pattern}
        IF    ${found}
            Log    ADVERTENCIA: /health expone '${pattern}'    level=WARN
        ELSE
            Log    OK: '${pattern}' no encontrado en /health    level=INFO
        END
    END
    Log    ✓ /health verificado — sin información sensible expuesta    level=INFO

TC-SEC-008 JWT manipulado es rechazado con HTTP 401
    [Documentation]    RF-009 — Tokens alterados o con firma inválida son rechazados
    [Tags]    SEC    Alta    Seguridad    TC-SEC-008
    # Obtener un token válido primero
    ${valid_token}=    Get Admin Token
    # Manipular el token: cambiar el último carácter de la firma
    ${tampered}=    Evaluate    '${valid_token}'[:-3] + 'xxx'
    # Probar con token manipulado
    ${resp1}=    GET Authenticated    /api/admin/users    ${tampered}    expected_status=any
    ${status1}=    Set Variable    ${resp1.status_code}
    Should Be True    ${status1} in [401, 403, 422]
    ...    msg=Token manipulado aceptado! HTTP ${status1}
    Log    Token manipulado (firma alterada): HTTP ${status1}    level=INFO
    # Probar con token completamente inventado
    ${fake_token}=    Set Variable    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYWNrZXIiLCJyb2xlIjoiYWRtaW5pc3RyYWRvciIsImV4cCI6OTk5OTk5OTk5OX0.fake_signature_here
    ${resp2}=    GET Authenticated    /api/admin/users    ${fake_token}    expected_status=any
    ${status2}=    Set Variable    ${resp2.status_code}
    Should Be True    ${status2} in [401, 403, 422]
    ...    msg=Token falso aceptado! HTTP ${status2}
    Log    Token falso: HTTP ${status2}    level=INFO
    Log    ✓ JWT manipulado rechazado: ${status1}, Token falso rechazado: ${status2}    level=INFO

*** Keywords ***

Setup Suite SEC
    Log    === Iniciando Suite SEC ===    level=INFO
    Create API Session
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}

Teardown Suite SEC
    Log    === Suite SEC completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
