@echo off
echo ========================================
echo   Media Finder - Build Executavel
echo ========================================
echo.

echo [1/3] Limpando builds anteriores...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo [2/3] Construindo executavel com PyInstaller...
poetry run pyinstaller MediaFinder.spec --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [3/3] Build concluido com sucesso!
    echo.
    echo Executavel criado em: dist\MediaFinder.exe
    echo.
    echo Pressione qualquer tecla para abrir a pasta...
    pause >nul
    explorer dist
) else (
    echo.
    echo [ERRO] Falha ao construir o executavel!
    echo.
    pause
)
