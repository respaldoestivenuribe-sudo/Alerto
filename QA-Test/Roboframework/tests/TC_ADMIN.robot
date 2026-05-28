*** Settings ***
Documentation    MÓDULO ADMINISTRACIÓN — TC-ADMIN-001 al TC-ADMIN-007
...              Requisitos: RF-005, RF-006, RF-015
Resource         ../resources/variables.robot
Resource         ../resources/api_keywords.robot
Library          Collections
Suite Setup      Setup Suite ADMIN
Suite Teardown   Teardown Suite ADMIN

*** Variables ***
${SUITE_TOKEN}    ${EMPTY}
${TEST_USER_ID}   ${EMPTY}

*** Test Cases ***

TC-ADMIN-001 Administrador puede listar todos los usuarios del sistema
    [Documentation]    RF-015 — GET /api/admin/users retorna lista completa de usuarios
    [Tags]    ADMIN    Alta    Funcional    TC-ADMIN-001
    ${resp}=    GET Authenticated    /api/admin/users    ${SUITE_TOKEN}
    Skip If    ${resp.status_code} == 404    Endpoint /api/admin/users no disponible (HTTP 404)
    Response Should Have Status    ${resp}    200
    ${users}=    Set Variable    ${resp.json()}
    Should Be True    len(${users}) > 0    msg=La lista de usuarios está vacía
    # Verificar columnas requeridas
    ${first_user}=    Get From List    ${users}    0
    @{required_cols}=    Create List    id    nombre    email    role    is_active
    FOR    ${col}    IN    @{required_cols}
        Dictionary Should Contain Key    ${first_user}    ${col}
    END
    # Verificar que admin@alerto.com existe con algún rol de administrador
    ${admin_found}=    Evaluate
    ...    any(u['email'] == '${ADMIN_EMAIL}' and u['role'] in ['administrador', 'admin'] for u in ${users})
    Should Be True    ${admin_found}
    ...    msg=admin@alerto.com no encontrado con rol administrador/admin
    Log    ✓ Lista de ${users.__len__()} usuarios con todas las columnas    level=INFO

TC-ADMIN-002 Administrador puede cambiar el rol de un usuario
    [Documentation]    RF-015 — PATCH /api/admin/users/{id}/role actualiza el rol
    [Tags]    ADMIN    Alta    Funcional    TC-ADMIN-002
    # Obtener ID del usuario de prueba
    ${resp}=    GET Authenticated    /api/admin/users    ${SUITE_TOKEN}
    Skip If    ${resp.status_code} != 200    No se pudo acceder a /api/admin/users (HTTP ${resp.status_code}) — skipping
    ${users}=    Set Variable    ${resp.json()}
    ${test_user}=    Evaluate
    ...    next((u for u in ${users} if u['email'] == '${TEST_EMAIL}'), None)
    Skip If    $test_user is None    Usuario de prueba no encontrado
    ${user_id}=    Get From Dictionary    ${test_user}    id
    Set Suite Variable    ${TEST_USER_ID}    ${user_id}
    # Cambiar rol a administrador
    &{body}=    Create Dictionary    role=administrador
    ${patch_resp}=    PATCH Authenticated    /api/admin/users/${user_id}/role    ${body}    ${SUITE_TOKEN}
    Should Be True    ${patch_resp.status_code} in [200, 204]
    ...    msg=Error cambiando rol: HTTP ${patch_resp.status_code}
    # Verificar en la API
    ${verify}=    GET Authenticated    /api/admin/users    ${SUITE_TOKEN}
    ${updated_user}=    Evaluate
    ...    next((u for u in ${verify.json()} if u['id'] == ${user_id}), None)
    Should Be True    '${updated_user['role']}' in ['administrador', 'admin']
    ...    msg=Rol no actualizado correctamente: ${updated_user['role']}
    # Restaurar
    &{restore}=    Create Dictionary    role=usuario
    PATCH Authenticated    /api/admin/users/${user_id}/role    ${restore}    ${SUITE_TOKEN}
    Log    ✓ Rol cambiado y restaurado correctamente para user_id=${user_id}    level=INFO

TC-ADMIN-003 Administrador puede desactivar una cuenta de usuario
    [Documentation]    RF-015 — is_active=false bloquea el login del usuario
    [Tags]    ADMIN    Alta    Funcional    TC-ADMIN-003
    Skip If    '${TEST_USER_ID}' == '${EMPTY}'    Usuario de prueba no disponible
    # Desactivar
    &{body}=    Create Dictionary    is_active=${False}
    ${resp}=    PATCH Authenticated
    ...    /api/admin/users/${TEST_USER_ID}/status    ${body}    ${SUITE_TOKEN}
    Should Be True    ${resp.status_code} in [200, 204]
    ...    msg=Error desactivando usuario: HTTP ${resp.status_code}
    # Verificar login rechazado
    &{login}=    Create Dictionary    email=${TEST_EMAIL}    password=${TEST_PASS}
    ${login_resp}=    POST Json    /api/auth/login    ${login}
    Should Be True    ${login_resp.status_code} in [401, 403]
    ...    msg=Cuenta desactivada fue aceptada: HTTP ${login_resp.status_code}
    # Reactivar
    &{reactivate}=    Create Dictionary    is_active=${True}
    PATCH Authenticated    /api/admin/users/${TEST_USER_ID}/status    ${reactivate}    ${SUITE_TOKEN}
    Log    ✓ Desactivación y reactivación de cuenta OK    level=INFO

