# CodeTrace - Guía de Compilación e Instalación

## Requisitos Previos

### Para Desarrollo
- Python 3.8+
- pip install -r requirements.txt

### Para Compilar
- PyInstaller: `pip install pyinstaller`
- Inno Setup 6 (opcional, para crear instalador): https://jrsoftware.org/isdl.php

## Estructura del Proyecto

```
CodeTrace/
├── main.py              # Punto de entrada
├── build.bat            # Script de compilación automática
├── modules/
│   └── ocr.py           # Módulo OCR con Tesseract
├── tesseract/           # Tesseract OCR portable (incluido)
│   ├── tesseract.exe
│   └── tessdata/
├── images/              # Iconos e imágenes
├── installer/
│   └── CodeTrace.iss    # Script de Inno Setup
└── dist/                # Ejecutables generados
```

## Compilación Rápida

### Opción 1: Script Automático (Recomendado)
```batch
build.bat
```
Este script:
1. Limpia builds anteriores
2. Compila el ejecutable con PyInstaller
3. Genera el instalador si Inno Setup está instalado

### Opción 2: Manual

#### Paso 1: Generar Ejecutable
```batch
pyinstaller main.py -w --onefile --icon images/logo_app.png -n CodeTrace
```

#### Paso 2: Generar Instalador (requiere Inno Setup)
```batch
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\CodeTrace.iss
```

## Archivos Generados

- `dist/CodeTrace.exe` - Ejecutable portable (requiere copiar tesseract/ e images/)
- `dist/CodeTrace_Setup_1.0.0.exe` - Instalador completo (incluye todo)

## Distribución

### Usando el Instalador (Recomendado)
Distribuye `CodeTrace_Setup_1.0.0.exe`. El instalador:
- Instala el ejecutable en Program Files
- Copia Tesseract OCR automáticamente
- Crea accesos directos
- Permite desinstalar limpiamente

### Versión Portable
Para una versión portable, copia estos archivos/carpetas juntos:
```
CodeTrace/
├── CodeTrace.exe
├── tesseract/
└── images/
```

## Notas Técnicas

### Tesseract OCR
- La aplicación configura automáticamente la variable `TESSDATA_PREFIX`
- Tesseract debe estar en la carpeta `tesseract/` junto al ejecutable
- Se incluye solo el idioma inglés (`eng.traineddata`)

### Rutas
El módulo OCR detecta automáticamente si está en:
- **Desarrollo**: Usa rutas relativas al proyecto
- **Compilado**: Usa rutas relativas al ejecutable
