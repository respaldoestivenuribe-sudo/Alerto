# Casos de Prueba Manual — Sistema Alerto
**Versión:** 1.0  
**Fecha:** 2026-05-26  
**Referencia:** SRS Alerto Rev. 1.0  

---

## Convenciones

| Campo | Descripción |
|---|---|
| **ID** | Identificador único: `TC-[MÓDULO]-[NNN]` |
| **Tipo** | Funcional · Seguridad · Rendimiento · Integración · UI · Regresión |
| **Prioridad** | 🔴 Alta · 🟡 Media · 🟢 Baja |
| **Estado** | ⬜ Pendiente · ✅ Aprobado · ❌ Fallido · ⚠️ Bloqueado · ➖ N/A |

---

# MÓDULO 1 — AUTENTICACIÓN (AUTH)
> Requisitos cubiertos: RF-014, RF-015, RF-016

---

## TC-AUTH-001
**Título:** Registro exitoso de nuevo usuario  
**Requisito:** RF-014, RF-015  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Contenedores activos. Email `nuevo@test.com` no registrado.

**Datos de prueba:**
```
Nombre:            Juan Prueba
Email:             nuevo@test.com
Contraseña:        Test1234!
Pregunta:          ¿Cuál es el nombre de tu primera mascota?
Respuesta:         firulais
```

**Pasos:**
1. Navegar a `http://localhost:3000/register`
2. Completar el formulario con los datos de prueba
3. Hacer clic en **Crear Cuenta**
4. Verificar redirección a `/login`
5. En BD: `SELECT * FROM users WHERE email='nuevo@test.com';`

**Resultado esperado:**
- Redirección exitosa a `/login`
- Registro en tabla `users` con `role='usuario'` e `is_active=true`
- `password_hash` comienza con `$2b$` (bcrypt)
- `security_answer` también almacenada como hash bcrypt
- Registro en `audit_log` con `action='register'` y `result='success'`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-002
**Título:** Registro con email duplicado es rechazado  
**Requisito:** RF-014  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** `admin@alerto.com` ya existe en BD.

**Datos de prueba:**
```
Email: admin@alerto.com
Contraseña: cualquiera
```

**Pasos:**
1. Ir a `/register`
2. Ingresar email `admin@alerto.com` con cualquier contraseña y datos válidos
3. Clic en **Crear Cuenta**

**Resultado esperado:**
- Mensaje de error: *"El correo ya está registrado."*
- HTTP 400 en el endpoint `/api/auth/register`
- No se inserta duplicado en BD
- `audit_log` registra `result='failure'`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-003
**Título:** Registro con contraseña de menos de 6 caracteres es rechazado  
**Requisito:** RF-014  
**Tipo:** Funcional · 🟡 Media  
**Precondiciones:** Ninguna.

**Datos de prueba:**
```
Contraseña: abc
```

**Pasos:**
1. Ir a `/register`
2. Ingresar contraseña de 3 caracteres
3. Clic en **Crear Cuenta**

**Resultado esperado:**
- Validación del formulario impide el envío (HTML5 o mensaje de error Pydantic)
- HTTP 422 si la petición llega al backend

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-004
**Título:** Login exitoso con credenciales válidas  
**Requisito:** RF-014, RF-015  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Usuario `admin@alerto.com` con contraseña `alerto123**` existe.

**Pasos:**
1. Navegar a `http://localhost:3000/login`
2. Ingresar `admin@alerto.com` / `alerto123**`
3. Clic en **Ingresar al Sistema**
4. Verificar redirección a `/precipitation`
5. En DevTools → Application → LocalStorage: verificar existencia de `token`
6. Decodificar el JWT y verificar payload

**Resultado esperado:**
- Redirección exitosa a `/precipitation`
- `localStorage['token']` contiene JWT válido
- JWT payload contiene: `sub`, `id`, `name`, `role='administrador'`, `exp`
- `audit_log` registra `action='login'` y `result='success'`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-005
**Título:** Login con contraseña incorrecta es rechazado  
**Requisito:** RF-014  
**Tipo:** Funcional · Seguridad · 🔴 Alta  
**Precondiciones:** Usuario `admin@alerto.com` existe.

**Datos de prueba:**
```
Email:      admin@alerto.com
Contraseña: contraseña_incorrecta
```

**Pasos:**
1. Ir a `/login`
2. Ingresar credenciales incorrectas
3. Clic en **Ingresar al Sistema**

**Resultado esperado:**
- Mensaje de error: *"Credenciales inválidas."*
- HTTP 401 en el endpoint
- NO se revela si el usuario existe (mensaje genérico)
- `audit_log` registra `result='failure'` con detalles
- No se almacena token

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-006
**Título:** Cierre de sesión elimina token y redirige al login  
**Requisito:** RF-015  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Usuario autenticado en sesión activa.

**Pasos:**
1. Iniciar sesión con credenciales válidas
2. Navegar a `/precipitation`
3. Clic en botón **Salir** en la barra superior
4. Verificar redirección
5. Verificar LocalStorage
6. Intentar navegar manualmente a `/risk`

**Resultado esperado:**
- Redirección a `/login`
- `localStorage['token']` eliminado (vacío)
- Acceso directo a `/risk` redirige a `/login` (ProtectedRoute activo)

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-007
**Título:** Acceso a rutas protegidas sin sesión redirige a login  
**Requisito:** RF-015  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Ningún token en LocalStorage.

**Pasos:**
1. En browser nuevo (incógnito), intentar navegar a `http://localhost:3000/risk`
2. Intentar navegar a `http://localhost:3000/admin`
3. Intentar navegar a `http://localhost:3000/simulator`

**Resultado esperado:**
- Todas las rutas redirigen a `/login` inmediatamente
- No se carga ningún dato de la API

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-008
**Título:** Usuario con rol `usuario` no puede acceder a rutas de admin  
**Requisito:** RF-015 (RBAC)  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Existe usuario con `role='usuario'` y sesión activa.

**Pasos:**
1. Crear usuario regular (sin rol administrador)
2. Iniciar sesión con ese usuario
3. Intentar navegar manualmente a `http://localhost:3000/admin`
4. Desde Postman: `GET /api/admin/users` con token del usuario regular

**Resultado esperado:**
- Frontend redirige a `/precipitation` (AdminRoute lo bloquea)
- La API retorna HTTP 403 `"Acceso restringido a administradores."`
- El enlace **Administración** NO aparece en el sidebar

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-009
**Título:** Token JWT expirado es rechazado  
**Requisito:** RF-015  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Se dispone de un token JWT expirado (puede generarse manualmente).

