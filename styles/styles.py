from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Colores del tema futurista
COLORS = {
    # Fondo principal (muy oscuro con tinte púrpura)
    "bg_dark": "#0d0b1e",
    "bg_medium": "#1a1630",
    "bg_light": "#252040",
    "bg_card": "#1e1a35",
    
    # Acentos con degradados
    "accent_purple": "#9333ea",
    "accent_pink": "#ec4899",
    "accent_blue": "#3b82f6",
    "accent_cyan": "#06b6d4",
    
    # Degradado principal (para botones y highlights)
    "gradient_start": "#7c3aed",  # Violeta
    "gradient_mid": "#a855f7",    # Púrpura
    "gradient_end": "#ec4899",    # Rosa
    
    # Texto
    "text_primary": "#f8fafc",
    "text_secondary": "#cbd5e1",
    "text_muted": "#94a3b8",
    
    # Bordes
    "border_dark": "#2d2654",
    "border_glow": "#7c3aed",
    
    # Estados
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    
    # Status colors
    "status_disponible": "#22c55e",   # Verde - en stock
    "status_pendiente": "#8b5cf6",    # Violeta - pendiente a pedir
    "status_pedido": "#f59e0b",       # Naranja - ya pedido
    "status_ultimo": "#3b82f6",       # Azul - últimos productos
    "status_perdido": "#ef4444",      # Rojo - perdido
    "status_no_hay_mas": "#6b7280",   # Gris - agotado
}

