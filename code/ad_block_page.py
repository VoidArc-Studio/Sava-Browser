from PyQt5.QtWebEngineWidgets import QWebEnginePage

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
