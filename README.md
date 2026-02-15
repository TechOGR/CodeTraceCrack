# 📦 CodeTrace - Gestor de Códigos

CodeTrace es una aplicación de escritorio moderna y robusta diseñada para la gestión, seguimiento y extracción de códigos mediante OCR. Con una interfaz inspirada en estéticas futuristas, ofrece una experiencia de usuario fluida y eficiente para el manejo de inventarios de códigos.

## ✨ Características Principales

- **🖼️ Extracción OCR Avanzada**: Importa códigos directamente desde imágenes utilizando EasyOCR con preprocesamiento OpenCV.
- **🛠️ Gestión CRUD Completa**: Crea, lee, actualiza y elimina códigos de forma sencilla.
- **🎨 Interfaz Personalizada (Frameless)**: Ventana moderna sin bordes nativos, con barra de título personalizada y controles integrados.
- **🌓 Temas Dinámicos**: Soporte para Modo Oscuro (Futurista) y Modo Claro (Minimalista) con cambio en tiempo real.
- **🔐 Sistema de Login**: Control de acceso con roles (admin/peon) para permisos diferenciados.
- **🔍 Búsqueda Inteligente**: Autocompletado histórico que muestra el estado de los códigos mientras escribes.
- **📊 Estadísticas en Vivo**: Panel lateral con conteo automático por estados (Disponible, Pedido, Último de su tipo, etc.).
- **📥 Importación Masiva**: Soporte para archivos `.txt`, `.csv` y procesamiento por lotes de imágenes.

## 🚀 Tecnologías Utilizadas

- **Lenguaje**: Python 3.8+
- **Interfaz Gráfica**: PyQt5
- **Base de Datos**: SQLite3
- **Procesamiento de Imágenes**: 
  - OpenCV (cv2)
  - Pillow (PIL)
- **Motor OCR**: EasyOCR (no requiere instalación externa)

## 🛠️ Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/CodeTrace.git
   cd CodeTrace
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Uso

1. Ejecuta la aplicación:
   ```bash
   python main.py
   ```
2. **Agregar códigos**: Usa el botón "Agregar" para entrada manual o "Importar .txt" para listas.
3. **OCR**: Haz clic en "OCR Imagen" para procesar capturas de pantalla o fotos con códigos.
4. **Filtros**: Utiliza el panel superior para filtrar por códigos usados, duplicados o estados específicos.

## 📂 Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación.
- `ui.py`: Lógica de la interfaz de usuario y componentes PyQt5.
- `styles.py`: Definiciones de temas (Oscuro/Claro) y estilos QSS.
- `repository.py`: Gestión de la base de datos SQLite y lógica de negocio.
- `ocr.py`: Motor de procesamiento de imágenes y extracción de texto.

---
Desarrollado con ❤️ para la gestión eficiente de códigos.
