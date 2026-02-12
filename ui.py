import re
from typing import List, Optional
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, QStringListModel, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLineEdit,
    QPushButton, QLabel, QCheckBox, QComboBox, QFileDialog, QMessageBox, 
    QSplitter, QDialog, QFormLayout, QCompleter, QListView, QStyledItemDelegate,
    QFrame, QGridLayout
)
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush, QPen, QFont
from pathlib import Path
from datetime import datetime

from repository import CodeRepository, STATUS_LABELS, ALL_STATUSES, STATUS_DISPONIBLE
from ocr import extract_codes_from_image
from styles import get_status_color, COLORS

CODE_REGEX = re.compile(r"^[A-Z]{2,5}\d{3,9}$")

class StatusBadgeDelegate(QStyledItemDelegate):
    """Delegate para mostrar el status como un badge con color."""
    def paint(self, painter: QPainter, option, index: QModelIndex):
        status = index.data(Qt.UserRole)
        if status:
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Fondo del badge
            color = QColor(get_status_color(status))
            rect = option.rect.adjusted(8, 6, -8, -6)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 10, 10)
            
            # Texto
            painter.setPen(QPen(QColor("#ffffff")))
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
        self.setPlaceholderText("🔍 Buscar código... (autocompletado activo)")
        
        # Configurar completer
        self.completer_model = QStringListModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchStartsWith)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(self.completer)
        
        # Popup personalizado
        popup = QListView()
        popup.setSpacing(2)
        self.completer.setPopup(popup)
        
        # Timer para debounce
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._update_completions)
        
        self.textChanged.connect(self._on_text_changed)
        
    def _on_text_changed(self, text: str):
        self.search_timer.stop()
        if len(text) >= 2:
            self.search_timer.start(150)  # 150ms debounce
    
    def _update_completions(self):
        text = self.text().strip().upper()
        if len(text) < 2:
            return
        
        results = self.repo.search_codes_prefix(text, limit=15)
        # Crear lista con código y status
        items = []
        for r in results:
            status_label = STATUS_LABELS.get(r["status"], r["status"])
            items.append(f"{r['code']}  •  {status_label}")
        
        self.completer_model.setStringList(items)
    
    def get_clean_text(self) -> str:
        """Retorna el texto limpio sin el status."""
        text = self.text().strip()
        if "  •  " in text:
            return text.split("  •  ")[0]
        return text.upper()


class CodesTableModel(QAbstractTableModel):
    def __init__(self, repo: CodeRepository) -> None:
        super().__init__()
        self.repo = repo
        self.rows: List[dict] = []
        self.headers = ["✓", "Código", "Fecha", "Estado", "Status"]
        self.annotated_filter: Optional[bool] = None
        self.duplicates_only: Optional[bool] = None
        self.search_text: Optional[str] = None
        self.status_filter: Optional[str] = None
        self.order_by = "created_at"
        self.order_dir = "DESC"

    def load(self) -> None:
        self.beginResetModel()
        data = self.repo.list_codes(
            annotated=self.annotated_filter,
            duplicates_only=bool(self.duplicates_only),
            search=self.search_text,
            status=self.status_filter,
            order_by=self.order_by,
            order_dir=self.order_dir
        )
        self.rows = [dict(r) for r in data]
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        row = self.rows[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 1:
                return row["code"]
            if col == 2:
                # Formatear fecha más legible
                try:
                    dt = datetime.fromisoformat(row["created_at"])
                    return dt.strftime("%d/%m/%Y %H:%M")
                except:
                    return row["created_at"]
            if col == 3:
                return "✅ Usado" if row["annotated"] else ""
            if col == 4:
                return ""  # El status se muestra con el delegate
        if role == Qt.UserRole and col == 4:
            # Retornar el status para el delegate
            return row.get("status", STATUS_DISPONIBLE)
        if role == Qt.CheckStateRole and col == 0:
            return Qt.Checked if row["annotated"] else Qt.Unchecked
        if role == Qt.ToolTipRole:
            status = row.get("status", STATUS_DISPONIBLE)
            status_label = STATUS_LABELS.get(status, status)
            return f"Código: {row['code']}\nStatus: {status_label}\nDuplicado: {'Sí' if row['duplicate'] else 'No'}"
        return QVariant()

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if not index.isValid():
            return False
        if index.column() == 0 and role == Qt.CheckStateRole:
            row = self.rows[index.row()]
            checked = value == Qt.Checked
            self.repo.update_annotated(row["id"], checked)
            row["annotated"] = int(checked)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole, Qt.DisplayRole])
            return True
        return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)

