*** Settings ***
Documentation    Variables globales del sistema Alerto — QA Test Suite v1.0

*** Variables ***
# ── Servicios ──────────────────────────────────────────────────────────────
${API_URL}              http://localhost:8000
${FRONTEND_URL}         http://localhost:3000
${AIRFLOW_URL}          http://localhost:8080
${DB_HOST}              localhost
${DB_PORT}              15432
${DB_NAME}              alerto_db
${DB_USER}              alerto
${DB_PASS}              alerto123

# ── Credenciales de prueba ─────────────────────────────────────────────────
${ADMIN_EMAIL}          admin@alerto.com
${ADMIN_PASS}           alerto123**
${TEST_EMAIL}           qa.robot@test.com
${TEST_PASS}            Robot1234!
${TEST_NAME}            QA Robot
${TEST_QUESTION}        ¿Cuál es el nombre de tu primera mascota?
${TEST_ANSWER}          firulais

# ── Timeouts ──────────────────────────────────────────────────────────────
${API_TIMEOUT}          10
${UI_TIMEOUT}           15s
${PIPELINE_WAIT}        180s

# ── Navegador ─────────────────────────────────────────────────────────────
${BROWSER}              Chrome
${BROWSER_OPTIONS}      add_argument("--start-maximized");add_argument("--disable-extensions")

# ── Umbrales de rendimiento ────────────────────────────────────────────────
${MAX_RESPONSE_MS}      500
${MAX_LOAD_S}           3

# ── Resultados / Evidencias ───────────────────────────────────────────────
${RESULTS_DIR}          ${CURDIR}/../results
${SCREENSHOTS_DIR}      ${CURDIR}/../results/screenshots
