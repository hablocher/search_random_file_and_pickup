@echo off
REM Quick start script for Windows
echo ====================================
echo Media Finder - Quick Start
echo ====================================
echo.

REM Check if Poetry is installed
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Poetry nao encontrado. Por favor, instale Poetry primeiro:
    echo https://python-poetry.org/docs/#installation
    echo.
    echo Execute no PowerShell:
    echo ^(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing^).Content ^| python -
    pause
    exit /b 1
)

echo Poetry encontrado!
echo.

REM Install dependencies
echo Instalando dependencias...
poetry install
if %errorlevel% neq 0 (
    echo Erro ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ====================================
echo Instalacao concluida!
echo ====================================
echo.
echo Para usar:
echo   poetry run rfp-gui          - Interface grafica
echo   poetry run random-file-picker --help  - Linha de comando
echo.
pause
