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
    "status_disponible": "#22c55e",
    "status_pedido": "#f59e0b",
    "status_perdido": "#ef4444",
    "status_no_hay_mas": "#6b7280",
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
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {COLORS["accent_purple"]};
            margin-right: 10px;
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
    """Aplica el tema claro minimalista con acentos púrpura."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(250, 250, 255))
    palette.setColor(QPalette.WindowText, QColor(30, 27, 75))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 243, 255))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(30, 27, 75))
    palette.setColor(QPalette.Text, QColor(30, 27, 75))
    palette.setColor(QPalette.Button, QColor(245, 243, 255))
    palette.setColor(QPalette.ButtonText, QColor(30, 27, 75))
    palette.setColor(QPalette.Highlight, QColor(COLORS["accent_purple"]))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    palette.setColor(QPalette.Link, QColor(COLORS["accent_blue"]))
    app.setPalette(palette)
    
    app.setStyleSheet(f"""
        QWidget {{
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 13px;
        }}
        
        QToolTip {{
            color: #1e1b4b;
            background-color: #ffffff;
            border: 1px solid {COLORS["accent_purple"]};
            border-radius: 8px;
            padding: 8px 12px;
        }}
        
        QTableView {{
            background-color: #ffffff;
            alternate-background-color: #f5f3ff;
            gridline-color: #e9d5ff;
            border: 1px solid #e9d5ff;
            border-radius: 12px;
            selection-background-color: {COLORS["accent_purple"]};
            selection-color: #ffffff;
        }}
        
        QTableView::item {{
            padding: 8px 12px;
            border-bottom: 1px solid #f3e8ff;
        }}
        
        QHeaderView::section {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f5f3ff, stop:1 #ede9fe);
            color: #1e1b4b;
            padding: 12px 16px;
            border: none;
            border-bottom: 2px solid {COLORS["accent_purple"]};
            font-weight: 600;
        }}
        
        QLineEdit, QComboBox, QSpinBox, QDateEdit {{
            background-color: #ffffff;
            color: #1e1b4b;
            border: 1px solid #e9d5ff;
            border-radius: 10px;
            padding: 10px 16px;
        }}
        
        QLineEdit:focus, QComboBox:focus {{
            border: 2px solid {COLORS["accent_purple"]};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {COLORS["accent_purple"]};
            margin-right: 10px;
        }}
        
        QComboBox QAbstractItemView {{
            background: #ffffff;
            border: 1px solid {COLORS["accent_purple"]};
            border-radius: 8px;
            selection-background-color: {COLORS["accent_purple"]};
            selection-color: #ffffff;
        }}
        
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["gradient_start"]}, 
                stop:0.5 {COLORS["gradient_mid"]}, 
                stop:1 {COLORS["gradient_end"]});
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 600;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS["gradient_mid"]}, stop:1 {COLORS["accent_pink"]});
        }}
        
        QCheckBox {{
            color: #1e1b4b;
            spacing: 10px;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 6px;
            border: 2px solid #e9d5ff;
            background: #ffffff;
        }}
        
        QCheckBox::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS["gradient_start"]}, stop:1 {COLORS["gradient_end"]});
            border: 2px solid {COLORS["accent_purple"]};
        }}
        
        QLabel {{
            color: #1e1b4b;
        }}
        
        QSplitter::handle {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["accent_purple"]}, stop:1 {COLORS["accent_pink"]});
            width: 3px;
            border-radius: 1px;
        }}
        
        QScrollBar:vertical {{
            background: #f5f3ff;
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS["gradient_start"]}, stop:1 {COLORS["gradient_end"]});
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QListView {{
            background: #ffffff;
            border: 1px solid {COLORS["accent_purple"]};
            border-radius: 10px;
            padding: 4px;
        }}
        
        QListView::item {{
            padding: 10px 16px;
            border-radius: 6px;
            margin: 2px 4px;
        }}
        
        QListView::item:selected {{
            background: {COLORS["accent_purple"]};
            color: #ffffff;
        }}
    """)

def get_status_color(status: str) -> str:
    """Retorna el color asociado a un estado."""
    status_colors = {
        "disponible": COLORS["status_disponible"],
        "pedido": COLORS["status_pedido"],
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
