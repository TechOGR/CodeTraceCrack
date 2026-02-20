@echo off
setlocal enabledelayedexpansion

echo ============================================
echo    CodeTrace - Build Script
echo    Requiere Python 3.8 para Windows 7
echo ============================================
echo.

:: Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo ERROR: Este script debe ejecutarse desde el directorio raiz del proyecto
    pause
    exit /b 1
)

:: Verificar version de Python (debe ser 3.8.x para compatibilidad con Windows 7)
echo Verificando version de Python...
python --version 2>&1 | findstr /C:"3.8" >nul
if errorlevel 1 (
    echo.
    echo ADVERTENCIA: Se recomienda Python 3.8.x para compatibilidad con Windows 7
    echo Version actual:
    python --version
    echo.
    echo Para cambiar a Python 3.8, ejecuta: pyenv local 3.8.0
    echo.
    set /p CONTINUAR="Deseas continuar de todos modos? (S/N): "
    if /i not "!CONTINUAR!"=="S" exit /b 1
)

:: Crear carpeta dist si no existe
if not exist "dist" mkdir dist

echo [1/3] Limpiando builds anteriores...
if exist "dist\CodeTrace.exe" del /f "dist\CodeTrace.exe"
if exist "build" rmdir /s /q "build"
if exist "CodeTrace.spec" del /f "CodeTrace.spec"

echo [2/3] Compilando ejecutable con PyInstaller (Python 3.8)...
echo.
echo Incluyendo recursos: images, styles
echo.

:: Verificar que existe el icono (PNG o ICO)
if exist "images\\logo_app.ico" (
    python -m PyInstaller main.py -w --onefile --icon images\\logo_app.ico -n CodeTrace --add-data "images;images" --add-data "styles;styles"
) else if exist "images\\logo_app.png" (
    echo Usando logo_app.png como icono...
    python -m PyInstaller main.py -w --onefile --icon images\\logo_app.png -n CodeTrace --add-data "images;images" --add-data "styles;styles"
) else (
    echo ADVERTENCIA: No se encontro icono
    echo Compilando sin icono...
    python -m PyInstaller main.py -w --onefile -n CodeTrace --add-data "images;images" --add-data "styles;styles"
)

:: Verificar que se creo el ejecutable
if not exist "dist\CodeTrace.exe" (
    echo ERROR: No se pudo crear el ejecutable
    pause
    exit /b 1
)

echo.
echo [3/3] Ejecutable creado exitosamente!
echo       Ubicacion: dist\CodeTrace.exe
echo.

:: Verificar si Inno Setup esta instalado
set INNO_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if defined INNO_PATH (
    echo Inno Setup encontrado. Generando instalador...
    echo.
    "%INNO_PATH%" "installer\CodeTrace.iss"
    
    if exist "dist\CodeTrace_Setup_1.0.0.exe" (
        echo.
        echo ============================================
        echo    BUILD COMPLETADO EXITOSAMENTE!
        echo ============================================
        echo.
        echo Archivos generados:
        echo   - dist\CodeTrace.exe (ejecutable portable)
        echo   - dist\CodeTrace_Setup_1.0.0.exe (instalador)
        echo.
    ) else (
        echo.
        echo ADVERTENCIA: El instalador no se pudo crear.
        echo Verifica que Inno Setup este correctamente instalado.
        echo.
    )
) else (
    echo.
    echo NOTA: Inno Setup no encontrado.
    echo Para generar el instalador, instala Inno Setup 6 desde:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo Luego ejecuta manualmente:
    echo   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\CodeTrace.iss
    echo.
)

echo Presiona cualquier tecla para salir...
pause > nul
