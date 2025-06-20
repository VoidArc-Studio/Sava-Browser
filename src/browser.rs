use wry::webview::{WebViewBuilder, WebContext};
use adblock::engine::Engine;
use rand::seq::SliceRandom;
use crate::{bookmarks::BookmarkManager, history::HistoryManager};

pub struct Browser {
    webviews: Vec<wry::webview::WebView>,
    tabs: Vec<String>,
    current_tab: usize,
    incognito: bool,
    adblock: Engine,
    bookmarks: BookmarkManager,
    history: HistoryManager,
}

impl Browser {
    pub fn new() -> Self {
        let mut adblock = Engine::default();
        adblock.use_default_lists().expect("Failed to load adblock lists");
        Browser {
            webviews: vec![],
            tabs: vec!["https://startpage.com".to_string()],
            current_tab: 0,
            incognito: false,
            adblock,
            bookmarks: BookmarkManager::new(),
            history: HistoryManager::new(),
        }
    }

    pub fn navigate(&mut self, url: String) {
        if self.adblock.check_network_urls(&url, "", "").should_block {
            println!("Blocked ad/tracker: {}", url);
            return;
        }

        let user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ];
        let user_agent = user_agents.choose(&mut rand::thread_rng()).unwrap();

        let webview = WebViewBuilder::new()
            .with_url(&url)
            .with_incognito(self.incognito)
            .with_user_agent(user_agent)
            .with_javascript_enabled(!self.block_javascript(&url))
            .build()
            .unwrap();

        self.webviews[self.current_tab] = webview;
        self.tabs[self.current_tab] = url.clone();
        if !self.incognito {
            self.history.add_entry(url);
        }
    }

    pub fn new_tab(&mut self) {
        self.tabs.push("https://startpage.com".to_string());
        self.webviews.push(WebViewBuilder::new().build().unwrap());
        self.current_tab = self.tabs.len() - 1;
        self.navigate(self.tabs[self.current_tab].clone());
    }

    pub fn close_tab(&mut self, index: usize) {
        if self.tabs.len() > 1 && index < self.tabs.len() {
            self.tabs.remove(index);
            self.webviews.remove(index);
            self.current_tab = self.current_tab.min(self.tabs.len() - 1);
        }
    }

    pub fn toggle_incognito(&mut self) {
        self.incognito = !self.incognito;
        if self.incognito {
            self.webviews.clear();
            self.tabs = vec!["https://startpage.com".to_string()];
            self.current_tab = 0;
            self.navigate(self.tabs[0].clone());
        }
        println!("Incognito mode: {}", self.incognito);
    }

    pub fn add_bookmark(&mut self, url: String) {
        if !self.incognito {
            self.bookmarks.add_bookmark(url);
        }
    }

    fn block_javascript(&self, url: &str) -> bool {
        // TODO: Sprawdź ustawienia dla danej domeny
        false
    }
}