**Pasos:**
1. Desde Postman: construir un JWT con `exp` en el pasado usando `alerto_secret`
2. Hacer `GET /api/risk/current` con `Authorization: Bearer <token_expirado>`

**Resultado esperado:**
- HTTP 401 con mensaje `"Token expirado."`
- No se devuelven datos

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-010
**Título:** Cuenta desactivada no puede iniciar sesión  
**Requisito:** RF-015  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Administrador tiene acceso. Existe usuario `desact@test.com`.

**Pasos:**
1. Como admin: `PATCH /api/admin/users/{id}/status` con `{ "is_active": false }`
2. Intentar login con `desact@test.com`

**Resultado esperado:**
- HTTP 401 con mensaje `"Cuenta desactivada. Contacta al administrador."`
- `audit_log` registra `action='login'`, `result='failure'`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-011
**Título:** Recuperación de contraseña — paso 1: búsqueda de pregunta  
**Requisito:** RF-016  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Usuario `nuevo@test.com` registrado con pregunta de seguridad.

**Pasos:**
1. Navegar a `/reset-password`
2. Ingresar email `nuevo@test.com`
3. Clic en **Continuar**

**Resultado esperado:**
- Formulario avanza al paso 2
- Se muestra la pregunta de seguridad asociada al email
- HTTP 200 con `{ "security_question": "..." }`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-012
**Título:** Recuperación de contraseña — paso 2: cambio exitoso  
**Requisito:** RF-016  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Se completó TC-AUTH-011 exitosamente.

**Datos de prueba:**
```
Respuesta: firulais
Nueva contraseña: NuevaPass99!
```

**Pasos:**
1. En el paso 2, ingresar respuesta correcta
2. Ingresar nueva contraseña
3. Clic en **Restablecer Contraseña**
4. Intentar login con la nueva contraseña

**Resultado esperado:**
- Redirección a `/login`
- Login exitoso con `NuevaPass99!`
- `audit_log` registra `action='reset_password'`, `result='success'`
- Login con contraseña anterior falla

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-AUTH-013
**Título:** Recuperación de contraseña con respuesta incorrecta es rechazada  
**Requisito:** RF-016  
**Tipo:** Funcional · Seguridad · 🔴 Alta  
**Precondiciones:** Se completó TC-AUTH-011.

**Pasos:**
1. Paso 2 de recuperación
2. Ingresar respuesta INCORRECTA: `respuesta_falsa`
3. Clic en **Restablecer Contraseña**

**Resultado esperado:**
- Mensaje de error: *"Respuesta de seguridad incorrecta."*
- HTTP 400
- Contraseña no cambia en BD
- `audit_log` registra `result='failure'`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 2 — INTERFAZ DE USUARIO (UI)
> Requisitos cubiertos: RF-IU-001 a RF-IU-004, RF-IH-001, RNF-PORT-002

---

## TC-UI-001
**Título:** Página de login muestra layout split-panel correctamente  
**Requisito:** RF-IU-001  
**Tipo:** UI · 🟡 Media  
**Precondiciones:** Servidor frontend activo.

**Pasos:**
1. Navegar a `http://localhost:3000/login` en Chrome 100+
2. Observar la estructura visual
3. Verificar en resolución 1920×1080
4. Verificar en resolución 375×667 (simular con DevTools)

**Resultado esperado:**
- En escritorio (≥768px): panel izquierdo azul con logo + panel derecho blanco con formulario
- En móvil (<768px): panel izquierdo oculto; logo aparece sobre el formulario
- Logo cargado correctamente desde `/logo/Logo.png`
- Sin errores de consola relacionados con recursos

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-002
**Título:** Navegación por sidebar muestra el enlace activo correcto  
**Requisito:** RF-IU-001  
**Tipo:** UI · 🟡 Media  
**Precondiciones:** Sesión activa.

**Pasos:**
1. Iniciar sesión como admin
2. Hacer clic en **Precipitación** en el sidebar
3. Verificar highlight activo
4. Hacer clic en **Riesgo**
5. Verificar que Precipitación pierde el highlight y Riesgo lo gana
6. Verificar que **Administración** aparece solo para admin

**Resultado esperado:**
- Enlace activo resaltado con color primario y fondo diferenciado
- Solo el enlace de la página actual está resaltado
- Enlace **Administración** visible solo con rol `administrador`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-003
**Título:** Topbar muestra nombre real del usuario autenticado  
**Requisito:** RF-IU-001  
**Tipo:** UI · 🟡 Media  
**Precondiciones:** Sesión activa con usuario `Administrador`.

**Pasos:**
1. Iniciar sesión como `admin@alerto.com`
2. Observar la barra superior derecha

**Resultado esperado:**
- Se muestra "Hola, Administrador" (nombre del JWT)
- Rol mostrado: "Administrador"
- No aparece texto hardcodeado

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-004
**Título:** Interfaz cumple WCAG 2.1 — etiquetas ARIA en formularios  
**Requisito:** RF-IU-002  
**Tipo:** UI · Accesibilidad · 🔴 Alta  
**Precondiciones:** Ninguna.

**Pasos:**
1. Abrir DevTools → Elements
2. Inspeccionar formulario de login
3. Verificar atributos `aria-label` en botones de campana y logout
4. Verificar `for`/`htmlFor` en todos los campos de formulario
5. Verificar `scope="col"` en cabeceras de tablas
6. Navegar el formulario usando solo el teclado (Tab, Enter)

**Resultado esperado:**
- Todos los inputs tienen `id` asociado a su `label`
- Botones tienen `aria-label` descriptivos
- Tablas tienen `scope="col"` en `<th>`
- Navegación por teclado funcional sin trampa de foco

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-005
**Título:** Interfaz responsiva en resolución tablet (1024×768)  
**Requisito:** RF-IU-002  
**Tipo:** UI · 🟡 Media  
**Precondiciones:** DevTools disponibles.

**Pasos:**
1. En Chrome DevTools, establecer viewport 1024×768
2. Navegar por todas las páginas: Precipitación, Riesgo, Alertas, Simulador
3. Verificar que ningún elemento desborda su contenedor
4. Verificar que las tablas tienen scroll horizontal si es necesario

**Resultado esperado:**
- Todos los elementos visibles y accesibles
- No hay scroll horizontal no intencional
- Sidebar visible correctamente
- Tarjetas métricas se reorganizan en grid responsivo

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-006
**Título:** Contraste mínimo 4.5:1 en textos principales  
**Requisito:** RF-IU-002 (WCAG AA)  
**Tipo:** Accesibilidad · 🟡 Media  
**Precondiciones:** Herramienta de verificación de contraste (axe DevTools o similar).

