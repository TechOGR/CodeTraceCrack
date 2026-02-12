import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from repository.db_querys import CodeRepository
from styles.styles import apply_dark_theme, apply_light_theme
from ui.ui import MainWindow

def run() -> None:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    repo = CodeRepository()
    win = MainWindow(repo, initial_theme="Oscuro")
    def on_theme(text: str) -> None:
        if text == "Oscuro":
            apply_dark_theme(app)
        else:
            apply_light_theme(app)
    win.theme_change_callback = on_theme
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