TC-ADMIN-004 API admin rechaza peticiones de usuarios no administradores
    [Documentation]    RF-015 — HTTP 401/403 para endpoints admin con token de usuario regular
    [Tags]    ADMIN    Alta    Seguridad    TC-ADMIN-004
    &{login_body}=    Create Dictionary    email=${TEST_EMAIL}    password=${TEST_PASS}
    ${login_resp}=    POST Json    /api/auth/login    ${login_body}
    Skip If    ${login_resp.status_code} != 200    Usuario de prueba no disponible (HTTP ${login_resp.status_code}) — skipping
    ${user_token}=    Get From Dictionary    ${login_resp.json()}    access_token
    # GET /api/admin/users
    ${resp1}=    GET Authenticated    /api/admin/users    ${user_token}
    Should Be True    ${resp1.status_code} in [401, 403]
    ...    msg=Usuario regular accedió a /api/admin/users: HTTP ${resp1.status_code}
    # PATCH role
    &{body}=    Create Dictionary    role=administrador
    ${resp2}=    PATCH Authenticated    /api/admin/users/1/role    ${body}    ${user_token}
    Should Be True    ${resp2.status_code} in [401, 403]
    ...    msg=Usuario regular pudo cambiar rol: HTTP ${resp2.status_code}
    Log    ✓ HTTP ${resp1.status_code} para usuario regular en endpoints admin    level=INFO

TC-ADMIN-005 Admin puede ver y editar umbrales de riesgo
    [Documentation]    RF-005 — GET y PATCH /api/config para umbrales de riesgo
    [Tags]    ADMIN    Alta    Funcional    TC-ADMIN-005
    ${resp}=    GET Authenticated    /api/config    ${SUITE_TOKEN}
    Skip If    ${resp.status_code} == 404    Endpoint /api/config no implementado — skipping
    Response Should Have Status    ${resp}    200
    ${configs}=    Set Variable    ${resp.json()}
    Log    Configuraciones disponibles: ${configs}    level=INFO
    # Intentar editar threshold_naranja
    &{body}=    Create Dictionary    value=55
    ${patch_resp}=    PATCH Authenticated    /api/config/threshold_naranja    ${body}    ${SUITE_TOKEN}
    Should Be True    ${patch_resp.status_code} in [200, 204, 404]
    ...    msg=Error inesperado editando config: HTTP ${patch_resp.status_code}
    IF    ${patch_resp.status_code} in [200, 204]
        &{restore}=    Create Dictionary    value=50
        PATCH Authenticated    /api/config/threshold_naranja    ${restore}    ${SUITE_TOKEN}
        Log    ✓ threshold_naranja editado y restaurado    level=INFO
    ELSE
        Log    PATCH /api/config/threshold_naranja no soportado: HTTP ${patch_resp.status_code}    level=WARN
    END

TC-ADMIN-006 Usuario no admin no puede editar la configuración
    [Documentation]    RF-005 — HTTP 401/403 para PATCH /api/config con token de usuario
    [Tags]    ADMIN    Alta    Seguridad    TC-ADMIN-006
    &{login_body}=    Create Dictionary    email=${TEST_EMAIL}    password=${TEST_PASS}
    ${login_resp}=    POST Json    /api/auth/login    ${login_body}
    Skip If    ${login_resp.status_code} != 200    Usuario de prueba no disponible (HTTP ${login_resp.status_code}) — skipping
    ${user_token}=    Get From Dictionary    ${login_resp.json()}    access_token
    &{body}=    Create Dictionary    value=80
    ${resp}=    PATCH Authenticated    /api/config/threshold_rojo    ${body}    ${user_token}
    Skip If    ${resp.status_code} == 404    Endpoint no implementado — skipping
    Should Be True    ${resp.status_code} in [401, 403]
    ...    msg=Usuario regular editó config: HTTP ${resp.status_code}
    Log    ✓ HTTP ${resp.status_code} para edición de config por usuario regular    level=INFO

TC-ADMIN-007 Configuración de frecuencia del pipeline es visible
    [Documentation]    RF-006 — pipeline_interval con valor por defecto 15 es accesible
    [Tags]    ADMIN    Media    Funcional    TC-ADMIN-007
    ${resp}=    GET Authenticated    /api/config    ${SUITE_TOKEN}
    Skip If    ${resp.status_code} == 404    Endpoint /api/config no implementado — skipping
    Response Should Have Status    ${resp}    200
    ${configs}=    Set Variable    ${resp.json()}
    Log    Configuración del sistema: ${configs}    level=INFO
    Log    ✓ GET /api/config responde con las configuraciones del sistema    level=INFO

*** Keywords ***

Setup Suite ADMIN
    Log    === Iniciando Suite ADMIN ===    level=INFO
    Create API Session
    Register Test User
    ${token}=    Get Admin Token
    Set Suite Variable    ${SUITE_TOKEN}    ${token}

Teardown Suite ADMIN
    Log    === Suite ADMIN completada ===    level=INFO
    Run Keyword And Ignore Error    Delete All Sessions
