@echo off
cd /d %~dp0
echo Activando entorno virtual...
call entorno\Scripts\activate.bat

echo Entrando en mi_blog...
cd mi_blog

echo Ejecutando servidor...
python manage.py runserver

pause
