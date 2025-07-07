@echo off
echo ==========================================================
echo      Instalador del Proyecto - Python/Django
echo ==========================================================
echo Este script creara un entorno virtual, instalara las
echo dependencias y preparara la base de datos.
echo.

REM Verifica si Python esta disponible
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python no esta instalado o no esta en el PATH.
    echo Por favor, instala Python 3 y asegurate de marcar "Add Python to PATH".
    pause
    exit /b
)

REM Crea el entorno virtual si no existe
if not exist entorno (
    echo Creando entorno virtual...
    python -m venv entorno
) else (
    echo El entorno virtual 'entorno' ya existe.
)

REM Activa el entorno virtual
call "entorno\Scripts\activate.bat"

REM Verifica si el entorno se activo correctamente
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: No se pudo activar el entorno virtual.
    pause
    exit /b
)

REM Instala las dependencias desde requirements.txt
echo.
if exist mi_blog\requirements.txt (
    echo Instalando dependencias desde requirements.txt...
    cd mi_blog
    pip install -r requirements.txt
) else (
    echo Error: No se encontro el archivo requirements.txt dentro de mi_blog.
    pause
    exit /b
)

REM Ejecuta las migraciones de la base de datos
echo.
echo Preparando la base de datos (migraciones)...
python manage.py makemigrations
python manage.py migrate

REM Crea un superusuario
echo.
echo Ahora se creara un superusuario para acceder al panel de administracion.
python manage.py createsuperuser

echo.
echo ==========================================================
echo        Instalacion completada con exito!
echo ==========================================================
echo Para iniciar el servidor, usa el comando:
echo python manage.py runserver
echo.

pause