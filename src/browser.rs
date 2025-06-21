use wry::webview::{WebViewBuilder, WebView};
use rand::seq::SliceRandom;
use crate::{bookmarks::BookmarkManager, history::HistoryManager, settings::Settings};

pub struct Browser {
    webviews: Vec<WebView>,
    tabs: Vec<String>,
    current_tab: usize,
    incognito: bool,
    bookmarks: BookmarkManager,
    history: HistoryManager,
    settings: Settings,
}

impl Browser {
    pub fn new() -> Self {
        // Uwaga: Tworzenie WebView wymaga Window (z Wry/Tao), więc poniższy kod jest przykładowy.
        // W praktyce musisz przekazać Window do WebViewBuilder::new(window)
        Browser {
            webviews: Vec::new(),
            tabs: vec!["https://startpage.com".to_string()],
            current_tab: 0,
            incognito: false,
            bookmarks: BookmarkManager::new(),
            history: HistoryManager::new(),
            settings: Settings::load(),
        }
    }

    pub fn navigate(&mut self, url: String, window: wry::application::window::Window) {
        // Możesz dodać tu własny prosty blok reklam/domen

        let user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ];
        let user_agent = user_agents.choose(&mut rand::thread_rng()).unwrap();

        let webview = WebViewBuilder::new(window)
            .with_url(&url)
            .with_user_agent(user_agent)
            .with_incognito(self.incognito)
            .with_javascript_enabled(!self.settings.block_javascript)
            .with_webgl_enabled(!self.settings.block_fingerprinting)
            .build()
            .expect("Failed to build webview");

        if self.webviews.len() <= self.current_tab {
            self.webviews.push(webview);
        } else {
            self.webviews[self.current_tab] = webview;
        }
        self.tabs[self.current_tab] = url.clone();
        if !self.incognito {
            self.history.add_entry(url);
        }
    }

    pub fn new_tab(&mut self, window: wry::application::window::Window) {
        self.tabs.push(self.settings.homepage.clone());
        // Przy dodawaniu nowej karty przekazuj Window!
        let webview = WebViewBuilder::new(window)
            .with_url(&self.settings.homepage)
            .with_incognito(self.incognito)
            .with_javascript_enabled(!self.settings.block_javascript)
            .with_webgl_enabled(!self.settings.block_fingerprinting)
            .build()
            .expect("Failed to build webview");
        self.webviews.push(webview);
        self.current_tab = self.tabs.len() - 1;
    }

    pub fn close_tab(&mut self, index: usize) {
        if self.tabs.len() > 1 && index < self.tabs.len() {
            self.tabs.remove(index);
            self.webviews.remove(index);
            self.current_tab = self.current_tab.min(self.tabs.len() - 1);
        }
    }

    pub fn switch_tab(&mut self, index: usize, window: wry::application::window::Window) {
        if index < self.tabs.len() {
            self.current_tab = index;
            // Odśwież webview dla nowej karty
            let url = self.tabs[self.current_tab].clone();
            self.navigate(url, window);
        }
    }

    pub fn toggle_incognito(&mut self, window: wry::application::window::Window) {
        self.incognito = !self.incognito;
        if self.incognito {
            self.webviews.clear();
            self.tabs = vec![self.settings.homepage.clone()];
            self.current_tab = 0;
            self.navigate(self.tabs[0].clone(), window);
        }
        println!("Incognito mode: {}", self.incognito);
    }

    pub fn add_bookmark(&mut self, url: String) {
        if !self.incognito {
            self.bookmarks.add_bookmark(url);
        }
    }

    pub fn update_settings(&mut self, theme: String, homepage: String, block_ads: bool, block_js: bool) {
        self.settings.theme = theme;
        self.settings.homepage = homepage;
        self.settings.block_ads = block_ads;
        self.settings.block_javascript = block_js;
        self.settings.save();
    }
}
