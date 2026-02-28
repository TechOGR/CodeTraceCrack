"""
Script de prueba para simular ventas de productos.
Resta unidades del stock_remaining en la base de datos.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QListWidget, QListWidgetItem, QMessageBox,
    QFrame, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from repository.db_querys import CodeRepository, STATUS_LABELS


# Estilos modernos
STYLE = """
QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

QWidget#MainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a1a2e, stop:1 #16213e);
}

QLabel#Title {
    color: #ffffff;
    font-size: 22px;
    font-weight: bold;
    padding: 10px;
}

QLabel#Subtitle {
    color: #a0a0a0;
    font-size: 12px;
}

QLineEdit {
    background: #2d2d44;
    color: #ffffff;
    border: 1px solid #3d3d5c;
    border-radius: 8px;
    padding: 10px 15px;
    font-size: 13px;
}

QLineEdit:focus {
    border: 2px solid #6366f1;
}

QListWidget {
    background: #2d2d44;
    color: #ffffff;
    border: 1px solid #3d3d5c;
    border-radius: 10px;
    padding: 5px;
    outline: none;
}

QListWidget::item {
    padding: 12px 15px;
    border-radius: 6px;
    margin: 2px 4px;
}

QListWidget::item:hover {
    background: #3d3d5c;
}

QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1, stop:1 #8b5cf6);
    color: #ffffff;
}

QSpinBox {
    background: #2d2d44;
    color: #ffffff;
    border: 1px solid #3d3d5c;
    border-radius: 8px;
    padding: 10px 15px;
    font-size: 16px;
    font-weight: bold;
    min-width: 120px;
}

QSpinBox:focus {
    border: 2px solid #6366f1;
}

QSpinBox::up-button, QSpinBox::down-button {
    width: 25px;
    background: #3d3d5c;
    border: none;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #6366f1;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1, stop:1 #8b5cf6);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 25px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c7ff2, stop:1 #9d6eff);
}

QPushButton:pressed {
    background: #4f46e5;
}

QPushButton:disabled {
    background: #3d3d5c;
    color: #666666;
}

QPushButton#CancelBtn {
    background: #3d3d5c;
}

QPushButton#CancelBtn:hover {
    background: #4d4d6c;
}

QFrame#InfoPanel {
    background: #2d2d44;
    border: 1px solid #3d3d5c;
    border-radius: 10px;
    padding: 15px;
}

QLabel#InfoLabel {
    color: #e0e0e0;
    font-size: 13px;
}

QLabel#StockLabel {
    color: #22c55e;
    font-size: 18px;
    font-weight: bold;
}

QLabel#StockLow {
    color: #f59e0b;
    font-size: 18px;
    font-weight: bold;
}

