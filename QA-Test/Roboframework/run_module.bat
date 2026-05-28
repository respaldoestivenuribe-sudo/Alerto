@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Alerto QA — Ejecutar módulo específico
echo   Uso: run_module.bat [MODULE]
echo   Módulos: AUTH UI DATA RISK ADMIN SIM ALERTS SEC PERF INT NOTIF
echo ============================================================
echo.

if "%1"=="" (
  echo ERROR: Debes especificar un módulo.
  echo.
  echo Uso: run_module.bat AUTH
  echo      run_module.bat UI
  echo      run_module.bat SEC
  echo.
  exit /b 1
)

set "MODULE=%1"
set "SCRIPT_DIR=%~dp0"
set "TEST_FILE=%SCRIPT_DIR%tests\TC_%MODULE%.robot"

if not exist "%TEST_FILE%" (
  echo ERROR: Módulo '%MODULE%' no encontrado.
  echo Archivo esperado: %TEST_FILE%
  exit /b 1
)

set "RESULTS=%SCRIPT_DIR%results\%MODULE%_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "RESULTS=%RESULTS: =0%"
mkdir "%RESULTS%" 2>nul

echo Módulo    : %MODULE%
echo Suite     : %TEST_FILE%
echo Resultados: %RESULTS%
echo.

python -m robot ^
  --outputdir "%RESULTS%" ^
  --output    output.xml ^
  --log       log.html ^
  --report    report.html ^
  --loglevel  INFO ^
  --variable  SCREENSHOTS_DIR:%RESULTS%\screenshots ^
  --name      "TC-%MODULE%" ^
  "%TEST_FILE%"

set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if %RC%==0 (
  echo   MÓDULO %MODULE%: PASSED
) else (
  echo   MÓDULO %MODULE%: FAILED (RC=%RC%)
)
echo   Reporte: %RESULTS%\report.html
echo ============================================================

start "" "%RESULTS%\report.html"

exit /b %RC%
