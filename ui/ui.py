# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'ui\\ui.py'
# Bytecode version: 3.8.0rc1+ (3413)

import re
from typing import List, Optional
from PyQt5.QtCore import Qt, QSize, QAbstractTableModel, QModelIndex, QVariant, QStringListModel, QTimer, QPoint
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLineEdit, QPushButton, QLabel, QCheckBox, QComboBox, QFileDialog, QMessageBox, QSplitter, QDialog, QFormLayout, QCompleter, QListView, QStyledItemDelegate, QFrame, QGridLayout, QSizeGrip
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPainter, QBrush, QPen, QFont
from pathlib import Path
from datetime import datetime
from repository.db_querys import CodeRepository, STATUS_LABELS, ALL_STATUSES, STATUS_DISPONIBLE, STATUS_PENDIENTE, STATUS_PEDIDO, STATUS_PERDIDO, STATUS_NO_HAY_MAS, STATUS_ULTIMO
from modules.ocr import extract_codes_from_image
from modules.export_utils import export_to_csv
from styles.styles import get_status_color, COLORS

CODE_REGEX = re.compile('^[A-Z]{2,5}\\d{3,9}$')


class StatusBadgeDelegate(QStyledItemDelegate):
    """Delegate para mostrar el status como un badge con color."""
    def paint(self, painter: QPainter, option, index: QModelIndex):
        status = index.data(Qt.UserRole)
        if status:
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)
            color = QColor(get_status_color(status))
            rect = option.rect.adjusted(8, 6, -8, -6)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 10, 10)
            painter.setPen(QPen(QColor('#ffffff')))
            font = QFont()
            font.setBold(True)
            font.setPointSize(9)
            painter.setFont(font)
            label = STATUS_LABELS.get(status, status)
            painter.drawText(rect, Qt.AlignCenter, label)
            painter.restore()
        else:
            super().paint(painter, option, index)


class AutocompleteSearchEdit(QLineEdit):
    """Campo de búsqueda con autocompletado histórico que muestra el status."""
    def __init__(self, repo: CodeRepository, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.setPlaceholderText('Buscar código... (autocompletado activo)')
        self.completer_model = QStringListModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchStartsWith)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(self.completer)
        popup = QListView()
        popup.setSpacing(2)
        popup.setMinimumWidth(350)
        popup.setMinimumHeight(200)
        self.completer.setPopup(popup)
        self.completer.setMaxVisibleItems(10)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._update_completions)
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str):
        self.search_timer.stop()
        if len(text) >= 2:
            self.search_timer.start(150)

    def _update_completions(self):
        text = self.text().strip().upper()
        if len(text) < 2:
            return None
        results = self.repo.search_codes_prefix(text, limit=15)
        items = []
        for r in results:
            status_label = STATUS_LABELS.get(r['status'], r['status'])
            items.append(f"{r['code']}  •  {status_label}")
        self.completer_model.setStringList(items)

    def get_clean_text(self) -> str:
        """Retorna el texto limpio sin el status."""
        text = self.text().strip()
        if '  •  ' in text:
            return text.split('  •  ')[0]
        return text.upper()


