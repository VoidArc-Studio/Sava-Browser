import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QUrl, QSettings, Qt
from .sava_ui import SavaUI

def load_stylesheet(path):
    """Load QSS stylesheet from file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Stylesheet {path} not found.")
        return ""

class SavaBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sava Browser")
        self.setWindowIcon(QIcon(os.path.join("assets", "sava_icon.png")))
        self.settings = QSettings("SavaBrowser", "Settings")
        self.history = []
        self.bookmarks = self.load_file("bookmarks.json", [])
        self.downloads = []
        self.notes = self.load_file("notes.txt", "")
        self.sessions = self.load_file("sessions.json", [])
        self.speed_dial = self.load_file("speed_dial.json", [])
        self.web_panels = self.load_file("web_panels.json", [])
        self.ai = SavaAI()
        self.ad_block_enabled = self.settings.value("ad_block_enabled", True, type=bool)
        self.theme = self.settings.value("theme", "Vivaldi")
        self.ui = SavaUI(self)
        self.init_ui()
        self.autosave_session()

    def init_ui(self):
        """Initialize the user interface."""
        self.ui.setup_ui()
        welcome_path = os.path.abspath(os.path.join("assets", "welcome.html"))
        if os.path.exists(welcome_path):
            self.ui.add_new_tab(QUrl.fromLocalFile(welcome_path), "Witaj")
        else:
            QMessageBox.warning(self, "Błąd", "Strona powitalna nie znaleziona. Ładuję Startpage.")
            self.ui.add_new_tab(QUrl("https://www.startpage.com"), "Startpage")
        self.apply_theme()

    def apply_theme(self):
        """Apply the Vivaldi-inspired stylesheet."""
        qss_path = os.path.join("code", "sava_styles.qss")
        self.setStyleSheet(load_stylesheet(qss_path))

    def load_file(self, filename, default):
        """Load JSON or text file from /code/ directory."""
        try:
            with open(os.path.join("code", filename), "r") as f:
                return json.load(f) if filename.endswith(".json") else f.read()
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def save_file(self, filename, data):
        """Save JSON or text file to /code/ directory."""
        try:
            with open(os.path.join("code", filename), "w") as f:
                if filename.endswith(".json"):
                    json.dump(data, f, indent=2)
                else:
                    f.write(data)
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać {filename}: {e}")

    def autosave_session(self):
        """Autosave current session every 5 minutes."""
        from PyQt5.QtCore import QTimer
        timer = QTimer(self)
        timer.timeout.connect(self.save_current_session)
        timer.start(300000)  # 5 minutes

    def save_current_session(self):
        """Save current session."""
        session_name = f"AutoSave_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = {
            "name": session_name,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tabs": [{"url": self.ui.tabs.widget(i).url().toString(), "title": self.ui.tabs.tabText(i)} for i in range(self.ui.tabs.count())]
        }
        self.sessions.append(session)
        self.save_file("sessions.json", self.sessions)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Noto Sans", 11))  # Linux-friendly font
    app.setStyle("Fusion")
    browser = SavaBrowser()
    browser.showMaximized()
    sys.exit(app.exec_())
