import csv
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def export_to_csv(parent, data, status_labels):
    """
    Exporta la lista de códigos y sus estados a un archivo CSV.
    Formato: Código;Descripción;Stock_Caja;Stock_Cajas;Stock_Restante;Estado;Usado;Imagen;Fecha
    
    Args:
        parent: El widget padre para los diálogos.
        data: Lista de diccionarios con los datos de los códigos.
        status_labels: Diccionario que mapea códigos de estado a etiquetas legibles.
    """
    if not data:
        QMessageBox.warning(parent, "Exportar CSV", "No hay datos para exportar.")
        return
    
    # Crear carpeta saved si no existe
    saved_dir = Path.cwd() / "saved"
    saved_dir.mkdir(exist_ok=True)
    
    # Nombre de archivo por defecto con fecha
    default_name = f"codes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    default_path = str(saved_dir / default_name)

    file_path, _ = QFileDialog.getSaveFileName(
        parent, 
        "Exportar códigos", 
        default_path, 
        "CSV Files (*.csv);;All Files (*)"
    )

    if file_path:
        if not file_path.endswith('.csv'):
            file_path += '.csv'
            
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                
                # Cabecera compatible con importación
                writer.writerow(["Código", "Descripción", "Stock_Caja", "Stock_Cajas", "Stock_Restante", "Estado", "Usado", "Imagen", "Fecha"])
                
                for item in data:
                    code = item.get('code', '')
                    description = item.get('description') or ''
                    stock_per_box = item.get('stock_per_box') or ''
                    stock_boxes = item.get('stock_boxes') or ''
                    stock_remaining = item.get('stock_remaining') or ''
                    status_id = item.get('status', 'disponible')
                    status_text = status_labels.get(status_id, "Disponible")
                    used = "Sí" if item.get('annotated') else "No"
                    image_path = item.get('image_path') or ''
                    fecha = item.get('created_at', '')
                    
                    writer.writerow([code, description, stock_per_box, stock_boxes, stock_remaining, status_text, used, image_path, fecha])
                    
            QMessageBox.information(parent, "Exportación exitosa", f"Exportados {len(data)} códigos a:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"No se pudo exportar:\n{str(e)}")
