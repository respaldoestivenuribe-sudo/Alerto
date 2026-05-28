# Plan de Pruebas — Sistema Alerto
**Versión:** 1.0  
**Fecha:** 2026-05-26  
**Elaborado por:** Equipo QA  
**Estado:** Activo  
**Documento base:** Especificación de Requisitos de Software (SRS) Rev. 1.0

---

## 1. Introducción

### 1.1 Propósito
Este documento define la estrategia, alcance, recursos y criterios de aceptación para las pruebas del sistema **Alerto**, plataforma de monitoreo de precipitación y generación automática de alertas de riesgo de inundación para el Distrito de Medellín.

### 1.2 Contexto del sistema
Alerto integra un pipeline ELT (Bronze → Silver → Gold), un motor de lógica difusa para clasificación de riesgo, una API REST (FastAPI), y una interfaz web reactiva (React + Vite). El sistema consume datos de Open-Meteo cada 15 minutos y expone niveles de riesgo VERDE / AMARILLO / NARANJA / ROJO.

### 1.3 Referencias
| Documento | Versión | Descripción |
|---|---|---|
| SRS Alerto | Rev. 1.0 | Especificación de Requisitos de Software (IEEE 830) |
| docker-compose.yml | — | Configuración de servicios Docker |
| init.sql | — | Esquema de base de datos PostgreSQL |

---

## 2. Alcance

### 2.1 En alcance
| Módulo | Descripción |
|---|---|
| Autenticación | Registro, login, cierre de sesión, recuperación de contraseña |
| Interfaz de usuario | Responsividad, accesibilidad, visualización de datos |
| Pipeline de datos | Extracción Open-Meteo, transformación dbt, motor de riesgo |
| Motor de riesgo | Clasificación difusa, generación de alertas |
| Administración | RBAC, gestión de usuarios, configuración del sistema |
| Simulador | Inserción de datos sintéticos, disparo del pipeline |
| Seguridad | Autenticación JWT, headers de seguridad, rate limiting, audit log |
| Rendimiento | Tiempos de respuesta de UI, carga concurrente |
| Integración | API Open-Meteo, pipeline Airflow, base de datos |

### 2.2 Fuera de alcance
- Integración con servicios SMS externos (Twilio) — no implementado en la versión actual
- Infraestructura TLS/HTTPS — responsabilidad del equipo DevOps
- Réplica Master/Slave de PostgreSQL — fuera del ambiente de desarrollo
- TOTP/MFA — no implementado en la versión actual

---

## 3. Objetivos

1. Verificar que todos los requisitos funcionales (RF-001 a RF-016) están implementados y funcionan correctamente.
2. Validar el cumplimiento de los requisitos no funcionales críticos (seguridad, rendimiento, disponibilidad).
3. Identificar defectos antes del despliegue en ambiente de producción.
4. Garantizar la trazabilidad completa entre requisitos y casos de prueba.
5. Documentar evidencia de prueba ejecutada para cada requisito.

---

## 4. Estrategia de pruebas

### 4.1 Tipos de prueba aplicados

| Tipo | Objetivo | Herramienta (esta fase) |
|---|---|---|
| **Funcional manual** | Verificar comportamiento esperado por RF | Navegador + Postman |
| **Prueba de interfaz** | Responsividad, accesibilidad, UX | Navegador (Chrome, Firefox, Edge) |
| **Prueba de integración** | Comunicación entre servicios | Postman + Airflow UI |
| **Prueba de seguridad** | Controles de acceso, headers, rate limiting | Postman + DevTools |
| **Prueba de rendimiento** | Tiempos de respuesta de UI | DevTools Network + cronómetro |
| **Prueba de regresión** | Verificar que correcciones no rompen funcionalidad existente | Manual |

### 4.2 Niveles de prueba

```
Pruebas de Sistema (End-to-End)
        ↑
Pruebas de Integración (API ↔ DB ↔ Pipeline)
        ↑
Pruebas de Componente (Endpoints individuales)
        ↑
Pruebas de Interfaz (Frontend)
```

### 4.3 Enfoque por prioridad de riesgo
Las pruebas se ejecutan en el siguiente orden de prioridad:

