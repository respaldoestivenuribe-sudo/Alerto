@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Alerto QA — Ejecutar todas las suites de prueba
echo   Robot Framework 7.1
echo ============================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "RESULTS=%SCRIPT_DIR%results\run_all_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "RESULTS=%RESULTS: =0%"

echo Directorio de resultados: %RESULTS%
echo.

:: Verificar que robotframework-requests está instalado
python -c "from RequestsLibrary import RequestsLibrary" 2>nul
if %ERRORLEVEL% neq 0 (
  echo [!] RequestsLibrary no encontrada. Instalando dependencias...
  python -m pip install -r "%SCRIPT_DIR%requirements.txt" --quiet
)


mkdir "%RESULTS%" 2>nul

python -m robot ^
  --outputdir "%RESULTS%" ^
  --output    output.xml ^
  --log       log.html ^
  --report    report.html ^
  --loglevel  INFO ^
  --variable  SCREENSHOTS_DIR:%RESULTS%\screenshots ^
  --name      "Alerto QA Suite" ^
  "%SCRIPT_DIR%tests\TC_AUTH.robot" ^
  "%SCRIPT_DIR%tests\TC_UI.robot" ^
  "%SCRIPT_DIR%tests\TC_DATA.robot" ^
  "%SCRIPT_DIR%tests\TC_RISK.robot" ^
  "%SCRIPT_DIR%tests\TC_ADMIN.robot" ^
  "%SCRIPT_DIR%tests\TC_SIM.robot" ^
  "%SCRIPT_DIR%tests\TC_ALERTS.robot" ^
  "%SCRIPT_DIR%tests\TC_SEC.robot" ^
  "%SCRIPT_DIR%tests\TC_PERF.robot" ^
  "%SCRIPT_DIR%tests\TC_INT.robot" ^
  "%SCRIPT_DIR%tests\TC_NOTIF.robot"

set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if %RC%==0 (
  echo   RESULTADO: PASSED
) else (
  echo   RESULTADO: FAILED (RC=%RC%)
)
echo   Reporte: %RESULTS%\report.html
echo ============================================================

start "" "%RESULTS%\report.html"

exit /b %RC%