class MainWindow(QMainWindow):
    def __init__(self, repo: CodeRepository, initial_theme: str = "Oscuro") -> None:
        super().__init__()
        self.repo = repo
        self.theme_change_callback = None
        self.setWindowTitle("📦 CodeTrace - Gestor de Códigos")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(16)
        root.setContentsMargins(20, 20, 20, 20)

        # === HEADER ===
        header = QHBoxLayout()
        title_label = QLabel("📦 CodeTrace")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            padding: 8px 0;
        """)
        header.addWidget(title_label)
        header.addStretch()
        
        self.theme_toggle = QComboBox()
        self.theme_toggle.addItems(["🌙 Oscuro", "☀️ Claro"])
        self.theme_toggle.setFixedWidth(130)
        header.addWidget(QLabel("🎨 Tema"))
        header.addWidget(self.theme_toggle)
        root.addLayout(header)

        # === TOOLBAR ===
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        self.btn_add = QPushButton("➕ Agregar")
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_delete = QPushButton("🗑️ Borrar")
        self.btn_import_txt = QPushButton("📄 Importar .txt")
        self.btn_import_img = QPushButton("🖼️ OCR Imagen")
        self.btn_clear = QPushButton("⚠️ Vaciar")
        
        for btn in [self.btn_add, self.btn_edit, self.btn_delete, 
                    self.btn_import_txt, self.btn_import_img]:
            toolbar.addWidget(btn)
        
        toolbar.addStretch()
        toolbar.addWidget(self.btn_clear)
        root.addLayout(toolbar)

        # === FILTROS ===
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                padding: 8px;
            }}
        """)
        filters = QHBoxLayout(filter_frame)
        filters.setSpacing(16)
        
        # Filtros de checkbox
        self.chk_anotados = QCheckBox("✅ Usados")
        self.chk_no_anotados = QCheckBox("⬜ No usados")
        self.chk_duplicados = QCheckBox("🔄 Duplicados")
        
        filters.addWidget(self.chk_anotados)
        filters.addWidget(self.chk_no_anotados)
        filters.addWidget(self.chk_duplicados)
        
        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {COLORS['border_dark']};")
        filters.addWidget(sep)
        
        # Filtro de status
        filters.addWidget(QLabel("🏷️ Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos", None)
        for st in ALL_STATUSES:
            self.status_filter.addItem(STATUS_LABELS[st], st)
        self.status_filter.setFixedWidth(140)
        filters.addWidget(self.status_filter)
        
        filters.addStretch()
        
        # Orden
        filters.addWidget(QLabel("↕️ Orden:"))
        self.sort = QComboBox()
        self.sort.addItems(["Fecha ↓", "Fecha ↑", "Código A-Z", "Código Z-A", "Status"])
        self.sort.setFixedWidth(120)
        filters.addWidget(self.sort)
        
        # Búsqueda con autocompletado
        self.search = AutocompleteSearchEdit(repo)
        self.search.setFixedWidth(280)
        filters.addWidget(self.search)
        
        root.addWidget(filter_frame)

        # === STATS BAR ===
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 12px;
            padding: 4px 8px;
        """)
        root.addWidget(self.stats_label)

        # === CONTENT ===
        splitter = QSplitter()
        
        # Tabla
        self.table = QTableView()
        self.table_model = CodesTableModel(repo)
        self.table.setModel(self.table_model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        
        # Delegate para status
        self.status_delegate = StatusBadgeDelegate()
        self.table.setItemDelegateForColumn(4, self.status_delegate)
        
        hh = self.table.horizontalHeader()
        try:
            from PyQt5.QtWidgets import QHeaderView
            hh.setStretchLastSection(False)
            hh.setSectionResizeMode(0, QHeaderView.Fixed)
            hh.setSectionResizeMode(1, QHeaderView.Stretch)
            hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            hh.setSectionResizeMode(4, QHeaderView.Fixed)
        except Exception:
            pass

        # Panel derecho con estadísticas
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(16)
        
        preview_title = QLabel("🖼️ Vista previa")
        preview_title.setProperty("heading", True)
        right_layout.addWidget(preview_title)
        
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumWidth(280)
        self.preview.setMinimumHeight(200)
        self.preview.setStyleSheet(f"""
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border_dark']};
            border-radius: 12px;
        """)
        right_layout.addWidget(self.preview)
        
        # Stats panel
        stats_title = QLabel("📊 Estadísticas")
        stats_title.setProperty("heading", True)
        right_layout.addWidget(stats_title)
        
        self.stats_panel = QGridLayout()
        self.stats_widgets = {}
        for i, (st, label) in enumerate(STATUS_LABELS.items()):
            color = get_status_color(st)
            stat_label = QLabel(f"🟢 {label}: 0")
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
        splitter.setSizes([850, 350])
        root.addWidget(splitter)

        # === CONNECTIONS ===
        self.btn_import_txt.clicked.connect(self.on_import_txt)
        self.btn_import_img.clicked.connect(self.on_import_img)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.theme_toggle.currentTextChanged.connect(self.on_theme_changed)
        self.chk_anotados.stateChanged.connect(self.on_filters_changed)
        self.chk_no_anotados.stateChanged.connect(self.on_filters_changed)
        self.chk_duplicados.stateChanged.connect(self.on_filters_changed)
        self.status_filter.currentIndexChanged.connect(self.on_filters_changed)
        self.search.textChanged.connect(self.on_filters_changed)
        self.sort.currentTextChanged.connect(self.on_sort_changed)
        self.table.doubleClicked.connect(self.on_edit)

        # Cargar datos iniciales
        self.table_model.load()
        self._update_column_widths()
        self._update_stats()
        self.theme_toggle.setCurrentText("🌙 Oscuro" if initial_theme == "Oscuro" else "☀️ Claro")
    
    def _update_column_widths(self):
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(4, 120)

    def _update_stats(self):
        """Actualiza las estadísticas en el panel lateral."""
        stats = self.repo.stats()
        total = stats.get("total", 0)
        
        for st, label in STATUS_LABELS.items():
            count = stats.get(st, 0)
            color = get_status_color(st)
            self.stats_widgets[st].setText(f"{label}: {count}")
        
        self.stats_label.setText(
            f"📊 Total: {total} códigos  |  "
            f"✅ Usados: {stats.get('annotated', 0)}  |  "
            f"🔄 Duplicados: {stats.get('duplicates', 0)}"
        )

    def on_import_txt(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo .txt", "", "Text Files (*.txt)")
        if not path:
            return
        p = Path(path)
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        items = []
        for ln in lines:
            s = ln.strip().upper()
            if not s:
                continue
            if not CODE_REGEX.match(s):
                continue
            items.append((s, False, datetime.utcnow(), STATUS_DISPONIBLE))
        if not items:
            QMessageBox.information(self, "Importación", "No se encontraron códigos válidos.")
            return
        self.repo.add_codes(items)
        self.table_model.load()
        self._update_column_widths()
        self._update_stats()
        QMessageBox.information(self, "✅ Importación", f"Importados {len(items)} códigos.")

    def on_import_img(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Seleccionar imágenes", "", "Images (*.png *.jpg *.jpeg)")
        if not paths:
            return
        total = 0
        first = None
        for path in paths:
            p = Path(path)
            try:
                raw_items = extract_codes_from_image(p)
                # Agregar status por defecto
                items = [(code, ann, dt, STATUS_DISPONIBLE) for code, ann, dt in raw_items]
            except Exception as e:
                QMessageBox.critical(self, "❌ OCR", f"Error en OCR: {e}")
                continue
            if items:
                self.repo.add_codes(items)
                total += len(items)
                if first is None:
                    first = p
        self.table_model.load()
        self._update_column_widths()
        self._update_stats()
        if first is not None:
            pix = QPixmap(str(first))
            self.preview.setPixmap(pix.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if total > 0:
            QMessageBox.information(self, "✅ OCR", f"Importados {total} códigos desde imágenes.")
        else:
            QMessageBox.information(self, "⚠️ OCR", "No se detectaron códigos válidos.")

    def on_clear(self) -> None:
        ok = QMessageBox.question(self, "⚠️ Confirmar", "¿Eliminar TODOS los códigos? Esta acción no se puede deshacer.")
        if ok == QMessageBox.Yes:
            self.repo.remove_all()
            self.table_model.load()
            self._update_stats()

    def on_theme_changed(self, text: str) -> None:
        if callable(self.theme_change_callback):
            theme = "Oscuro" if "Oscuro" in text else "Claro"
            self.theme_change_callback(theme)

    def _selected_row(self) -> Optional[int]:
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return None
        return sel[0].row()

    def on_add(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("➕ Agregar código")
        dlg.setMinimumWidth(350)
        fl = QFormLayout(dlg)
        fl.setSpacing(16)
        fl.setContentsMargins(20, 20, 20, 20)
        
        le = QLineEdit()
        le.setPlaceholderText("Ej: TY568467")
        
        status_combo = QComboBox()
        for st in ALL_STATUSES:
            status_combo.addItem(STATUS_LABELS[st], st)
        
        cb = QCheckBox("Marcar como usado")
        
        fl.addRow("🏷️ Código:", le)
        fl.addRow("📌 Status:", status_combo)
        fl.addRow("", cb)
        
        btns = QHBoxLayout()
        btns.setSpacing(10)
        b_ok = QPushButton("✅ Guardar")
        b_cancel = QPushButton("❌ Cancelar")
        btns.addWidget(b_ok)
        btns.addWidget(b_cancel)
        fl.addRow(btns)
        
        b_ok.clicked.connect(dlg.accept)
        b_cancel.clicked.connect(dlg.reject)
        
        if dlg.exec_() == QDialog.Accepted:
            s = le.text().strip().upper()
            if not s or not CODE_REGEX.match(s):
                QMessageBox.warning(self, "⚠️ Validación", "Código inválido. Formato: 2-5 letras + 3-9 números")
                return
            status = status_combo.currentData()
            self.repo.add_codes([(s, cb.isChecked(), datetime.utcnow(), status)])
            self.table_model.load()
            self._update_column_widths()
            self._update_stats()

    def on_edit(self, index=None) -> None:
        r = self._selected_row()
        if r is None:
            QMessageBox.information(self, "✏️ Edición", "Selecciona una fila para editar.")
            return
        row = self.table_model.rows[r]
        
        dlg = QDialog(self)
        dlg.setWindowTitle("✏️ Editar código")
        dlg.setMinimumWidth(350)
        fl = QFormLayout(dlg)
        fl.setSpacing(16)
        fl.setContentsMargins(20, 20, 20, 20)
        
        le = QLineEdit(row["code"])
        
        status_combo = QComboBox()
        current_status = row.get("status", STATUS_DISPONIBLE)
        for st in ALL_STATUSES:
            status_combo.addItem(STATUS_LABELS[st], st)
            if st == current_status:
                status_combo.setCurrentIndex(status_combo.count() - 1)
        
        cb = QCheckBox("Marcar como usado")
        cb.setChecked(bool(row["annotated"]))
        
        fl.addRow("🏷️ Código:", le)
        fl.addRow("📌 Status:", status_combo)
        fl.addRow("", cb)
        
        btns = QHBoxLayout()
        btns.setSpacing(10)
        b_ok = QPushButton("✅ Guardar")
        b_cancel = QPushButton("❌ Cancelar")
        btns.addWidget(b_ok)
        btns.addWidget(b_cancel)
        fl.addRow(btns)
        
        b_ok.clicked.connect(dlg.accept)
        b_cancel.clicked.connect(dlg.reject)
        
        if dlg.exec_() == QDialog.Accepted:
            s = le.text().strip().upper()
            if not s or not CODE_REGEX.match(s):
                QMessageBox.warning(self, "⚠️ Validación", "Código inválido. Formato: 2-5 letras + 3-9 números")
                return
            status = status_combo.currentData()
            self.repo.update_code(row["id"], s, cb.isChecked(), status)
            self.table_model.load()
            self._update_column_widths()
            self._update_stats()

    def on_delete(self) -> None:
        r = self._selected_row()
        if r is None:
            QMessageBox.information(self, "🗑️ Borrar", "Selecciona una fila para borrar.")
            return
        row = self.table_model.rows[r]
        ok = QMessageBox.question(self, "⚠️ Confirmar", f"¿Eliminar código {row['code']}?")
        if ok == QMessageBox.Yes:
            self.repo.delete_code(row["id"])
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
        
        self.table_model.duplicates_only = self.chk_duplicados.isChecked()
        
        # Filtro de status
        self.table_model.status_filter = self.status_filter.currentData()
        
        # Obtener texto limpio del autocompletado
        search_text = self.search.get_clean_text() if hasattr(self.search, 'get_clean_text') else self.search.text().strip().upper()
        self.table_model.search_text = search_text or None
        
        self.table_model.load()
        self._update_column_widths()

    def on_sort_changed(self, text: str) -> None:
        if "Fecha ↓" in text:
            self.table_model.order_by = "created_at"
            self.table_model.order_dir = "DESC"
        elif "Fecha ↑" in text:
            self.table_model.order_by = "created_at"
            self.table_model.order_dir = "ASC"
        elif "A-Z" in text:
            self.table_model.order_by = "code"
            self.table_model.order_dir = "ASC"
        elif "Z-A" in text:
            self.table_model.order_by = "code"
            self.table_model.order_dir = "DESC"
        elif "Status" in text:
            self.table_model.order_by = "status"
            self.table_model.order_dir = "ASC"
        self.table_model.load()
        self._update_column_widths()