1. **Crítico:** Autenticación, RBAC, generación de alertas, pipeline de datos
2. **Alto:** Visualización de datos, motor de riesgo, seguridad
3. **Medio:** Simulador, administración, configuración
4. **Bajo:** Rendimiento, compatibilidad multi-browser, accesibilidad

---

## 5. Criterios de entrada y salida

### 5.1 Criterios de entrada (inicio de pruebas)
- [ ] Ambiente Docker levantado y todos los servicios `healthy`
- [ ] Base de datos inicializada con `init.sql`
- [ ] Usuario administrador seedeado (`admin@alerto.com`)
- [ ] Pipeline de Airflow ejecutado al menos una vez exitosamente
- [ ] Acceso a Postman con colección importada

### 5.2 Criterios de salida (fin del ciclo)
- [ ] 100% de casos de prueba de prioridad **Alta/Esencial** ejecutados
- [ ] 0 defectos de severidad **Crítica** abiertos
- [ ] Máximo 2 defectos de severidad **Alta** con plan de remediación
- [ ] Cobertura de requisitos ≥ 90%

---

## 6. Ambiente de pruebas

| Componente | Detalle |
|---|---|
| **Sistema operativo** | Windows 11 / Linux (dentro de contenedor) |
| **Orquestación** | Docker Compose v3.9 |
| **Frontend** | `http://localhost:3000` (Vite dev server) |
| **Backend API** | `http://localhost:8000` |
| **Airflow** | `http://localhost:8080` (admin/admin) |
| **PostgreSQL** | `localhost:5432` |
| **Navegadores** | Chrome 100+, Firefox 95+, Edge 100+ |
| **Cliente API** | Postman v10+ |
| **Usuario de prueba admin** | admin@alerto.com / alerto123** |
| **Usuario de prueba regular** | Se crea durante las pruebas |

---

## 7. Roles y responsabilidades

| Rol | Responsabilidad |
|---|---|
| **QA Lead** | Planificación, revisión de casos, métricas de calidad |
| **Analista QA** | Ejecución de casos manuales, reporte de defectos |
| **Desarrollador Backend** | Soporte en pruebas de API y pipeline |
| **Desarrollador Frontend** | Soporte en pruebas de UI y accesibilidad |
| **DevOps** | Soporte en ambiente y configuración de contenedores |

---

## 8. Gestión de defectos

### 8.1 Severidades
| Severidad | Descripción | Ejemplo |
|---|---|---|
| **Crítica** | El sistema no puede usarse, pérdida de datos, fallo de seguridad grave | Login sin autenticación, datos corruptos |
| **Alta** | Funcionalidad principal rota, sin alternativa | Pipeline no genera alertas, RBAC no funciona |
| **Media** | Funcionalidad parcialmente rota, existe alternativa | Paginación incorrecta, badge de color erróneo |
| **Baja** | Problema cosmético o de usabilidad menor | Texto mal alineado, typo |

### 8.2 Flujo de defectos
```
Detectado → Reportado → Asignado → En corrección → Verificado → Cerrado
                                                        ↓ (si falla)
                                                    Reabierto
```

---

## 9. Métricas de calidad

| Métrica | Fórmula | Meta |
|---|---|---|
| Cobertura de requisitos | (Requisitos con TC / Total requisitos) × 100 | ≥ 90% |
| Tasa de defectos críticos | Defectos críticos / Total casos ejecutados | 0% |
| Tasa de éxito | Casos aprobados / Total ejecutados × 100 | ≥ 85% |
| Densidad de defectos | Defectos / Módulo | ≤ 3 por módulo |

---

## 10. Matriz de trazabilidad (resumen)