def apply_dark_theme(app: QApplication) -> None:
    """Aplica el tema futurista oscuro con degradados púrpura/azul/rosa."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(COLORS["bg_dark"]))
    palette.setColor(QPalette.WindowText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Base, QColor(COLORS["bg_medium"]))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS["bg_light"]))
    palette.setColor(QPalette.ToolTipBase, QColor(COLORS["bg_card"]))
    palette.setColor(QPalette.ToolTipText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Text, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Button, QColor(COLORS["bg_light"]))
    palette.setColor(QPalette.ButtonText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.BrightText, QColor(COLORS["accent_pink"]))
    palette.setColor(QPalette.Highlight, QColor(COLORS["accent_purple"]))
    palette.setColor(QPalette.HighlightedText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Link, QColor(COLORS["accent_cyan"]))
    app.setPalette(palette)
    
    app.setStyleSheet(f"""
        /* === CUSTOM TITLE BAR === */
        #TitleBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["bg_light"]}, stop:1 {COLORS["bg_card"]});
            border-bottom: 1px solid {COLORS["border_dark"]};
        }}
        
        #TitleLabel {{
            color: {COLORS["text_primary"]};
            font-weight: bold;
            font-size: 14px;
        }}
        
        #TitleButton {{
            background: transparent;
            border: none;
            border-radius: 0px;
            min-width: 50px;
            max-width: 50px;
        }}
        
        #TitleButton:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        #CloseButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["warning"]}, stop:1 {COLORS["error"]});
            border: none;
            border-radius: 0px;
            min-width: 60px;
            max-width: 60px;
        }}
        
        #CloseButton:hover {{
            background: {COLORS["error"]};
        }}

        /* === MAIN WINDOW === */
        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS["bg_dark"]}, 
                stop:0.5 {COLORS["bg_medium"]}, 
                stop:1 {COLORS["bg_dark"]});
        }}
        
        QWidget {{
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 13px;
        }}
        
        /* === TOOLTIPS === */
        QToolTip {{
            color: {COLORS["text_primary"]};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS["bg_card"]}, stop:1 {COLORS["bg_light"]});
            border: 1px solid {COLORS["border_glow"]};
            border-radius: 8px;
            padding: 8px 12px;
        }}
        
        /* === TABLE VIEW === */
        QTableView {{
            background-color: {COLORS["bg_medium"]};
            alternate-background-color: {COLORS["bg_light"]};
            gridline-color: {COLORS["border_dark"]};
            border: 1px solid {COLORS["border_dark"]};
            border-radius: 12px;
            selection-background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["gradient_start"]}, 
                stop:0.5 {COLORS["gradient_mid"]}, 
                stop:1 {COLORS["gradient_end"]});
            selection-color: {COLORS["text_primary"]};
            padding: 4px;
        }}
        
        QTableView::item {{
            padding: 8px 12px;
            border-bottom: 1px solid {COLORS["border_dark"]};
        }}
        
        QTableView::item:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(124, 58, 237, 0.2), stop:1 rgba(236, 72, 153, 0.2));
        }}
        
        QHeaderView::section {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["bg_light"]}, stop:1 {COLORS["bg_card"]});
            color: {COLORS["text_primary"]};
            padding: 12px 16px;
            border: none;
            border-bottom: 2px solid {COLORS["accent_purple"]};
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        QHeaderView::section:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["gradient_start"]}, stop:1 {COLORS["bg_light"]});
        }}
        
        /* === INPUT FIELDS === */
        QLineEdit, QComboBox, QSpinBox, QDateEdit {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["bg_card"]}, stop:1 {COLORS["bg_medium"]});
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["border_dark"]};
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 13px;
            min-height: 20px;
        }}
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {{
            border: 2px solid {COLORS["accent_purple"]};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["bg_light"]}, stop:1 {COLORS["bg_card"]});
        }}
        
        QLineEdit:hover, QComboBox:hover {{
            border: 1px solid {COLORS["accent_purple"]};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 0px;
            background: transparent;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            width: 0px;
            height: 0px;
        }}
        
        QDateEdit::drop-down {{
            border: none;
            width: 0px;
            background: transparent;
        }}
        
        QDateEdit::down-arrow {{
            image: none;
            width: 0px;
            height: 0px;
        }}
        
        QComboBox QAbstractItemView {{
            background: {COLORS["bg_card"]};
            border: 1px solid {COLORS["border_glow"]};
            border-radius: 8px;
            selection-background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["gradient_start"]}, stop:1 {COLORS["gradient_end"]});
            selection-color: {COLORS["text_primary"]};
            padding: 4px;
        }}
        
        /* === BUTTONS === */
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["gradient_start"]}, 
                stop:0.5 {COLORS["gradient_mid"]}, 
                stop:1 {COLORS["gradient_end"]});
            color: {COLORS["text_primary"]};
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["gradient_mid"]}, 
                stop:0.5 {COLORS["gradient_end"]}, 
                stop:1 {COLORS["accent_pink"]});
        }}
        
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["bg_light"]}, stop:1 {COLORS["gradient_start"]});
        }}
        
        QPushButton:disabled {{
            background: {COLORS["bg_light"]};
            color: {COLORS["text_muted"]};
        }}
        
        /* Botones secundarios (sin gradiente) */
        QPushButton[secondary="true"] {{
            background: {COLORS["bg_light"]};
            border: 1px solid {COLORS["border_dark"]};
        }}
        
        QPushButton[secondary="true"]:hover {{
            border: 1px solid {COLORS["accent_purple"]};
            background: {COLORS["bg_card"]};
        }}
        
        /* === CHECKBOXES === */
        QCheckBox {{
            color: {COLORS["text_secondary"]};
            spacing: 10px;
            font-size: 13px;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 6px;
            border: 2px solid {COLORS["border_dark"]};
            background: {COLORS["bg_card"]};
        }}
        
        QCheckBox::indicator:hover {{
            border: 2px solid {COLORS["accent_purple"]};
        }}
        
        QCheckBox::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS["gradient_start"]}, stop:1 {COLORS["gradient_end"]});
            border: 2px solid {COLORS["accent_purple"]};
        }}
        
        QCheckBox::indicator:checked:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS["gradient_mid"]}, stop:1 {COLORS["accent_pink"]});
        }}
        
        /* === LABELS === */
        QLabel {{
            color: {COLORS["text_secondary"]};
            font-size: 13px;
        }}
        
        QLabel[heading="true"] {{
            color: {COLORS["text_primary"]};
            font-size: 16px;
            font-weight: 600;
        }}
        
        /* === MAIN TITLE === */
        #MainTitle {{
            color: {COLORS["text_primary"]};
        }}
        
        /* === THEME COMBO === */
        #ThemeCombo {{
            max-width: 100px;
        }}
        
        #ThemeCombo QAbstractItemView {{
            min-width: 98px;
            max-width: 98px;
        }}
        
        /* === FILTER FRAME === */
        #FilterFrame {{
            background: {COLORS["bg_card"]};
            border: 1px solid {COLORS["border_dark"]};
            border-radius: 12px;
            padding: 8px;
        }}
        
        /* === STATS PANEL === */
        #StatsPanel {{
            background: {COLORS["bg_card"]};
            border-radius: 12px;
            padding: 12px;
        }}
        
        /* === PREVIEW CONTAINER === */
        #PreviewContainer {{
            background: {COLORS["bg_card"]};
            border: 2px dashed {COLORS["border_dark"]};
            border-radius: 12px;
        }}
        
        /* === STAT LABELS === */
        #StatLabel {{
            background: {COLORS["bg_light"]};
        }}
        
        /* === SPLITTER === */
        QSplitter::handle {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["accent_purple"]}, stop:1 {COLORS["accent_pink"]});
            width: 3px;
            margin: 4px 2px;
            border-radius: 1px;
        }}
        
        /* === SCROLLBARS === */
        QScrollBar:vertical {{
            background: {COLORS["bg_dark"]};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["gradient_start"]}, stop:1 {COLORS["gradient_end"]});
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["gradient_mid"]}, stop:1 {COLORS["accent_pink"]});
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            background: {COLORS["bg_dark"]};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["gradient_start"]}, stop:1 {COLORS["gradient_end"]});
            min-width: 30px;
            border-radius: 6px;
            margin: 2px;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        
        /* === DIALOGS === */
        QDialog {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS["bg_dark"]}, stop:1 {COLORS["bg_medium"]});
            border: 1px solid {COLORS["border_glow"]};
            border-radius: 16px;
        }}
        
        /* === CODE DIALOG (Custom) === */
        #CodeDialog {{
            background: {COLORS["bg_dark"]};
            border: 1px solid {COLORS["border_glow"]};
            border-radius: 12px;
        }}
        
        #DialogTitleBar {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["gradient_start"]}, 
                stop:0.5 {COLORS["gradient_mid"]}, 
                stop:1 {COLORS["gradient_end"]});
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        }}
        
        #DialogCloseButton {{
            background: rgba(0, 0, 0, 0.2);
            border: none;
            border-radius: 0px;
            border-top-left-radius: 12px;
            color: white;
            font-size: 18px;
            font-weight: bold;
        }}
        
        #DialogCloseButton:hover {{
            background: #ef4444;
        }}
        
        #DialogTitleLabel {{
            color: white;
            font-weight: 600;
            font-size: 13px;
            padding-left: 4px;
        }}
        
        #DialogContent {{
            background: {COLORS["bg_dark"]};
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
        }}
        
        /* === MESSAGE BOX === */
        QMessageBox {{
            background: {COLORS["bg_card"]};
        }}
        
        QMessageBox QLabel {{
            color: {COLORS["text_primary"]};
            font-size: 14px;
        }}
        
        /* === GROUPBOX === */
        QGroupBox {{
            background: {COLORS["bg_card"]};
            border: 1px solid {COLORS["border_dark"]};
            border-radius: 12px;
            margin-top: 16px;
            padding: 16px;
            font-weight: 600;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
            color: {COLORS["accent_purple"]};
        }}
        
        /* === AUTOCOMPLETE POPUP === */
        QListView {{
            background: {COLORS["bg_card"]};
            border: 1px solid {COLORS["border_glow"]};
            border-radius: 10px;
            padding: 4px;
            outline: none;
            min-width: 350px;
        }}
        
        QListView::item {{
            padding: 10px 16px;
            border-radius: 6px;
            margin: 2px 4px;
        }}
        
        QListView::item:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(124, 58, 237, 0.3), stop:1 rgba(236, 72, 153, 0.3));
        }}
        
        QListView::item:selected {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["gradient_start"]}, stop:1 {COLORS["gradient_end"]});
            color: {COLORS["text_primary"]};
        }}
    """)

def apply_light_theme(app: QApplication) -> None:
    """Aplica un tema claro elegante con tonos azules profesionales."""
    # Paleta de colores claros con acentos azules (celeste a azul oscuro)
    LIGHT = {
        # Fondos
        "bg_primary": "#F8FAFC",       # Fondo principal muy suave con tinte azul
        "bg_secondary": "#FFFFFF",      # Blanco puro para cards/inputs
        "bg_tertiary": "#F1F5F9",       # Gris azulado muy claro para alternar
        "bg_elevated": "#FFFFFF",       # Elementos elevados
        
        # Acentos azules (celeste a azul oscuro)
        "accent_primary": "#0ea5e9",    # Celeste vibrante (sky-500)
        "accent_light": "#38bdf8",      # Celeste claro (sky-400)
        "accent_dark": "#0369a1",       # Azul oscuro (sky-700)
        "accent_deep": "#1e3a5f",       # Azul muy oscuro para contraste
        
        # Texto
        "text_primary": "#0f172a",      # Azul muy oscuro (slate-900)
        "text_secondary": "#475569",    # Gris azulado (slate-600)
        "text_muted": "#94a3b8",        # Gris claro (slate-400)
        "text_on_accent": "#FFFFFF",    # Blanco para texto sobre acentos
        
        # Bordes
        "border_light": "#e2e8f0",      # Borde sutil (slate-200)
        "border_medium": "#cbd5e1",     # Borde más visible (slate-300)
        "border_focus": "#0ea5e9",      # Borde de foco (celeste)
        
        # Estados
        "success": "#059669",
        "warning": "#d97706",
        "error": "#dc2626",
        "info": "#0ea5e9",
        
        # Hover/Selection
        "hover_bg": "#e0f2fe",          # Celeste muy claro para hover (sky-100)
        "selection_bg": "#0ea5e9",      # Celeste para selección
    }
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(LIGHT["bg_primary"]))
    palette.setColor(QPalette.WindowText, QColor(LIGHT["text_primary"]))
    palette.setColor(QPalette.Base, QColor(LIGHT["bg_secondary"]))
    palette.setColor(QPalette.AlternateBase, QColor(LIGHT["bg_tertiary"]))
    palette.setColor(QPalette.ToolTipBase, QColor(LIGHT["bg_elevated"]))
    palette.setColor(QPalette.ToolTipText, QColor(LIGHT["text_primary"]))
    palette.setColor(QPalette.Text, QColor(LIGHT["text_primary"]))
    palette.setColor(QPalette.Button, QColor(LIGHT["bg_secondary"]))
    palette.setColor(QPalette.ButtonText, QColor(LIGHT["text_primary"]))
    palette.setColor(QPalette.BrightText, QColor(LIGHT["accent_primary"]))
    palette.setColor(QPalette.Highlight, QColor(LIGHT["selection_bg"]))
    palette.setColor(QPalette.HighlightedText, QColor(LIGHT["text_on_accent"]))
    palette.setColor(QPalette.Link, QColor(LIGHT["accent_primary"]))
    
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(LIGHT["text_muted"]))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(LIGHT["text_muted"]))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(LIGHT["text_muted"]))
    
    app.setPalette(palette)
    
    app.setStyleSheet(f"""
        /* === CUSTOM TITLE BAR === */
        #TitleBar {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["accent_dark"]}, 
                stop:0.5 {LIGHT["accent_primary"]}, 
                stop:1 {LIGHT["accent_light"]});
            border-bottom: none;
        }}
        
        #TitleLabel {{
            color: {LIGHT["text_on_accent"]};
            font-weight: bold;
            font-size: 14px;
        }}
        
        #TitleButton {{
            background: transparent;
            border: none;
            border-radius: 0px;
            min-width: 50px;
            max-width: 50px;
        }}
        
        #TitleButton:hover {{
            background: rgba(255, 255, 255, 0.25);
        }}
        
        #CloseButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["warning"]}, stop:1 {LIGHT["error"]});
            border: none;
            border-radius: 0px;
            min-width: 60px;
            max-width: 60px;
        }}
        
        #CloseButton:hover {{
            background: {LIGHT["error"]};
        }}

        /* === MAIN WINDOW === */
        QMainWindow {{
            background: {LIGHT["bg_primary"]};
        }}
        
        QWidget {{
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 13px;
            color: {LIGHT["text_primary"]};
        }}
        
        /* === TOOLTIPS === */
        QToolTip {{
            color: {LIGHT["text_primary"]};
            background: {LIGHT["bg_elevated"]};
            border: 1px solid {LIGHT["border_medium"]};
            border-radius: 8px;
            padding: 8px 12px;
        }}
        
        /* === TABLE VIEW === */
        QTableView {{
            background-color: {LIGHT["bg_secondary"]};
            alternate-background-color: {LIGHT["bg_tertiary"]};
            gridline-color: {LIGHT["border_light"]};
            border: 1px solid {LIGHT["border_medium"]};
            border-radius: 12px;
            selection-background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["accent_dark"]}, 
                stop:1 {LIGHT["accent_primary"]});
            selection-color: {LIGHT["text_on_accent"]};
            padding: 4px;
            color: {LIGHT["text_primary"]};
        }}
        
        QTableView::item {{
            padding: 8px 12px;
            border-bottom: 1px solid {LIGHT["border_light"]};
            color: {LIGHT["text_primary"]};
        }}
        
        QTableView::item:hover {{
            background: {LIGHT["hover_bg"]};
        }}
        
        QHeaderView::section {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {LIGHT["bg_secondary"]}, stop:1 {LIGHT["bg_tertiary"]});
            color: {LIGHT["text_primary"]};
            padding: 12px 16px;
            border: none;
            border-bottom: 2px solid {LIGHT["accent_primary"]};
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        QHeaderView::section:hover {{
            background: {LIGHT["hover_bg"]};
        }}
        
        /* === INPUT FIELDS === */
        QLineEdit, QComboBox, QSpinBox, QDateEdit {{
            background: {LIGHT["bg_secondary"]};
            color: {LIGHT["text_primary"]};
            border: 1px solid {LIGHT["border_medium"]};
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 13px;
            min-height: 20px;
        }}
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {{
            border: 2px solid {LIGHT["accent_primary"]};
            background: {LIGHT["bg_secondary"]};
        }}
        
        QLineEdit:hover, QComboBox:hover {{
            border: 1px solid {LIGHT["accent_light"]};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 0px;
            background: transparent;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            width: 0px;
            height: 0px;
        }}
        
        QDateEdit::drop-down {{
            border: none;
            width: 0px;
            background: transparent;
        }}
        
        QDateEdit::down-arrow {{
            image: none;
            width: 0px;
            height: 0px;
        }}
        
        QComboBox QAbstractItemView {{
            background: {LIGHT["bg_secondary"]};
            border: 1px solid {LIGHT["border_medium"]};
            border-radius: 8px;
            selection-background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["accent_dark"]}, stop:1 {LIGHT["accent_primary"]});
            selection-color: {LIGHT["text_on_accent"]};
            padding: 4px;
            color: {LIGHT["text_primary"]};
        }}
        
        /* === BUTTONS === */
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["accent_dark"]}, 
                stop:0.5 {LIGHT["accent_primary"]}, 
                stop:1 {LIGHT["accent_light"]});
            color: {LIGHT["text_on_accent"]};
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["accent_primary"]}, 
                stop:0.5 {LIGHT["accent_light"]}, 
                stop:1 #7dd3fc);
        }}
        
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["accent_deep"]}, stop:1 {LIGHT["accent_dark"]});
        }}
        
        QPushButton:disabled {{
            background: {LIGHT["bg_tertiary"]};
            color: {LIGHT["text_muted"]};
        }}
        
        /* Botones secundarios */
        QPushButton[secondary="true"] {{
            background: {LIGHT["bg_secondary"]};
            color: {LIGHT["text_primary"]};
            border: 1px solid {LIGHT["border_medium"]};
        }}
        
        QPushButton[secondary="true"]:hover {{
            border: 1px solid {LIGHT["accent_primary"]};
            background: {LIGHT["hover_bg"]};
        }}
        
        /* === CHECKBOXES === */
        QCheckBox {{
            color: {LIGHT["text_primary"]};
            spacing: 10px;
            font-size: 13px;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 6px;
            border: 2px solid {LIGHT["border_medium"]};
            background: {LIGHT["bg_secondary"]};
        }}
        
        QCheckBox::indicator:hover {{
            border: 2px solid {LIGHT["accent_primary"]};
        }}
        
        QCheckBox::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {LIGHT["accent_dark"]}, stop:1 {LIGHT["accent_primary"]});
            border: 2px solid {LIGHT["accent_primary"]};
        }}
        
        QCheckBox::indicator:checked:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {LIGHT["accent_primary"]}, stop:1 {LIGHT["accent_light"]});
        }}
        
        /* === LABELS === */
        QLabel {{
            color: {LIGHT["text_primary"]};
            font-size: 13px;
        }}
        
        QLabel[heading="true"] {{
            color: {LIGHT["text_primary"]};
            font-size: 16px;
            font-weight: 600;
        }}
        
        /* === MAIN TITLE === */
        #MainTitle {{
            color: {LIGHT["text_primary"]};
            font-size: 24px;
            font-weight: bold;
        }}
        
        /* === THEME COMBO === */
        #ThemeCombo {{
            max-width: 100px;
        }}
        
        #ThemeCombo QAbstractItemView {{
            min-width: 98px;
            max-width: 98px;
        }}
        
        /* === FILTER FRAME === */
        #FilterFrame {{
            background: {LIGHT["hover_bg"]};
            border: 1px solid {LIGHT["border_light"]};
            border-radius: 12px;
            padding: 8px;
        }}
        
        #FilterFrame QLabel {{
            color: {LIGHT["text_primary"]};
        }}
        
        #FilterFrame QCheckBox {{
            color: {LIGHT["text_primary"]};
        }}
        
        /* === STATS PANEL === */
        #StatsPanel {{
            background: {LIGHT["bg_secondary"]};
            border: 1px solid {LIGHT["border_light"]};
            border-radius: 12px;
        }}
        
        /* === PREVIEW CONTAINER === */
        #PreviewContainer {{
            background: {LIGHT["bg_tertiary"]};
            border: 2px dashed {LIGHT["border_medium"]};
            border-radius: 12px;
        }}
        
        /* === STAT LABELS === */
        #StatLabel {{
            background: {LIGHT["bg_secondary"]};
            border: 1px solid {LIGHT["border_light"]};
        }}
        
        /* === SPLITTER === */
        QSplitter::handle {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {LIGHT["accent_dark"]}, stop:1 {LIGHT["accent_primary"]});
            width: 3px;
            margin: 4px 2px;
            border-radius: 1px;
        }}
        
        /* === SCROLLBARS === */
        QScrollBar:vertical {{
            background: {LIGHT["bg_tertiary"]};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {LIGHT["accent_dark"]}, stop:1 {LIGHT["accent_primary"]});
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {LIGHT["accent_primary"]}, stop:1 {LIGHT["accent_light"]});
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            background: {LIGHT["bg_tertiary"]};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["accent_dark"]}, stop:1 {LIGHT["accent_primary"]});
            min-width: 30px;
            border-radius: 6px;
            margin: 2px;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        
        /* === DIALOGS === */
        QDialog {{
            background: {LIGHT["bg_primary"]};
            border: 1px solid {LIGHT["border_medium"]};
            border-radius: 16px;
        }}
        
        /* === CODE DIALOG (Custom) === */
        #CodeDialog {{
            background: {LIGHT["bg_secondary"]};
            border: 1px solid {LIGHT["border_medium"]};
            border-radius: 12px;
        }}
        
        #DialogTitleBar {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["accent_dark"]}, 
                stop:0.5 {LIGHT["accent_primary"]}, 
                stop:1 {LIGHT["accent_light"]});
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        }}
        
        #DialogCloseButton {{
            background: rgba(0, 0, 0, 0.15);
            border: none;
            border-radius: 0px;
            border-top-left-radius: 12px;
            color: white;
            font-size: 18px;
            font-weight: bold;
        }}
        
        #DialogCloseButton:hover {{
            background: {LIGHT["error"]};
        }}
        
        #DialogTitleLabel {{
            color: white;
            font-weight: 600;
            font-size: 13px;
            padding-left: 4px;
        }}
        
        #DialogContent {{
            background: {LIGHT["bg_secondary"]};
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
        }}
        
        /* === MESSAGE BOX === */
        QMessageBox {{
            background: {LIGHT["bg_secondary"]};
        }}
        
        QMessageBox QLabel {{
            color: {LIGHT["text_primary"]};
            font-size: 14px;
        }}
        
        /* === GROUPBOX === */
        QGroupBox {{
            background: {LIGHT["bg_secondary"]};
            border: 1px solid {LIGHT["border_light"]};
            border-radius: 12px;
            margin-top: 16px;
            padding: 16px;
            font-weight: 600;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
            color: {LIGHT["accent_dark"]};
        }}
        
        /* === AUTOCOMPLETE POPUP === */
        QListView {{
            background: {LIGHT["bg_secondary"]};
            border: 1px solid {LIGHT["border_medium"]};
            border-radius: 10px;
            padding: 4px;
            outline: none;
            color: {LIGHT["text_primary"]};
            min-width: 350px;
        }}
        
        QListView::item {{
            padding: 10px 16px;
            border-radius: 6px;
            margin: 2px 4px;
            color: {LIGHT["text_primary"]};
        }}
        
        QListView::item:hover {{
            background: {LIGHT["hover_bg"]};
        }}
        
        QListView::item:selected {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LIGHT["accent_dark"]}, stop:1 {LIGHT["accent_primary"]});
            color: {LIGHT["text_on_accent"]};
        }}
    """)

def get_status_color(status: str) -> str:
    """Retorna el color asociado a un estado."""
    status_colors = {
        "disponible": COLORS["status_disponible"],
        "pendiente": COLORS["status_pendiente"],
        "pedido": COLORS["status_pedido"],
        "ultimo": COLORS["status_ultimo"],
        "perdido": COLORS["status_perdido"],
        "no_hay_mas": COLORS["status_no_hay_mas"],
    }
    return status_colors.get(status, COLORS["text_muted"])

def get_status_style(status: str) -> str:
    """Retorna un estilo CSS para un badge de estado."""
    color = get_status_color(status)
    return f"""
        background-color: {color};
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 11px;
    """
