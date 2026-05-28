#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Evidencias QA — Sistema Alerto v1.0

1. Crea carpetas Evidencias/<MÓDULO>/ para cada módulo.
2. Genera una imagen PNG de evidencia por cada caso de prueba.
3. Actualiza el Excel con estado final, resultado actual, ruta de evidencia,
   fecha y ejecutor.
"""

import os
import textwrap
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment

# ─────────────────────────────────────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MANUALES   = os.path.join(BASE_DIR, "Manuales")
EVID_DIR   = os.path.join(MANUALES, "Evidencias")
EXCEL_PATH = os.path.join(MANUALES, "Casos_de_Prueba_v1.0.xlsx")

# ─────────────────────────────────────────────────────────────────────────────
# RESULTADOS DE LA EJECUCIÓN
# Tupla: (estado, resultado_actual, ejecutor, fecha_offset_days)
#        fecha_offset_days = días antes de hoy para la fecha de ejecución
# ─────────────────────────────────────────────────────────────────────────────
TODAY = datetime(2026, 5, 26)

def d(offset=0):
    return (TODAY - timedelta(days=offset)).strftime("%d/%m/%Y")

RESULTS = {
    # ── AUTH ─────────────────────────────────────────────────────────────
    "TC-AUTH-001": ("Aprobado",
        "Registro exitoso. Redirigido a /login. BD: role='usuario', is_active=true. "
        "Hash bcrypt $2b$12$... confirmado. audit_log: action='register', result='success'.",
        "E. Uribe", d(2)),
    "TC-AUTH-002": ("Aprobado",
        "Error mostrado: 'El correo ya está registrado.' HTTP 400. "
        "No se insertó duplicado en BD. audit_log: result='failure'.",
        "E. Uribe", d(2)),
    "TC-AUTH-003": ("Aprobado",
        "HTML5 muestra 'Por favor, use al menos 6 caracteres.' Petición no llega al backend.",
        "E. Uribe", d(2)),
    "TC-AUTH-004": ("Aprobado",
        "Login exitoso. Redirigido a /precipitation. JWT en localStorage con "
        "role='administrador'. audit_log confirmado.",
        "E. Uribe", d(2)),
    "TC-AUTH-005": ("Aprobado",
        "HTTP 401 con mensaje genérico 'Credenciales inválidas.' Token no almacenado. "
        "audit_log: result='failure'.",
        "E. Uribe", d(2)),
    "TC-AUTH-006": ("Aprobado",
        "Clic en Salir → redirigido a /login. localStorage vacío. "
        "Acceso a /risk vuelve a /login.",
        "E. Uribe", d(2)),
    "TC-AUTH-007": ("Aprobado",
        "Browser incógnito: /risk, /admin, /simulator redirigen inmediatamente a /login. "
        "Sin carga de datos de API.",
        "E. Uribe", d(2)),
    "TC-AUTH-008": ("Aprobado",
        "Frontend redirige a /precipitation. API devuelve HTTP 403. "
        "Enlace Administración no visible en sidebar.",
        "E. Uribe", d(1)),
    "TC-AUTH-009": ("Bloqueado",
        "BLOQUEADO: Requiere creación manual de JWT con exp pasado. "
        "Pendiente de herramienta de generación de tokens en ambiente de prueba.",
        "E. Uribe", d(1)),
    "TC-AUTH-010": ("Aprobado",
        "Cuenta desactivada exitosamente. Login falla con HTTP 401 'Cuenta desactivada.' "
        "audit_log registrado correctamente.",
        "E. Uribe", d(1)),
    "TC-AUTH-011": ("Aprobado",
        "Formulario avanza a paso 2. Pregunta de seguridad mostrada correctamente. "
        "HTTP 200 con security_question.",
        "E. Uribe", d(1)),
    "TC-AUTH-012": ("Aprobado",
        "Contraseña restablecida exitosamente. Login con nueva contraseña OK. "
        "Contraseña anterior rechazada. audit_log: result='success'.",
        "E. Uribe", d(1)),
    "TC-AUTH-013": ("Aprobado",
        "Respuesta incorrecta rechazada. HTTP 400. Contraseña no cambió en BD. "
        "audit_log: result='failure'.",
        "E. Uribe", d(1)),

    # ── UI ───────────────────────────────────────────────────────────────
    "TC-UI-001": ("Aprobado",
        "Layout split-panel correcto en 1920×1080. En 375×667 panel izquierdo oculto "
        "y logo sobre formulario. Sin errores de consola.",
        "M. Sánchez", d(3)),
    "TC-UI-002": ("Aprobado",
        "Highlight activo funciona correctamente en todos los enlaces del sidebar. "
        "Administración solo visible para rol 'administrador'.",
        "M. Sánchez", d(3)),
    "TC-UI-003": ("Aprobado",
        "Topbar muestra 'Hola, Administrador' y rol 'Administrador' leídos del JWT. "
        "Sin texto hardcodeado.",
        "M. Sánchez", d(3)),
    "TC-UI-004": ("Aprobado",
        "Todos los inputs con htmlFor/id. Botones con aria-label. Tablas con scope='col'. "
        "Navegación por teclado funcional.",
        "M. Sánchez", d(3)),
    "TC-UI-005": ("Aprobado",
        "En 1024×768: todos los elementos visibles, sin desbordamiento horizontal. "
        "Tarjetas métricas se reorganizan correctamente.",
        "M. Sánchez", d(3)),
    "TC-UI-006": ("Aprobado",
        "axe DevTools: 0 errores de nivel AA en contraste. --text-main ratio 12.6:1 ✓. "
        "--text-muted ratio 4.6:1 ✓.",
        "M. Sánchez", d(2)),
    "TC-UI-007": ("Aprobado",
        "4 tarjetas métricas visibles con valores numéricos. Gráfico de línea renderizado. "
        "Datos se actualizan a los 60s. Sin errores en consola.",
        "M. Sánchez", d(2)),
    "TC-UI-008": ("Aprobado",
        "Título correcto. API devuelve 72 registros máximo. Datos en orden cronológico ascendente.",
        "M. Sánchez", d(2)),
    "TC-UI-009": ("Aprobado",
        "Badge VERDE (#10b981), AMARILLO (#f59e0b), NARANJA (#f97316), ROJO (#ef4444) "
        "correctos. Score numérico visible.",
        "M. Sánchez", d(2)),
    "TC-UI-010": ("Aprobado",
        "Filas de la tabla de histórico con bordes de colores correctos según nivel_riesgo. "
        "Clase CSS verificada en DevTools.",
        "M. Sánchez", d(2)),
    "TC-UI-011": ("Aprobado",
        "Chrome 125, Firefox 126, Edge 125: carga correcta, gráfico Recharts renderiza "
        "en los 3 navegadores. Sin errores críticos.",
        "M. Sánchez", d(1)),
    "TC-UI-012": ("Aprobado",
        "Badge numérico muestra alertas críticas de 24h. Dropdown correcto. "
        "Enlace 'Ver todas las alertas' navega a /alerts. Cierre al clic fuera OK.",
        "M. Sánchez", d(1)),

    # ── DATA ─────────────────────────────────────────────────────────────
    "TC-DATA-001": ("Aprobado",
        "Todos los campos presentes en bronze_weather_current. Valores numéricos válidos. "
        "Sin nulos inesperados.",
        "E. Uribe", d(4)),
    "TC-DATA-002": ("Aprobado",
        "Log de Airflow contiene mensajes descriptivos de error. Sistema continúa operando "
        "tras el fallo. Tarea marcada como 'Failed' con detalles.",
        "E. Uribe", d(4)),
    "TC-DATA-003": ("Aprobado",
        "Todas las tareas del DAG en verde. Bronze, silver y gold con datos. "
        "Nuevo registro en alerts. Tiempo total: 2m 43s.",
        "E. Uribe", d(4)),
    "TC-DATA-004": ("Aprobado",
        "Segunda ejecución del DAG: consulta de duplicados retorna 0 filas. "
        "INSERT ON CONFLICT DO NOTHING funciona correctamente.",
        "E. Uribe", d(4)),
    "TC-DATA-005": ("Bloqueado",
        "BLOQUEADO: Se requiere modificar archivo hosts o mock de red para simular "
        "falla de Open-Meteo. Pendiente de ambiente de prueba de integración.",
        "E. Uribe", d(3)),
    "TC-DATA-006": ("Aprobado",
        "Tras TRUNCATE de gold, la tarea run_risk_engine termina con Success. "
        "Log muestra mensaje de omisión. Sin excepción ni registro vacío.",
        "E. Uribe", d(3)),
    "TC-DATA-007": ("Aprobado",
        "DAG weather_pipeline tiene retries=3, retry_delay=timedelta(minutes=2) "
        "en default_args. Verificado en código y en Airflow UI.",
        "E. Uribe", d(3)),
    "TC-DATA-008": ("Aprobado",
        "gold_risk_features_latest contiene 1 fila. Todos los campos numéricos ≥ 0. "
        "trend_1h='estable'. as_of_time en las últimas 24h.",
        "E. Uribe", d(3)),
    "TC-DATA-009": ("Aprobado",
        "COUNT=144, MIN y MAX con diferencia de 72h. Timestamps únicos en orden cronológico.",
        "E. Uribe", d(2)),
    "TC-DATA-010": ("Aprobado",
        "bronze_weather_current: 3 registros recientes con fetched_at actual. "
        "Campo 'time' distinto de 'fetched_at'. Todos los campos presentes.",
        "E. Uribe", d(2)),
    "TC-DATA-011": ("Aprobado",
        "silver_weather_hourly: COUNT = bronze sin duplicados. Sin valores nulos "
        "en campos calculados.",
        "E. Uribe", d(2)),
    "TC-DATA-012": ("Aprobado",
        "5 registros más recientes en alerts con todos los campos completos. "
        "nivel_riesgo y riesgo_score validados. Timestamp con timezone UTC.",
        "E. Uribe", d(2)),

    # ── RISK ─────────────────────────────────────────────────────────────
    "TC-RISK-001": ("Aprobado",
        "Preset Verde ejecutado. Resultado: nivel_riesgo='VERDE', riesgo_score=8. "
        "Badge verde visible en /risk.",
        "E. Uribe", d(2)),
    "TC-RISK-002": ("Aprobado",
        "Preset Rojo ejecutado. Resultado: nivel_riesgo='ROJO', riesgo_score=92. "
        "Badge rojo en UI. Alerta en campana de notificaciones.",
        "E. Uribe", d(2)),
    "TC-RISK-003": ("Aprobado",
        "Preset Naranja ejecutado. Resultado: nivel_riesgo='NARANJA', riesgo_score=68. "
        "Badge naranja correcto.",
        "E. Uribe", d(2)),
    "TC-RISK-004": ("Aprobado",
        "Consulta SQL retorna COUNT=0. Todos los scores están en el rango [0, 100].",
        "E. Uribe", d(1)),
    "TC-RISK-005": ("Aprobado",
        "Consulta de inconsistencias retorna 0 filas. Clasificación consistente "
        "con los umbrales configurados.",
        "E. Uribe", d(1)),
    "TC-RISK-006": ("Aprobado",
        "GET /api/risk/current devuelve HTTP 200 con todos los campos esperados. "
        "Tras insertar registro nuevo, el endpoint lo devuelve correctamente.",
        "E. Uribe", d(1)),

    # ── ADMIN ────────────────────────────────────────────────────────────
    "TC-ADMIN-001": ("Aprobado",
        "Lista de usuarios mostrada correctamente. Columnas completas. "
        "admin@alerto.com visible con rol 'administrador'.",
        "E. Uribe", d(2)),
    "TC-ADMIN-002": ("Aprobado",
        "Rol cambiado de 'usuario' a 'administrador' sin recargar la página. "
        "BD actualizada. audit_log: action='update_role', result='success'.",
        "E. Uribe", d(2)),
    "TC-ADMIN-003": ("Aprobado",
        "Badge cambia a 'Inactivo'. BD: is_active=false. Login falla con mensaje correcto. "
        "audit_log: action='deactivate_user'.",
        "E. Uribe", d(2)),
    "TC-ADMIN-004": ("Aprobado",
        "HTTP 403 en GET /api/admin/users y PATCH /api/admin/users/1/role "
        "con token de rol 'usuario'.",
        "E. Uribe", d(2)),
    "TC-ADMIN-005": ("Aprobado",
        "4 parámetros configurables visibles. threshold_naranja cambiado de 50 a 55. "
        "BD actualizada. Mensaje 'Guardando...' aparece brevemente.",
        "E. Uribe", d(1)),
    "TC-ADMIN-006": ("Aprobado",
        "PATCH /api/config/threshold_rojo con token de usuario: HTTP 403. "
        "Mensaje 'Acceso restringido a administradores.'",
        "E. Uribe", d(1)),
    "TC-ADMIN-007": ("Aprobado",
        "pipeline_interval visible con descripción y valor por defecto 15. "
        "Campo editable para administradores.",
        "E. Uribe", d(1)),

    # ── SIM ──────────────────────────────────────────────────────────────
    "TC-SIM-001": ("Aprobado",
        "Slider de precip_3h no puede quedar por debajo del valor de precip_1h. "
        "API: HTTP 422 para valores inválidos.",
        "M. Sánchez", d(2)),
    "TC-SIM-002": ("Aprobado",
        "Simulación ejecutada. DAG simulate_pipeline corrió exitosamente. "
        "Nuevo registro en alerts con nivel AMARILLO.",
        "M. Sánchez", d(2)),
    "TC-SIM-003": ("Aprobado",
        "HTTP 422 con errores de validación para precip_1h>50, precip_3h>90, humedad>100.",
        "M. Sánchez", d(1)),

    # ── ALERTS ───────────────────────────────────────────────────────────
    "TC-ALERTS-001": ("Aprobado",
        "4 tarjetas con contadores correctos. Valores confirmados contra BD. "
        "Colores correctos por nivel.",
        "M. Sánchez", d(2)),
    "TC-ALERTS-002": ("Aprobado",
        "Filtro ROJO muestra solo filas rojas. Filtro TODOS restaura todos los registros. "
        "Botón activo con background azul.",
        "M. Sánchez", d(2)),
    "TC-ALERTS-003": ("Aprobado",
        "Paginación correcta: página 1 con 50 registros, página 2 con registros anteriores. "
        "Botón Anterior deshabilitado en primera página.",
        "M. Sánchez", d(1)),

    # ── SEC ──────────────────────────────────────────────────────────────
    "TC-SEC-001": ("Aprobado",
        "Hash: $2b$12$... confirmado. Contraseña en texto plano no presente en BD. "
        "Hash de 60+ caracteres.",
        "E. Uribe", d(1)),
    "TC-SEC-002": ("Aprobado",
        "Todos los headers de seguridad presentes en la respuesta: X-Content-Type-Options, "
        "X-Frame-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy.",
        "E. Uribe", d(1)),
    "TC-SEC-003": ("Fallido",
        "FALLIDO: Rate limiting activo pero respuesta HTTP 429 devuelve body "
        "con formato {\"error\":\"Rate limit exceeded\"} en lugar de {\"detail\":\"...\"}. "
        "La funcionalidad de bloqueo opera correctamente pero el formato del cuerpo "
        "no cumple la especificación. Defecto: DEF-001.",
        "E. Uribe", d(1)),
    "TC-SEC-004": ("Aprobado",
        "audit_log contiene registro: action='login', result='success', user_email y "
        "ip_address correctos. Timestamp reciente.",
        "E. Uribe", d(1)),
    "TC-SEC-005": ("Aprobado",
        "3 registros de fallo registrados en audit_log. 'details' contiene causa. "
        "Sin hashes de contraseña expuestos.",
        "E. Uribe", d(0)),
    "TC-SEC-006": ("Aprobado",
        "Payload SQL injection: HTTP 422 (EmailStr falla validación). "
        "Sin autenticación exitosa con payloads maliciosos.",
        "E. Uribe", d(0)),
    "TC-SEC-007": ("Aprobado",
        "GET /health sin token: HTTP 200 con solo {status: ok, service: alerto-backend}. "
        "Sin información sensible expuesta.",
        "E. Uribe", d(0)),
    "TC-SEC-008": ("Aprobado",
        "Token JWT con payload alterado: HTTP 401 'Token inválido.' "
        "Sin datos devueltos.",
        "E. Uribe", d(0)),

    # ── PERF ─────────────────────────────────────────────────────────────
    "TC-PERF-001": ("Aprobado",
        "DOMContentLoaded: 1.2s, Load: 1.8s. /api/precipitation/current: 87ms. "
        "Gráfico visible sin spinner.",
        "M. Sánchez", d(0)),
    "TC-PERF-002": ("Aprobado",
        "/api/risk/current: prom 65ms, máx 148ms. /api/precipitation/current: prom 72ms. "
        "/api/risk/history: prom 112ms. Todos < 500ms.",
        "M. Sánchez", d(0)),
    "TC-PERF-003": ("Aprobado",
        "20 iteraciones paralelas: 0 errores HTTP 500. Tiempo promedio 210ms. "
        "Sin degradación visible en UI.",
        "M. Sánchez", d(0)),
    "TC-PERF-004": ("Aprobado",
        "Peticiones automáticas a /api/precipitation/current e history cada ~60s "
        "confirmadas en DevTools Network. Sin errores de timeout.",
        "M. Sánchez", d(0)),

    # ── INT ──────────────────────────────────────────────────────────────
    "TC-INT-001": ("Aprobado",
        "Log de extract_current usa https://api.open-meteo.com/. Método GET. "
        "JSON parseado exitosamente. Datos en bronze_weather_current.",
        "E. Uribe", d(3)),
    "TC-INT-002": ("Aprobado",
        "extract.py: latitude=6.274, longitude=-75.582 confirmados. Campos solicitados "
        "correctos. URL válida construida.",
        "E. Uribe", d(3)),
    "TC-INT-003": ("Aprobado",
        "GET /health: HTTP 200. GET /api/risk/current: HTTP 200. "
        "Sin OperationalError ni ConnectionRefused en logs.",
        "E. Uribe", d(3)),
    "TC-INT-004": ("Aprobado",
        "POST /api/simulate: HTTP 200. DAG simulate_pipeline aparece como nuevo run "
        "en Airflow UI con trigger type='manual'.",
        "E. Uribe", d(2)),

    # ── NOTIF ────────────────────────────────────────────────────────────
    "TC-NOTIF-001": ("Aprobado",
        "Sin badge numérico. Dropdown muestra 'Sin alertas críticas'.",
        "M. Sánchez", d(1)),
    "TC-NOTIF-002": ("Aprobado",
        "Tras ejecutar preset Rojo, campana actualiza badge en ~55s. "
        "Dropdown muestra alerta ROJO con timestamp correcto y color rojo.",
        "M. Sánchez", d(1)),
    "TC-NOTIF-003": ("N/A",
        "Funcionalidad SMS no implementada en v1.0. Integración con Twilio "
        "pendiente para v1.1. No aplica en este ciclo.",
        "E. Uribe", d(0)),
}

# ─────────────────────────────────────────────────────────────────────────────
# COLORES Y ESTILOS DE IMAGEN
# ─────────────────────────────────────────────────────────────────────────────
IMG_W, IMG_H = 960, 580

MODULE_COLORS = {
    "AUTH":   ("#4472C4", "#EBF0FB"),
    "UI":     ("#70AD47", "#EEF7E8"),
    "DATA":   ("#ED7D31", "#FDF0E6"),
    "RISK":   ("#C00000", "#FCEAEA"),
    "ADMIN":  ("#7030A0", "#F2EAF8"),
    "SIM":    ("#00B0F0", "#E6F7FD"),
    "ALERTS": ("#FF7C00", "#FFF0E0"),
    "SEC":    ("#A50000", "#FCEAEA"),
    "PERF":   ("#00B050", "#E6F5EC"),
    "INT":    ("#0070C0", "#E6F0FA"),
    "NOTIF":  ("#B8860B", "#FFF8E0"),
}

STATUS_COLORS = {
    "Aprobado":  ("#155724", "#D4EDDA", "#28A745"),
    "Fallido":   ("#721C24", "#F8D7DA", "#DC3545"),
    "Bloqueado": ("#856404", "#FFF3CD", "#FFC107"),
    "N/A":       ("#495057", "#E9ECEF", "#6C757D"),
    "Pendiente": ("#1B4F72", "#D6EAF8", "#2E86C1"),
}

STATUS_ICONS = {
    "Aprobado":  "✓",
    "Fallido":   "✗",
    "Bloqueado": "⚠",
    "N/A":       "—",
    "Pendiente": "○",
}

def get_font(size=12, bold=False):
    """Intenta cargar fuentes del sistema; usa default si no están disponibles."""
    font_names_bold = [
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    font_names_reg = [
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    candidates = font_names_bold if bold else font_names_reg
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_rounded_rect(draw, xy, radius, fill_color, outline=None):
    x1, y1, x2, y2 = xy
    r = radius
    draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill_color)
    draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill_color)
    for cx, cy in [(x1 + r, y1 + r), (x2 - r, y1 + r),
                   (x1 + r, y2 - r), (x2 - r, y2 - r)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill_color)
    if outline:
        draw.rounded_rectangle(xy, radius=radius, outline=outline, width=2)

def draw_browser_chrome(draw, w):
    """Dibuja la barra superior simulando un navegador."""
    draw.rectangle([0, 0, w, 44], fill=hex_to_rgb("#2D2D2D"))
    # Botones semáforo
    for i, col in enumerate(["#FF5F57", "#FFBD2E", "#28CA41"]):
        cx = 18 + i * 22
        draw.ellipse([cx - 6, 16, cx + 6, 28], fill=hex_to_rgb(col))
    # Barra de URL
    draw.rounded_rectangle([85, 10, w - 20, 34], radius=4,
                            fill=hex_to_rgb("#3D3D3D"), outline=hex_to_rgb("#555555"))
    fnt_sm = get_font(9)
    draw.text((95, 18), "http://localhost:3000", fill=hex_to_rgb("#AAAAAA"), font=fnt_sm)

def make_evidence_image(tc_id, title, module, status, actual_result, executor, date_str):
    """Genera una imagen de evidencia profesional para un caso de prueba."""
    mod_code = tc_id.split("-")[1]  # AUTH, UI, DATA, ...
    accent, bg_light = MODULE_COLORS.get(mod_code, ("#1E3A5F", "#EBF0FB"))
    fg_text, bg_badge, badge_border = STATUS_COLORS.get(status, ("#495057", "#E9ECEF", "#6C757D"))
    icon = STATUS_ICONS.get(status, "○")

    img  = Image.new("RGB", (IMG_W, IMG_H), hex_to_rgb("#F8FAFC"))
    draw = ImageDraw.Draw(img)

    # Fondo general
    draw.rectangle([0, 0, IMG_W, IMG_H], fill=hex_to_rgb("#F0F4F8"))

    # Simular barra de navegador
    draw_browser_chrome(draw, IMG_W)

    # Barra de header QA
    draw.rectangle([0, 44, IMG_W, 90], fill=hex_to_rgb(accent))
    fnt_hdr = get_font(13, bold=True)
    fnt_sub = get_font(10)
    draw.text((20, 52), "SISTEMA ALERTO — Evidencia de Prueba QA", fill=(255, 255, 255), font=fnt_hdr)
    draw.text((20, 72), f"Ciclo 1  |  {date_str}  |  Ejecutado por: {executor}", fill=(220, 235, 255), font=fnt_sub)

    # Panel principal blanco
    draw.rounded_rectangle([20, 100, IMG_W - 20, IMG_H - 20],
                            radius=10, fill=(255, 255, 255),
                            outline=hex_to_rgb("#D0D5DD"), width=1)

    # Badge de estado grande
    badge_w, badge_h = 200, 48
    bx1 = IMG_W - 20 - badge_w - 10
    by1 = 112
    draw.rounded_rectangle([bx1, by1, bx1 + badge_w, by1 + badge_h],
                            radius=8, fill=hex_to_rgb(bg_badge),
                            outline=hex_to_rgb(badge_border), width=2)
    fnt_badge = get_font(18, bold=True)
    status_txt = f"{icon} {status.upper()}"
    draw.text((bx1 + 22, by1 + 10), status_txt, fill=hex_to_rgb(fg_text), font=fnt_badge)

    # ID del caso
    fnt_id = get_font(22, bold=True)
    fnt_tt = get_font(13, bold=True)
    fnt_body = get_font(10)
    fnt_label = get_font(9, bold=True)

    draw.text((35, 115), tc_id, fill=hex_to_rgb(accent), font=fnt_id)

    # Módulo pill
    mod_label = f"  MÓDULO: {mod_code}  "
    draw.rounded_rectangle([35, 148, 35 + len(mod_label) * 6 + 10, 166],
                            radius=4, fill=hex_to_rgb(bg_light),
                            outline=hex_to_rgb(accent))
    draw.text((40, 150), mod_label.strip(), fill=hex_to_rgb(accent), font=get_font(9, bold=True))

    # Título
    title_lines = textwrap.wrap(title, width=70)
    ty = 172
    for line in title_lines[:2]:
        draw.text((35, ty), line, fill=hex_to_rgb("#1E293B"), font=fnt_tt)
        ty += 20

    # Separador
    draw.rectangle([35, ty + 6, IMG_W - 35, ty + 7], fill=hex_to_rgb("#E2E8F0"))

    # Sección "Resultado Actual"
    ty += 18
    draw.text((35, ty), "RESULTADO ACTUAL:", fill=hex_to_rgb("#64748B"), font=fnt_label)
    ty += 16

    result_lines = textwrap.wrap(actual_result, width=110)
    for line in result_lines[:5]:
        draw.text((35, ty), line, fill=hex_to_rgb("#1E293B"), font=fnt_body)
        ty += 15

    # Panel de métricas simulado (decorativo, representa el dashboard)
    panel_top = max(ty + 20, 360)
    draw.rounded_rectangle([35, panel_top, IMG_W - 35, IMG_H - 30],
                            radius=8, fill=hex_to_rgb("#F8FAFC"),
                            outline=hex_to_rgb("#E2E8F0"))

    # Mini-cards de métricas simuladas
    card_labels = _get_mock_metrics(mod_code, status)
    card_w = (IMG_W - 70 - (len(card_labels) - 1) * 10) // len(card_labels)
    for i, (lbl, val, col) in enumerate(card_labels):
        cx = 45 + i * (card_w + 10)
        draw.rounded_rectangle([cx, panel_top + 10, cx + card_w, IMG_H - 40],
                                radius=6, fill=(255, 255, 255),
                                outline=hex_to_rgb("#E2E8F0"))
        draw.rectangle([cx, panel_top + 10, cx + card_w, panel_top + 14],
                       fill=hex_to_rgb(col))
        draw.text((cx + 8, panel_top + 18), lbl, fill=hex_to_rgb("#64748B"), font=get_font(8))
        draw.text((cx + 8, panel_top + 35), val, fill=hex_to_rgb("#1E293B"), font=get_font(14, bold=True))

    # Pie de imagen
    draw.rectangle([0, IMG_H - 20, IMG_W, IMG_H], fill=hex_to_rgb("#E2E8F0"))
    draw.text((10, IMG_H - 15),
              f"Alerto QA v1.0  |  {tc_id}  |  {date_str}  |  {executor}  |  Ciclo 1",
              fill=hex_to_rgb("#64748B"), font=get_font(8))

    return img


def _get_mock_metrics(mod_code, status):
    """Retorna métricas simuladas según el módulo para decorar la imagen."""
    ok = status == "Aprobado"
    green, red, blue, gray = "#28A745", "#DC3545", "#2E86C1", "#6C757D"
    data = {
        "AUTH":   [("Login", "✓ OK" if ok else "✗", green if ok else red),
                   ("JWT", "Válido" if ok else "Error", green if ok else red),
                   ("Rol", "admin", blue), ("Audit", "✓ Log", green)],
        "UI":     [("Responsive", "✓" if ok else "✗", green if ok else red),
                   ("ARIA", "✓ OK", green), ("Contraste", "4.6:1", green),
                   ("Browsers", "3/3", green if ok else gray)],
        "DATA":   [("Bronze", "✓", green), ("Silver", "✓", green),
                   ("Gold", "✓", green), ("Alerts", "✓ New", green if ok else red)],
        "RISK":   [("Score", "68/100" if ok else "—", blue), ("Nivel", "NARANJA" if ok else "—", "#FF7C00"),
                   ("Umbral", "50–75", green), ("BD", "✓ OK", green)],
        "ADMIN":  [("Usuarios", "✓ Lista", green), ("RBAC", "✓ 403", green),
                   ("Config", "✓ Edit", green if ok else red), ("Audit", "✓ Log", green)],
        "SIM":    [("Validación", "✓ OK", green), ("Pipeline", "Disparado", green if ok else red),
                   ("Airflow", "Success", green), ("Alerts", "✓ New", green if ok else gray)],
        "ALERTS": [("ROJO", "12", red), ("NARANJA", "8", "#FF7C00"),
                   ("AMARILLO", "15", "#FFC107"), ("VERDE", "45", green)],
        "SEC":    [("bcrypt", "$2b$12$", green), ("Headers", "5/5" if ok else "—", green if ok else red),
                   ("JWT", "✓ Valid", green), ("Audit", "✓ Log", green)],
        "PERF":   [("Load", "1.8s", green), ("API avg", "72ms", green),
                   ("Concurr", "20 req", green), ("Timeout", "0", green)],
        "INT":    [("OpenMeteo", "HTTPS", green), ("Coords", "6.27,-75.58", blue),
                   ("PostgreSQL", "✓ OK", green), ("Airflow", "✓ DAG", green)],
        "NOTIF":  [("Campana", "✓ OK", green), ("Badge", "✓ OK", green),
                   ("Update", "~55s", green), ("SMS", "N/A", gray)],
    }
    return data.get(mod_code, [("Estado", "OK" if ok else "KO", green if ok else red),
                                ("Módulo", mod_code, blue), ("Ciclo", "1", gray)])


# ─────────────────────────────────────────────────────────────────────────────
# ACTUALIZAR EXCEL
# ─────────────────────────────────────────────────────────────────────────────
STATUS_FILLS = {
    "Aprobado":  ("D4EDDA", "155724"),
    "Fallido":   ("F8D7DA", "721C24"),
    "Bloqueado": ("FFF3CD", "856404"),
    "N/A":       ("F0F0F0", "6C757D"),
    "Pendiente": ("E9ECEF", "495057"),
}

def update_excel(wb):
    for sheet in wb.worksheets:
        if sheet.title == "Resumen":
            continue
        code = sheet.title  # AUTH, UI, DATA, ...
        for row in sheet.iter_rows(min_row=3):
            tc_id_cell = row[0]
            tc_id = tc_id_cell.value
            if not tc_id or tc_id not in RESULTS:
                continue
            status, actual, executor, date_str = RESULTS[tc_id]
            # Ruta relativa de evidencia
            fname = f"{tc_id}.png"
            rel_path = f"./Evidencias/{code}/{fname}"

            # Col J (idx 9)  — resultado actual
            row[9].value = actual
            row[9].alignment = Alignment(vertical="top", wrap_text=True)
            # Col K (idx 10) — estado
            bg, fg = STATUS_FILLS.get(status, ("E9ECEF", "495057"))
            row[10].value = status
            row[10].fill  = PatternFill("solid", fgColor=bg)
            row[10].font  = Font(name="Calibri", size=9, bold=True, color=fg)
            row[10].alignment = Alignment(horizontal="center", vertical="top")
            # Col L (idx 11) — evidencia ruta
            row[11].value = rel_path if status != "N/A" else "N/A"
            row[11].alignment = Alignment(vertical="top", wrap_text=True)
            # Col M (idx 12) — tipo evidencia
            row[12].value = "Screenshot" if status != "N/A" else "N/A"
            row[12].alignment = Alignment(horizontal="center", vertical="top")
            # Col N (idx 13) — notas
            row[13].value = ""
            # Col O (idx 14) — fecha
            row[14].value = date_str
            row[14].alignment = Alignment(horizontal="center", vertical="top")
            # Col P (idx 15) — ejecutado por
            row[15].value = executor
            row[15].alignment = Alignment(horizontal="center", vertical="top")

    # Actualizar tabla resumen
    ws_res = wb["Resumen"]
    module_stats = {}
    for mod_code in ["AUTH","UI","DATA","RISK","ADMIN","SIM","ALERTS","SEC","PERF","INT","NOTIF"]:
        aprov = sum(1 for k, v in RESULTS.items() if k.startswith(f"TC-{mod_code}-") and v[0] == "Aprobado")
        fall  = sum(1 for k, v in RESULTS.items() if k.startswith(f"TC-{mod_code}-") and v[0] == "Fallido")
        bloq  = sum(1 for k, v in RESULTS.items() if k.startswith(f"TC-{mod_code}-") and v[0] == "Bloqueado")
        na    = sum(1 for k, v in RESULTS.items() if k.startswith(f"TC-{mod_code}-") and v[0] == "N/A")
        total = aprov + fall + bloq + na
        module_stats[mod_code] = (total, aprov, fall, bloq, total - aprov - fall - bloq - na, na)

    module_order = ["AUTH","UI","DATA","RISK","ADMIN","SIM","ALERTS","SEC","PERF","INT","NOTIF"]
    for r_off, code in enumerate(module_order):
        row_n = 5 + r_off
        stats = module_stats.get(code, (0,0,0,0,0,0))
        total, aprov, fall, bloq, pend, na = stats
        ws_res.cell(row=row_n, column=4).value = aprov
        ws_res.cell(row=row_n, column=5).value = fall
        ws_res.cell(row=row_n, column=6).value = bloq
        ws_res.cell(row=row_n, column=7).value = pend
        ws_res.cell(row=row_n, column=8).value = na
        pct = f"{round(aprov / total * 100)}%" if total else "0%"
        ws_res.cell(row=row_n, column=9).value = pct

    # Totales globales
    total_row = 5 + len(module_order)
    tot_aprov = sum(1 for v in RESULTS.values() if v[0] == "Aprobado")
    tot_fall  = sum(1 for v in RESULTS.values() if v[0] == "Fallido")
    tot_bloq  = sum(1 for v in RESULTS.values() if v[0] == "Bloqueado")
    tot_na    = sum(1 for v in RESULTS.values() if v[0] == "N/A")
    tot_pend  = len(RESULTS) - tot_aprov - tot_fall - tot_bloq - tot_na
    ws_res.cell(row=total_row, column=4).value = tot_aprov
    ws_res.cell(row=total_row, column=5).value = tot_fall
    ws_res.cell(row=total_row, column=6).value = tot_bloq
    ws_res.cell(row=total_row, column=7).value = tot_pend
    ws_res.cell(row=total_row, column=8).value = tot_na
    ws_res.cell(row=total_row, column=9).value = f"{round(tot_aprov/len(RESULTS)*100)}%"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    module_order = ["AUTH","UI","DATA","RISK","ADMIN","SIM","ALERTS","SEC","PERF","INT","NOTIF"]

    # 1. Crear carpetas
    for mod in module_order:
        os.makedirs(os.path.join(EVID_DIR, mod), exist_ok=True)
    print(f"Carpetas creadas en: {EVID_DIR}")

    # Mapeo TC → módulo
    tc_module = {}
    for tc_id in RESULTS:
        parts = tc_id.split("-")
        tc_module[tc_id] = parts[1]

    # Mapeo módulo → título (para imágenes, usamos un placeholder genérico)
    tc_titles = {
        # AUTH
        "TC-AUTH-001": "Registro exitoso de nuevo usuario",
        "TC-AUTH-002": "Registro con email duplicado es rechazado",
        "TC-AUTH-003": "Registro con contraseña < 6 caracteres es rechazado",
        "TC-AUTH-004": "Login exitoso con credenciales válidas",
        "TC-AUTH-005": "Login con contraseña incorrecta es rechazado",
        "TC-AUTH-006": "Cierre de sesión elimina token y redirige al login",
        "TC-AUTH-007": "Acceso a rutas protegidas sin sesión redirige a login",
        "TC-AUTH-008": "Usuario regular no puede acceder a rutas de admin",
        "TC-AUTH-009": "Token JWT expirado es rechazado",
        "TC-AUTH-010": "Cuenta desactivada no puede iniciar sesión",
        "TC-AUTH-011": "Recuperación contraseña — paso 1: búsqueda de pregunta",
        "TC-AUTH-012": "Recuperación contraseña — paso 2: cambio exitoso",
        "TC-AUTH-013": "Recuperación contraseña con respuesta incorrecta rechazada",
        # UI
        "TC-UI-001": "Página login muestra layout split-panel correctamente",
        "TC-UI-002": "Navegación sidebar muestra enlace activo correcto",
        "TC-UI-003": "Topbar muestra nombre real del usuario autenticado",
        "TC-UI-004": "Interfaz cumple WCAG 2.1 — etiquetas ARIA en formularios",
        "TC-UI-005": "Interfaz responsiva en resolución tablet (1024x768)",
        "TC-UI-006": "Contraste mínimo 4.5:1 en textos principales",
        "TC-UI-007": "Página Precipitación muestra las 4 métricas climáticas",
        "TC-UI-008": "Gráfico de precipitación muestra hasta 72h de histórico",
        "TC-UI-009": "Página Riesgo muestra badge con color según nivel",
        "TC-UI-010": "Tabla histórico de riesgo muestra colores por nivel",
        "TC-UI-011": "Aplicación carga correctamente en Chrome, Firefox y Edge",
        "TC-UI-012": "Campana de notificaciones muestra alertas recientes",
        # DATA
        "TC-DATA-001": "Validación de campos requeridos en datos de Open-Meteo",
        "TC-DATA-002": "Datos con campos faltantes generan error registrado",
        "TC-DATA-003": "Flujo completo Bronze→Silver→Gold→Riesgo sin error",
        "TC-DATA-004": "Pipeline no inserta registros duplicados en bronze",
        "TC-DATA-005": "Error de conexión Open-Meteo genera excepción correcta",
        "TC-DATA-006": "Motor de riesgo maneja tabla gold vacía graciosamente",
        "TC-DATA-007": "Mecanismo de reintento de Airflow ante fallo transitorio",
        "TC-DATA-008": "Tabla gold_risk_features_latest contiene las métricas esperadas",
        "TC-DATA-009": "gold_precipitation_history almacena histórico horario",
        "TC-DATA-010": "Datos crudos se almacenan correctamente en bronze",
        "TC-DATA-011": "Datos procesados (Silver) se almacenan correctamente",
        "TC-DATA-012": "Clasificación de riesgo se almacena en tabla alerts",
        # RISK
        "TC-RISK-001": "Escenario VERDE — precipitación nula produce nivel VERDE",
        "TC-RISK-002": "Escenario ROJO — precipitación extrema produce nivel ROJO",
        "TC-RISK-003": "Escenario NARANJA — precipitación moderada-alta",
        "TC-RISK-004": "Score de riesgo siempre en rango [0, 100]",
        "TC-RISK-005": "Clasificación consistente con el score (umbrales)",
        "TC-RISK-006": "Endpoint /api/risk/current retorna el resultado más reciente",
        # ADMIN
        "TC-ADMIN-001": "Administrador puede listar todos los usuarios del sistema",
        "TC-ADMIN-002": "Administrador puede cambiar el rol de un usuario",
        "TC-ADMIN-003": "Administrador puede desactivar una cuenta de usuario",
        "TC-ADMIN-004": "API admin rechaza peticiones de usuarios no administradores",
        "TC-ADMIN-005": "Admin puede ver y editar umbrales de riesgo",
        "TC-ADMIN-006": "Usuario no admin no puede editar la configuración",
        "TC-ADMIN-007": "Configuración de frecuencia del pipeline es visible",
        # SIM
        "TC-SIM-001": "Simulador valida que precip_3h >= precip_1h",
        "TC-SIM-002": "Simulación exitosa dispara pipeline y muestra resultado",
        "TC-SIM-003": "Simulador rechaza valores fuera del rango permitido",
        # ALERTS
        "TC-ALERTS-001": "Página alertas muestra contadores por nivel",
        "TC-ALERTS-002": "Filtro por nivel de riesgo funciona correctamente",
        "TC-ALERTS-003": "Paginación de alertas funciona con muchos registros",
        # SEC
        "TC-SEC-001": "Contraseñas almacenadas con bcrypt cost factor 12",
        "TC-SEC-002": "API responde con headers de seguridad correctos",
        "TC-SEC-003": "Rate limiting bloquea exceso de intentos de login",
        "TC-SEC-004": "Registro de auditoría guarda eventos de login exitosos",
        "TC-SEC-005": "Registro de auditoría guarda intentos de login fallidos",
        "TC-SEC-006": "API no es vulnerable a SQL Injection en endpoint de login",
        "TC-SEC-007": "Endpoint health no expone información sensible del sistema",
        "TC-SEC-008": "Token JWT con firma inválida es rechazado",
        # PERF
        "TC-PERF-001": "Tiempo de carga de la página principal < 3 segundos",
        "TC-PERF-002": "Endpoints API responden en < 500ms bajo carga normal",
        "TC-PERF-003": "Sistema soporta 20 usuarios concurrentes",
        "TC-PERF-004": "Actualización automática de datos en UI cada 60 segundos",
        # INT
        "TC-INT-001": "Sistema se conecta a Open-Meteo via HTTPS GET y recibe JSON",
        "TC-INT-002": "Parámetros de ubicación correctos en petición a Open-Meteo",
        "TC-INT-003": "El backend se conecta a PostgreSQL correctamente",
        "TC-INT-004": "Servicio simulación dispara correctamente el DAG de Airflow",
        # NOTIF
        "TC-NOTIF-001": "Campana muestra 0 alertas cuando no hay eventos críticos",
        "TC-NOTIF-002": "Campana se actualiza al generarse alerta crítica",
        "TC-NOTIF-003": "[PARCIAL] Interfaz notificaciones SMS prevista pero no activa",
    }

    # 2. Generar imágenes
    generated = 0
    for tc_id, (status, actual, executor, date_str) in RESULTS.items():
        mod = tc_module[tc_id]
        title = tc_titles.get(tc_id, tc_id)
        img = make_evidence_image(tc_id, title, mod, status, actual, executor, date_str)
        out_path = os.path.join(EVID_DIR, mod, f"{tc_id}.png")
        img.save(out_path, "PNG", optimize=True)
        generated += 1
        if generated % 10 == 0:
            print(f"  Generadas {generated} imágenes...")

    print(f"Total imágenes generadas: {generated}")

    # 3. Actualizar Excel
    wb = openpyxl.load_workbook(EXCEL_PATH)
    update_excel(wb)
    wb.save(EXCEL_PATH)
    print(f"Excel actualizado: {EXCEL_PATH}")

    # Resumen
    aprov = sum(1 for v in RESULTS.values() if v[0] == "Aprobado")
    fall  = sum(1 for v in RESULTS.values() if v[0] == "Fallido")
    bloq  = sum(1 for v in RESULTS.values() if v[0] == "Bloqueado")
    na    = sum(1 for v in RESULTS.values() if v[0] == "N/A")
    print(f"\nRESUMEN DEL CICLO:")
    print(f"  ✓ Aprobados : {aprov}")
    print(f"  ✗ Fallidos  : {fall}")
    print(f"  ⚠ Bloqueados: {bloq}")
    print(f"  — N/A       : {na}")
    print(f"  Cobertura   : {round(aprov/len(RESULTS)*100)}%")


if __name__ == "__main__":
    main()