class LoginDialog(QDialog):
    """Diálogo de login con usuario y contraseña."""
    USERS = {
        'peon': ('1234', 'peon'),
        'admin': ('admin', 'admin')
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setObjectName('CodeDialog')
        self._old_pos = None
        self.user_role = None
        self.username = None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar
        self.title_bar = QWidget()
        self.title_bar.setObjectName('DialogTitleBar')
        self.title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        self.btn_close = QPushButton('×')
        self.btn_close.setObjectName('DialogCloseButton')
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)
        title_layout.addWidget(self.btn_close)
        
        self.title_label = QLabel('Iniciar Sesión - CodeTrace')
        self.title_label.setObjectName('DialogTitleLabel')
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        main_layout.addWidget(self.title_bar)
        
        # Content
        self.content_widget = QWidget()
        self.content_widget.setObjectName('DialogContent')
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 35, 40, 35)
        self.content_layout.setSpacing(20)
        
        # User input with label
        user_container = QVBoxLayout()
        user_container.setSpacing(6)
        user_label = QLabel('Usuario')
        user_label.setStyleSheet('font-weight: 600; font-size: 13px;')
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText('Ingresa tu usuario')
        self.user_input.setFixedHeight(42)
        self.user_input.setStyleSheet('padding: 10px 14px;')
        user_container.addWidget(user_label)
        user_container.addWidget(self.user_input)
        self.content_layout.addLayout(user_container)
        
        # Password input with label
        pass_container = QVBoxLayout()
        pass_container.setSpacing(6)
        pass_label = QLabel('Contraseña')
        pass_label.setStyleSheet('font-weight: 600; font-size: 13px;')
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText('Ingresa tu contraseña')
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFixedHeight(42)
        self.pass_input.setStyleSheet('padding: 10px 14px;')
        self.pass_input.returnPressed.connect(self._do_login)
        pass_container.addWidget(pass_label)
        pass_container.addWidget(self.pass_input)
        self.content_layout.addLayout(pass_container)
        
        # Error label
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: #ef4444; font-size: 12px; padding: 4px 0;')
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)
        self.content_layout.addWidget(self.error_label)
        
        # Login button
        self.btn_login = QPushButton('Iniciar Sesión')
        self.btn_login.setFixedHeight(44)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet('font-size: 14px; font-weight: 600;')
        self.btn_login.clicked.connect(self._do_login)
        self.content_layout.addWidget(self.btn_login)
        
        main_layout.addWidget(self.content_widget)
        self.setFixedSize(380, 320)
    
    def _do_login(self):
        user = self.user_input.text().strip().lower()
        pwd = self.pass_input.text()
        
        if user in self.USERS:
            expected_pwd, role = self.USERS[user]
            if pwd == expected_pwd:
                self.username = user
                self.user_role = role
                self.accept()
                return
        
        self.error_label.setText('Usuario o contraseña incorrectos')
        self.error_label.setVisible(True)
        self.pass_input.clear()
        self.pass_input.setFocus()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self._old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            delta = QPoint(event.globalPos() - self._old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self._old_pos = None


class CodeDialog(QDialog):
    """Diálogo personalizado con barra de título fina y botón cerrar a la izquierda."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setObjectName('CodeDialog')
        self._old_pos = None
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.title_bar = QWidget()
        self.title_bar.setObjectName('DialogTitleBar')
        self.title_bar.setFixedHeight(36)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        self.btn_close = QPushButton('×')
        self.btn_close.setObjectName('DialogCloseButton')
        self.btn_close.setFixedSize(36, 36)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)
        title_layout.addWidget(self.btn_close)
        self.title_label = QLabel(title)
        self.title_label.setObjectName('DialogTitleLabel')
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        main_layout.addWidget(self.title_bar)
        self.content_widget = QWidget()
        self.content_widget.setObjectName('DialogContent')
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(16)
        main_layout.addWidget(self.content_widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self._old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            delta = QPoint(event.globalPos() - self._old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self._old_pos = None


class CodesTableModel(QAbstractTableModel):
    def __init__(self, repo: CodeRepository) -> None:
        super().__init__()
        self.repo = repo
        self.rows = []
        self.headers = ['#', 'Código', 'Fecha', 'Estado']
        self.annotated_filter = None
        self.search_text = None
        self.status_filter = None
        self.order_by = 'created_at'
        self.order_dir = 'DESC'

    def load(self) -> None:
        self.beginResetModel()
        data = self.repo.list_codes(annotated=self.annotated_filter, duplicates_only=False, search=self.search_text, status=self.status_filter, order_by=self.order_by, order_dir=self.order_dir)
        self.rows = [dict(r) for r in data]
        self.endResetModel()

    def rowCount(self, parent: QModelIndex=QModelIndex()) -> int:
        return len(self.rows)

    def columnCount(self, parent: QModelIndex=QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        row = self.rows[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return index.row() + 1
            elif col == 1:
                return row['code']
            elif col == 2:
                try:
                    dt = datetime.fromisoformat(row['created_at'])
                    return dt.strftime('%d/%m/%Y %H:%M')
                except:
                    return row['created_at']
            elif col == 3:
                return ''
        if role == Qt.UserRole and col == 3:
            return row.get('status', STATUS_DISPONIBLE)
        if role == Qt.TextAlignmentRole and col == 0:
            return Qt.AlignCenter
        if role == Qt.ToolTipRole:
            status = row.get('status', STATUS_DISPONIBLE)
            status_label = STATUS_LABELS.get(status, status)
            return f"Código: {row['code']}\nEstado: {status_label}"
        return QVariant()

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)


class MainWindow(QMainWindow):
    def __init__(self, repo: CodeRepository, home_path, initial_theme: str='Claro', user_role: str='peon', username: str='peon') -> None:
        super().__init__()
        self.repo = repo
        self.theme_change_callback = None
        self.user_role = user_role
        self.username = username
        self.logout_requested = False
        self.imagePath = Path.joinpath(home_path, 'images')
        self.iconApp = QPixmap(str(Path.joinpath(self.imagePath, 'logo_app.png')))
        self.setWindowIcon(QIcon(self.iconApp))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        self._old_pos = None
        self.setWindowTitle('CodeTrace - Gestor de Códigos')
        self.resize(1250, 750)
        self.setMinimumSize(1050, 700)
        self.main_container = QWidget()
        self.main_container.setObjectName('MainContainer')
        self.setCentralWidget(self.main_container)
        root = QVBoxLayout(self.main_container)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)
        self.title_bar = QWidget()
        self.title_bar.setObjectName('TitleBar')
        self.title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 0, 0)
        title_layout.setSpacing(0)
        self.title_icon = QLabel()
        self.title_icon.setPixmap(QPixmap(self.iconApp).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.title_icon.setStyleSheet('margin-right: 8px;')
        self.title_text = QLabel('CodeTrace - Gestor de Códigos')
        self.title_text.setObjectName('TitleLabel')
        title_layout.addWidget(self.title_icon)
        title_layout.addWidget(self.title_text)
        title_layout.addStretch()
        window_icons_path = str(Path.joinpath(home_path, 'images', 'window_controls'))
        self.btn_min = QPushButton()
        self.btn_min.setIcon(QIcon(f'{window_icons_path}/minimize.png'))
        self.btn_min.setIconSize(QSize(30, 30))
        self.btn_min.setObjectName('TitleButton')
        self.btn_min.setFixedSize(40, 40)
        self.btn_min.setCursor(Qt.PointingHandCursor)
        self.btn_max = QPushButton()
        self.btn_max.setIcon(QIcon(f'{window_icons_path}/maximize.png'))
        self.btn_max.setIconSize(QSize(25, 25))
        self.btn_max.setObjectName('TitleButton')
        self.btn_max.setFixedSize(40, 40)
        self.btn_max.setCursor(Qt.PointingHandCursor)
        self.icon_maximize_path = f'{window_icons_path}/maximize.png'
        self.icon_restore_path = f'{window_icons_path}/restore.png'
        self.btn_close = QPushButton()
        self.btn_close.setIcon(QIcon(f'{window_icons_path}/close.png'))
        self.btn_close.setIconSize(QSize(50, 40))
        self.btn_close.setObjectName('CloseButton')
        self.btn_close.setFixedSize(50, 40)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        for btn in [self.btn_min, self.btn_max, self.btn_close]:
            title_layout.addWidget(btn)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self._toggle_max_restore)
        self.btn_close.clicked.connect(self.close)
        root.addWidget(self.title_bar)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(20, 20, 20, 20)
        root.addWidget(content_widget)
        header = QHBoxLayout()
        header_icon = QLabel()
        icon_logo_path = str(Path.joinpath(home_path, 'images', 'icon_logo.png'))
        if Path(icon_logo_path).exists():
            header_icon.setPixmap(QPixmap(icon_logo_path).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(header_icon)
        self.title_label = QLabel('CodeTrace')
        self.title_label.setObjectName('MainTitle')
        self.title_label.setStyleSheet('''
            font-size: 24px;
            font-weight: bold;
            padding: 8px 0;
            margin-left: 8px;
        ''')
        iconLabel = QLabel()
        iconLabel.setPixmap(self.iconApp.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(iconLabel)
        header.addWidget(self.title_label)
        header.addStretch()
        theme_icon = QLabel()
        icon_theme_path = str(Path.joinpath(home_path, 'images', 'icon_theme.png'))
        if Path(icon_theme_path).exists():
            theme_icon.setPixmap(QPixmap(icon_theme_path).scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(theme_icon)
        theme_label = QLabel('Tema')
        theme_label.setStyleSheet('margin-left: 4px;')
        header.addWidget(theme_label)
        self.theme_toggle = QComboBox()
        self.theme_toggle.setObjectName('ThemeCombo')
        self.theme_toggle.addItems(['Claro', 'Oscuro'])
        self.theme_toggle.setFixedWidth(100)
        self.theme_toggle.setMaxVisibleItems(2)
        self.theme_toggle.view().setFixedWidth(98)
        header.addWidget(self.theme_toggle)
        content_layout.addLayout(header)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        icon_size = QSize(22, 22)
        actions_path = str(Path.joinpath(home_path, 'images', 'actions'))
        self.btn_add = QPushButton('Agregar')
        self.btn_add.setIcon(QIcon(f'{actions_path}/add.png'))
        self.btn_add.setIconSize(icon_size)
        self.btn_edit = QPushButton('Editar')
        self.btn_edit.setIcon(QIcon(f'{actions_path}/edit.png'))
        self.btn_edit.setIconSize(icon_size)
        self.btn_delete = QPushButton('Borrar')
        self.btn_delete.setIcon(QIcon(f'{actions_path}/delete.png'))
        self.btn_delete.setIconSize(icon_size)
        self.btn_import = QPushButton('Importar')
        self.btn_import.setIcon(QIcon(f'{actions_path}/import_txt.png'))
        self.btn_import.setIconSize(icon_size)
        self.btn_import_img = QPushButton('OCR Imagen')
        self.btn_import_img.setIcon(QIcon(f'{actions_path}/import_image.png'))
        self.btn_import_img.setIconSize(icon_size)
        self.btn_export_csv = QPushButton('Exportar CSV')
        self.btn_export_csv.setIcon(QIcon(f'{actions_path}/export.png'))
        self.btn_export_csv.setIconSize(icon_size)
        for btn in [self.btn_add, self.btn_edit, self.btn_delete, self.btn_import, self.btn_import_img, self.btn_export_csv]:
            toolbar.addWidget(btn)
        toolbar.addStretch()
        # User indicator with logout button
        self.user_indicator = QWidget()
        user_layout = QHBoxLayout(self.user_indicator)
        user_layout.setContentsMargins(8, 4, 8, 4)
        user_layout.setSpacing(6)
        self.user_icon_label = QLabel()
        user_icon_path = str(Path.joinpath(home_path, 'images', f'user_{self.user_role}.png'))
        if Path(user_icon_path).exists():
            self.user_icon_label.setPixmap(QPixmap(user_icon_path).scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        user_layout.addWidget(self.user_icon_label)
        self.user_name_label = QLabel(self.username.capitalize())
        self.user_name_label.setStyleSheet('font-weight: bold; font-size: 13px;')
        user_layout.addWidget(self.user_name_label)
        # Logout button
        self.btn_logout = QPushButton('✕')
        self.btn_logout.setObjectName('LogoutButton')
        self.btn_logout.setFixedSize(24, 24)
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setToolTip('Cerrar sesión')
        self.btn_logout.setStyleSheet('''
            QPushButton#LogoutButton {
                background: rgba(239, 68, 68, 0.15);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 12px;
                color: #ef4444;
                font-size: 12px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton#LogoutButton:hover {
                background: #ef4444;
                color: white;
            }
        ''')
        user_layout.addWidget(self.btn_logout)
        toolbar.addWidget(self.user_indicator)
        content_layout.addLayout(toolbar)
        self.filter_frame = QFrame()
        self.filter_frame.setObjectName('FilterFrame')
        filters = QHBoxLayout(self.filter_frame)
        filters.setSpacing(16)
        self.chk_anotados = QCheckBox('Editados')
        self.chk_no_anotados = QCheckBox('No Editados')
        filters.addWidget(self.chk_anotados)
        filters.addWidget(self.chk_no_anotados)
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {COLORS['border_dark']};")
        filters.addWidget(sep)
        filters.addWidget(QLabel('Estado:'))
        self.status_filter = QComboBox()
        self.status_filter.addItem('Todos', None)
        for st in ALL_STATUSES:
            self.status_filter.addItem(STATUS_LABELS[st], st)
        self.status_filter.setFixedWidth(140)
        filters.addWidget(self.status_filter)
        filters.addStretch()
        filters.addWidget(QLabel('Orden:'))
        self.sort = QComboBox()
        self.sort.addItems(['Fecha ↓', 'Fecha ↑', 'Código A-Z', 'Código Z-A', 'Estado'])
        self.sort.setFixedWidth(120)
        filters.addWidget(self.sort)
        self.search = AutocompleteSearchEdit(repo)
        self.search.setFixedWidth(280)
        filters.addWidget(self.search)
        content_layout.addWidget(self.filter_frame)
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 12px;
            padding: 4px 8px;
        """)
        content_layout.addWidget(self.stats_label)
        splitter = QSplitter()
        self.table = QTableView()
        self.table_model = CodesTableModel(repo)
        self.table.setModel(self.table_model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.status_delegate = StatusBadgeDelegate()
        self.table.setItemDelegateForColumn(3, self.status_delegate)
        hh = self.table.horizontalHeader()
        try:
            from PyQt5.QtWidgets import QHeaderView
            hh.setStretchLastSection(False)
            hh.setSectionResizeMode(0, QHeaderView.Fixed)
            hh.setSectionResizeMode(1, QHeaderView.Stretch)
            hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            hh.setSectionResizeMode(3, QHeaderView.Fixed)
        except Exception:
            pass
        right_panel = QWidget()
        right_panel.setObjectName('StatsPanel')
        right_panel.setMinimumWidth(250)
        right_panel.setMaximumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(16)
        stats_title = QLabel('Estadísticas')
        stats_title.setProperty('heading', True)
        right_layout.addWidget(stats_title)
        self.stats_panel = QGridLayout()
        self.stats_widgets = {}
        for i, (st, label) in enumerate(STATUS_LABELS.items()):
            color = get_status_color(st)
            stat_label = QLabel(f'{label}: 0')
            stat_label.setStyleSheet(f"""
                color: {color};
                font-weight: bold;
                padding: 8px 12px;
                background: {COLORS['bg_card']};
                border-radius: 8px;
                border-left: 3px solid {color};
            """)
            self.stats_widgets[st] = stat_label
            self.stats_panel.addWidget(stat_label, i // 2, i % 2)
        stats_widget = QWidget()
        stats_widget.setLayout(self.stats_panel)
        right_layout.addWidget(stats_widget)
        right_layout.addStretch()
        splitter.addWidget(self.table)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([850, 320])
        content_layout.addWidget(splitter, 1)
        self.sizegrip = QSizeGrip(self)
        self.sizegrip.setFixedSize(16, 16)
        self.btn_import.clicked.connect(self.on_import_file)
        self.btn_import_img.clicked.connect(self.on_import_img)
        self.btn_export_csv.clicked.connect(self.on_export_csv)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_logout.clicked.connect(self.on_logout)
        self.theme_toggle.currentTextChanged.connect(self.on_theme_changed)
        self.chk_anotados.stateChanged.connect(self.on_filters_changed)
        self.chk_no_anotados.stateChanged.connect(self.on_filters_changed)
        self.status_filter.currentIndexChanged.connect(self.on_filters_changed)
        self.search.textChanged.connect(self.on_filters_changed)
        self.sort.currentTextChanged.connect(self.on_sort_changed)
        self.table.doubleClicked.connect(self.on_edit)
        self.table_model.load()
        self._update_column_widths()
        self._update_stats()
        self.theme_toggle.setCurrentText('Claro' if initial_theme == 'Claro' else 'Oscuro')
        # Apply role-based access control
        self._apply_role_permissions()

    def _toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_max.setIcon(QIcon(self.icon_maximize_path))
        else:
            self.showMaximized()
            self.btn_max.setIcon(QIcon(self.icon_restore_path))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.rect().contains(event.pos()):
            self._old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            delta = QPoint(event.globalPos() - self._old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self._old_pos = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sizegrip.move(self.width() - self.sizegrip.width(), self.height() - self.sizegrip.height())

    def _update_column_widths(self):
        """Ajusta el ancho de las columnas de la tabla."""
        row_count = self.table_model.rowCount()
        # Calculate width based on digit count: 1-9=35px, 10-99=45px, 100-999=55px, etc.
        if row_count < 10:
            id_width = 35
        elif row_count < 100:
            id_width = 45
        elif row_count < 1000:
            id_width = 55
        else:
            id_width = 65
        self.table.setColumnWidth(0, id_width)
        self.table.setColumnWidth(2, 140)
        self.table.setColumnWidth(3, 110)

    def _update_stats(self):
        """Actualiza las estadísticas en el panel lateral."""
        stats = self.repo.stats()
        total = stats.get('total', 0)
        for st, label in STATUS_LABELS.items():
            count = stats.get(st, 0)
            color = get_status_color(st)
            self.stats_widgets[st].setText(f'{label}: {count}')
        self.stats_label.setText(f"Total: {total} códigos  |  Editados: {stats.get('annotated', 0)}")

    def on_import_file(self) -> None:
        """Importa códigos desde archivo TXT o CSV."""
        path, _ = QFileDialog.getOpenFileName(self, 'Seleccionar archivo', '', 'Archivos soportados (*.txt *.csv);;Text Files (*.txt);;CSV Files (*.csv)')
        if not path:
            return None
        p = Path(path)
        ext = p.suffix.lower()
        items = []
        if ext == '.csv':
            items = self._import_csv(p)
        else:
            items = self._import_txt(p)
        if not items:
            QMessageBox.information(self, 'Importación', 'No se encontraron códigos válidos.')
            return None
        codes_to_import = [item[0] for item in items]
        existing = self.repo.codes_exist(codes_to_import)
        if existing:
            items = [item for item in items if item[0] not in existing]
            dup_list = ', '.join(existing[:10])
            if len(existing) > 10:
                dup_list += f'... y {len(existing) - 10} más'
            QMessageBox.warning(self, 'Códigos duplicados', f'Los siguientes códigos ya existen y no se importarán:\n\n{dup_list}')
        if not items:
            QMessageBox.information(self, 'Importación', 'Todos los códigos ya existían.')
            return None
        self.repo.add_codes(items)
        self.table_model.load()
        self._update_column_widths()
        self._update_stats()
        QMessageBox.information(self, 'Importación exitosa', f'Importados {len(items)} códigos.')

    def _import_txt(self, path: Path) -> list:
        """Importa códigos desde un archivo TXT (un código por línea)."""
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
        items = []
        for ln in lines:
            s = ln.strip().upper()
            if not s:
                continue
            if not CODE_REGEX.match(s):
                continue
            items.append((s, False, datetime.utcnow(), STATUS_DISPONIBLE))
        return items

    def _import_csv(self, path: Path) -> list:
        """Importa códigos desde un archivo CSV exportado por CodeTrace.
        Detecta automáticamente el delimitador (coma o punto y coma).
        """
        import csv
        items = []
        label_to_status = {
            'disponible': STATUS_DISPONIBLE,
            'pendiente': STATUS_PENDIENTE,
            'pedido': STATUS_PEDIDO,
            'perdido': STATUS_PERDIDO,
            'no hay más': STATUS_NO_HAY_MAS,
            'no hay mas': STATUS_NO_HAY_MAS,
            'último': STATUS_ULTIMO,
            'ultimo': STATUS_ULTIMO
        }
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                sample = f.read(1024)
                f.seek(0)
                # Auto-detect delimiter
                if sample.count(',') > sample.count(';'):
                    delimiter = ','
                else:
                    delimiter = ';'
                reader = csv.reader(f, delimiter=delimiter)
                header = next(reader, None)
                if not header:
                    return []
                header_lower = [h.strip().lower() for h in header]
                code_idx = None
                for i, h in enumerate(header_lower):
                    if 'código' in h or 'codigo' in h or 'code' in h:
                        code_idx = i
                        break
                if code_idx is None:
                    code_idx = 0
                status_idx = None
                for i, h in enumerate(header_lower):
                    if 'estado' in h or 'status' in h:
                        status_idx = i
                        break
                if status_idx is None:
                    status_idx = 1
                usado_idx = None
                for i, h in enumerate(header_lower):
                    if 'usado' in h or 'editado' in h:
                        usado_idx = i
                        break
                for row in reader:
                    if not row or len(row) <= code_idx:
                        continue
                    code = row[code_idx].strip().upper()
                    if not code or not CODE_REGEX.match(code):
                        continue
                    status_text = row[status_idx].strip().lower() if status_idx is not None and len(row) > status_idx else ''
                    status = label_to_status.get(status_text, STATUS_DISPONIBLE)
                    editado = False
                    if usado_idx is not None and len(row) > usado_idx:
                        usado_text = row[usado_idx].strip().lower()
                        editado = usado_text in ['sí', 'si', 'yes', '1', 'true']
                    items.append((code, editado, datetime.utcnow(), status))
        except Exception as e:
            QMessageBox.warning(self, 'Error CSV', f'Error al leer CSV: {e}')
            return []
        return items

    def on_import_img(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, 'Seleccionar imágenes', '', 'Images (*.png *.jpg *.jpeg)')
        if not paths:
            return None
        total = 0
        all_duplicates = []
        for path in paths:
            p = Path(path)
            try:
                raw_items = extract_codes_from_image(p)
                items = [(code, ann, dt, STATUS_DISPONIBLE) for code, ann, dt in raw_items]
            except Exception as e:
                QMessageBox.critical(self, 'Error OCR', f'Error en OCR: {e}')
                continue
            if items:
                codes_to_import = [item[0] for item in items]
                existing = self.repo.codes_exist(codes_to_import)
                if existing:
                    all_duplicates.extend(existing)
                    items = [item for item in items if item[0] not in existing]
                if items:
                    self.repo.add_codes(items)
                    total += len(items)
        self.table_model.load()
        self._update_column_widths()
        self._update_stats()
        if all_duplicates:
            dup_list = ', '.join(all_duplicates[:10])
            if len(all_duplicates) > 10:
                dup_list += f'... y {len(all_duplicates) - 10} más'
            QMessageBox.warning(self, 'Códigos duplicados', f'Los siguientes códigos ya existían y no se importaron:\n\n{dup_list}')
        if total > 0:
            QMessageBox.information(self, 'OCR exitoso', f'Importados {total} códigos desde imágenes.')
        elif not all_duplicates:
            QMessageBox.information(self, 'OCR sin resultados', 'No se detectaron códigos válidos.')

    def on_export_csv(self) -> None:
        """Exporta los datos actuales de la tabla a CSV."""
        export_to_csv(self, self.table_model.rows, STATUS_LABELS)

    def _apply_role_permissions(self) -> None:
        """Aplica permisos según el rol del usuario."""
        if self.user_role == 'peon':
            # Peon: solo puede buscar y ver, no puede modificar nada
            self.btn_add.setEnabled(False)
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_import.setEnabled(False)
            self.btn_import_img.setEnabled(False)
            self.btn_export_csv.setEnabled(False)
            # Disable double-click edit for peon
            self.table.doubleClicked.disconnect(self.on_edit)

    def on_logout(self) -> None:
        """Cierra la sesión actual y muestra el diálogo de login."""
        ok = QMessageBox.question(self, 'Cerrar Sesión', '¿Deseas cerrar la sesión actual?')
        if ok == QMessageBox.Yes:
            # Signal to main.py to restart with login
            self.logout_requested = True
            self.close()

    def on_theme_changed(self, text: str) -> None:
        if callable(self.theme_change_callback):
            theme = 'Oscuro' if 'Oscuro' in text else 'Claro'
            self.theme_change_callback(theme)

    def _selected_row(self) -> Optional[int]:
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return None
        return sel[0].row()

    def on_add(self) -> None:
        dlg = CodeDialog('Agregar código', self)
        dlg.setMinimumWidth(380)
        fl = QFormLayout()
        fl.setSpacing(12)
        le = QLineEdit()
        le.setPlaceholderText('Ej: TY568467')
        status_combo = QComboBox()
        for st in ALL_STATUSES:
            status_combo.addItem(STATUS_LABELS[st], st)
        cb = QCheckBox('Marcar como editado')
        fl.addRow('Código:', le)
        fl.addRow('Estado:', status_combo)
        fl.addRow('', cb)
        dlg.content_layout.addLayout(fl)
        btns = QHBoxLayout()
        btns.setSpacing(10)
        b_ok = QPushButton('Guardar')
        b_cancel = QPushButton('Cancelar')
        b_cancel.setProperty('secondary', True)
        btns.addWidget(b_ok)
        btns.addWidget(b_cancel)
        dlg.content_layout.addLayout(btns)
        b_ok.clicked.connect(dlg.accept)
        b_cancel.clicked.connect(dlg.reject)
        if dlg.exec_() == QDialog.Accepted:
            s = le.text().strip().upper()
            if not s or not CODE_REGEX.match(s):
                QMessageBox.warning(self, 'Validación', 'Código inválido. Formato: 2-5 letras + 3-9 números')
                return None
            existing = self.repo.codes_exist([s])
            if existing:
                QMessageBox.warning(self, 'Código duplicado', f'El código {s} ya existe en la base de datos.')
                return None
            status = status_combo.currentData()
            self.repo.add_codes([(s, cb.isChecked(), datetime.utcnow(), status)])
            self.table_model.load()
            self._update_column_widths()
            self._update_stats()

    def on_edit(self, index=None) -> None:
        r = self._selected_row()
        if r is None:
            QMessageBox.information(self, 'Edición', 'Selecciona una fila para editar.')
            return None
        row = self.table_model.rows[r]
        dlg = CodeDialog('Editar código', self)
        dlg.setMinimumWidth(380)
        fl = QFormLayout()
        fl.setSpacing(12)
        le = QLineEdit(row['code'])
        status_combo = QComboBox()
        current_status = row.get('status', STATUS_DISPONIBLE)
        for st in ALL_STATUSES:
            status_combo.addItem(STATUS_LABELS[st], st)
            if st == current_status:
                status_combo.setCurrentIndex(status_combo.count() - 1)
        cb = QCheckBox('Marcar como editado')
        cb.setChecked(bool(row['annotated']))
        fl.addRow('Código:', le)
        fl.addRow('Estado:', status_combo)
        fl.addRow('', cb)
        dlg.content_layout.addLayout(fl)
        btns = QHBoxLayout()
        btns.setSpacing(10)
        b_ok = QPushButton('Guardar')
        b_cancel = QPushButton('Cancelar')
        b_cancel.setProperty('secondary', True)
        btns.addWidget(b_ok)
        btns.addWidget(b_cancel)
        dlg.content_layout.addLayout(btns)
        b_ok.clicked.connect(dlg.accept)
        b_cancel.clicked.connect(dlg.reject)
        if dlg.exec_() == QDialog.Accepted:
            s = le.text().strip().upper()
            if not s or not CODE_REGEX.match(s):
                QMessageBox.warning(self, 'Validación', 'Código inválido. Formato: 2-5 letras + 3-9 números')
                return None
            status = status_combo.currentData()
            self.repo.update_code(row['id'], s, cb.isChecked(), status)
            self.table_model.load()
            self._update_column_widths()
            self._update_stats()

    def on_delete(self) -> None:
        r = self._selected_row()
        if r is None:
            QMessageBox.information(self, 'Borrar', 'Selecciona una fila para borrar.')
            return None
        row = self.table_model.rows[r]
        ok = QMessageBox.question(self, 'Confirmar', f"¿Eliminar código {row['code']}?")
        if ok == QMessageBox.Yes:
            self.repo.delete_code(row['id'])
            self.table_model.load()
            self._update_column_widths()
            self._update_stats()

    def on_filters_changed(self) -> None:
        if self.chk_anotados.isChecked() and self.chk_no_anotados.isChecked():
            self.table_model.annotated_filter = None
        elif self.chk_anotados.isChecked():
            self.table_model.annotated_filter = True
        elif self.chk_no_anotados.isChecked():
            self.table_model.annotated_filter = False
        else:
            self.table_model.annotated_filter = None
        self.table_model.status_filter = self.status_filter.currentData()
        search_text = self.search.get_clean_text() if hasattr(self.search, 'get_clean_text') else self.search.text().strip().upper()
        self.table_model.search_text = search_text or None
        self.table_model.load()
        self._update_column_widths()

    def on_sort_changed(self, text: str) -> None:
        if 'Fecha ↓' in text:
            self.table_model.order_by = 'created_at'
            self.table_model.order_dir = 'DESC'
        elif 'Fecha ↑' in text:
            self.table_model.order_by = 'created_at'
            self.table_model.order_dir = 'ASC'
        elif 'A-Z' in text:
            self.table_model.order_by = 'code'
            self.table_model.order_dir = 'ASC'
        elif 'Z-A' in text:
            self.table_model.order_by = 'code'
            self.table_model.order_dir = 'DESC'
        elif 'Estado' in text:
            self.table_model.order_by = 'status'
            self.table_model.order_dir = 'ASC'
        self.table_model.load()
        self._update_column_widths()
