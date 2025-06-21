import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QToolBar, QAction, QMenu, QDialog, QFormLayout,
                             QComboBox, QCheckBox, QLabel, QListWidget, QMessageBox, QFileDialog, QGridLayout,
                             QDockWidget, QTextEdit)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, Qt, QSettings, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QFont, QCursor, QPixmap
import uuid
import datetime

# Mock Sava AI with enhanced responses
class SavaAI:
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
            return f"Sava AI (Programmer): '{query}' - Solution:\n```python\n# Example\ndef demo():\n    return 'Sava AI'\nprint(demo())\n```"
        elif self.current_mode == "Web Search":
            return f"Sava AI (Web Search): Searching Startpage for '{query}' - Results: [Mock Result 1], [Mock Result 2]."
        return "Sava AI: Unknown mode."

# Custom WebEnginePage with advanced ad-blocking
class AdBlockingWebEnginePage(QWebEnginePage):
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
        self.bookmarks = self.load_bookmarks()
        self.downloads = []
        self.notes = self.load_notes()
        self.sessions = self.load_sessions()
        self.ai = SavaAI()
        self.ad_block_enabled = self.settings.value("ad_block_enabled", True, type=bool)
        self.theme = self.settings.value("theme", "Vivaldi")
        self.tab_groups = {}
        self.web_panels = []
        self.init_ui()

    def init_ui(self):
        # Sidebar (Vivaldi-style)
        self.sidebar = QDockWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setFeatures(QDockWidget.NoDockWidgetFeatures)
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        self.sidebar.setWidget(sidebar_widget)
        sidebar_widget.setLayout(sidebar_layout)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)

        # Sidebar buttons
        sidebar_layout.addWidget(QPushButton("🌐 Web", clicked=self.hide_sidebar_content))
        self.notes_btn = QPushButton("📝 Notes")
        self.notes_btn.clicked.connect(self.show_notes)
        sidebar_layout.addWidget(self.notes_btn)
        sidebar_layout.addWidget(QPushButton("🔒 Privacy", clicked=self.show_privacy_dashboard))
        sidebar_layout.addWidget(QPushButton("🕒 History", clicked=self.show_history))
        sidebar_layout.addWidget(QPushButton("↓ Downloads", clicked=self.show_downloads))
        sidebar_layout.addWidget(QPushButton("📑 Tabs", clicked=self.show_tab_overview))
        sidebar_layout.addWidget(QPushButton("💾 Sessions", clicked=self.show_sessions))
        self.web_panel_btn = QPushButton("➕ Web Panel")
        self.web_panel_btn.clicked.connect(self.add_web_panel)
        sidebar_layout.addWidget(self.web_panel_btn)
        sidebar_layout.addStretch()

        # Notes panel
        self.notes_widget = QTextEdit()
        self.notes_widget.setPlaceholderText("Jot down your notes here...")
        self.notes_widget.textChanged.connect(self.save_notes)
        self.notes_widget.hide()
        sidebar_layout.addWidget(self.notes_widget)

        # Web panels
        self.web_panel_widgets = []
        for panel_url in self.web_panels:
            web_panel = QWebEngineView()
            web_panel.setUrl(QUrl(panel_url))
            web_panel.setFixedHeight(200)
            web_panel.hide()
            sidebar_layout.addWidget(web_panel)
            self.web_panel_widgets.append(web_panel)

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.main_layout.addWidget(self.toolbar)

        # Navigation buttons
        self.back_btn = QAction("◄", self)
        self.back_btn.setToolTip("Back")
        self.back_btn.triggered.connect(self.navigate_back)
        self.toolbar.addAction(self.back_btn)

        self.forward_btn = QAction("►", self)
        self.forward_btn.setToolTip("Forward")
        self.forward_btn.triggered.connect(self.navigate_forward)
        self.toolbar.addAction(self.forward_btn)

        self.reload_btn = QAction("↻", self)
        self.reload_btn.setToolTip("Reload")
        self.reload_btn.triggered.connect(self.reload_page)
        self.toolbar.addAction(self.reload_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search with Startpage or type 'sava:query' for AI")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setFont(QFont("Roboto", 12))
        self.url_bar.setMinimumWidth(700)
        self.toolbar.addWidget(self.url_bar)

        # AI Assistant
        self.ai_btn = QAction("🤖", self)
        self.ai_btn.setToolTip("Sava AI Assistant")
        self.ai_btn.triggered.connect(self.open_ai_dialog)
        self.toolbar.addAction(self.ai_btn)

        # Bookmarks
        self.bookmark_btn = QAction("★", self)
        self.bookmark_btn.setToolTip("Bookmark this page")
        self.bookmark_btn.triggered.connect(self.add_bookmark)
        self.toolbar.addAction(self.bookmark_btn)

        # Tab Group
        self.tab_group_btn = QAction("📂", self)
        self.tab_group_btn.setToolTip("Group Tabs")
        self.tab_group_btn.triggered.connect(self.group_tabs)
        self.toolbar.addAction(self.tab_group_btn)

        # Menu
        self.menu = QMenu("Menu", self)
        self.new_tab_action = QAction("New Tab", self)
        self.new_tab_action.triggered.connect(self.add_new_tab)
        self.bookmarks_menu = QMenu("Bookmarks", self)
        self.update_bookmarks_menu()
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(self.new_tab_action)
        self.menu.addMenu(self.bookmarks_menu)
        self.menu.addAction(self.settings_action)
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setToolTip("Menu")
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
            self.add_new_tab(QUrl.fromLocalFile(welcome_path), "Welcome")
        else:
            QMessageBox.warning(self, "Error", "Welcome page not found. Loading Startpage.")
            self.add_new_tab(QUrl("https://www.startpage.com"), "Startpage")

        # Apply theme
        self.apply_theme()

    def apply_theme(self):
        stylesheet = """
            QMainWindow { background-color: #f5f6f5; }
            QDockWidget { background-color: #2a2b2e; color: #ffffff; }
            QDockWidget::title { background: #2a2b2e; }
            QToolBar { 
                background: #ffffff; 
                border: none; 
                padding: 10px;
                box-shadow: 0 3px 6px rgba(0,0,0,0.1);
            }
            QLineEdit { 
                padding: 12px; 
                border: none; 
                border-radius: 30px; 
                margin: 5px 20px; 
                background: #f0f0f0; 
                transition: background 0.3s, box-shadow 0.3s;
            }
            QLineEdit:focus { 
                background: #ffffff; 
                box-shadow: 0 0 10px rgba(255, 107, 0, 0.5);
            }
            QPushButton, QAction { 
                padding: 12px; 
                font-size: 14px; 
                border-radius: 10px; 
                background: transparent;
                color: #333;
                transition: background 0.2s, transform 0.1s;
            }
            QPushButton:hover, QAction:hover { 
                background: #e0e0e0; 
                transform: scale(1.05);
            }
            QTabWidget::pane { border: none; background: #fff; }
            QTabBar::tab { 
                background: #d8d9d8; 
                padding: 14px 30px; 
                margin-right: 2px; 
                border-top-left-radius: 10px; 
                border-top-right-radius: 10px; 
                font-size: 14px;
                transition: background 0.3s, box-shadow 0.3s;
            }
            QTabBar::tab:selected { 
                background: #ffffff; 
                border-bottom: 4px solid #ff6b00; 
                box-shadow: 0 -3px 6px rgba(0,0,0,0.1);
            }
            QTabBar::tab:hover { 
                background: #c8c9c8; 
            }
            QTabBar::close-button { 
                width: 16px; 
                height: 16px; 
                background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAABmJLR0QA/wD/AP+gvaeTAAAAdUlEQVQokZWOQQrCQAxF7x+wW7AJbsAKbsAK3IAV2IBtYAM2YJfsr3k4Mzs7O8/8vs/MY4wxhhiXyZSO+/1+CoWCoiiKoiRJkmzZSIkiKoiRJkmJ4sU4Hs/zPM/zPM/zvM/zPM/zPM/zPM/zPM/zPM/zvJ/3B5z6L9Yf8r0SAAAAAElFTkSuQkCC);
                border-radius: 8px;
                margin-right: 5px;
            }
            QTabBar::close-button:hover { 
                background: #ff5555; 
            }
            QTextEdit { 
                background: #f9f9f9; 
                border: none; 
                border-radius: 10px; 
                padding: 12px; 
                font-size: 14px;
            }
        """
        if self.theme == "Dark":
            stylesheet = stylesheet.replace("#f5f6f5", "#1c2526").replace("#ffffff", "#2e2f30").replace("#f0f0f0", "#3a3b3c").replace("#d8d9d8", "#4a4b4c").replace("#c8c9c8", "#5a5b5c").replace("#2a2b2e", "#1c2526").replace("#ff6b00", "#ff8c00")
        self.setStyleSheet(stylesheet)
        self.sidebar.setStyleSheet("QPushButton { background: transparent; color: #ffffff; padding: 14px; text-align: left; font-size: 14px; } QPushButton:hover { background: #ff6b00; }")

    def add_new_tab(self, qurl=None, label="New Tab", group_id=None):
        if qurl is None:
            qurl = QUrl("https://www.startpage.com")
        browser = QWebEngineView()
        profile = QWebEngineProfile("SavaProfile", browser)
        page = AdBlockingWebEnginePage(profile, browser) if self.ad_block_enabled else QWebEnginePage(profile, browser)
        browser.setPage(page)
        try:
            browser.setUrl(qurl)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load URL: {e}")
            return
        browser.urlChanged.connect(lambda qurl, b=browser: self.update_url_bar(qurl, b))
        browser.titleChanged.connect(lambda title, b=browser: self.update_tab_title(title, b))
        browser.loadFinished.connect(lambda ok, qurl=qurl, b=browser: self.log_history(qurl, b))
        # POPRAWKA TUTAJ:
        browser.page().profile().downloadRequested.connect(self.handle_download)
        i = self.tabs.addTab(browser, label)
        if group_id:
            self.tab_groups.setdefault(group_id, []).append(i)
            self.tabs.setTabText(i, f"[{group_id}] {label}")
        self.tabs.setCurrentIndex(i)
        anim = QPropertyAnimation(self.tabs.widget(i), b"geometry")
        anim.setDuration(200)
        anim.setStartValue(self.tabs.geometry().adjusted(0, 50, 0, 0))
        anim.setEndValue(self.tabs.geometry())
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()

    def close_tab(self, i):
        if self.tabs.count() > 1:
            for group_id, tabs in self.tab_groups.items():
                if i in tabs:
                    tabs.remove(i)
                    if not tabs:
                        del self.tab_groups[group_id]
                    break
            self.tabs.removeTab(i)
        else:
            QMessageBox.warning(self, "Warning", "Cannot close the last tab.")

    def navigate_to_url(self):
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
                QMessageBox.critical(self, "Error", f"Invalid URL: {e}")

    def navigate_back(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().back()

    def navigate_forward(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().forward()

    def reload_page(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().reload()

    def log_history(self, qurl, browser):
        if self.tabs.indexOf(browser) != -1:
            self.history.append({
                "url": qurl.toString(),
                "title": browser.title() or "Untitled",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    def update_url_bar(self, qurl=None, browser=None):
        if browser := self.tabs.currentWidget():
            self.url_bar.setText(browser.url().toString())

    def update_tab_title(self, title, browser):
        if (index := self.tabs.indexOf(browser)) != -1:
            group_prefix = next((f"[{gid}] " for gid, tabs in self.tab_groups.items() if index in tabs), "")
            self.tabs.setTabText(index, f"{group_prefix}{title[:30] if title else 'New Tab'}")

    def load_bookmarks(self):
        try:
            with open(os.path.join("code", "bookmarks.json"), "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_bookmarks(self):
        try:
            with open(os.path.join("code", "bookmarks.json"), "w") as f:
                json.dump(self.bookmarks, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save bookmarks: {e}")

    def add_bookmark(self):
        if browser := self.tabs.currentWidget():
            url = browser.url().toString()
            title = browser.title() or "Untitled"
            self.bookmarks.append({"url": url, "title": title})
            self.save_bookmarks()
            self.update_bookmarks_menu()
            QMessageBox.information(self, "Bookmark Added", f"Bookmarked: {title}")

    def update_bookmarks_menu(self):
        self.bookmarks_menu.clear()
        for bookmark in self.bookmarks:
            action = QAction(bookmark["title"], self)
            action.triggered.connect(lambda checked, url=bookmark["url"]: self.add_new_tab(QUrl(url)))
            self.bookmarks_menu.addAction(action)

    def handle_download(self, download: QWebEngineDownloadItem):
        suggested_path = download.path()
        path, _ = QFileDialog.getSaveFileName(self, "Save File", suggested_path)
        if path:
            download.setPath(path)
            download.accept()
            self.downloads.append({
                "path": path,
                "url": download.url().toString(),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            QMessageBox.information(self, "Download Started", f"Downloading to {path}")

    def load_notes(self):
        try:
            with open(os.path.join("code", "notes.txt"), "r") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def save_notes(self):
        try:
            with open(os.path.join("code", "notes.txt"), "w") as f:
                f.write(self.notes_widget.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save notes: {e}")

    def load_sessions(self):
        try:
            with open(os.path.join("code", "sessions.json"), "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_sessions(self):
        try:
            with open(os.path.join("code", "sessions.json"), "w") as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save sessions: {e}")

    def hide_sidebar_content(self):
        self.notes_widget.hide()
        for panel in self.web_panel_widgets:
            panel.hide()

    def show_notes(self):
        self.hide_sidebar_content()
        self.notes_widget.setText(self.notes)
        self.notes_widget.show()

    def add_web_panel(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Web Panel")
        layout = QVBoxLayout()
        url_input = QLineEdit()
        url_input.setPlaceholderText("Enter URL for web panel")
        layout.addWidget(QLabel("URL:"))
        layout.addWidget(url_input)
        save_btn = QPushButton("Add Panel")
        save_btn.clicked.connect(lambda: self.create_web_panel(url_input.text(), dialog))
        layout.addWidget(save_btn)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QLabel { font-size: 14px; color: #333; }
            QLineEdit { padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
            QPushButton { background-color: #ff6b00; color: white; padding: 12px; border-radius: 8px; }
            QPushButton:hover { background-color: #e55f00; }
        """)
        dialog.exec_()

    def create_web_panel(self, url, dialog):
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        try:
            web_panel = QWebEngineView()
            web_panel.setUrl(QUrl(url))
            web_panel.setFixedHeight(200)
            web_panel.hide()
            self.sidebar.widget().layout().addWidget(web_panel)
            self.web_panel_widgets.append(web_panel)
            self.web_panels.append(url)
            web_panel.mousePressEvent = lambda e: [self.hide_sidebar_content(), web_panel.show()]
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add web panel: {e}")

    def group_tabs(self):
        if self.tabs.count() < 2:
            QMessageBox.warning(self, "Warning", "Need at least two tabs to group.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Group Tabs")
        layout = QVBoxLayout()
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter group name")
        layout.addWidget(QLabel("Group Name:"))
        layout.addWidget(name_input)
        tabs_list = QListWidget()
        for i in range(self.tabs.count()):
            if not any(i in tabs for tabs in self.tab_groups.values()):
                tabs_list.addItem(self.tabs.tabText(i))
        layout.addWidget(QLabel("Select Tabs:"))
        layout.addWidget(tabs_list)
        save_btn = QPushButton("Create Group")
        save_btn.clicked.connect(lambda: self.create_tab_group(name_input.text(), [i for i in range(self.tabs.count()) if tabs_list.item(i) and tabs_list.item(i).isSelected()], dialog))
        layout.addWidget(save_btn)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QLabel { font-size: 14px; color: #333; }
            QLineEdit { padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
            QListWidget { font-size: 13px; padding: 10px; }
            QListWidget::item:hover { background: #ffe5cc; }
            QPushButton { background-color: #ff6b00; color: white; padding: 12px; border-radius: 8px; }
            QPushButton:hover { background-color: #e55f00; }
        """)
        dialog.exec_()

    def create_tab_group(self, group_name, selected_indices, dialog):
        if not group_name or not selected_indices:
            QMessageBox.warning(self, "Error", "Please provide a group name and select at least one tab.")
            return
        group_id = str(uuid.uuid4())[:8]
        self.tab_groups[group_id] = selected_indices
        for i in selected_indices:
            self.tabs.setTabText(i, f"[{group_name}] {self.tabs.tabText(i)}")
        dialog.accept()

    def show_sessions(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Sessions")
        dialog.setMinimumSize(700, 400)
        layout = QVBoxLayout()
        session_list = QListWidget()
        for session in self.sessions:
            session_list.addItem(f"{session['name']} ({session['timestamp']})")
        session_list.itemClicked.connect(lambda item: self.load_session(self.sessions[session_list.currentRow()]))
        layout.addWidget(session_list)
        save_session_btn = QPushButton("Save Current Session")
        save_session_btn.clicked.connect(self.save_current_session)
        layout.addWidget(save_session_btn)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QListWidget { font-size: 13px; color: #333; padding: 10px; }
            QListWidget::item:hover { background: #ffe5cc; cursor: pointer; }
            QPushButton { background-color: #ff6b00; color: white; padding: 12px; border-radius: 8px; }
            QPushButton:hover { background-color: #e55f00; }
        """)
        dialog.exec_()

    def save_current_session(self):
        session_name, ok = QInputDialog.getText(self, "Save Session", "Session Name:")
        if ok and session_name:
            session = {
                "name": session_name,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tabs": [{"url": self.tabs.widget(i).url().toString(), "title": self.tabs.tabText(i)} for i in range(self.tabs.count())]
            }
            self.sessions.append(session)
            self.save_sessions()
            QMessageBox.information(self, "Session Saved", f"Session '{session_name}' saved.")

    def load_session(self, session):
        for i in range(self.tabs.count() - 1, -1, -1):
            self.close_tab(i)
        for tab in session["tabs"]:
            self.add_new_tab(QUrl(tab["url"]), tab["title"])
        QMessageBox.information(self, "Session Loaded", f"Session '{session['name']}' loaded.")

    def open_ai_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Sava AI Assistant")
        dialog.setMinimumSize(700, 500)
        layout = QVBoxLayout()
        mode_combo = QComboBox()
        mode_combo.addItems(self.ai.modes)
        mode_combo.setCurrentText(self.ai.current_mode)
        mode_combo.currentTextChanged.connect(lambda mode: setattr(self.ai, "current_mode", mode))
        layout.addWidget(QLabel("Select Mode:"))
        layout.addWidget(mode_combo)
        query_input = QLineEdit()
        query_input.setPlaceholderText("Ask Sava AI (e.g., 'sava:write a Python script' or 'sava:search AI trends')")
        layout.addWidget(QLabel("Query:"))
        layout.addWidget(query_input)
        response_label = QLabel("Sava AI will respond here.")
        response_label.setWordWrap(True)
        response_label.setMinimumHeight(200)
        layout.addWidget(QLabel("Response:"))
        layout.addWidget(response_label)
        submit_btn = QPushButton("Submit Query")
        submit_btn.clicked.connect(lambda: response_label.setText(self.ai.process_query(query_input.text())))
        layout.addWidget(submit_btn)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QLabel { font-size: 14px; color: #333; margin-top: 10px; }
            QLineEdit { 
                padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; background: #f9f9f9;
            }
            QLineEdit:focus { border: 1px solid #ff6b00; box-shadow: 0 0 6px rgba(255, 107, 0, 0.5); }
            QComboBox { 
                padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; background: #f9f9f9;
            }
            QComboBox:focus { border: 1px solid #ff6b00; }
            QPushButton { 
                background-color: #ff6b00; color: white; padding: 12px; border-radius: 8px; font-size: 14px;
                transition: background-color 0.3s, transform 0.1s;
            }
            QPushButton:hover { background-color: #e55f00; transform: scale(1.02); }
        """)
        dialog.exec_()

    def show_ai_response(self, response):
        dialog = QDialog(self)
        dialog.setWindowTitle("Sava AI Response")
        dialog.setMinimumSize(700, 400)
        layout = QVBoxLayout()
        response_label = QLabel(response)
        response_label.setWordWrap(True)
        layout.addWidget(response_label)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QLabel { font-size: 14px; color: #333; padding: 15px; }
        """)
        dialog.exec_()

    def show_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Browsing History")
        dialog.setMinimumSize(700, 400)
        layout = QVBoxLayout()
        history_list = QListWidget()
        for entry in self.history:
            history_list.addItem(f"{entry['timestamp']} - {entry['title']} ({entry['url']})")
        history_list.itemClicked.connect(lambda item: self.add_new_tab(QUrl(item.text().split(" ")[-1].strip("()"))))
        layout.addWidget(history_list)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QListWidget { font-size: 13px; color: #333; padding: 10px; }
            QListWidget::item:hover { background: #ffe5cc; cursor: pointer; }
        """)
        dialog.exec_()

    def show_downloads(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Downloads")
        dialog.setMinimumSize(700, 400)
        layout = QVBoxLayout()
        downloads_list = QListWidget()
        for entry in self.downloads:
            downloads_list.addItem(f"{entry['timestamp']} - {os.path.basename(entry['path'])} ({entry['url']})")
        layout.addWidget(downloads_list)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QListWidget { font-size: 13px; color: #333; padding: 10px; }
            QListWidget::item:hover { background: #ffe5cc; }
        """)
        dialog.exec_()

    def show_tab_overview(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Tab Overview")
        dialog.setMinimumSize(900, 600)
        layout = QGridLayout()
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            title = self.tabs.tabText(i)
            url = browser.url().toString()
            thumbnail = QLabel()
            thumbnail.setPixmap(QPixmap(100, 60))  # Placeholder for thumbnail
            thumbnail.setScaledContents(True)
            title_label = QLabel(f"<b>{title}</b><br>{url}")
            title_label.setWordWrap(True)
            title_label.mousePressEvent = lambda e, idx=i: [self.tabs.setCurrentIndex(idx), dialog.accept()]
            title_label.setCursor(QCursor(Qt.PointingHandCursor))
            layout.addWidget(thumbnail, i // 3, (i % 3) * 2)
            layout.addWidget(title_label, i // 3, (i % 3) * 2 + 1)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QLabel { font-size: 13px; color: #333; padding: 10px; }
            QLabel:hover { background: #ffe5cc; }
        """)
        dialog.exec_()

    def show_privacy_dashboard(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Privacy Dashboard")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        blocked_count = sum(self.tabs.widget(i).page().blocked_count for i in range(self.tabs.count()) if isinstance(self.tabs.widget(i).page(), AdBlockingWebEnginePage))
        layout.addWidget(QLabel(f"<h2>Privacy Dashboard</h2>"))
        layout.addWidget(QLabel(f"Ads/Trackers Blocked: {blocked_count}"))
        layout.addWidget(QLabel(f"Ad Blocking: {'Enabled' if self.ad_block_enabled else 'Disabled'}"))
        layout.addWidget(QLabel("<b>Tip:</b> Enable ad-blocking for enhanced privacy."))
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QLabel { font-size: 14px; color: #333; padding: 10px; }
        """)
        dialog.exec_()

    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumSize(600, 400)
        layout = QFormLayout()
        theme_combo = QComboBox()
        theme_combo.addItems(["Vivaldi", "Dark"])
        theme_combo.setCurrentText(self.theme)
        theme_combo.currentTextChanged.connect(lambda theme: setattr(self, "theme", theme))
        layout.addRow("Theme:", theme_combo)
        ad_block_check = QCheckBox("Enable Ad Blocking")
        ad_block_check.setChecked(self.ad_block_enabled)
        ad_block_check.stateChanged.connect(lambda state: setattr(self, "ad_block_enabled", state == Qt.Checked))
        layout.addRow("Ad Blocking:", ad_block_check)
        sidebar_check = QCheckBox("Show Sidebar")
        sidebar_check.setChecked(not self.sidebar.isHidden())
        sidebar_check.stateChanged.connect(lambda state: self.sidebar.setVisible(state == Qt.Checked))
        layout.addRow("Sidebar:", sidebar_check)
        homepage_input = QLineEdit()
        homepage_input.setText(self.settings.value("homepage", "file:///" + os.path.abspath(os.path.join("assets", "welcome.html"))))
        layout.addRow("Homepage:", homepage_input)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: [self.settings.setValue("theme", self.theme), self.settings.setValue("ad_block_enabled", self.ad_block_enabled), self.settings.setValue("homepage", homepage_input.text()), self.apply_theme(), dialog.accept()])
        layout.addRow(save_btn)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 12px; padding: 15px; }
            QLabel { font-size: 14px; color: #333; }
            QComboBox { padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
            QComboBox:focus { border: 1px solid #ff6b00; }
            QCheckBox { padding: 10px; font-size: 14px; }
            QLineEdit { padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
            QPushButton { background-color: #ff6b00; color: white; padding: 12px; border-radius: 8px; }
            QPushButton:hover { background-color: #e55f00; }
        """)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Roboto", 11))
    app.setStyle("Fusion")
    browser = SavaBrowser()
    browser.showMaximized()
    sys.exit(app.exec_())
