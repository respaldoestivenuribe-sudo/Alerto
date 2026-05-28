@echo off
setlocal

echo ============================================================
echo   Alerto QA — Instalación de dependencias
echo   Robot Framework + bibliotecas de prueba
echo ============================================================
echo.

:: Detectar Python disponible
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo ERROR: Python no encontrado en el PATH.
  echo Instala Python 3.9+ y añádelo al PATH.
  pause
  exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo Python detectado: %%i
echo.

echo Instalando robotframework y bibliotecas...
python -m pip install --upgrade pip --quiet

python -m pip install ^
  robotframework==7.1 ^
  robotframework-requests==0.9.7 ^
  robotframework-seleniumlibrary==6.3.0 ^
  robotframework-databaselibrary==1.4.4 ^
  psycopg2-binary ^
  Flask==3.0.3 ^
  Flask-Cors==4.0.1 ^
  selenium ^
  webdriver-manager ^
  requests

if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Falló la instalación de alguna dependencia.
  pause
  exit /b 1
)

echo.
echo ============================================================
echo   Verificando instalación...
echo ============================================================
python -c "import robot; print('  robot:', robot.version.VERSION)"
python -c "from RequestsLibrary import RequestsLibrary; print('  RequestsLibrary: OK')"
python -c "from SeleniumLibrary import SeleniumLibrary; print('  SeleniumLibrary: OK')"
python -c "import flask; print('  Flask:', flask.__version__)"

echo.
echo ============================================================
echo   Instalación completada exitosamente.
echo   Ahora puedes ejecutar: run_dashboard.bat
echo ============================================================
pause
