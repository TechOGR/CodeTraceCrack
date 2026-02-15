import sys
import atexit

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

from repository.db_querys import CodeRepository
from styles.styles import apply_dark_theme, apply_light_theme
from ui.ui import MainWindow, LoginDialog

from pathlib import Path

APP_UNIQUE_ID = "CodeTrace_SingleInstance_Lock"

class SingleInstanceLock:
    """Previene múltiples instancias de la aplicación usando QLocalServer."""
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.server = None
        self._locked = False
    
    def try_lock(self) -> bool:
        """Intenta obtener el lock. Retorna True si es la única instancia."""
        # Intentar conectar a una instancia existente
        socket = QLocalSocket()
        socket.connectToServer(self.app_id)
        if socket.waitForConnected(500):
            # Ya hay una instancia corriendo
            socket.close()
            return False
        
        # No hay instancia, crear servidor
        self.server = QLocalServer()
        # Limpiar servidor anterior si quedó huérfano
        QLocalServer.removeServer(self.app_id)
        if self.server.listen(self.app_id):
            self._locked = True
            return True
        return False
    
    def unlock(self):
        """Libera el lock."""
        if self.server:
            self.server.close()
            self.server = None
        self._locked = False

def run() -> None:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    
    # Verificar instancia única
    instance_lock = SingleInstanceLock(APP_UNIQUE_ID)
    if not instance_lock.try_lock():
        QMessageBox.warning(
            None, 
            "CodeTrace", 
            "Ya hay una instancia de CodeTrace en ejecución."
        )
        sys.exit(1)
    
    # Registrar cleanup al salir
    atexit.register(instance_lock.unlock)
    
    apply_light_theme(app)  # Start with light theme
    
    while True:
        # Show login dialog
        login = LoginDialog()
        if login.exec_() != 1:  # User cancelled or closed
            instance_lock.unlock()
            sys.exit(0)
        
        user_role = login.user_role
        username = login.username
        
        repo = CodeRepository()
        win = MainWindow(repo, initial_theme="Claro", home_path=Path.cwd(), user_role=user_role, username=username)
        
        def on_theme(text: str) -> None:
            if text == "Oscuro":
                apply_dark_theme(app)
            else:
                apply_light_theme(app)
        
        win.theme_change_callback = on_theme
        win.show()
        app.exec_()
        
        # Check if logout was requested
        if not win.logout_requested:
            break
        # Reset theme for next login
        apply_light_theme(app)
    
    sys.exit(0)

if __name__ == "__main__":
    run()
