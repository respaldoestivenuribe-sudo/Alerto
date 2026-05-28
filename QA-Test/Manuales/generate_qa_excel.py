#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Excel QA — Sistema Alerto v1.0
Crea Casos_de_Prueba_v1.0.xlsx con 75 casos, hojas por módulo,
colores, dropdowns y columnas de evidencia (screenshot/video).
"""

import os
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import Rule
from openpyxl.styles.differential import DifferentialStyle

# ─────────────────────────────────────────────────────────────────────────────
# PALETA
# ─────────────────────────────────────────────────────────────────────────────
C_HDR_BG   = "1E3A5F"
C_HDR_FG   = "FFFFFF"
C_EVID_BG  = "FFFCE6"   # amarillo muy claro para columnas de evidencia
C_ALT      = "F7FAFF"   # azul muy claro para filas alternas

C_ALTA     = "FFE0E0"
C_MEDIA    = "FFF8E1"
C_BAJA     = "E8F5E9"
C_NA_PRI   = "F0F0F0"

C_PEND     = "E9ECEF"
C_APROV    = "D4EDDA"
C_FALL     = "F8D7DA"
C_BLOQ     = "FFF3CD"
C_NA_ST    = "F0F0F0"

# ─────────────────────────────────────────────────────────────────────────────
# DEFINICIÓN DE COLUMNAS
#   (nombre, ancho, es_evidencia?)
# ─────────────────────────────────────────────────────────────────────────────
COLUMNS = [
    ("ID",                    14, False),
    ("Título",                38, False),
    ("Requisito",             14, False),
    ("Tipo",                  22, False),
    ("Prioridad",             12, False),
    ("Precondiciones",        42, False),
    ("Datos de Prueba",       32, False),
    ("Pasos",                 62, False),
    ("Resultado Esperado",    54, False),
    ("Resultado Actual",      44, False),
    ("Estado",                14, False),
    # ── Evidencia ────────────────
    ("Evidencia (Ruta/URL)",  46, True),
    ("Tipo Evidencia",        18, True),
    ("Notas Evidencia",       36, True),
    ("Fecha Ejecución",       18, True),
    ("Ejecutado Por",         20, True),
]

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE ESTILO
# ─────────────────────────────────────────────────────────────────────────────
def thin_border():
    s = Side(style="thin", color="D0D5DD")
    return Border(left=s, right=s, top=s, bottom=s)

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def priority_fill(p):
    return fill({"Alta": C_ALTA, "Media": C_MEDIA, "Baja": C_BAJA}.get(p, C_NA_PRI))

def status_fill(s):
    return fill({
        "Pendiente": C_PEND,
        "Aprobado":  C_APROV,
        "Fallido":   C_FALL,
        "Bloqueado": C_BLOQ,
        "N/A":       C_NA_ST,
    }.get(s, C_PEND))

# ─────────────────────────────────────────────────────────────────────────────
# DATOS — 75 CASOS DE PRUEBA
# Tuplas: (id, titulo, requisito, tipo, prioridad, precond, datos, pasos,
#          resultado_esperado, estado_inicial)
# ─────────────────────────────────────────────────────────────────────────────

AUTH = [
    ("TC-AUTH-001", "Registro exitoso de nuevo usuario",
     "RF-014, RF-015", "Funcional", "Alta",
     "Contenedores activos. Email nuevo@test.com no registrado.",
     "Nombre: Juan Prueba\nEmail: nuevo@test.com\nContraseña: Test1234!\nPregunta: ¿Nombre primera mascota?\nRespuesta: firulais",
     "1. Navegar a /register\n2. Completar formulario con datos de prueba\n3. Clic en Crear Cuenta\n4. Verificar redirección a /login\n5. BD: SELECT * FROM users WHERE email='nuevo@test.com';",
     "• Redirección exitosa a /login\n• BD: role='usuario', is_active=true\n• password_hash comienza con $2b$ (bcrypt)\n• security_answer también como hash bcrypt\n• audit_log: action='register', result='success'",
     "Pendiente"),

    ("TC-AUTH-002", "Registro con email duplicado es rechazado",
     "RF-014", "Funcional", "Alta",
     "admin@alerto.com ya existe en BD.",
     "Email: admin@alerto.com\nContraseña: cualquiera",
     "1. Ir a /register\n2. Ingresar email admin@alerto.com con datos válidos\n3. Clic en Crear Cuenta",
     "• Mensaje: 'El correo ya está registrado.'\n• HTTP 400 en /api/auth/register\n• No se inserta duplicado en BD\n• audit_log: result='failure'",
     "Pendiente"),

    ("TC-AUTH-003", "Registro con contraseña < 6 caracteres es rechazado",
     "RF-014", "Funcional", "Media",
     "Ninguna.",
     "Contraseña: abc (3 caracteres)",
     "1. Ir a /register\n2. Ingresar contraseña de 3 caracteres\n3. Clic en Crear Cuenta",
     "• Validación del formulario impide el envío (HTML5 o Pydantic)\n• HTTP 422 si la petición llega al backend",
     "Pendiente"),

    ("TC-AUTH-004", "Login exitoso con credenciales válidas",
     "RF-014, RF-015", "Funcional", "Alta",
     "Usuario admin@alerto.com con contraseña alerto123** existe.",
     "Email: admin@alerto.com\nContraseña: alerto123**",
     "1. Navegar a /login\n2. Ingresar admin@alerto.com / alerto123**\n3. Clic en Ingresar al Sistema\n4. Verificar redirección a /precipitation\n5. DevTools → LocalStorage: verificar token\n6. Decodificar JWT y verificar payload",
     "• Redirección exitosa a /precipitation\n• localStorage['token'] contiene JWT válido\n• JWT payload: sub, id, name, role='administrador', exp\n• audit_log: action='login', result='success'",
     "Pendiente"),

    ("TC-AUTH-005", "Login con contraseña incorrecta es rechazado",
     "RF-014", "Funcional · Seguridad", "Alta",
     "Usuario admin@alerto.com existe.",
     "Email: admin@alerto.com\nContraseña: contraseña_incorrecta",
     "1. Ir a /login\n2. Ingresar credenciales incorrectas\n3. Clic en Ingresar al Sistema",
     "• Mensaje: 'Credenciales inválidas.'\n• HTTP 401\n• Mensaje genérico (no revela si el usuario existe)\n• audit_log: result='failure'\n• No se almacena token",
     "Pendiente"),

    ("TC-AUTH-006", "Cierre de sesión elimina token y redirige al login",
     "RF-015", "Funcional", "Alta",
     "Usuario autenticado en sesión activa.",
     "",
     "1. Iniciar sesión con credenciales válidas\n2. Navegar a /precipitation\n3. Clic en botón Salir en topbar\n4. Verificar redirección\n5. Verificar LocalStorage\n6. Intentar navegar a /risk",
     "• Redirección a /login\n• localStorage['token'] eliminado\n• Acceso directo a /risk redirige a /login (ProtectedRoute activo)",
     "Pendiente"),

    ("TC-AUTH-007", "Acceso a rutas protegidas sin sesión redirige a login",
     "RF-015", "Seguridad", "Alta",
     "Ningún token en LocalStorage (browser incógnito).",
     "",
     "1. En browser incógnito, intentar navegar a /risk\n2. Intentar navegar a /admin\n3. Intentar navegar a /simulator",
     "• Todas las rutas redirigen a /login inmediatamente\n• No se carga ningún dato de la API",
     "Pendiente"),

    ("TC-AUTH-008", "Usuario 'usuario' no puede acceder a rutas de admin",
     "RF-015", "Seguridad", "Alta",
     "Existe usuario con role='usuario' y sesión activa.",
     "",
     "1. Crear usuario regular (sin rol administrador)\n2. Iniciar sesión con ese usuario\n3. Navegar manualmente a /admin\n4. Postman: GET /api/admin/users con token del usuario regular",
     "• Frontend redirige a /precipitation (AdminRoute lo bloquea)\n• API retorna HTTP 403: 'Acceso restringido a administradores.'\n• Enlace Administración NO aparece en sidebar",
     "Pendiente"),

    ("TC-AUTH-009", "Token JWT expirado es rechazado",
     "RF-015", "Seguridad", "Alta",
     "Se dispone de un token JWT expirado.",
     "JWT con exp en el pasado firmado con alerto_secret",
     "1. Postman: construir JWT con exp en el pasado usando alerto_secret\n2. GET /api/risk/current con Authorization: Bearer <token_expirado>",
     "• HTTP 401 con mensaje 'Token expirado.'\n• No se devuelven datos",
     "Pendiente"),

    ("TC-AUTH-010", "Cuenta desactivada no puede iniciar sesión",
     "RF-015", "Funcional", "Alta",
     "Administrador tiene acceso. Existe usuario desact@test.com.",
     "",
     "1. Como admin: PATCH /api/admin/users/{id}/status con {\"is_active\": false}\n2. Intentar login con desact@test.com",
     "• HTTP 401: 'Cuenta desactivada. Contacta al administrador.'\n• audit_log: action='login', result='failure'",
     "Pendiente"),

    ("TC-AUTH-011", "Recuperación contraseña — paso 1: búsqueda de pregunta",
     "RF-016", "Funcional", "Alta",
     "Usuario nuevo@test.com registrado con pregunta de seguridad.",
     "Email: nuevo@test.com",
     "1. Navegar a /reset-password\n2. Ingresar email nuevo@test.com\n3. Clic en Continuar",
     "• Formulario avanza al paso 2\n• Se muestra la pregunta de seguridad asociada al email\n• HTTP 200 con {\"security_question\": \"...\"}",
     "Pendiente"),

    ("TC-AUTH-012", "Recuperación contraseña — paso 2: cambio exitoso",
     "RF-016", "Funcional", "Alta",
     "TC-AUTH-011 completado exitosamente.",
     "Respuesta: firulais\nNueva contraseña: NuevaPass99!",
     "1. En el paso 2, ingresar respuesta correcta: firulais\n2. Ingresar nueva contraseña: NuevaPass99!\n3. Clic en Restablecer Contraseña\n4. Intentar login con la nueva contraseña",
     "• Redirección a /login\n• Login exitoso con NuevaPass99!\n• audit_log: action='reset_password', result='success'\n• Login con contraseña anterior falla",
     "Pendiente"),

    ("TC-AUTH-013", "Recuperación contraseña con respuesta incorrecta rechazada",
     "RF-016", "Funcional · Seguridad", "Alta",
     "TC-AUTH-011 completado.",
     "Respuesta: respuesta_falsa",
     "1. Paso 2 de recuperación\n2. Ingresar respuesta INCORRECTA: respuesta_falsa\n3. Clic en Restablecer Contraseña",
     "• Mensaje: 'Respuesta de seguridad incorrecta.'\n• HTTP 400\n• Contraseña no cambia en BD\n• audit_log: result='failure'",
     "Pendiente"),
]

UI = [
    ("TC-UI-001", "Página login muestra layout split-panel correctamente",
     "RF-IU-001", "UI", "Media",
     "Servidor frontend activo en localhost:3000.",
     "Resoluciones: 1920x1080 y 375x667 (móvil simulado)",
     "1. Navegar a /login en Chrome 100+\n2. Observar estructura visual a 1920x1080\n3. DevTools: simular resolución 375x667\n4. Verificar logo y ausencia de errores en consola",
     "• Escritorio (≥768px): panel izquierdo azul + panel derecho blanco con formulario\n• Móvil (<768px): panel izquierdo oculto, logo aparece sobre el formulario\n• Logo cargado desde /logo/Logo.png\n• Sin errores en consola de navegador",
     "Pendiente"),

    ("TC-UI-002", "Navegación sidebar muestra enlace activo correcto",
     "RF-IU-001", "UI", "Media",
     "Sesión activa con rol administrador.",
     "",
     "1. Iniciar sesión como admin\n2. Clic en Precipitación en el sidebar\n3. Verificar highlight activo\n4. Clic en Riesgo\n5. Verificar cambio de highlight\n6. Verificar que Administración aparece solo para admin",
     "• Enlace activo resaltado con color primario y fondo diferenciado\n• Solo el enlace de la página actual está resaltado\n• Enlace Administración visible solo con rol 'administrador'",
     "Pendiente"),

    ("TC-UI-003", "Topbar muestra nombre real del usuario autenticado",
     "RF-IU-001", "UI", "Media",
     "Sesión activa con usuario Administrador.",
     "Cuenta: admin@alerto.com",
     "1. Iniciar sesión como admin@alerto.com\n2. Observar la barra superior derecha",
     "• Se muestra 'Hola, Administrador' (nombre del JWT)\n• Rol mostrado: 'Administrador'\n• No aparece texto hardcodeado",
     "Pendiente"),

    ("TC-UI-004", "Interfaz cumple WCAG 2.1 — etiquetas ARIA en formularios",
     "RF-IU-002", "UI · Accesibilidad", "Alta",
     "Ninguna.",
     "",
     "1. Abrir DevTools → Elements\n2. Inspeccionar formulario de login\n3. Verificar atributos aria-label en botones de campana y logout\n4. Verificar htmlFor en todos los campos de formulario\n5. Verificar scope='col' en cabeceras de tablas\n6. Navegar el formulario con solo teclado (Tab, Enter)",
     "• Todos los inputs tienen id asociado a su label\n• Botones tienen aria-label descriptivos\n• Tablas tienen scope='col' en <th>\n• Navegación por teclado funcional sin trampa de foco",
     "Pendiente"),

    ("TC-UI-005", "Interfaz responsiva en resolución tablet (1024x768)",
     "RF-IU-002", "UI", "Media",
     "DevTools disponibles.",
     "Viewport: 1024x768",
     "1. DevTools: establecer viewport 1024x768\n2. Navegar por: Precipitación, Riesgo, Alertas, Simulador\n3. Verificar que ningún elemento desborda su contenedor\n4. Verificar scroll horizontal en tablas si es necesario",
     "• Todos los elementos visibles y accesibles\n• Sin scroll horizontal no intencional\n• Sidebar visible correctamente\n• Tarjetas métricas se reorganizan en grid responsivo",
     "Pendiente"),

    ("TC-UI-006", "Contraste mínimo 4.5:1 en textos principales",
     "RF-IU-002", "Accesibilidad", "Media",
     "axe DevTools instalado en Chrome.",
     "",
     "1. Instalar extensión axe DevTools en Chrome\n2. Navegar a /login\n3. Ejecutar análisis axe\n4. Revisar reportes de contraste\n5. Repetir en /precipitation y /risk",
     "• 0 errores de nivel AA en contraste de texto\n• --text-main (#1e293b) sobre blanco: ratio ≥ 12:1\n• --text-muted (#64748b) sobre blanco: verificar ≥ 4.5:1",
     "Pendiente"),

    ("TC-UI-007", "Página Precipitación muestra las 4 métricas climáticas correctas",
     "RF-IU-003", "Funcional · UI", "Alta",
     "Pipeline ejecutado al menos una vez. Sesión activa.",
     "",
     "1. Navegar a /precipitation\n2. Verificar 4 tarjetas métricas\n3. Verificar gráfico de línea\n4. Esperar 60 segundos y verificar actualización de datos",
     "• Tarjetas: Última hora (mm), Últimas 3h (mm), Últimas 6h (mm), Humedad 6h (%)\n• Valores numéricos visibles (no '—' si hay datos)\n• Gráfico de línea con eje X tiempo y eje Y mm\n• Sin errores en consola de navegador",
     "Pendiente"),

    ("TC-UI-008", "Gráfico de precipitación muestra hasta 72h de histórico",
     "RF-IU-003", "Funcional · UI", "Media",
     "Datos en gold_precipitation_history.",
     "",
     "1. Navegar a /precipitation\n2. Verificar título de la card del gráfico\n3. DevTools Network: verificar respuesta de /api/precipitation/history?limit=72",
     "• Título: 'Histórico de Precipitación (últimas 72h)'\n• API devuelve máximo 72 registros\n• Datos mostrados en orden cronológico ascendente",
     "Pendiente"),

    ("TC-UI-009", "Página Riesgo muestra badge con color según nivel",
     "RF-IU-004", "Funcional · UI", "Alta",
     "Al menos un registro en tabla alerts. Sesión activa.",
     "Niveles a verificar: VERDE, AMARILLO, NARANJA, ROJO",
     "1. Navegar a /risk\n2. Verificar badge del nivel de riesgo actual\n3. Por cada nivel verificar color:\n   VERDE → #10b981\n   AMARILLO → #f59e0b\n   NARANJA → #f97316\n   ROJO → #ef4444\n4. Verificar score numérico (0–100%)",
     "• Badge visible con texto del nivel y color correspondiente\n• Score numérico visible con símbolo %\n• Timestamp de última evaluación visible",
     "Pendiente"),

    ("TC-UI-010", "Tabla histórico de riesgo muestra colores en filas por nivel",
     "RF-IU-004", "UI", "Media",
     "Múltiples registros de distintos niveles en alerts.",
     "",
     "1. Navegar a /risk\n2. Verificar tabla de histórico\n3. Inspeccionar clases CSS de cada fila con DevTools",
     "• Filas ROJO: borde izquierdo rojo\n• Filas NARANJA: borde izquierdo naranja\n• Filas AMARILLO: borde izquierdo amarillo\n• Filas VERDE: borde izquierdo verde",
     "Pendiente"),

    ("TC-UI-011", "Aplicación carga correctamente en Chrome, Firefox y Edge",
     "RF-IH-001, RNF-PORT-002", "Compatibilidad", "Alta",
     "Chrome 100+, Firefox 95+, Edge 100+ disponibles.",
     "",
     "1. Abrir /login en Chrome → iniciar sesión → navegar\n2. Repetir en Firefox 95+\n3. Repetir en Edge 100+\n4. En cada browser: verificar login, gráfico de precipitación, tabla de riesgo",
     "• Carga correcta en los 3 navegadores\n• Gráfico de línea (Recharts) renderiza en todos\n• Sin errores de consola críticos en ninguno\n• Layout sin diferencias visuales relevantes",
     "Pendiente"),

    ("TC-UI-012", "Campana de notificaciones muestra alertas recientes",
     "RF-IU-001, RF-008", "Funcional", "Alta",
     "Existen alertas NARANJA o ROJO en las últimas 24h. Sesión activa.",
     "",
     "1. Iniciar sesión\n2. Observar icono de campana en topbar\n3. Verificar badge numérico\n4. Hacer clic en la campana\n5. Verificar el dropdown",
     "• Badge numérico indica alertas críticas (NARANJA/ROJO) en 24h\n• Dropdown muestra alertas con nivel, color e icono\n• Enlace 'Ver todas las alertas' navega a /alerts\n• Dropdown se cierra al hacer clic fuera",
     "Pendiente"),
]

DATA = [
    ("TC-DATA-001", "Validación de campos requeridos en datos de Open-Meteo",
     "RF-001", "Integración", "Alta",
     "Pipeline ejecutado. Acceso a BD.",
     "SQL: SELECT * FROM bronze_weather_current ORDER BY fetched_at DESC LIMIT 1;",
     "1. Ejecutar pipeline\n2. BD: SELECT * FROM bronze_weather_current ORDER BY fetched_at DESC LIMIT 1;\n3. Verificar que todos los campos están presentes",
     "• Campos presentes: fetched_at, time, precipitation, rain, showers, relative_humidity, cloudcover, windspeed_10m\n• Valores son números válidos (no NaN ni null inesperado)",
     "Pendiente"),

    ("TC-DATA-002", "Datos con campos faltantes generan error registrado en Airflow",
     "RF-001, RF-003", "Integración", "Alta",
     "Acceso a logs de Airflow.",
     "",
     "1. Airflow UI (localhost:8080): revisar log del último DAG run de weather_pipeline\n2. Si hay ejecuciones fallidas, verificar mensajes de error\n3. Verificar que el error no interrumpió completamente el sistema",
     "• Si hubo error: log contiene mensaje descriptivo con la causa\n• Error registrado sin que el sistema deje de funcionar\n• Tarea de Airflow muestra estado 'Failed' con detalles",
     "Pendiente"),

    ("TC-DATA-003", "Flujo completo Bronze→Silver→Gold→Riesgo sin error",
     "RF-002", "Integración", "Alta",
     "Airflow activo, dbt instalado.",
     "SQL de verificación por cada capa del pipeline",
     "1. Airflow UI: localizar DAG weather_pipeline\n2. Ejecutar manualmente (Trigger DAG)\n3. Monitorear cada tarea hasta completar\n4. Verificar datos en cada capa:\n   SELECT COUNT(*) FROM bronze_weather_hourly;\n   SELECT COUNT(*) FROM silver_weather_hourly;\n   SELECT * FROM gold_risk_features_latest;\n   SELECT * FROM alerts ORDER BY evaluated_at DESC LIMIT 1;",
     "• Todas las tareas del DAG en verde (Success)\n• Datos presentes en bronze, silver y gold\n• Registro nuevo en alerts con nivel de riesgo válido\n• Tiempo total de ejecución < 5 minutos",
     "Pendiente"),

    ("TC-DATA-004", "Pipeline no inserta registros duplicados en bronze_weather_hourly",
     "RF-002, RF-011", "Funcional", "Alta",
     "Pipeline ejecutado al menos una vez.",
     "SQL: SELECT time, COUNT(*) FROM bronze_weather_hourly GROUP BY time HAVING COUNT(*) > 1;",
     "1. Ejecutar el DAG weather_pipeline dos veces seguidas\n2. BD: SELECT time, COUNT(*) FROM bronze_weather_hourly GROUP BY time HAVING COUNT(*) > 1;",
     "• La consulta retorna 0 filas\n• Restricción UNIQUE en columna 'time' previene duplicados\n• Segunda ejecución usa INSERT ... ON CONFLICT DO NOTHING",
     "Pendiente"),

    ("TC-DATA-005", "Error de conexión Open-Meteo genera excepción correcta",
     "RF-003", "Integración", "Alta",
     "Capacidad de bloquear URL de Open-Meteo (URL falsa en extractor).",
     "",
     "1. Simular falla de red hacia api.open-meteo.com (URL falsa en el extractor)\n2. Disparar el DAG weather_pipeline\n3. Observar el estado de la tarea de extracción",
     "• Tarea de Airflow muestra estado 'Failed' (no 'Success')\n• Log contiene traceback del error con mensaje descriptivo\n• No se insertan filas vacías en bronze\n• Las tareas downstream no se ejecutan",
     "Pendiente"),

    ("TC-DATA-006", "Motor de riesgo maneja tabla gold vacía graciosamente",
     "RF-003", "Funcional", "Alta",
     "Acceso a BD.",
     "SQL: TRUNCATE public_gold.gold_risk_features_latest; (solo para prueba, restaurar después)",
     "1. Vaciar tabla gold:\n   TRUNCATE public_gold.gold_risk_features_latest;\n2. Ejecutar tarea run_risk_engine del DAG simulate_pipeline\n3. Observar el log",
     "• Tarea run_risk_engine termina con estado 'Success'\n• Log muestra: 'No hay datos en gold_risk_features_latest, omitiendo ciclo.'\n• Sin excepción NoResultFound\n• No se inserta registro vacío en alerts",
     "Pendiente"),

    ("TC-DATA-007", "Mecanismo de reintento de Airflow ante fallo transitorio",
     "RF-004", "Funcional", "Media",
     "DAG weather_pipeline con retries=3 configurado.",
     "",
     "1. Airflow UI: revisar configuración del DAG\n2. Inspeccionar default_args del DAG en el código fuente\n3. Verificar que retries y retry_delay están definidos",
     "• DAG tiene retries ≥ 1 en default_args\n• retry_delay definido (ej. timedelta(minutes=2))\n• En la UI se puede ver el contador de reintentos en ejecuciones fallidas",
     "Pendiente"),

    ("TC-DATA-008", "Tabla gold_risk_features_latest contiene las métricas esperadas",
     "RF-007", "Integración", "Alta",
     "Pipeline ejecutado.",
     "SQL: SELECT precipitation_1h, precipitation_3h, humidity_avg_6h, trend_1h FROM gold_risk_features_latest;",
     "BD:\nSELECT precipitation_1h, precipitation_3h, precipitation_6h, precipitation_24h, intensity_mm_h, humidity_avg_6h, trend_1h, as_of_time FROM public_gold.gold_risk_features_latest;",
     "• 1 fila presente\n• Campos numéricos con valores válidos (≥ 0)\n• trend_1h ∈ {'subiendo', 'bajando', 'estable'}\n• as_of_time reciente (últimas 24h si el pipeline corrió)",
     "Pendiente"),

    ("TC-DATA-009", "gold_precipitation_history almacena histórico horario",
     "RF-007, RF-012", "Funcional", "Media",
     "Pipeline ejecutado múltiples veces.",
     "SQL: SELECT COUNT(*), MIN(time_local), MAX(time_local) FROM gold_precipitation_history;",
     "BD:\nSELECT COUNT(*), MIN(time_local), MAX(time_local) FROM public_gold.gold_precipitation_history;",
     "• COUNT > 1\n• Los timestamps son únicos y en orden cronológico",
     "Pendiente"),

    ("TC-DATA-010", "Datos crudos se almacenan correctamente en bronze",
     "RF-011", "Funcional", "Alta",
     "Pipeline ejecutado.",
     "SQL: SELECT id, fetched_at, time, precipitation FROM bronze_weather_current ORDER BY fetched_at DESC LIMIT 3;",
     "1. Ejecutar pipeline\n2. BD:\n   SELECT id, fetched_at, time, precipitation, relative_humidity\n   FROM bronze_weather_current\n   ORDER BY fetched_at DESC LIMIT 3;",
     "• Registros recientes con fetched_at actual\n• Todos los campos de meteorología presentes\n• 'time' (timestamp del dato) diferente de 'fetched_at' (timestamp de extracción)",
     "Pendiente"),

    ("TC-DATA-011", "Datos procesados (Silver) se almacenan correctamente",
     "RF-012", "Integración", "Media",
     "dbt run ejecutado.",
     "SQL: SELECT COUNT(*), MIN(time), MAX(time) FROM silver_weather_hourly;",
     "BD:\nSELECT COUNT(*), MIN(time), MAX(time) FROM public_silver.silver_weather_hourly;",
     "• COUNT igual al de bronze (desduplicado)\n• Sin valores nulos en campos calculados",
     "Pendiente"),

    ("TC-DATA-012", "Clasificación de riesgo se almacena en tabla alerts",
     "RF-013", "Funcional", "Alta",
     "Motor de riesgo ejecutado.",
     "SQL: SELECT id, evaluated_at, nivel_riesgo, riesgo_score FROM alerts ORDER BY evaluated_at DESC LIMIT 5;",
     "BD:\nSELECT id, evaluated_at, nivel_riesgo, riesgo_score, precip_1h, precip_3h, humedad_prom_6h\nFROM public.alerts ORDER BY evaluated_at DESC LIMIT 5;",
     "• Registros con todos los campos completos\n• nivel_riesgo ∈ {'VERDE', 'AMARILLO', 'NARANJA', 'ROJO'}\n• riesgo_score entre 0 y 100\n• evaluated_at con timezone UTC",
     "Pendiente"),
]

RISK = [
    ("TC-RISK-001", "Escenario VERDE — precipitación nula produce nivel VERDE",
     "RF-008, RF-010", "Funcional", "Alta",
     "Simulador disponible. Sesión activa.",
     "Preset Verde: precip_1h=0, precip_3h=0, humedad=30",
     "1. Navegar a /simulator\n2. Seleccionar preset Verde\n3. Ejecutar simulación\n4. Esperar 2-3 minutos\n5. Navegar a /risk y verificar nivel actual",
     "• nivel_riesgo = 'VERDE'\n• riesgo_score entre 0 y 25\n• Badge verde visible en la UI",
     "Pendiente"),

    ("TC-RISK-002", "Escenario ROJO — precipitación extrema produce nivel ROJO",
     "RF-008, RF-010", "Funcional", "Alta",
     "Simulador disponible. Sesión activa.",
     "Preset Rojo: precip_1h=40, precip_3h=75, humedad=95",
     "1. Navegar a /simulator\n2. Seleccionar preset Rojo\n3. Ejecutar simulación\n4. Esperar 2-3 minutos\n5. Verificar en /risk y en BD",
     "• nivel_riesgo = 'ROJO'\n• riesgo_score entre 75 y 100\n• Badge rojo en UI\n• Alerta aparece en campana de notificaciones",
     "Pendiente"),

    ("TC-RISK-003", "Escenario NARANJA — precipitación moderada-alta",
     "RF-008, RF-010", "Funcional", "Alta",
     "Simulador disponible.",
     "Preset Naranja: precip_1h=18, precip_3h=35, humedad=85",
     "1. Navegar a /simulator\n2. Usar preset Naranja\n3. Ejecutar y verificar en /risk",
     "• nivel_riesgo = 'NARANJA'\n• riesgo_score entre 50 y 75",
     "Pendiente"),

    ("TC-RISK-004", "Score de riesgo siempre en rango [0, 100]",
     "RF-010", "Funcional", "Alta",
     "Al menos 10 registros en alerts.",
     "SQL: SELECT COUNT(*) FROM alerts WHERE riesgo_score < 0 OR riesgo_score > 100;",
     "BD:\nSELECT COUNT(*) FROM public.alerts\nWHERE riesgo_score < 0 OR riesgo_score > 100;",
     "• COUNT = 0 (ningún registro fuera del rango)",
     "Pendiente"),

    ("TC-RISK-005", "Clasificación consistente con el score (umbrales)",
     "RF-010", "Funcional", "Alta",
     "Múltiples registros en alerts.",
     "SQL de verificación de inconsistencias nivel vs score",
     "BD — verificar inconsistencias:\nSELECT nivel_riesgo, riesgo_score FROM public.alerts\nWHERE\n  (nivel_riesgo='VERDE'    AND riesgo_score >= 25) OR\n  (nivel_riesgo='AMARILLO' AND (riesgo_score < 25 OR riesgo_score >= 50)) OR\n  (nivel_riesgo='NARANJA'  AND (riesgo_score < 50 OR riesgo_score >= 75)) OR\n  (nivel_riesgo='ROJO'     AND riesgo_score < 75);",
     "• La consulta retorna 0 filas (ninguna inconsistencia entre nivel y score)",
     "Pendiente"),

    ("TC-RISK-006", "Endpoint /api/risk/current retorna el resultado más reciente",
     "RF-008", "Funcional", "Alta",
     "Sesión activa. Al menos un registro en alerts.",
     "",
     "1. Postman: GET /api/risk/current\n   Header: Authorization: Bearer <token>\n2. Verificar respuesta\n3. Insertar manualmente un registro nuevo en alerts\n4. Repetir la petición y verificar que retorna el nuevo registro",
     "• HTTP 200 con campos: nivel_riesgo, riesgo_score, nivel_lluvia, evaluated_at\n• Tras insertar registro nuevo, el endpoint devuelve ese registro (ORDER BY DESC LIMIT 1)",
     "Pendiente"),
]

ADMIN = [
    ("TC-ADMIN-001", "Administrador puede listar todos los usuarios del sistema",
     "RF-015", "Funcional", "Alta",
     "Sesión activa con rol 'administrador'.",
     "",
     "1. Navegar a /admin\n2. Verificar que la pestaña Usuarios está seleccionada\n3. Verificar que aparece la tabla de usuarios",
     "• Lista de todos los usuarios registrados\n• Columnas: Nombre, Email, Rol, Estado, Creado, Acciones\n• Usuario admin@alerto.com visible con rol 'administrador'",
     "Pendiente"),

    ("TC-ADMIN-002", "Administrador puede cambiar el rol de un usuario",
     "RF-015", "Funcional", "Alta",
     "Existe usuario con rol 'usuario'. Sesión admin activa.",
     "Usuario objetivo: nuevo@test.com",
     "1. Ir a /admin → pestaña Usuarios\n2. Localizar usuario nuevo@test.com\n3. En selector de rol, cambiar de 'usuario' a 'administrador'\n4. BD: SELECT role FROM users WHERE email='nuevo@test.com';\n5. Verificar en audit_log",
     "• Selector cambia el valor sin recargar la página\n• BD: role='administrador' para ese usuario\n• audit_log: action='update_role', result='success'",
     "Pendiente"),

    ("TC-ADMIN-003", "Administrador puede desactivar una cuenta de usuario",
     "RF-015", "Funcional", "Alta",
     "Existe usuario activo.",
     "",
     "1. Ir a /admin → Usuarios\n2. Hacer clic en el toggle de estado (ToggleRight → ToggleLeft)\n3. Verificar badge cambia de Activo a Inactivo\n4. BD: SELECT is_active FROM users WHERE email='nuevo@test.com';\n5. Intentar login con ese usuario",
     "• Badge cambia a 'Inactivo'\n• BD: is_active = false\n• Login falla con mensaje de cuenta desactivada\n• audit_log: action='deactivate_user'",
     "Pendiente"),

    ("TC-ADMIN-004", "API admin rechaza peticiones de usuarios no administradores",
     "RF-015", "Seguridad", "Alta",
     "Token JWT de usuario con role='usuario'.",
     "Token de usuario regular (no administrador)",
     "1. Postman: GET /api/admin/users con token de rol 'usuario'\n2. PATCH /api/admin/users/1/role con token de rol 'usuario'",
     "• HTTP 403 en ambos endpoints\n• Body: {\"detail\": \"Acceso restringido a administradores.\"}",
     "Pendiente"),

    ("TC-ADMIN-005", "Admin puede ver y editar umbrales de riesgo (RF-005)",
     "RF-005", "Funcional", "Alta",
     "Sesión admin activa. Tabla system_config inicializada.",
     "Nuevo valor para threshold_naranja: 55",
     "1. Navegar a /admin → pestaña Configuración\n2. Verificar 4 parámetros configurables\n3. Cambiar threshold_naranja de 50 a 55\n4. Hacer clic fuera del campo (blur event)\n5. BD: SELECT value FROM system_config WHERE key='threshold_naranja';",
     "• 4 configuraciones visibles con descripción y valor actual\n• BD muestra el nuevo valor tras editar\n• Mensaje 'Guardando...' aparece brevemente",
     "Pendiente"),

    ("TC-ADMIN-006", "Usuario no admin no puede editar la configuración",
     "RF-005", "Seguridad", "Alta",
     "Token de rol 'usuario'.",
     "Token de usuario regular",
     "1. Postman: PATCH /api/config/threshold_rojo con token de rol 'usuario'\n   Body: {\"value\": \"80\"}",
     "• HTTP 403: 'Acceso restringido a administradores.'",
     "Pendiente"),

    ("TC-ADMIN-007", "Configuración de frecuencia del pipeline es visible",
     "RF-006", "Funcional", "Media",
     "Sesión admin activa.",
     "",
     "1. Navegar a /admin → pestaña Configuración\n2. Buscar el parámetro pipeline_interval\n3. Verificar descripción y valor por defecto",
     "• Parámetro pipeline_interval visible\n• Descripción: 'Frecuencia de ejecución del pipeline en minutos'\n• Valor por defecto: 15\n• Campo editable para administradores",
     "Pendiente"),
]

SIM = [
    ("TC-SIM-001", "Simulador valida que precip_3h >= precip_1h",
     "RF-002", "Funcional", "Media",
     "Sesión activa.",
     "precip_1h=20mm, precip_3h=10mm (inválido)",
     "1. Navegar a /simulator\n2. Ajustar precip_1h=20 y precip_3h=10 (inválido)\n3. Observar si el slider de 3h se ajusta automáticamente\n4. Postman: POST /api/simulate con {\"precip_1h\":20, \"precip_3h\":10, \"humedad\":50}",
     "• UI: slider de 3h no puede quedar por debajo del valor de 1h\n• API: HTTP 422 con mensaje 'precip_3h debe ser mayor o igual a precip_1h'",
     "Pendiente"),

    ("TC-SIM-002", "Simulación exitosa dispara pipeline y muestra resultado",
     "RF-002", "Funcional · Integración", "Alta",
     "Airflow activo y DAG simulate_pipeline registrado.",
     "Preset Amarillo: precip_1h=10, precip_3h=20, humedad=70",
     "1. Navegar a /simulator\n2. Seleccionar preset Amarillo\n3. Clic en Ejecutar Simulación\n4. Verificar mensaje de estado 'ok'\n5. Esperar 2-3 minutos\n6. Airflow UI: verificar DAG simulate_pipeline ejecutado\n7. Verificar en /risk el nuevo nivel",
     "• Mensaje de confirmación en la UI\n• DAG simulate_pipeline aparece en ejecución en Airflow UI\n• Nuevo registro en alerts con nivel AMARILLO\n• Sin token de Airflow expuesto al usuario",
     "Pendiente"),

    ("TC-SIM-003", "Simulador rechaza valores fuera del rango permitido",
     "RF-002", "Funcional", "Media",
     "Postman disponible.",
     "precip_1h=200, precip_3h=300, humedad=150 (todos fuera de rango)",
     "1. POST /api/simulate con {\"precip_1h\":200, \"precip_3h\":300, \"humedad\":150}",
     "• HTTP 422 con errores de validación para cada campo fuera de rango\n• precip_1h máximo: 50, precip_3h máximo: 90, humedad máximo: 100",
     "Pendiente"),
]

ALERTS_MOD = [
    ("TC-ALERTS-001", "Página alertas muestra contadores por nivel",
     "RF-008", "Funcional · UI", "Alta",
     "Múltiples registros de distintos niveles en alerts. Sesión activa.",
     "SQL: SELECT nivel_riesgo, COUNT(*) FROM alerts GROUP BY nivel_riesgo;",
     "1. Navegar a /alerts\n2. Verificar la franja de tarjetas de conteo superior\n3. BD: SELECT nivel_riesgo, COUNT(*) FROM public.alerts GROUP BY nivel_riesgo;\n4. Comparar contadores UI vs BD",
     "• 4 tarjetas: ROJO, NARANJA, AMARILLO, VERDE\n• Contadores coinciden con la BD\n• Colores de tarjetas correctos por nivel",
     "Pendiente"),

    ("TC-ALERTS-002", "Filtro por nivel de riesgo funciona correctamente",
     "RF-008", "Funcional · UI", "Media",
     "Registros de múltiples niveles en alerts. Sesión activa.",
     "",
     "1. Navegar a /alerts\n2. Hacer clic en filtro ROJO\n3. Verificar que solo aparecen filas con nivel ROJO\n4. Hacer clic en TODOS\n5. Verificar que vuelven todos los registros",
     "• Filtro ROJO: solo filas rojas visibles\n• Filtro TODOS: todas las filas visibles\n• El filtro activo está visualmente destacado (background azul)",
     "Pendiente"),

    ("TC-ALERTS-003", "Paginación de alertas funciona con muchos registros",
     "RF-008", "Funcional", "Media",
     "Más de 50 registros en alerts.",
     "",
     "1. Navegar a /alerts\n2. Verificar página 1 con máximo 50 filas\n3. Hacer clic en Siguiente\n4. Verificar página 2 con registros más antiguos\n5. Hacer clic en Anterior para volver",
     "• Página 1: máximo 50 registros\n• Botón Siguiente deshabilitado si hay < 50 en página actual\n• Botón Anterior deshabilitado en la primera página\n• Los registros son diferentes entre páginas",
     "Pendiente"),
]

SEC = [
    ("TC-SEC-001", "Contraseñas almacenadas con bcrypt cost factor 12",
     "RNF-SEG-001", "Seguridad", "Alta",
     "Usuario registrado en BD.",
     "SQL: SELECT password_hash FROM users WHERE email='admin@alerto.com';",
     "BD:\nSELECT password_hash FROM users WHERE email = 'admin@alerto.com';\nVerificar formato del hash.",
     "• Hash comienza con $2b$12$ (bcrypt cost factor 12)\n• Contraseña NO está en texto plano\n• Hash tiene al menos 60 caracteres",
     "Pendiente"),

    ("TC-SEC-002", "API responde con headers de seguridad correctos",
     "RNF-SEG-004", "Seguridad", "Alta",
     "Backend activo.",
     "",
     "1. Postman: GET http://localhost:8000/health\n2. Revisar los headers de la respuesta",
     "• X-Content-Type-Options: nosniff\n• X-Frame-Options: DENY\n• X-XSS-Protection: 1; mode=block\n• Referrer-Policy: strict-origin-when-cross-origin\n• Permissions-Policy: geolocation=(), microphone=()",
     "Pendiente"),

    ("TC-SEC-003", "Rate limiting bloquea exceso de intentos de login",
     "RNF-SEG-004", "Seguridad", "Alta",
     "Backend activo.",
     "15 intentos consecutivos de login en < 1 minuto",
     "1. Postman Collection Runner: ejecutar POST /api/auth/login 15 veces en rápida sucesión\n2. Observar las respuestas a partir del intento 11",
     "• Intentos 1–10: HTTP 401 (credenciales inválidas) o 200\n• A partir del intento 11 en el mismo minuto: HTTP 429 Too Many Requests\n• El bloqueo se levanta pasado 1 minuto",
     "Pendiente"),

    ("TC-SEC-004", "Registro de auditoría guarda eventos de login exitosos",
     "RNF-SEG-003", "Seguridad", "Alta",
     "Usuario registrado.",
     "SQL: SELECT ts, user_email, action, result, ip_address FROM audit_log WHERE action='login' ORDER BY ts DESC LIMIT 5;",
     "1. Iniciar sesión con admin@alerto.com\n2. BD:\nSELECT ts, user_email, action, result, ip_address\nFROM audit_log WHERE action='login' ORDER BY ts DESC LIMIT 5;",
     "• Registro con action='login', result='success'\n• user_email = admin@alerto.com\n• ts con fecha/hora reciente\n• ip_address registrada",
     "Pendiente"),

    ("TC-SEC-005", "Registro de auditoría guarda intentos de login fallidos",
     "RNF-SEG-003", "Seguridad", "Alta",
     "Ninguna.",
     "",
     "1. Intentar login con contraseña incorrecta 3 veces\n2. BD:\nSELECT ts, user_email, action, result, details\nFROM audit_log WHERE action='login' AND result='failure'\nORDER BY ts DESC LIMIT 5;",
     "• 3 registros con result='failure'\n• details contiene causa del fallo\n• Ningún hash de contraseña expuesto en details",
     "Pendiente"),

    ("TC-SEC-006", "API no es vulnerable a SQL Injection en el endpoint de login",
     "RNF-SEG-004", "Seguridad", "Alta",
     "Backend activo.",
     "Payload 1: {\"email\": \"' OR '1'='1\", \"password\": \"' OR '1'='1\"}\nPayload 2: {\"email\": \"admin@alerto.com'--\", \"password\": \"x\"}",
     "1. Postman: POST /api/auth/login\n   Body: {\"email\": \"' OR '1'='1\", \"password\": \"' OR '1'='1\"}\n2. También intentar:\n   {\"email\": \"admin@alerto.com'--\", \"password\": \"x\"}",
     "• HTTP 422 (validación EmailStr falla) o HTTP 401\n• No se produce autenticación exitosa con payloads de inyección\n• No se devuelven datos de BD no autorizados",
     "Pendiente"),

    ("TC-SEC-007", "Endpoint health no expone información sensible del sistema",
     "RNF-SEG-004", "Seguridad", "Media",
     "Backend activo.",
     "",
     "1. GET http://localhost:8000/health sin token de autenticación",
     "• HTTP 200 con solo {\"status\": \"ok\", \"service\": \"alerto-backend\"}\n• No expone versiones de dependencias, paths, ni configuración interna",
     "Pendiente"),

    ("TC-SEC-008", "Token JWT con firma inválida es rechazado",
     "RNF-SEG-004, RF-015", "Seguridad", "Alta",
     "Postman disponible.",
     "JWT válido con un carácter del payload modificado manualmente",
     "1. Tomar un JWT válido y modificar un carácter del payload (base64)\n2. GET /api/risk/current con ese token alterado",
     "• HTTP 401: 'Token inválido.'",
     "Pendiente"),
]

PERF = [
    ("TC-PERF-001", "Tiempo de carga de la página principal < 3 segundos",
     "RNF-DIS-002", "Rendimiento", "Alta",
     "Sesión activa. DevTools abiertos.",
     "",
     "1. DevTools → pestaña Network\n2. Hard-reload (Ctrl+Shift+R) en /precipitation\n3. Registrar tiempo en DOMContentLoaded y Load\n4. Verificar tiempo de respuesta de /api/precipitation/current y /api/precipitation/history",
     "• Página completamente cargada en < 3 segundos\n• /api/precipitation/current: tiempo de respuesta < 500ms\n• Gráfico visible sin loading spinner después de carga inicial",
     "Pendiente"),

    ("TC-PERF-002", "Endpoints API responden en < 500ms bajo carga normal",
     "RNF-REN-001", "Rendimiento", "Alta",
     "Postman disponible.",
     "10 llamadas a cada endpoint de forma secuencial",
     "1. Medir tiempo de respuesta (10 llamadas cada uno):\n   GET /api/risk/current\n   GET /api/precipitation/current\n   GET /api/risk/history?limit=100\n2. Registrar tiempo promedio y máximo por endpoint",
     "• Promedio < 200ms por endpoint\n• Máximo < 500ms por endpoint\n• Sin timeouts en ninguna llamada",
     "Pendiente"),

    ("TC-PERF-003", "Sistema soporta 20 usuarios concurrentes",
     "RNF-REN-002", "Rendimiento", "Media",
     "Postman Newman o herramienta de carga disponible.",
     "20 iteraciones paralelas",
     "1. Crear colección Postman con las 5 llamadas principales\n2. Ejecutar con 20 iteraciones paralelas usando Newman\n3. Verificar respuestas y tiempos",
     "• 0 errores HTTP 500\n• Tiempo promedio de respuesta < 1 segundo\n• Sin degradación visible en la UI durante la prueba",
     "Pendiente"),

    ("TC-PERF-004", "Actualización automática de datos en UI cada 60 segundos",
     "RNF-DIS-002", "Rendimiento · UI", "Media",
     "Sesión activa.",
     "",
     "1. Navegar a /precipitation\n2. Abrir DevTools → pestaña Network\n3. Esperar 65 segundos sin interacción\n4. Verificar que se realizan nuevas peticiones a la API",
     "• Peticiones automáticas a /api/precipitation/current e history cada ~60s\n• Los datos en pantalla se actualizan sin reload manual\n• Sin errores de timeout",
     "Pendiente"),
]

INT = [
    ("TC-INT-001", "Sistema se conecta a Open-Meteo via HTTPS GET y recibe JSON",
     "RF-IS-001, RF-IC-001", "Integración", "Alta",
     "Pipeline ejecutado.",
     "",
     "1. Airflow UI: buscar log de la tarea extract_current\n2. Verificar que la URL usada es https://api.open-meteo.com/...\n3. Verificar que los datos recibidos se parsearon como JSON",
     "• URL usa protocolo HTTPS\n• Método HTTP es GET\n• Respuesta parseada exitosamente como JSON\n• Datos guardados en bronze_weather_current",
     "Pendiente"),

    ("TC-INT-002", "Parámetros de ubicación correctos en petición a Open-Meteo",
     "RF-IS-001", "Integración", "Media",
     "Acceso al código fuente de extracción.",
     "Coordenadas esperadas: lat=6.274, lon=-75.582 (Medellín)",
     "1. Revisar airflow/plugins/elt/extract.py\n2. Verificar parámetros de latitud y longitud\n3. Verificar los campos solicitados en la API",
     "• latitude=6.274, longitude=-75.582 (Medellín, Colombia)\n• Campos solicitados: precipitation, rain, showers, relative_humidity, windspeed_10m\n• URL construida correctamente",
     "Pendiente"),

    ("TC-INT-003", "El backend se conecta a PostgreSQL correctamente",
     "RF-011", "Integración", "Alta",
     "Todos los contenedores activos.",
     "",
     "1. GET http://localhost:8000/health → verificar HTTP 200\n2. GET /api/risk/current → verificar que no hay error 500\n3. Revisar logs: docker logs alerto_backend",
     "• Backend responde sin errores de conexión a BD\n• Sin mensajes OperationalError o ConnectionRefused en logs",
     "Pendiente"),

    ("TC-INT-004", "Servicio de simulación dispara correctamente el DAG de Airflow",
     "RF-002", "Integración", "Alta",
     "Airflow activo.",
     "Valores válidos de simulación con token JWT",
     "1. POST /api/simulate con valores válidos y token JWT\n2. Airflow UI: verificar que el DAG simulate_pipeline aparece como nuevo run\n3. Verificar el trigger type (debe ser 'manual')",
     "• DAG simulate_pipeline inicia con estado Running o Success\n• HTTP 200 en la petición de simulación\n• Sin errores 500 ni de autenticación hacia Airflow",
     "Pendiente"),
]

NOTIF = [
    ("TC-NOTIF-001", "Campana muestra 0 alertas cuando no hay eventos críticos",
     "RF-008", "Funcional", "Media",
     "No hay alertas NARANJA/ROJO en las últimas 24h.",
     "",
     "1. Iniciar sesión\n2. Observar la campana en el topbar",
     "• Sin badge numérico (o badge con '0')\n• Al hacer clic: dropdown muestra 'Sin alertas críticas'",
     "Pendiente"),

    ("TC-NOTIF-002", "Campana se actualiza en tiempo real al generarse alerta crítica",
     "RF-008", "Funcional", "Alta",
     "Sin alertas críticas activas. Sesión activa.",
     "",
     "1. Observar campana sin alertas\n2. Desde el simulador, ejecutar escenario ROJO\n3. Esperar 2-3 minutos que el pipeline procese\n4. Verificar la campana sin recargar la página",
     "• La campana actualiza su badge (máx. 60 segundos de diferencia)\n• El dropdown muestra la nueva alerta ROJO con timestamp correcto\n• Color rojo (#ef4444) en el icono de la alerta",
     "Pendiente"),

    ("TC-NOTIF-003", "[PARCIAL] Interfaz notificaciones SMS prevista pero no activa",
     "RF-009, RF-IH-002", "Funcional", "N/A",
     "N/A — funcionalidad no implementada en v1.0.",
     "",
     "1. Verificar en backend/app/ — buscar integración con servicio SMS\n2. Verificar en requirements.txt — presencia de librería SMS",
     "PARA VERSIÓN FUTURA:\n• SMS disparado ante alerta ROJO/NARANJA\n• Contenido: nivel, score, timestamp, enlace al sistema\nOBSERVACIÓN: Requiere integración con Twilio o similar.\nMarcado N/A para v1.0, pendiente para v1.1.",
     "N/A"),
]

ALL_MODULES = [
    ("AUTH",   "Autenticación",       AUTH,      "4472C4"),
    ("UI",     "Interfaz de Usuario", UI,        "70AD47"),
    ("DATA",   "Pipeline de Datos",   DATA,      "ED7D31"),
    ("RISK",   "Motor de Riesgo",     RISK,      "C00000"),
    ("ADMIN",  "Administración",      ADMIN,     "7030A0"),
    ("SIM",    "Simulador",           SIM,       "00B0F0"),
    ("ALERTS", "Alertas",             ALERTS_MOD,"FF7C00"),
    ("SEC",    "Seguridad",           SEC,       "A50000"),
    ("PERF",   "Rendimiento",         PERF,      "00B050"),
    ("INT",    "Integración",         INT,       "0070C0"),
    ("NOTIF",  "Notificaciones",      NOTIF,     "FFC000"),
]

# ─────────────────────────────────────────────────────────────────────────────
# GENERACIÓN DEL EXCEL
# ─────────────────────────────────────────────────────────────────────────────

def add_cf_status(ws, last_row):
    """Agrega formato condicional a la columna K (Estado) para que los colores
    se actualicen automáticamente cuando el tester cambia el valor."""
    rules = [
        ("containsText", "Aprobado",  "D4EDDA", "155724"),
        ("containsText", "Fallido",   "F8D7DA", "721C24"),
        ("containsText", "Bloqueado", "FFF3CD", "856404"),
        ("containsText", "Pendiente", "E9ECEF", "495057"),
        ("containsText", "N/A",       "F0F0F0", "6C757D"),
    ]
    for op, text, bg, fg in rules:
        dxf = DifferentialStyle(
            fill=PatternFill(bgColor=bg),
            font=Font(color=fg, bold=True),
        )
        rule = Rule(type="containsText", operator=op, text=text, dxf=dxf)
        ws.conditional_formatting.add(f"K2:K{last_row}", rule)


def write_module_sheet(wb, code, name, cases, tab_color):
    ws = wb.create_sheet(title=code)
    ws.sheet_properties.tabColor = tab_color

    hdr_fill  = fill(C_HDR_BG)
    hdr_font  = Font(name="Calibri", bold=True, color=C_HDR_FG, size=10)
    hdr_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    bd        = thin_border()
    evid_fill = fill(C_EVID_BG)
    alt_fill  = fill(C_ALT)

    # ── Fila de título del módulo ─────────────────────────────────────────
    ws.merge_cells(f"A1:{get_column_letter(len(COLUMNS))}1")
    title_cell = ws["A1"]
    title_cell.value = f"MÓDULO: {name} ({code}) — {len(cases)} casos de prueba"
    title_cell.font  = Font(name="Calibri", bold=True, color=C_HDR_FG, size=12)
    title_cell.fill  = fill(tab_color)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    # ── Cabecera de columnas ──────────────────────────────────────────────
    for col_i, (col_name, col_w, is_evid) in enumerate(COLUMNS, 1):
        cell = ws.cell(row=2, column=col_i, value=col_name)
        cell.fill      = hdr_fill
        cell.font      = hdr_font
        cell.alignment = hdr_align
        cell.border    = bd
        ws.column_dimensions[get_column_letter(col_i)].width = col_w
    ws.row_dimensions[2].height = 32

    # ── Filas de datos ────────────────────────────────────────────────────
    content_font  = Font(name="Calibri", size=9)
    wrap_top      = Alignment(vertical="top", wrap_text=True)
    center_top    = Alignment(horizontal="center", vertical="top", wrap_text=True)

    for r_off, case in enumerate(cases):
        row = 3 + r_off
        tc_id, title, req, tipo, priority, precond, t_data, steps, expected, estado = case

        values = [
            tc_id, title, req, tipo, priority,
            precond, t_data, steps, expected,
            "",       # Resultado actual
            estado,
            "",       # Evidencia ruta
            "N/A",    # Tipo evidencia
            "",       # Notas evidencia
            "",       # Fecha ejecución
            "",       # Ejecutado por
        ]

        row_bg = fill(C_ALT) if r_off % 2 == 0 else None

        for col_i, val in enumerate(values, 1):
            cell = ws.cell(row=row, column=col_i, value=val)
            cell.font   = content_font
            cell.border = bd
            _, _, is_evid = COLUMNS[col_i - 1]

            if col_i == 5:                              # Prioridad
                cell.fill      = priority_fill(priority)
                cell.alignment = center_top
            elif col_i == 11:                           # Estado
                cell.fill      = status_fill(estado)
                cell.alignment = center_top
                cell.font      = Font(name="Calibri", size=9, bold=True)
            elif is_evid:                               # Columnas de evidencia
                cell.fill      = evid_fill
                cell.alignment = wrap_top
            else:
                cell.alignment = wrap_top
                if row_bg:
                    cell.fill = row_bg

        # Altura de fila según el contenido más largo
        n_lines = max(len(str(v).split("\n")) for v in [steps, expected, precond, t_data])
        ws.row_dimensions[row].height = max(35, min(n_lines * 13, 160))

    # ── Validaciones de datos ─────────────────────────────────────────────
    last_data_row = 2 + len(cases)

    dv_estado = DataValidation(
        type="list",
        formula1='"Pendiente,Aprobado,Fallido,Bloqueado,N/A"',
        allow_blank=False, showDropDown=False,
        prompt="Selecciona el resultado de la ejecución", promptTitle="Estado"
    )
    dv_estado.sqref = f"K3:K{last_data_row}"
    ws.add_data_validation(dv_estado)

    dv_evid = DataValidation(
        type="list",
        formula1='"Screenshot,Video,Ambos,N/A"',
        allow_blank=True, showDropDown=False,
        prompt="Tipo de evidencia adjuntada", promptTitle="Tipo Evidencia"
    )
    dv_evid.sqref = f"M3:M{last_data_row}"
    ws.add_data_validation(dv_evid)

    # ── Formato condicional ───────────────────────────────────────────────
    add_cf_status(ws, last_data_row)

    # ── Paneles y filtro ──────────────────────────────────────────────────
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:{get_column_letter(len(COLUMNS))}{last_data_row}"

    return ws


def create_summary_sheet(wb):
    ws = wb.create_sheet(title="Resumen", index=0)
    ws.sheet_properties.tabColor = "1E3A5F"

    bd       = thin_border()
    hdr_fill = fill(C_HDR_BG)
    hdr_font = Font(name="Calibri", bold=True, color=C_HDR_FG, size=10)
    center   = Alignment(horizontal="center", vertical="center")

    # ── Encabezado principal ──────────────────────────────────────────────
    ws.merge_cells("A1:I1")
    ws["A1"].value = "CASOS DE PRUEBA MANUAL — SISTEMA ALERTO v1.0"
    ws["A1"].font  = Font(name="Calibri", bold=True, size=18, color=C_HDR_FG)
    ws["A1"].fill  = fill(C_HDR_BG)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 45

    ws.merge_cells("A2:I2")
    ws["A2"].value = "Fecha: 2026-05-26  |  Ref: SRS Alerto Rev. 1.0  |  Total: 75 casos  |  Módulos: 11  |  Requisitos cubiertos: 32"
    ws["A2"].font  = Font(name="Calibri", size=10, italic=True, color=C_HDR_FG)
    ws["A2"].fill  = fill("2D5A9B")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    ws.row_dimensions[3].height = 8  # separador

    # ── Tabla de módulos ──────────────────────────────────────────────────
    headers_mod = ["Módulo", "Nombre", "TC Total", "Aprobados", "Fallidos",
                   "Bloqueados", "Pendientes", "N/A", "Progreso"]
    for col_i, h in enumerate(headers_mod, 1):
        cell = ws.cell(row=4, column=col_i, value=h)
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = center
        cell.border    = bd
    ws.row_dimensions[4].height = 28

    col_ws = [12, 28, 10, 12, 12, 12, 12, 8, 14]
    for i, w in enumerate(col_ws, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    total_tc = 0
    for r_off, (code, name, cases, tab_color) in enumerate(ALL_MODULES):
        row = 5 + r_off
        count = len(cases)
        na    = sum(1 for c in cases if c[9] == "N/A")
        pend  = count - na
        total_tc += count

        row_data = [code, name, count, 0, 0, 0, pend, na, "0%"]
        row_bg = fill(C_ALT) if r_off % 2 == 0 else None

        for col_i, val in enumerate(row_data, 1):
            cell = ws.cell(row=row, column=col_i, value=val)
            cell.font   = Font(name="Calibri", size=10)
            cell.border = bd
            cell.alignment = center
            if col_i == 1:
                cell.fill = fill(tab_color)
                cell.font = Font(name="Calibri", bold=True, color=C_HDR_FG, size=10)
            elif row_bg:
                cell.fill = row_bg

        ws.row_dimensions[row].height = 22

    # Fila TOTAL
    total_row = 5 + len(ALL_MODULES)
    for col_i, val in enumerate(["TOTAL", "Todos los módulos", total_tc, 0, 0, 0, total_tc - 1, 1, "0%"], 1):
        cell = ws.cell(row=total_row, column=col_i, value=val)
        cell.font      = Font(name="Calibri", bold=True, size=10, color=C_HDR_FG)
        cell.fill      = hdr_fill
        cell.alignment = center
        cell.border    = bd
    ws.row_dimensions[total_row].height = 26

    # ── Guía de evidencias ────────────────────────────────────────────────
    ev_row = total_row + 2

    ws.merge_cells(f"A{ev_row}:I{ev_row}")
    ws[f"A{ev_row}"].value = "GUÍA PARA REGISTRAR EVIDENCIAS (Screenshots y Videos)"
    ws[f"A{ev_row}"].font  = Font(name="Calibri", bold=True, size=12, color=C_HDR_FG)
    ws[f"A{ev_row}"].fill  = hdr_fill
    ws[f"A{ev_row}"].alignment = center
    ws.row_dimensions[ev_row].height = 28

    guide = [
        ("Col L — Evidencia (Ruta/URL)",
         "Ingresa la ruta relativa al archivo de evidencia o un enlace (URL) al video/imagen.",
         "Ej: ./evidencias/AUTH/TC-AUTH-001_registro_ok.png"),
        ("Col M — Tipo Evidencia",
         "Selecciona del dropdown: Screenshot / Video / Ambos / N/A",
         ""),
        ("Col N — Notas Evidencia",
         "Descripción adicional (contexto, errores visibles, observaciones).",
         "Ej: 'Error visible en consola: 401 Unauthorized'"),
        ("Col O — Fecha Ejecución",
         "Fecha en que se ejecutó el caso (formato DD/MM/YYYY).",
         "Ej: 26/05/2026"),
        ("Col P — Ejecutado Por",
         "Nombre o iniciales del tester que ejecutó el caso.",
         "Ej: J. Gómez"),
        ("Organización de carpetas recomendada",
         "Crear carpeta evidencias/ junto a este archivo, con subcarpetas por módulo:\n"
         "evidencias/AUTH/  evidencias/UI/  evidencias/DATA/  evidencias/RISK/  ...",
         "Ej: ./evidencias/RISK/TC-RISK-002_nivel_rojo_score_82.mp4"),
        ("Herramientas de captura — Screenshots",
         "Windows: Snipping Tool (Win+Shift+S) · DevTools F12 → screenshot · PrtSc",
         "Nombrar: TC-MODULO-NNN_descripcion_breve.png"),
        ("Herramientas de captura — Videos cortos",
         "Windows: Xbox Game Bar (Win+G) · ShareX (libre) · Loom (en línea)\n"
         "Duración sugerida: ≤ 60 segundos por caso de prueba.",
         "Nombrar: TC-MODULO-NNN_descripcion_breve.mp4"),
    ]

    sub_hdr_fill = fill("2D5A9B")
    for i, (campo, desc, ejemplo) in enumerate(guide):
        r = ev_row + 1 + i
        # Campo
        c1 = ws.cell(row=r, column=1, value=campo)
        c1.font      = Font(name="Calibri", bold=True, size=9, color=C_HDR_FG)
        c1.fill      = sub_hdr_fill
        c1.border    = bd
        c1.alignment = Alignment(vertical="top", wrap_text=True)

        # Descripción
        ws.merge_cells(f"B{r}:F{r}")
        c2 = ws.cell(row=r, column=2, value=desc)
        c2.font      = Font(name="Calibri", size=9)
        c2.alignment = Alignment(vertical="top", wrap_text=True)
        c2.border    = bd

        # Ejemplo
        ws.merge_cells(f"G{r}:I{r}")
        c3 = ws.cell(row=r, column=7, value=ejemplo)
        c3.font      = Font(name="Calibri", size=9, italic=True, color="555555")
        c3.fill      = fill(C_EVID_BG)
        c3.alignment = Alignment(vertical="top", wrap_text=True)
        c3.border    = bd

        ws.row_dimensions[r].height = 22 if "\n" not in desc else 34

    ws.freeze_panes = "A3"
    return ws


def main():
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    create_summary_sheet(wb)

    for code, name, cases, tab_color in ALL_MODULES:
        write_module_sheet(wb, code, name, cases, tab_color)

    out_dir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Manuales")
    out_path = os.path.join(out_dir, "Casos_de_Prueba_v1.0.xlsx")
    os.makedirs(out_dir, exist_ok=True)
    wb.save(out_path)

    total = sum(len(m[2]) for m in ALL_MODULES)
    print(f"Excel generado: {out_path}")
    print(f"Hojas: {len(ALL_MODULES) + 1} (1 Resumen + {len(ALL_MODULES)} módulos)")
    print(f"Total casos de prueba: {total}")


if __name__ == "__main__":
    main()