**Pasos:**
1. Instalar extensión axe DevTools en Chrome
2. Navegar a `/login`
3. Ejecutar análisis axe
4. Revisar reportes de contraste
5. Repetir en `/precipitation` y `/risk`

**Resultado esperado:**
- 0 errores de nivel AA en contraste de texto
- Variables CSS `--text-main` (#1e293b) sobre fondo blanco: ratio ≥ 12:1 ✓
- Variables CSS `--text-muted` (#64748b) sobre blanco: verificar ≥ 4.5:1

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-007
**Título:** Página Precipitación muestra las 4 métricas climáticas correctas  
**Requisito:** RF-IU-003  
**Tipo:** Funcional · UI · 🔴 Alta  
**Precondiciones:** Pipeline ejecutado al menos una vez. Sesión activa.

**Pasos:**
1. Navegar a `/precipitation`
2. Verificar que se muestran 4 tarjetas métricas
3. Verificar que el gráfico de línea se renderiza
4. Esperar 60 segundos y verificar que los datos se actualizan

**Resultado esperado:**
- Tarjetas: **Última hora (mm)**, **Últimas 3h (mm)**, **Últimas 6h (mm)**, **Humedad 6h (%)**
- Valores numéricos visibles (no `—` si hay datos)
- Gráfico de línea renderizado con eje X de tiempo y eje Y de mm
- Sin errores en consola de navegador

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-008
**Título:** Gráfico de precipitación muestra hasta 72 horas de histórico  
**Requisito:** RF-IU-003  
**Tipo:** Funcional · UI · 🟡 Media  
**Precondiciones:** Datos en `gold_precipitation_history`.

**Pasos:**
1. Navegar a `/precipitation`
2. Verificar el título de la card del gráfico
3. Contar puntos en el gráfico o verificar con DevTools Network la respuesta de `/api/precipitation/history?limit=72`

**Resultado esperado:**
- Título: "Histórico de Precipitación (últimas 72h)"
- API devuelve máximo 72 registros
- Gráfico muestra los datos en orden cronológico ascendente

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-009
**Título:** Página Riesgo muestra badge con color según nivel  
**Requisito:** RF-IU-004  
**Tipo:** Funcional · UI · 🔴 Alta  
**Precondiciones:** Al menos un registro en tabla `alerts`. Sesión activa.

**Pasos:**
1. Navegar a `/risk`
2. Verificar badge del nivel de riesgo actual
3. Para cada nivel, verificar color:
   - VERDE → verde (`#10b981`)
   - AMARILLO → amarillo (`#f59e0b`)
   - NARANJA → naranja (`#f97316`)
   - ROJO → rojo (`#ef4444`)
4. Verificar el valor numérico del score (0–100%)

**Resultado esperado:**
- Badge visible con texto del nivel y color correspondiente
- Score numérico visible con símbolo `%`
- Timestamp de última evaluación visible

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-010
**Título:** Tabla de histórico de riesgo muestra colores en filas según nivel  
**Requisito:** RF-IU-004  
**Tipo:** UI · 🟡 Media  
**Precondiciones:** Múltiples registros de distintos niveles en `alerts`.

**Pasos:**
1. Navegar a `/risk`
2. Verificar tabla de histórico
3. Inspeccionar clases CSS de cada fila

**Resultado esperado:**
- Filas con `nivel_riesgo=ROJO` tienen borde izquierdo rojo
- Filas con nivel NARANJA tienen borde naranja
- Filas AMARILLO tienen borde amarillo
- Filas VERDE tienen borde verde

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-011
**Título:** Aplicación carga correctamente en Chrome, Firefox y Edge  
**Requisito:** RF-IH-001, RNF-PORT-002  
**Tipo:** Compatibilidad · 🔴 Alta  
**Precondiciones:** Chrome 100+, Firefox 95+, Edge 100+ disponibles.

**Pasos:**
1. Abrir `http://localhost:3000/login` en Chrome → iniciar sesión → navegar
2. Repetir en Firefox 95+
3. Repetir en Edge 100+
4. En cada browser: verificar login, gráfico de precipitación, tabla de riesgo

**Resultado esperado:**
- Carga correcta en los 3 navegadores
- Gráfico de línea (Recharts) renderiza en todos
- Sin errores de consola críticos en ninguno
- Layout sin diferencias visuales relevantes

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-UI-012
**Título:** Campana de notificaciones muestra alertas recientes  
**Requisito:** RF-IU-001, RF-008  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Existen alertas NARANJA o ROJO en las últimas 24h. Sesión activa.

**Pasos:**
1. Iniciar sesión
2. Observar el icono de campana en el topbar
3. Verificar si hay badge numérico
4. Hacer clic en la campana
5. Verificar el dropdown

**Resultado esperado:**
- Badge numérico indica cantidad de alertas críticas (NARANJA/ROJO) en 24h
- Dropdown muestra lista de alertas con nivel, color e icono
- Enlace "Ver todas las alertas" navega a `/alerts`
- El dropdown se cierra al hacer clic fuera

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 3 — PIPELINE DE DATOS (DATA)
> Requisitos cubiertos: RF-001, RF-002, RF-003, RF-004, RF-007, RF-011, RF-012, RF-013

---

## TC-DATA-001
**Título:** Validación de campos requeridos en datos de Open-Meteo  
**Requisito:** RF-001  
**Tipo:** Integración · 🔴 Alta  
**Precondiciones:** Pipeline ejecutado. Acceso a BD.

**Pasos:**
1. En BD: `SELECT * FROM bronze_weather_current ORDER BY fetched_at DESC LIMIT 1;`
2. Verificar que todos los campos están presentes

**Resultado esperado:**
- Campos presentes y no nulos: `fetched_at`, `time`, `precipitation`, `rain`, `showers`, `relative_humidity`, `cloudcover`, `windspeed_10m`
- Los valores son números válidos (no NaN ni null inesperado)

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-002
**Título:** Datos con campos faltantes de Open-Meteo generan error registrado  
**Requisito:** RF-001, RF-003  
**Tipo:** Integración · 🔴 Alta  
**Precondiciones:** Acceso a logs de Airflow.

**Pasos:**
1. En Airflow UI (`localhost:8080`), revisar el log del último DAG run de `weather_pipeline`
2. Si hay ejecuciones fallidas, verificar los mensajes de error
3. Verificar que el error no interrumpió completamente el sistema

**Resultado esperado:**
- Si hubo error: log contiene mensaje descriptivo con la causa
- El error fue registrado (raise en el extractor) sin que el sistema deje de funcionar
- La tarea de Airflow muestra estado `Failed` con detalles del error

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-003
**Título:** Flujo completo Bronze → Silver → Gold → Riesgo se ejecuta sin error  
**Requisito:** RF-002  
**Tipo:** Integración · 🔴 Alta  
**Precondiciones:** Airflow activo, dbt instalado.

**Pasos:**
1. En Airflow UI, localizar el DAG `weather_pipeline`
2. Ejecutar manualmente (Trigger DAG)
3. Monitorear cada tarea hasta completar
4. Verificar datos en cada capa:

```sql
-- Bronze
SELECT COUNT(*) FROM bronze_weather_hourly;
-- Silver (dbt view)
SELECT COUNT(*) FROM public_silver.silver_weather_hourly;
-- Gold
SELECT * FROM public_gold.gold_risk_features_latest;
-- Risk result
SELECT * FROM public.alerts ORDER BY evaluated_at DESC LIMIT 1;
```

**Resultado esperado:**
- Todas las tareas del DAG en verde (`Success`)
- Datos presentes en bronze, silver y gold
- Registro nuevo en `alerts` con nivel de riesgo válido
- Tiempo total de ejecución < 5 minutos

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-004
**Título:** Pipeline no inserta registros duplicados en bronze_weather_hourly  
**Requisito:** RF-002, RF-011  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Pipeline ejecutado al menos una vez.

**Pasos:**
1. Ejecutar el DAG `weather_pipeline` dos veces seguidas
2. Verificar:
```sql
SELECT time, COUNT(*) FROM bronze_weather_hourly GROUP BY time HAVING COUNT(*) > 1;
```

**Resultado esperado:**
- La consulta retorna 0 filas
- Restricción `UNIQUE` en columna `time` previene duplicados
- Segunda ejecución usa `INSERT ... ON CONFLICT DO NOTHING` o equivalente

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-005
**Título:** Error de conexión con Open-Meteo genera excepción y no marca éxito silencioso  
**Requisito:** RF-003  
**Tipo:** Integración · 🔴 Alta  
**Precondiciones:** Capacidad de bloquear temporalmente la URL de Open-Meteo (editar hosts o simular).

**Pasos:**
1. Simular falla de red hacia `api.open-meteo.com` (ej. URL falsa en el extractor)
2. Disparar el DAG `weather_pipeline`
3. Observar el estado de la tarea de extracción

**Resultado esperado:**
- La tarea de Airflow muestra estado `Failed` (no `Success`)
- El log contiene el traceback del error con mensaje descriptivo
- No se insertan filas vacías o incorrectas en bronze
- Las tareas downstream no se ejecutan si la extracción falla

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-006
**Título:** El motor de riesgo maneja graciosamente una tabla gold vacía  
**Requisito:** RF-003  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Acceso a BD.

**Pasos:**
1. Vaciar temporalmente la vista/tabla gold:
```sql
-- Solo para prueba, restaurar después
TRUNCATE public_gold.gold_risk_features_latest;
```
2. Ejecutar el DAG `simulate_pipeline` (solo la tarea `run_risk_engine`)
3. Observar el log

**Resultado esperado:**
- Tarea `run_risk_engine` termina con estado `Success`
- Log muestra mensaje: *"No hay datos en gold_risk_features_latest, omitiendo ciclo."*
- No se produce excepción `NoResultFound`
- No se inserta registro vacío en `alerts`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-007
**Título:** Mecanismo de reintento de Airflow funciona ante fallo transitorio  
**Requisito:** RF-004  
**Tipo:** Funcional · 🟡 Media  
**Precondiciones:** DAG `weather_pipeline` con `retries=3` configurado.

**Pasos:**
1. En Airflow UI, revisar la configuración del DAG
2. Inspeccionar `default_args` del DAG en el código fuente
3. Verificar que `retries` y `retry_delay` están definidos

**Resultado esperado:**
- DAG tiene `retries ≥ 1` en `default_args`
- `retry_delay` definido (ej. `timedelta(minutes=2)`)
- En la UI se puede ver el contador de reintentos en ejecuciones fallidas

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-008
**Título:** Tabla gold_risk_features_latest contiene las métricas esperadas  
**Requisito:** RF-007  
**Tipo:** Integración · 🔴 Alta  
**Precondiciones:** Pipeline ejecutado.

**Pasos:**
```sql
SELECT precipitation_1h, precipitation_3h, precipitation_6h, precipitation_24h,
       intensity_mm_h, humidity_avg_6h, trend_1h, as_of_time
FROM public_gold.gold_risk_features_latest;
```

**Resultado esperado:**
- 1 fila presente
- Todos los campos numéricos tienen valores válidos (≥ 0)
- `trend_1h` contiene uno de: `'subiendo'`, `'bajando'`, `'estable'`
- `as_of_time` es reciente (últimas 24h si el pipeline corrió)

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-009
**Título:** gold_precipitation_history almacena histórico horario  
**Requisito:** RF-007, RF-012  
**Tipo:** Funcional · 🟡 Media  
**Precondiciones:** Pipeline ejecutado múltiples veces.

**Pasos:**
```sql
SELECT COUNT(*), MIN(time_local), MAX(time_local)
FROM public_gold.gold_precipitation_history;
```

**Resultado esperado:**
- COUNT > 1
- Los timestamps son únicos y en orden cronológico

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-010
**Título:** Datos crudos se almacenan correctamente en bronze  
**Requisito:** RF-011  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Pipeline ejecutado.

**Pasos:**
1. Ejecutar pipeline
2. Verificar:
```sql
SELECT id, fetched_at, time, precipitation, relative_humidity
FROM bronze_weather_current
ORDER BY fetched_at DESC LIMIT 3;
```

**Resultado esperado:**
- Registros recientes con `fetched_at` actual
- Todos los campos de meteorología presentes
- `time` (timestamp del dato) diferente de `fetched_at` (timestamp de extracción)

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-011
**Título:** Datos procesados (Silver) se almacenan correctamente  
**Requisito:** RF-012  
**Tipo:** Integración · 🟡 Media  
**Precondiciones:** dbt run ejecutado.

**Pasos:**
```sql
SELECT COUNT(*), MIN(time), MAX(time)
FROM public_silver.silver_weather_hourly;
```

**Resultado esperado:**
- COUNT igual al de bronze (desduplicado)
- Sin valores nulos en campos calculados

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-DATA-012
**Título:** Clasificación de riesgo se almacena en tabla alerts  
**Requisito:** RF-013  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Motor de riesgo ejecutado.

**Pasos:**
```sql
SELECT id, evaluated_at, nivel_riesgo, riesgo_score,
       precip_1h, precip_3h, humedad_prom_6h
FROM public.alerts
ORDER BY evaluated_at DESC LIMIT 5;
```

**Resultado esperado:**
- Registros con todos los campos completos
- `nivel_riesgo` ∈ {'VERDE', 'AMARILLO', 'NARANJA', 'ROJO'}
- `riesgo_score` entre 0 y 100
- `evaluated_at` con timezone UTC

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 4 — MOTOR DE RIESGO (RISK)
> Requisitos cubiertos: RF-005, RF-008, RF-010

---

## TC-RISK-001
**Título:** Escenario VERDE — precipitación nula produce nivel VERDE  
**Requisito:** RF-008, RF-010  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Simulador disponible. Sesión activa.

**Pasos:**
1. Navegar a `/simulator`
2. Seleccionar preset **Verde** (precip_1h=0, precip_3h=0, humedad=30)
3. Ejecutar simulación
4. Esperar 2–3 minutos
5. Navegar a `/risk` y verificar nivel actual

**Resultado esperado:**
- `nivel_riesgo = 'VERDE'`
- `riesgo_score` entre 0 y 25
- Badge verde visible en la UI

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-RISK-002
**Título:** Escenario ROJO — precipitación extrema produce nivel ROJO  
**Requisito:** RF-008, RF-010  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Simulador disponible. Sesión activa.

**Pasos:**
1. Navegar a `/simulator`
2. Seleccionar preset **Rojo** (precip_1h=40, precip_3h=75, humedad=95)
3. Ejecutar simulación
4. Esperar 2–3 minutos
5. Verificar en `/risk` y en BD

**Resultado esperado:**
- `nivel_riesgo = 'ROJO'`
- `riesgo_score` entre 75 y 100
- Badge rojo en UI
- Alerta aparece en campana de notificaciones

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-RISK-003
**Título:** Escenario NARANJA — precipitación moderada-alta produce nivel NARANJA  
**Requisito:** RF-008, RF-010  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Simulador disponible.

**Pasos:**
1. Usar preset **Naranja** (precip_1h=18, precip_3h=35, humedad=85)
2. Ejecutar y verificar en `/risk`

**Resultado esperado:**
- `nivel_riesgo = 'NARANJA'`
- `riesgo_score` entre 50 y 75

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-RISK-004
**Título:** Score de riesgo está siempre en el rango [0, 100]  
**Requisito:** RF-010  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Al menos 10 registros en `alerts`.

**Pasos:**
```sql
SELECT COUNT(*) FROM public.alerts
WHERE riesgo_score < 0 OR riesgo_score > 100;
```

**Resultado esperado:**
- COUNT = 0 (ningún registro fuera del rango)

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-RISK-005
**Título:** Clasificación es consistente con el score (umbrales)  
**Requisito:** RF-010  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Múltiples registros en `alerts`.

**Pasos:**
```sql
-- No deben existir inconsistencias
SELECT nivel_riesgo, riesgo_score FROM public.alerts
WHERE
    (nivel_riesgo = 'VERDE'    AND riesgo_score >= 25) OR
    (nivel_riesgo = 'AMARILLO' AND (riesgo_score < 25 OR riesgo_score >= 50)) OR
    (nivel_riesgo = 'NARANJA'  AND (riesgo_score < 50 OR riesgo_score >= 75)) OR
    (nivel_riesgo = 'ROJO'     AND riesgo_score < 75);
```

**Resultado esperado:**
- La consulta retorna 0 filas

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-RISK-006
**Título:** Endpoint `/api/risk/current` retorna el resultado más reciente  
**Requisito:** RF-008  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Sesión activa. Al menos un registro en `alerts`.

**Pasos:**
1. En Postman: `GET http://localhost:8000/api/risk/current`
   - Header: `Authorization: Bearer <token>`
2. Verificar respuesta
3. Insertar manualmente un registro nuevo en `alerts`
4. Repetir la petición y verificar que retorna el nuevo registro

**Resultado esperado:**
- HTTP 200 con campos: `nivel_riesgo`, `riesgo_score`, `nivel_lluvia`, `evaluated_at`
- Tras insertar registro nuevo, el endpoint devuelve ese registro (ORDER BY DESC LIMIT 1)

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 5 — ADMINISTRACIÓN (ADMIN)
> Requisitos cubiertos: RF-005, RF-006, RF-015

---

## TC-ADMIN-001
**Título:** Administrador puede listar todos los usuarios del sistema  
**Requisito:** RF-015  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Sesión activa con rol `administrador`.

**Pasos:**
1. Navegar a `/admin`
2. Verificar que la pestaña **Usuarios** está seleccionada
3. Verificar que aparece la tabla de usuarios

**Resultado esperado:**
- Lista de todos los usuarios registrados
- Columnas: Nombre, Email, Rol, Estado, Creado, Acciones
- Usuario `admin@alerto.com` visible con rol `administrador`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-ADMIN-002
**Título:** Administrador puede cambiar el rol de un usuario  
**Requisito:** RF-015  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Existe usuario con rol `usuario`. Sesión admin activa.

**Pasos:**
1. Ir a `/admin` → pestaña Usuarios
2. Localizar usuario `nuevo@test.com`
3. En el selector de rol, cambiar de `usuario` a `administrador`
4. Verificar en BD: `SELECT role FROM users WHERE email='nuevo@test.com';`
5. Verificar en `audit_log`

**Resultado esperado:**
- El selector cambia el valor sin recargar la página
- BD muestra `role='administrador'` para ese usuario
- `audit_log` registra `action='update_role'` con `result='success'`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-ADMIN-003
**Título:** Administrador puede desactivar una cuenta de usuario  
**Requisito:** RF-015  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Existe usuario activo.

**Pasos:**
1. Ir a `/admin` → Usuarios
2. Localizar usuario, hacer clic en el toggle de estado (ToggleRight → ToggleLeft)
3. Verificar badge cambia de **Activo** a **Inactivo**
4. Verificar en BD: `SELECT is_active FROM users WHERE email='nuevo@test.com';`
5. Intentar login con ese usuario

**Resultado esperado:**
- Badge cambia a "Inactivo"
- BD muestra `is_active = false`
- Login falla con mensaje de cuenta desactivada
- `audit_log` registra `action='deactivate_user'`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-ADMIN-004
**Título:** API de admin rechaza peticiones de usuarios no administradores  
**Requisito:** RF-015  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Token JWT de usuario con `role='usuario'`.

**Pasos:**
1. En Postman: `GET /api/admin/users` con token de rol `usuario`
2. `PATCH /api/admin/users/1/role` con token de rol `usuario`

**Resultado esperado:**
- HTTP 403 en ambos endpoints
- Body: `{ "detail": "Acceso restringido a administradores." }`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-ADMIN-005
**Título:** Administrador puede ver y editar umbrales de riesgo (RF-005)  
**Requisito:** RF-005  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Sesión admin activa. Tabla `system_config` inicializada.

**Pasos:**
1. Navegar a `/admin` → pestaña **Configuración**
2. Verificar que se muestran los 4 parámetros configurables
3. Cambiar valor de `threshold_naranja` de 50 a 55
4. Hacer clic fuera del campo (blur event)
5. Verificar en BD: `SELECT value FROM system_config WHERE key='threshold_naranja';`

**Resultado esperado:**
- 4 configuraciones visibles con descripción y valor actual
- Tras editar: BD muestra el nuevo valor
- Mensaje "Guardando..." aparece brevemente

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-ADMIN-006
**Título:** Usuario no administrador no puede editar la configuración  
**Requisito:** RF-005  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Token de rol `usuario`.

**Pasos:**
1. En Postman: `PATCH /api/config/threshold_rojo` con token de rol `usuario`
   - Body: `{ "value": "80" }`

**Resultado esperado:**
- HTTP 403 `"Acceso restringido a administradores."`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-ADMIN-007
**Título:** Configuración de frecuencia del pipeline es visible  
**Requisito:** RF-006  
**Tipo:** Funcional · 🟡 Media  
**Precondiciones:** Sesión admin.

**Pasos:**
1. Navegar a `/admin` → Configuración
2. Buscar el parámetro `pipeline_interval`
3. Verificar descripción y valor por defecto

**Resultado esperado:**
- Parámetro `pipeline_interval` visible con descripción "Frecuencia de ejecución del pipeline en minutos"
- Valor por defecto: `15`
- Campo editable para administradores

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 6 — SIMULADOR (SIM)
> Relacionado con RF-002, RF-010

---

## TC-SIM-001
**Título:** Simulador valida que precip_3h ≥ precip_1h  
**Requisito:** RF-002  
**Tipo:** Funcional · 🟡 Media  
**Precondiciones:** Sesión activa.

**Pasos:**
1. Navegar a `/simulator`
2. Ajustar manualmente: `precip_1h = 20 mm`, `precip_3h = 10 mm` (inválido)
3. Observar si el slider de 3h se ajusta automáticamente
4. Intentar ejecutar desde Postman con valores inválidos:
   - `POST /api/simulate` con `{ "precip_1h": 20, "precip_3h": 10, "humedad": 50 }`

**Resultado esperado:**
- En la UI: el slider de 3h no puede quedar por debajo del valor de 1h
- En API: HTTP 422 con mensaje "precip_3h debe ser mayor o igual a precip_1h"

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-SIM-002
**Título:** Simulación exitosa dispara el pipeline y aparece resultado  
**Requisito:** RF-002  
**Tipo:** Funcional · Integración · 🔴 Alta  
**Precondiciones:** Airflow activo y DAG `simulate_pipeline` registrado.

**Pasos:**
1. Navegar a `/simulator`
2. Seleccionar preset **Amarillo**
3. Clic en **Ejecutar Simulación**
4. Verificar mensaje de estado "ok"
5. Esperar 2–3 minutos
6. Verificar en Airflow UI que el DAG `simulate_pipeline` se ejecutó
7. Verificar en `/risk` el nuevo nivel

**Resultado esperado:**
- Mensaje de confirmación en la UI: *"Pipeline disparado exitosamente"* (o similar)
- DAG `simulate_pipeline` aparece en ejecución en Airflow UI
- Nuevo registro en `alerts` con nivel AMARILLO
- No se requiere token de Airflow expuesto al usuario

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-SIM-003
**Título:** Simulador rechaza valores fuera del rango permitido  
**Requisito:** RF-002  
**Tipo:** Funcional · 🟡 Media  
**Precondiciones:** Postman disponible.

**Pasos:**
1. `POST /api/simulate` con `{ "precip_1h": 200, "precip_3h": 300, "humedad": 150 }`

**Resultado esperado:**
- HTTP 422 con errores de validación para cada campo fuera de rango
- `precip_1h` máximo: 50, `precip_3h` máximo: 90, `humedad` máximo: 100

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 7 — ALERTAS (ALERTS)
> Requisitos cubiertos: RF-008

---

## TC-ALERTS-001
**Título:** Página de alertas muestra contadores por nivel  
**Requisito:** RF-008  
**Tipo:** Funcional · UI · 🔴 Alta  
**Precondiciones:** Múltiples registros de distintos niveles en `alerts`. Sesión activa.

**Pasos:**
1. Navegar a `/alerts`
2. Verificar la franja de tarjetas de conteo superior
3. Contar manualmente en BD los registros por nivel y comparar

```sql
SELECT nivel_riesgo, COUNT(*) FROM public.alerts GROUP BY nivel_riesgo;
```

**Resultado esperado:**
- 4 tarjetas: ROJO, NARANJA, AMARILLO, VERDE
- Contadores coinciden con la BD
- Colores de tarjetas correctos por nivel

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-ALERTS-002
**Título:** Filtro por nivel de riesgo funciona correctamente  
**Requisito:** RF-008  
**Tipo:** Funcional · UI · 🟡 Media  
**Precondiciones:** Registros de múltiples niveles en `alerts`. Sesión activa.

**Pasos:**
1. Navegar a `/alerts`
2. Hacer clic en filtro **ROJO**
3. Verificar que solo aparecen filas con nivel ROJO
4. Hacer clic en **TODOS**
5. Verificar que vuelven todos los registros

**Resultado esperado:**
- Filtro ROJO: solo filas rojas visibles
- Filtro TODOS: todas las filas visibles
- El filtro activo está visualmente destacado (background azul)

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-ALERTS-003
**Título:** Paginación de alertas funciona con muchos registros  
**Requisito:** RF-008  
**Tipo:** Funcional · 🟡 Media  
**Precondiciones:** Más de 50 registros en `alerts`.

**Pasos:**
1. Navegar a `/alerts`
2. Verificar página 1 con máximo 50 filas
3. Hacer clic en **Siguiente**
4. Verificar página 2 con registros más antiguos
5. Hacer clic en **Anterior** para volver

**Resultado esperado:**
- Página 1: 50 registros (o menos si hay menos de 50 en total)
- Botón **Siguiente** deshabilitado si hay menos de 50 registros en la página actual
- Botón **Anterior** deshabilitado en la primera página
- Los registros son diferentes entre páginas

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 8 — SEGURIDAD (SEC)
> Requisitos cubiertos: RNF-SEG-001, RNF-SEG-003, RNF-SEG-004

---

## TC-SEC-001
**Título:** Contraseñas almacenadas con bcrypt (cost factor 12)  
**Requisito:** RNF-SEG-001  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Usuario registrado en BD.

**Pasos:**
```sql
SELECT password_hash FROM users WHERE email = 'admin@alerto.com';
```
Verificar el formato del hash.

**Resultado esperado:**
- Hash comienza con `$2b$12$` (bcrypt con cost factor 12)
- La contraseña NO está en texto plano
- El hash tiene al menos 60 caracteres

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-SEC-002
**Título:** API responde con headers de seguridad correctos  
**Requisito:** RNF-SEG-004  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Backend activo.

**Pasos:**
1. En Postman: `GET http://localhost:8000/health`
2. Revisar los headers de la respuesta

**Resultado esperado:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=()`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-SEC-003
**Título:** Rate limiting bloquea exceso de intentos de login  
**Requisito:** RNF-SEG-004  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Backend activo.

**Pasos:**
1. En Postman, crear un runner que ejecute `POST /api/auth/login` 15 veces en rápida sucesión
2. Observar las respuestas a partir del intento 11

**Resultado esperado:**
- Primeros 10 intentos: HTTP 401 (credenciales inválidas) o 200 (si son válidas)
- A partir del intento 11 en el mismo minuto: HTTP 429 `Too Many Requests`
- El bloqueo se levanta pasado 1 minuto

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-SEC-004
**Título:** Registro de auditoría guarda eventos de login  
**Requisito:** RNF-SEG-003  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Usuario registrado.

**Pasos:**
1. Iniciar sesión con `admin@alerto.com`
2. Verificar en BD:
```sql
SELECT ts, user_email, action, result, ip_address
FROM audit_log
WHERE action = 'login'
ORDER BY ts DESC LIMIT 5;
```

**Resultado esperado:**
- Registro presente con `action='login'`, `result='success'`
- `user_email` = `admin@alerto.com`
- `ts` con fecha/hora reciente
- `ip_address` registrada

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-SEC-005
**Título:** Registro de auditoría guarda intentos de login fallidos  
**Requisito:** RNF-SEG-003  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Ninguna.

**Pasos:**
1. Intentar login con contraseña incorrecta 3 veces
2. Verificar en BD:
```sql
SELECT ts, user_email, action, result, details
FROM audit_log
WHERE action = 'login' AND result = 'failure'
ORDER BY ts DESC LIMIT 5;
```

**Resultado esperado:**
- 3 registros con `result='failure'`
- `details` contiene causa del fallo (ej. "contraseña incorrecta")
- Ningún hash de contraseña expuesto en `details`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-SEC-006
**Título:** API no es vulnerable a SQL Injection en el endpoint de login  
**Requisito:** RNF-SEG-004  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Backend activo.

**Pasos:**
1. En Postman: `POST /api/auth/login`
   ```json
   { "email": "' OR '1'='1", "password": "' OR '1'='1" }
   ```
2. También intentar:
   ```json
   { "email": "admin@alerto.com'--", "password": "x" }
   ```

**Resultado esperado:**
- HTTP 422 (validación de EmailStr falla) o HTTP 401
- No se produce autenticación exitosa con payloads de inyección
- No se devuelven datos de BD no autorizados

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-SEC-007
**Título:** Endpoint health no expone información sensible del sistema  
**Requisito:** RNF-SEG-004  
**Tipo:** Seguridad · 🟡 Media  
**Precondiciones:** Backend activo.

**Pasos:**
1. `GET http://localhost:8000/health` sin token

**Resultado esperado:**
- HTTP 200 con solo `{ "status": "ok", "service": "alerto-backend" }`
- No expone versiones de dependencias, paths, o configuración interna

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-SEC-008
**Título:** Token JWT con firma inválida es rechazado  
**Requisito:** RNF-SEG-004, RF-015  
**Tipo:** Seguridad · 🔴 Alta  
**Precondiciones:** Postman disponible.

**Pasos:**
1. Tomar un JWT válido y modificar un carácter del payload (base64)
2. Hacer `GET /api/risk/current` con ese token alterado

**Resultado esperado:**
- HTTP 401 `"Token inválido."`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 9 — RENDIMIENTO Y DISPONIBILIDAD (PERF)
> Requisitos cubiertos: RNF-REN-001, RNF-REN-002, RNF-DIS-002, RNF-FIA-001

---

## TC-PERF-001
**Título:** Tiempo de carga de la página principal < 3 segundos  
**Requisito:** RNF-DIS-002  
**Tipo:** Rendimiento · 🔴 Alta  
**Precondiciones:** Sesión activa. DevTools abiertos.

**Pasos:**
1. Abrir DevTools → pestaña **Network**
2. Hacer hard-reload (Ctrl+Shift+R) en `/precipitation`
3. Registrar el tiempo en el indicador `DOMContentLoaded` y `Load`
4. Verificar tiempo de `/api/precipitation/current` y `/api/precipitation/history`

**Resultado esperado:**
- Página completamente cargada en < 3 segundos
- Petición `/api/precipitation/current`: tiempo de respuesta < 500ms
- Gráfico visible sin loading spinner después de carga inicial

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-PERF-002
**Título:** Endpoints API responden en < 500ms bajo carga normal  
**Requisito:** RNF-REN-001  
**Tipo:** Rendimiento · 🔴 Alta  
**Precondiciones:** Postman disponible.

**Pasos:**
1. Medir tiempo de respuesta de los siguientes endpoints (10 llamadas cada uno):
   - `GET /api/risk/current`
   - `GET /api/precipitation/current`
   - `GET /api/risk/history?limit=100`
2. Registrar tiempo promedio y máximo

**Resultado esperado:**
- Promedio < 200ms por endpoint
- Máximo < 500ms por endpoint
- Sin timeouts

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-PERF-003
**Título:** Sistema soporta 20 usuarios concurrentes  
**Requisito:** RNF-REN-002  
**Tipo:** Rendimiento · 🟡 Media  
**Precondiciones:** Postman Newman o herramienta de carga disponible.

**Pasos:**
1. Crear colección Postman con las 5 llamadas principales
2. Ejecutar con 20 iteraciones paralelas
3. Verificar respuestas y tiempos

**Resultado esperado:**
- 0 errores HTTP 500
- Tiempo promedio de respuesta < 1 segundo
- Sin degradación visible en la UI durante la prueba

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-PERF-004
**Título:** Actualización automática de datos en UI cada 60 segundos  
**Requisito:** RNF-DIS-002  
**Tipo:** Rendimiento · UI · 🟡 Media  
**Precondiciones:** Sesión activa.

**Pasos:**
1. Navegar a `/precipitation`
2. Abrir DevTools → Network
3. Esperar 65 segundos
4. Verificar que se realizan nuevas peticiones a la API

**Resultado esperado:**
- Peticiones automáticas a `/api/precipitation/current` e `/api/precipitation/history` cada ~60s
- Los datos en pantalla se actualizan sin reload manual
- Sin errores de timeout

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 10 — INTEGRACIÓN (INT)
> Requisitos cubiertos: RF-IS-001, RF-IC-001, RF-IH-001

---

## TC-INT-001
**Título:** Sistema se conecta a Open-Meteo via HTTPS GET y recibe datos JSON  
**Requisito:** RF-IS-001, RF-IC-001  
**Tipo:** Integración · 🔴 Alta  
**Precondiciones:** Pipeline ejecutado.

**Pasos:**
1. En logs de Airflow, buscar el log de la tarea `extract_current`
2. Verificar que la URL usada es `https://api.open-meteo.com/...`
3. Verificar que los datos recibidos se parsearon como JSON

**Resultado esperado:**
- URL usa protocolo HTTPS
- Método HTTP es GET
- Respuesta parseada exitosamente como JSON
- Datos guardados en `bronze_weather_current`

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-INT-002
**Título:** Parámetros de ubicación correctos en petición a Open-Meteo  
**Requisito:** RF-IS-001  
**Tipo:** Integración · 🟡 Media  
**Precondiciones:** Acceso al código fuente de extracción.

**Pasos:**
1. Revisar `airflow/plugins/elt/extract.py`
2. Verificar los parámetros de latitud y longitud
3. Verificar los campos solicitados en la API

**Resultado esperado:**
- `latitude=6.274`, `longitude=-75.582` (Medellín, Colombia)
- Campos solicitados: precipitation, rain, showers, relative_humidity, windspeed_10m
- URL válida construida correctamente

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-INT-003
**Título:** El backend se conecta a PostgreSQL correctamente  
**Requisito:** RF-011  
**Tipo:** Integración · 🔴 Alta  
**Precondiciones:** Todos los contenedores activos.

**Pasos:**
1. `GET http://localhost:8000/health` → verificar HTTP 200
2. `GET /api/risk/current` → verificar que no hay error 500
3. Revisar logs del contenedor backend: `docker logs alerto_backend`

**Resultado esperado:**
- Backend responde sin errores de conexión a BD
- Sin mensajes `OperationalError` o `ConnectionRefused` en logs

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-INT-004
**Título:** Servicio de simulación dispara correctamente el DAG de Airflow  
**Requisito:** RF-002  
**Tipo:** Integración · 🔴 Alta  
**Precondiciones:** Airflow activo.

**Pasos:**
1. `POST /api/simulate` con valores válidos y token JWT
2. En Airflow UI: verificar que el DAG `simulate_pipeline` aparece como nuevo run
3. Verificar el trigger type (debe ser "manual")

**Resultado esperado:**
- DAG `simulate_pipeline` inicia con estado `Running` o `Success`
- HTTP 200 en la petición de simulación
- Sin errores 500 ni de autenticación hacia Airflow

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

# MÓDULO 11 — NOTIFICACIONES (NOTIF)
> Requisitos cubiertos: RF-008, RF-009, RF-IH-002

---

## TC-NOTIF-001
**Título:** Campana muestra 0 alertas cuando no hay eventos críticos  
**Requisito:** RF-008  
**Tipo:** Funcional · 🟡 Media  
**Precondiciones:** No hay alertas NARANJA/ROJO en las últimas 24h.

**Pasos:**
1. Iniciar sesión
2. Observar la campana en el topbar

**Resultado esperado:**
- Sin badge numérico (o badge con "0")
- Al hacer clic: dropdown muestra "Sin alertas críticas"

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-NOTIF-002
**Título:** Campana se actualiza en tiempo real al generarse alerta crítica  
**Requisito:** RF-008  
**Tipo:** Funcional · 🔴 Alta  
**Precondiciones:** Sin alertas críticas. Sesión activa.

**Pasos:**
1. Observar campana sin alertas
2. Desde el simulador, ejecutar escenario ROJO
3. Esperar 2–3 minutos que el pipeline procese
4. Verificar la campana sin recargar la página

**Resultado esperado:**
- La campana actualiza su badge (máx. 60 segundos de diferencia)
- El dropdown muestra la nueva alerta ROJO con timestamp correcto
- Color rojo (#ef4444) en el icono de la alerta

**Resultado actual:** _(completar al ejecutar)_  
**Estado:** ⬜ Pendiente

---

## TC-NOTIF-003
**Título:** [PARCIAL] Interfaz de notificaciones SMS prevista pero no activa  
**Requisito:** RF-009, RF-IH-002, RF-IS-002  
**Tipo:** Funcional · ➖ N/A (versión actual)  
**Precondiciones:** N/A — funcionalidad no implementada en v1.0.

**Pasos:**
1. Verificar en código: `backend/app/` — buscar integración con servicio SMS
2. Verificar en `requirements.txt` — presencia de librería de SMS

**Resultado esperado (para versión futura):**
- Cuando se genere alerta ROJO o NARANJA, se debe disparar un SMS a los usuarios registrados con número de teléfono
- El SMS debe contener: nivel de riesgo, score, timestamp, enlace al sistema

**Observación:** Esta funcionalidad está definida en el SRS (RF-009) pero requiere integración con servicio externo (Twilio o similar). Marcado como N/A para v1.0, pendiente para v1.1.

**Estado:** ➖ N/A

---

---

## Resumen de ejecución

| Módulo | Total TC | Aprobados | Fallidos | Bloqueados | Pendientes |
|---|---|---|---|---|---|
| AUTH | 13 | — | — | — | 13 |
| UI | 12 | — | — | — | 12 |
| DATA | 12 | — | — | — | 12 |
| RISK | 6 | — | — | — | 6 |
| ADMIN | 7 | — | — | — | 7 |
| SIM | 3 | — | — | — | 3 |
| ALERTS | 3 | — | — | — | 3 |
| SEC | 8 | — | — | — | 8 |
| PERF | 4 | — | — | — | 4 |
| INT | 4 | — | — | — | 4 |
| NOTIF | 3 | — | — | 1 N/A | 2 |
| **TOTAL** | **75** | **0** | **0** | **1** | **74** |

---

*Documento generado por equipo QA — Alerto v1.0*  
*Próxima revisión: tras primera ejecución del ciclo de pruebas*
