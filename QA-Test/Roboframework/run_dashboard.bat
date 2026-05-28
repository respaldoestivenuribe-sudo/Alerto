@echo off
setlocal

echo ============================================================
echo   Alerto QA Dashboard
echo   URL: http://localhost:9090
echo ============================================================
echo.

set "SCRIPT_DIR=%~dp0"

:: Verificar Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo ERROR: Python no encontrado. Instala Python 3.9+ y añádelo al PATH.
  pause
  exit /b 1
)

:: Instalar/verificar dependencias del dashboard
echo Verificando dependencias...
python -c "import flask, flask_cors" 2>nul
if %ERRORLEVEL% neq 0 (
  echo Instalando Flask...
  python -m pip install flask flask-cors --quiet
)

:: Instalar Robot Framework y bibliotecas de prueba
python -c "from RequestsLibrary import RequestsLibrary" 2>nul
if %ERRORLEVEL% neq 0 (
  echo Instalando Robot Framework y bibliotecas...
  python -m pip install -r "%SCRIPT_DIR%requirements.txt" --quiet
  if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Hubo errores instalando dependencias.
    echo     Ejecuta install_deps.bat para más detalles.
    echo.
  ) else (
    echo [OK] Dependencias instaladas.
  )
) else (
  echo [OK] Dependencias ya instaladas.
)

echo.

:: Crear directorio de resultados
mkdir "%SCRIPT_DIR%results" 2>nul

:: Abrir navegador después de 2 segundos
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:9090"

echo Iniciando servidor en http://localhost:9090
echo Presiona Ctrl+C para detener.
echo.

:: Iniciar servidor usando el mismo Python que tiene las deps
python "%SCRIPT_DIR%dashboard\app.py"