QLabel#StockCritical {
    color: #ef4444;
    font-size: 18px;
    font-weight: bold;
}
"""


class VentasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = CodeRepository()
        self.selected_product = None
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        self.setWindowTitle('💰 Simulador de Ventas - CodeTrace')
        self.setFixedSize(500, 750)
        self.setObjectName('MainWindow')
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel('🛒 Punto de Venta')
        title.setObjectName('Title')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel('Selecciona un producto y la cantidad a vender')
        subtitle.setObjectName('Subtitle')
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍 Buscar producto...')
        self.search_input.textChanged.connect(self.filter_products)
        layout.addWidget(self.search_input)
        
        # Lista de productos
        self.product_list = QListWidget()
        self.product_list.itemClicked.connect(self.on_product_selected)
        layout.addWidget(self.product_list)
        
        # Panel de información del producto seleccionado
        self.info_panel = QFrame()
        self.info_panel.setObjectName('InfoPanel')
        info_layout = QVBoxLayout(self.info_panel)
        info_layout.setSpacing(8)
        
        self.info_code = QLabel('Código: -')
        self.info_code.setObjectName('InfoLabel')
        info_layout.addWidget(self.info_code)
        
        self.info_desc = QLabel('Descripción: -')
        self.info_desc.setObjectName('InfoLabel')
        info_layout.addWidget(self.info_desc)
        
        self.info_stock = QLabel('Stock disponible: -')
        self.info_stock.setObjectName('StockLabel')
        info_layout.addWidget(self.info_stock)
        
        self.info_status = QLabel('Estado: -')
        self.info_status.setObjectName('InfoLabel')
        info_layout.addWidget(self.info_status)
        
        layout.addWidget(self.info_panel)
        
        # Cantidad a vender
        qty_layout = QHBoxLayout()
        qty_label = QLabel('Cantidad a vender:')
        qty_label.setStyleSheet('color: #ffffff; font-size: 14px;')
        qty_layout.addWidget(qty_label)
        
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setEnabled(False)
        qty_layout.addWidget(self.qty_spin)
        
        qty_layout.addStretch()
        layout.addLayout(qty_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_sell = QPushButton('✓ Vender')
        self.btn_sell.setEnabled(False)
        self.btn_sell.clicked.connect(self.process_sale)
        btn_layout.addWidget(self.btn_sell)
        
        btn_cancel = QPushButton('✕ Cerrar')
        btn_cancel.setObjectName('CancelBtn')
        btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def load_products(self):
        """Carga todos los productos con stock."""
        self.all_products = []
        rows = self.repo.list_codes(order_by='code', order_dir='ASC')
        
        for row in rows:
            product = dict(row)
            # Solo mostrar productos con stock configurado
            if product.get('stock_remaining') is not None:
                self.all_products.append(product)
        
        self.display_products(self.all_products)
    
    def display_products(self, products):
        """Muestra los productos en la lista."""
        self.product_list.clear()
        
        for product in products:
            code = product['code']
            desc = product.get('description') or 'Sin descripción'
            stock = product.get('stock_remaining', 0)
            status = STATUS_LABELS.get(product.get('status', 'disponible'), 'Disponible')
            
            # Truncar descripción
            if len(desc) > 25:
                desc = desc[:22] + '...'
            
            # Formato: CÓDIGO - Descripción [Stock: X]
            text = f"{code}  •  {desc}  •  Stock: {stock}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, product)
            
            # Color según stock
            if stock <= 0:
                item.setForeground(QColor('#ef4444'))  # Rojo
            elif stock < (product.get('stock_per_box') or 100):
                item.setForeground(QColor('#f59e0b'))  # Naranja
            else:
                item.setForeground(QColor('#22c55e'))  # Verde
            
            self.product_list.addItem(item)
    
    def filter_products(self, text):
        """Filtra productos por búsqueda."""
        text = text.strip().lower()
        if not text:
            self.display_products(self.all_products)
            return
        
        filtered = []
        for p in self.all_products:
            code = p['code'].lower()
            desc = (p.get('description') or '').lower()
            if text in code or text in desc:
                filtered.append(p)
        
        self.display_products(filtered)
    
    def on_product_selected(self, item):
        """Maneja la selección de un producto."""
        self.selected_product = item.data(Qt.UserRole)
        
        if not self.selected_product:
            return
        
        code = self.selected_product['code']
        desc = self.selected_product.get('description') or 'Sin descripción'
        stock = self.selected_product.get('stock_remaining', 0)
        per_box = self.selected_product.get('stock_per_box', 0)
        status = STATUS_LABELS.get(self.selected_product.get('status', 'disponible'), 'Disponible')
        
        # Actualizar panel de información
        self.info_code.setText(f'Código: {code}')
        self.info_desc.setText(f'Descripción: {desc}')
        self.info_status.setText(f'Estado: {status}')
        
        # Stock con color
        if stock <= 0:
            self.info_stock.setObjectName('StockCritical')
            self.info_stock.setText(f'⚠️ Stock: {stock} unidades (SIN STOCK)')
        elif per_box and stock < per_box:
            self.info_stock.setObjectName('StockLow')
            self.info_stock.setText(f'⚡ Stock: {stock} unidades (BAJO)')
        else:
            self.info_stock.setObjectName('StockLabel')
            self.info_stock.setText(f'✓ Stock: {stock} unidades')
        
        # Refrescar estilos
        self.info_stock.setStyleSheet(self.info_stock.styleSheet())
        
        # Configurar spinner
        self.qty_spin.setMaximum(max(1, stock))
        self.qty_spin.setValue(1)
        self.qty_spin.setEnabled(stock > 0)
        
        # Habilitar botón de venta
        self.btn_sell.setEnabled(stock > 0)
    
    def process_sale(self):
        """Procesa la venta restando del stock."""
        if not self.selected_product:
            return
        
        qty = self.qty_spin.value()
        code_id = self.selected_product['id']
        code = self.selected_product['code']
        current_stock = self.selected_product.get('stock_remaining', 0)
        per_box = self.selected_product.get('stock_per_box')
        boxes = self.selected_product.get('stock_boxes')
        
        new_stock = current_stock - qty
        
        # Confirmar venta
        msg = QMessageBox(self)
        msg.setWindowTitle('Confirmar Venta')
        msg.setIcon(QMessageBox.Question)
        msg.setText(f'¿Confirmar venta de {qty} unidades?')
        msg.setInformativeText(
            f'Producto: {code}\n'
            f'Stock actual: {current_stock}\n'
            f'Cantidad a vender: {qty}\n'
            f'Stock después de venta: {new_stock}'
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        if msg.exec_() != QMessageBox.Yes:
            return
        
        # Actualizar stock en la base de datos
        self.repo.update_stock(code_id, per_box, boxes, new_stock)
        
        # Mostrar confirmación
        QMessageBox.information(
            self, 
            '✓ Venta Exitosa', 
            f'Se vendieron {qty} unidades de {code}.\n\nStock restante: {new_stock}'
        )
        
        # Recargar productos
        self.load_products()
        
        # Limpiar selección
        self.selected_product = None
        self.info_code.setText('Código: -')
        self.info_desc.setText('Descripción: -')
        self.info_stock.setText('Stock disponible: -')
        self.info_stock.setObjectName('StockLabel')
        self.info_status.setText('Estado: -')
        self.qty_spin.setEnabled(False)
        self.qty_spin.setValue(1)
        self.btn_sell.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    
    window = VentasWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
