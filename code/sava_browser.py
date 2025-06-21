import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QToolBar, QAction, QMenu, QDialog, QFormLayout,
    QComboBox, QCheckBox, QLabel, QListWidget, QMessageBox, QFileDialog, QGridLayout,
    QDockWidget, QTextEdit, QFrame, QInputDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, Qt, QSettings, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QFont, QCursor, QPixmap
import uuid
import datetime

def load_stylesheet(path):
    """Load QSS stylesheet from file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Stylesheet {path} not found.")
        return ""

class SavaAI:
    """Mock Sava AI with enhanced query processing."""
    def __init__(self):
        self.modes = ["Conversation", "Programmer", "Web Search"]
        self.current_mode = "Conversation"
        self.context = []

    def process_query(self, query):
        if not query.strip():
            return "Sava AI: Please provide a valid query."
        self.context.append(query)
        if len(self.context) > 5:
            self.context.pop(0)
        if self.current_mode == "Conversation":
            prev = self.context[-2] if len(self.context) > 1 else "no prior context"
            return f"Sava AI (Conversation): '{query}' - Continuing from '{prev}', here's a detailed response!"
        elif self.current_mode == "Programmer":
            return (f"Sava AI (Programmer): '{query}' - Solution:\n"
                    "```python\n# Example\ndef demo():\n    return 'Sava AI'\nprint(demo())\n```")
        elif self.current_mode == "Web Search":
            return f"Sava AI (Web Search): Searching Startpage for '{query}' - Results: [Mock Result 1], [Mock Result 2]."
        return "Sava AI: Unknown mode."

class AdBlockingWebEnginePage(QWebEnginePage):
    """Custom WebEnginePage with ad-blocking."""
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.ad_block_list = [
            "doubleclick.net", "adservice.google.com", "adserver", "banner", ".ads.", "tracking",
            "analytics", "googlesyndication.com", "adroll.com", "pubmatic.com", "openx.net", "rubiconproject.com"
        ]
        self.blocked_count = 0

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        url_str = url.toString().lower()
        if any(ad_domain in url_str for ad_domain in self.ad_block_list):
            self.blocked_count += 1
            print(f"Blocked ad/tracker: {url_str} (Total: {self.blocked_count})")
            return False
        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)

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
        self.tab_groups = {}
        self.web_panel_widgets = []
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        # Sidebar
        self.sidebar = QDockWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setFeatures(QDockWidget.NoDockWidgetFeatures)
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_widget.setLayout(sidebar_layout)
        self.sidebar.setWidget(sidebar_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)

        # Sidebar content
        sidebar_layout.addWidget(QLabel("<b>NAWIGACJA</b>"))
        sidebar_layout.addWidget(self.create_button("🌐 Web", self.hide_sidebar_content))
        self.notes_btn = self.create_button("📝 Notatki", self.show_notes)
        sidebar_layout.addWidget(self.notes_btn)
        sidebar_layout.addWidget(self.create_button("🕒 Historia", self.show_history))
        sidebar_layout.addWidget(QFrame(frameShape=QFrame.HLine, frameShadow=QFrame.Sunken))
        sidebar_layout.addWidget(QLabel("<b>INNE</b>"))
        sidebar_layout.addWidget(self.create_button("🔒 Prywatność", self.show_privacy_dashboard))
        sidebar_layout.addWidget(self.create_button("↓ Pobierania", self.show_downloads))
        sidebar_layout.addWidget(self.create_button("📑 Karty", self.show_tab_overview))
        sidebar_layout.addWidget(self.create_button("💾 Sesje", self.show_sessions))
        self.web_panel_btn = self.create_button("➕ Web Panel", self.add_web_panel)
        sidebar_layout.addWidget(self.web_panel_btn)
        sidebar_layout.addStretch()

        # Notes panel
        self.notes_widget = QTextEdit()
        self.notes_widget.setPlaceholderText("Wpisz notatki tutaj...")
        self.notes_widget.textChanged.connect(self.save_notes)
        self.notes_widget.hide()
        sidebar_layout.addWidget(self.notes_widget)

        # Web panels
        for panel in self.web_panels:
            self.create_web_panel_widget(panel["url"], panel["title"])

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(6, 6, 6, 6)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(Qt.QSize(22, 22))
        self.main_layout.addWidget(self.toolbar)

        # Navigation buttons
        self.back_btn = QAction(QIcon.fromTheme("go-previous"), "Wstecz", self)
        self.back_btn.triggered.connect(self.navigate_back)
        self.toolbar.addAction(self.back_btn)
        self.forward_btn = QAction(QIcon.fromTheme("go-next"), "Dalej", self)
        self.forward_btn.triggered.connect(self.navigate_forward)
        self.toolbar.addAction(self.forward_btn)
        self.reload_btn = QAction(QIcon.fromTheme("view-refresh"), "Odśwież", self)
        self.reload_btn.triggered.connect(self.reload_page)
        self.toolbar.addAction(self.reload_btn)
        self.toolbar.addSeparator()

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Szukaj w Startpage lub wpisz 'sava:zapytanie' dla AI")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setFont(QFont("Segoe UI", 12))
        self.url_bar.setMinimumWidth(600)
        self.toolbar.addWidget(self.url_bar)
        self.toolbar.addSeparator()

        # Additional buttons
        self.ai_btn = QAction(QIcon.fromTheme("system-search"), "Sava AI", self)
        self.ai_btn.triggered.connect(self.open_ai_dialog)
        self.toolbar.addAction(self.ai_btn)
        self.bookmark_btn = QAction(QIcon.fromTheme("bookmark-new"), "Zakładka", self)
        self.bookmark_btn.triggered.connect(self.add_bookmark)
        self.toolbar.addAction(self.bookmark_btn)
        self.tab_group_btn = QAction(QIcon.fromTheme("folder-new"), "Grupuj Karty", self)
        self.tab_group_btn.triggered.connect(self.group_tabs)
        self.toolbar.addAction(self.tab_group_btn)

        # Menu
        self.menu = QMenu("Menu", self)
        self.new_tab_action = QAction("Nowa Karta", self)
        self.new_tab_action.triggered.connect(self.add_new_tab)
        self.bookmarks_menu = QMenu("Zakładki", self)
        self.update_bookmarks_menu()
        self.settings_action = QAction("Ustawienia", self)
        self.settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(self.new_tab_action)
        self.menu.addMenu(self.bookmarks_menu)
        self.menu.addAction(self.settings_action)
        self.menu_btn = QPushButton(QIcon.fromTheme("application-menu"), "")
        self.menu_btn.setMenu(self.menu)
        self.toolbar.addWidget(self.menu_btn)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.main_layout.addWidget(self.tabs)

        # Load welcome page
        welcome_path = os.path.abspath(os.path.join("assets", "welcome.html"))
        if os.path.exists(welcome_path):
            self.add_new_tab(QUrl.fromLocalFile(welcome_path), "Witaj")
        else:
            QMessageBox.warning(self, "Błąd", "Strona powitalna nie znaleziona. Ładuję Startpage.")
            self.add_new_tab(QUrl("https://www.startpage.com"), "Startpage")

        self.apply_theme()

    def create_button(self, text, slot):
        """Create a sidebar button with consistent styling."""
        button = QPushButton(text)
        button.clicked.connect(slot)
        return button

    def apply_theme(self):
        """Apply the Vivaldi-inspired stylesheet."""
        qss_path = os.path.join("assets", "style.qss")
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

    def add_new_tab(self, qurl=None, label="Nowa Karta", group_id=None):
        """Add a new browser tab with animation."""
        if qurl is None:
            qurl = QUrl(self.settings.value("homepage", "https://www.startpage.com"))
        browser = QWebEngineView()
        profile = QWebEngineProfile("SavaProfile", browser)
        page = AdBlockingWebEnginePage(profile, browser) if self.ad_block_enabled else QWebEnginePage(profile, browser)
        browser.setPage(page)
        try:
            browser.setUrl(qurl)
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się załadować URL: {e}")
            return
        browser.urlChanged.connect(lambda qurl, b=browser: self.update_url_bar(qurl, b))
        browser.titleChanged.connect(lambda title, b=browser: self.update_tab_title(title, b))
        browser.loadFinished.connect(lambda ok, qurl=qurl, b=browser: self.log_history(qurl, b))
        browser.page().profile().downloadRequested.connect(self.handle_download)
        i = self.tabs.addTab(browser, label)
        if group_id:
            self.tab_groups.setdefault(group_id, []).append(i)
            self.tabs.setTabText(i, f"[{group_id}] {label}")
        self.tabs.setCurrentIndex(i)
        anim = QPropertyAnimation(self.tabs.widget(i), b"geometry")
        anim.setDuration(200)
        anim.setStartValue(self.tabs.geometry().adjusted(0, 30, 0, 0))
        anim.setEndValue(self.tabs.geometry())
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()

    def close_tab(self, i):
        """Close a tab, ensuring at least one remains."""
        if self.tabs.count() > 1:
            for group_id, tabs in self.tab_groups.items():
                if i in tabs:
                    tabs.remove(i)
                    if not tabs:
                        del self.tab_groups[group_id]
                    break
            self.tabs.removeTab(i)
        else:
            QMessageBox.warning(self, "Ostrzeżenie", "Nie można zamknąć ostatniej karty.")

    def navigate_to_url(self):
        """Navigate to URL or process Sava AI query."""
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
        if url_text.startswith("sava:"):
            query = url_text[5:].strip()
            response = self.ai.process_query(query)
            self.show_ai_response(response)
        else:
            if not url_text.startswith(("http://", "https://")):
                if "." in url_text and " " not in url_text:
                    url = f"https://{url_text}"
                else:
                    url = f"https://www.startpage.com/search?q={url_text}"
            else:
                url = url_text
            try:
                self.tabs.currentWidget().setUrl(QUrl(url))
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nieprawidłowy URL: {e}")

    def navigate_back(self):
        """Navigate to previous page."""
        if self.tabs.currentWidget():
            self.tabs.currentWidget().back()

    def navigate_forward(self):
        """Navigate to next page."""
        if self.tabs.currentWidget():
            self.tabs.currentWidget().forward()

    def reload_page(self):
        """Reload current page."""
        if self.tabs.currentWidget():
            self.tabs.currentWidget().reload()

    def log_history(self, qurl, browser):
        """Log browsing history."""
        if self.tabs.indexOf(browser) != -1:
            self.history.append({
                "url": qurl.toString(),
                "title": browser.title() or "Bez tytułu",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    def update_url_bar(self, qurl=None, browser=None):
        """Update URL bar with current tab's URL."""
        if browser := self.tabs.currentWidget():
            self.url_bar.setText(browser.url().toString())

    def update_tab_title(self, title, browser):
        """Update tab title with group prefix."""
        if (index := self.tabs.indexOf(browser)) != -1:
            group_prefix = next((f"[{gid}] " for gid, tabs in self.tab_groups.items() if index in tabs), "")
            self.tabs.setTabText(index, f"{group_prefix}{title[:30] if title else 'Nowa Karta'}")

    def add_bookmark(self):
        """Add current page to bookmarks."""
        if browser := self.tabs.currentWidget():
            url = browser.url().toString()
            title = browser.title() or "Bez tytułu"
            self.bookmarks.append({"url": url, "title": title})
            self.save_file("bookmarks.json", self.bookmarks)
            self.update_bookmarks_menu()
            QMessageBox.information(self, "Zakładka Dodana", f"Dodano: {title}")

    def update_bookmarks_menu(self):
        """Update bookmarks menu with current bookmarks."""
        self.bookmarks_menu.clear()
        for bookmark in self.bookmarks:
            action = QAction(bookmark["title"], self)
            action.triggered.connect(lambda checked, url=bookmark["url"]: self.add_new_tab(QUrl(url)))
            self.bookmarks_menu.addAction(action)

    def handle_download(self, download: QWebEngineDownloadItem):
        """Handle file downloads."""
        suggested_path = download.path()
        path, _ = QFileDialog.getSaveFileName(self, "Zapisz Plik", suggested_path)
        if path:
            download.setPath(path)
            download.accept()
            self.downloads.append({
                "path": path,
                "url": download.url().toString(),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            QMessageBox.information(self, "Rozpoczęto Pobieranie", f"Pobieranie do {path}")

    def save_notes(self):
        """Save notes to file."""
        self.save_file("notes.txt", self.notes_widget.toPlainText())

    def hide_sidebar_content(self):
        """Hide all sidebar content panels."""
        self.notes_widget.hide()
        for panel in self.web_panel_widgets:
            panel["widget"].hide()

    def show_notes(self):
        """Show notes panel in sidebar."""
        self.hide_sidebar_content()
        self.notes_widget.setText(self.notes)
        self.notes_widget.show()

    def create_web_panel(self, url, dialog):
        """Create a new web panel with title."""
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        title, ok = QInputDialog.getText(self, "Tytuł Panelu", "Podaj tytuł panelu:")
        if not ok or not title:
            title = "Panel Web"
        try:
            self.web_panels.append({"url": url, "title": title})
            self.create_web_panel_widget(url, title)
            self.save_file("web_panels.json", self.web_panels)
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się dodać panelu: {e}")

    def create_web_panel_widget(self, url, title):
        """Create web panel widget with remove button."""
        panel_widget = QWidget()
        panel_layout = QVBoxLayout()
        panel_widget.setLayout(panel_layout)
        web_view = QWebEngineView()
        web_view.setUrl(QUrl(url))
        web_view.setFixedHeight(200)
        web_view.hide()
        remove_btn = QPushButton("Usuń")
        remove_btn.clicked.connect(lambda: self.remove_web_panel(url))
        panel_layout.addWidget(QLabel(title))
        panel_layout.addWidget(web_view)
        panel_layout.addWidget(remove_btn)
        self.sidebar.widget().layout().addWidget(panel_widget)
        self.web_panel_widgets.append({"widget": web_view, "container": panel_widget})
        web_view.mousePressEvent = lambda e: [self.hide_sidebar_content(), web_view.show()]

    def remove_web_panel(self, url):
        """Remove a web panel."""
        self.web_panels = [p for p in self.web_panels if p["url"] != url]
        for panel in self.web_panel_widgets[:]:
            if panel["widget"].url().toString() == url:
                panel["container"].deleteLater()
                self.web_panel_widgets.remove(panel)
        self.save_file("web_panels.json", self.web_panels)

    def group_tabs(self):
        """Group selected tabs."""
        if self.tabs.count() < 2:
            QMessageBox.warning(self, "Ostrzeżenie", "Potrzebne są co najmniej dwie karty do grupowania.")
            return
        dialog = self.create_dialog("Grupuj Karty", 600, 400)
        layout = QVBoxLayout()
        name_input = QLineEdit()
        name_input.setPlaceholderText("Podaj nazwę grupy")
        layout.addWidget(QLabel("Nazwa Grupy:"))
        layout.addWidget(name_input)
        tabs_list = QListWidget()
        for i in range(self.tabs.count()):
            if not any(i in tabs for tabs in self.tab_groups.values()):
                tabs_list.addItem(self.tabs.tabText(i))
        layout.addWidget(QLabel("Wybierz Karty:"))
        layout.addWidget(tabs_list)
        save_btn = QPushButton("Utwórz Grupę")
        save_btn.clicked.connect(lambda: self.create_tab_group(
            name_input.text(), [i for i in range(self.tabs.count()) if tabs_list.item(i) and tabs_list.item(i).isSelected()], dialog))
        layout.addWidget(save_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def create_tab_group(self, group_name, selected_indices, dialog):
        """Create a tab group with selected tabs."""
        if not group_name or not selected_indices:
            QMessageBox.warning(self, "Błąd", "Podaj nazwę grupy i wybierz co najmniej jedną kartę.")
            return
        group_id = str(uuid.uuid4())[:8]
        self.tab_groups[group_id] = selected_indices
        for i in selected_indices:
            self.tabs.setTabText(i, f"[{group_name}] {self.tabs.tabText(i)}")
        dialog.accept()

    def save_current_session(self):
        """Save current session."""
        session_name, ok = QInputDialog.getText(self, "Zapisz Sesję", "Nazwa Sesji:")
        if ok and session_name:
            session = {
                "name": session_name,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tabs": [{"url": self.tabs.widget(i).url().toString(), "title": self.tabs.tabText(i)} for i in range(self.tabs.count())]
            }
            self.sessions.append(session)
            self.save_file("sessions.json", self.sessions)
            QMessageBox.information(self, "Sesja Zapisana", f"Sesja '{session_name}' zapisana.")

    def load_session(self, session):
        """Load a saved session."""
        for i in range(self.tabs.count() - 1, -1, -1):
            self.close_tab(i)
        for tab in session["tabs"]:
            try:
                self.add_new_tab(QUrl(tab["url"]), tab["title"])
            except Exception as e:
                print(f"Failed to load tab {tab['url']}: {e}")
        QMessageBox.information(self, "Sesja Załadowana", f"Sesja '{session['name']}' załadowana.")

    def create_dialog(self, title, width, height):
        """Create a styled dialog with consistent appearance."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(width, height)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QLabel { font-size: 14px; color: #23272e; margin-top: 10px; }
            QLineEdit { 
                padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; background: #f9f9f9;
            }
            QLineEdit:focus { border: 1.5px solid #ff6b00; box-shadow: 0 0 6px rgba(255, 107, 0, 0.5); }
            QComboBox { 
                padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; background: #f9f9f9;
            }
            QComboBox:focus { border: 1.5px solid #ff6b00; }
            QCheckBox { padding: 10px; font-size: 14px; }
            QListWidget { font-size: 13px; color: #23272e; padding: 10px; }
            QListWidget::item:hover { background: #ffe5cc; cursor: pointer; }
            QPushButton { 
                background-color: #ff6b00; color: white; padding: 12px; border-radius: 8px; font-size: 14px;
                transition: background-color 0.3s, transform 0.1s;
            }
            QPushButton:hover { background-color: #e55f00; transform: scale(1.02); }
        """)
        return dialog

    def open_ai_dialog(self):
        """Open Sava AI dialog."""
        dialog = self.create_dialog("Asystent Sava AI", 700, 500)
        layout = QVBoxLayout()
        mode_combo = QComboBox()
        mode_combo.addItems(self.ai.modes)
        mode_combo.setCurrentText(self.ai.current_mode)
        mode_combo.currentTextChanged.connect(lambda mode: setattr(self.ai, "current_mode", mode))
        layout.addWidget(QLabel("Wybierz Tryb:"))
        layout.addWidget(mode_combo)
        query_input = QLineEdit()
        query_input.setPlaceholderText("Zapytaj Sava AI (np. 'sava:napisz skrypt Python' lub 'sava:szukaj trendów AI')")
        layout.addWidget(QLabel("Zapytanie:"))
        layout.addWidget(query_input)
        response_label = QLabel("Sava AI odpowie tutaj.")
        response_label.setWordWrap(True)
        response_label.setMinimumHeight(200)
        layout.addWidget(QLabel("Odpowiedź:"))
        layout.addWidget(response_label)
        submit_btn = QPushButton("Wyślij Zapytanie")
        submit_btn.clicked.connect(lambda: response_label.setText(self.ai.process_query(query_input.text())))
        layout.addWidget(submit_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_ai_response(self, response):
        """Show Sava AI response in a dialog."""
        dialog = self.create_dialog("Odpowiedź Sava AI", 700, 400)
        layout = QVBoxLayout()
        response_label = QLabel(response)
        response_label.setWordWrap(True)
        layout.addWidget(response_label)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_history(self):
        """Show browsing history."""
        dialog = self.create_dialog("Historia Przeglądania", 700, 400)
        layout = QVBoxLayout()
        history_list = QListWidget()
        for entry in self.history:
            history_list.addItem(f"{entry['timestamp']} - {entry['title']} ({entry['url']})")
        history_list.itemClicked.connect(lambda item: self.add_new_tab(QUrl(item.text().split(" ")[-1].strip("()"))))
        layout.addWidget(history_list)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_downloads(self):
        """Show download history."""
        dialog = self.create_dialog("Pobierania", 700, 400)
        layout = QVBoxLayout()
        downloads_list = QListWidget()
        for entry in self.downloads:
            downloads_list.addItem(f"{entry['timestamp']} - {os.path.basename(entry['path'])} ({entry['url']})")
        layout.addWidget(downloads_list)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_tab_overview(self):
        """Show tab overview with thumbnails."""
        dialog = self.create_dialog("Przegląd Kart", 900, 600)
        layout = QGridLayout()
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            title = self.tabs.tabText(i)
            url = browser.url().toString()
            thumbnail = QLabel()
            thumbnail.setPixmap(QPixmap(100, 60))  # Placeholder
            thumbnail.setScaledContents(True)
            title_label = QLabel(f"<b>{title}</b><br>{url}")
            title_label.setWordWrap(True)
            title_label.mousePressEvent = lambda e, idx=i: [self.tabs.setCurrentIndex(idx), dialog.accept()]
            title_label.setCursor(QCursor(Qt.PointingHandCursor))
            layout.addWidget(thumbnail, i // 3, (i % 3) * 2)
            layout.addWidget(title_label, i // 3, (i % 3) * 2 + 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_privacy_dashboard(self):
        """Show privacy dashboard."""
        dialog = self.create_dialog("Panel Prywatności", 600, 400)
        layout = QVBoxLayout()
        blocked_count = sum(self.tabs.widget(i).page().blocked_count for i in range(self.tabs.count()) if isinstance(self.tabs.widget(i).page(), AdBlockingWebEnginePage))
        layout.addWidget(QLabel("<h2>Panel Prywatności</h2>"))
        layout.addWidget(QLabel(f"Zablokowane Reklamy/Śledzenie: {blocked_count}"))
        layout.addWidget(QLabel(f"Blokowanie Reklam: {'Włączone' if self.ad_block_enabled else 'Wyłączone'}"))
        layout.addWidget(QLabel("<b>Wskazówka:</b> Włącz blokowanie reklam dla lepszej prywatności."))
        dialog.setLayout(layout)
        dialog.exec_()

    def add_web_panel(self):
        """Add a new web panel."""
        dialog = self.create_dialog("Dodaj Panel Web", 600, 300)
        layout = QVBoxLayout()
        url_input = QLineEdit()
        url_input.setPlaceholderText("Wpisz URL panelu web")
        layout.addWidget(QLabel("URL:"))
        layout.addWidget(url_input)
        save_btn = QPushButton("Dodaj Panel")
        save_btn.clicked.connect(lambda: self.create_web_panel(url_input.text(), dialog))
        layout.addWidget(save_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_sessions(self):
        """Show saved sessions."""
        dialog = self.create_dialog("Sesje", 700, 400)
        layout = QVBoxLayout()
        session_list = QListWidget()
        for session in self.sessions:
            session_list.addItem(f"{session['name']} ({session['timestamp']})")
        session_list.itemClicked.connect(lambda item: self.load_session(self.sessions[session_list.currentRow()]))
        layout.addWidget(session_list)
        save_session_btn = QPushButton("Zapisz Bieżącą Sesję")
        save_session_btn.clicked.connect(self.save_current_session)
        layout.addWidget(save_session_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def open_settings(self):
        """Open settings dialog."""
        dialog = self.create_dialog("Ustawienia", 600, 400)
        layout = QFormLayout()
        theme_combo = QComboBox()
        theme_combo.addItems(["Vivaldi", "Dark"])
        theme_combo.setCurrentText(self.theme)
        theme_combo.currentTextChanged.connect(lambda theme: setattr(self, "theme", theme))
        layout.addRow("Motyw:", theme_combo)
        ad_block_check = QCheckBox("Włącz Blokowanie Reklam")
        ad_block_check.setChecked(self.ad_block_enabled)
        ad_block_check.stateChanged.connect(lambda state: setattr(self, "ad_block_enabled", state == Qt.Checked))
        layout.addRow("Blokowanie Reklam:", ad_block_check)
        sidebar_check = QCheckBox("Pokaż Pasek Boczny")
        sidebar_check.setChecked(not self.sidebar.isHidden())
        sidebar_check.stateChanged.connect(lambda state: self.sidebar.setVisible(state == Qt.Checked))
        layout.addRow("Pasek Boczny:", sidebar_check)
        homepage_input = QLineEdit()
        homepage_input.setText(self.settings.value("homepage", "file:///" + os.path.abspath(os.path.join("assets", "welcome.html"))))
        layout.addRow("Strona Startowa:", homepage_input)
        shortcut_new_tab = QLineEdit()
        shortcut_new_tab.setText(self.settings.value("shortcut_new_tab", "Ctrl+T"))
        layout.addRow("Skrót Nowej Karty:", shortcut_new_tab)
        save_btn = QPushButton("Zapisz")
        save_btn.clicked.connect(lambda: [
            self.settings.setValue("theme", self.theme),
            self.settings.setValue("ad_block_enabled", self.ad_block_enabled),
            self.settings.setValue("homepage", homepage_input.text()),
            self.settings.setValue("shortcut_new_tab", shortcut_new_tab.text()),
            self.apply_theme(),
            dialog.accept()
        ])
        layout.addRow(save_btn)
        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    app.setStyle("Fusion")
    browser = SavaBrowser()
    browser.showMaximized()
    sys.exit(app.exec_())