| Requisito | Descripción | IDs de Casos de Prueba | Cobertura |
|---|---|---|---|
| RF-IU-001 | Interfaz web responsiva | TC-UI-001, TC-UI-002, TC-UI-003 | ✅ |
| RF-IU-002 | Diseño responsivo y WCAG 2.1 | TC-UI-004, TC-UI-005, TC-UI-006 | ✅ |
| RF-IU-003 | Visualización de datos climáticos | TC-UI-007, TC-UI-008 | ✅ |
| RF-IU-004 | Visualización del nivel de riesgo | TC-UI-009, TC-UI-010 | ✅ |
| RF-IH-001 | Compatibilidad con dispositivos | TC-UI-011, TC-UI-012 | ✅ |
| RF-IH-002 | Recepción SMS | TC-NOTIF-003 | ⚠️ Parcial |
| RF-IS-001 | Integración Open-Meteo | TC-INT-001, TC-INT-002 | ✅ |
| RF-IS-002 | Integración mensajería | TC-NOTIF-003 | ⚠️ Parcial |
| RF-IC-001 | Comunicación HTTPS GET | TC-INT-001 | ✅ |
| RF-001 | Validación datos de entrada | TC-DATA-001, TC-DATA-002 | ✅ |
| RF-002 | Flujo Bronze→Silver→Gold→Riesgo | TC-DATA-003, TC-DATA-004 | ✅ |
| RF-003 | Manejo de fallos externos | TC-DATA-005, TC-DATA-006 | ✅ |
| RF-004 | Recuperación ante errores | TC-DATA-007 | ✅ |
| RF-005 | Configuración de umbrales | TC-ADMIN-005, TC-ADMIN-006 | ✅ |
| RF-006 | Frecuencia de ejecución | TC-ADMIN-007 | ✅ |
| RF-007 | Generación de datos procesados | TC-DATA-008, TC-DATA-009 | ✅ |
| RF-008 | Generación de alertas | TC-RISK-001, TC-RISK-002, TC-RISK-003 | ✅ |
| RF-009 | Notificaciones SMS | TC-NOTIF-003 | ⚠️ Parcial |
| RF-010 | Conversión datos a nivel de riesgo | TC-RISK-004, TC-RISK-005, TC-RISK-006 | ✅ |
| RF-011 | Almacenamiento datos crudos | TC-DATA-010 | ✅ |
| RF-012 | Almacenamiento datos procesados | TC-DATA-011 | ✅ |
| RF-013 | Almacenamiento niveles de riesgo | TC-DATA-012 | ✅ |
| RF-014 | Almacenamiento info de sesión | TC-AUTH-001, TC-AUTH-002 | ✅ |
| RF-015 | Gestión de usuarios RBAC | TC-AUTH-006 a TC-AUTH-010, TC-ADMIN-001 a TC-ADMIN-004 | ✅ |
| RF-016 | Restablecimiento seguro contraseña | TC-AUTH-011, TC-AUTH-012, TC-AUTH-013 | ✅ |
| RNF-REN-001 | Latencia máxima | TC-PERF-001, TC-PERF-002 | ✅ |
| RNF-REN-002 | Procesamiento concurrente | TC-PERF-003 | ✅ |
| RNF-SEG-001 | Cifrado de datos | TC-SEC-001 | ✅ |
| RNF-SEG-003 | Registro de auditoría | TC-SEC-004, TC-SEC-005 | ✅ |
| RNF-SEG-004 | Protección OWASP Top 10 | TC-SEC-006 a TC-SEC-010 | ✅ |
| RNF-DIS-002 | Tiempos de respuesta UI | TC-PERF-001 | ✅ |
| RNF-PORT-002 | Compatibilidad multi-browser | TC-UI-011, TC-UI-012 | ✅ |

> ⚠️ Parcial: Funcionalidad pendiente de implementación (SMS). Se verifica el contrato de la interfaz.

---

## 11. Cronograma estimado

| Fase | Actividad | Duración estimada |
|---|---|---|
| Preparación | Configurar ambiente, importar datos | 0.5 día |
| Ejecución ciclo 1 | Autenticación, UI, Datos | 1 día |
| Ejecución ciclo 1 | Riesgo, Admin, Simulador | 1 día |
| Ejecución ciclo 1 | Seguridad, Rendimiento, Integración | 1 día |
| Análisis | Reporte de defectos, métricas | 0.5 día |
| Regresión | Verificación de correcciones | 0.5 día |
| **Total** | | **~4.5 días hábiles** |
