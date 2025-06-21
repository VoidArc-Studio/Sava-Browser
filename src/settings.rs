use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Serialize, Deserialize)]
pub struct Settings {
    pub theme: String,
    pub homepage: String,
    pub ai_model: String,
    pub block_ads: bool,
    pub block_javascript: bool,
    pub block_fingerprinting: bool,
}

impl Settings {
    pub fn load() -> Self {
        // TODO: Wczytaj z pliku JSON
        Settings {
            theme: "dark".to_string(),
            homepage: "https://startpage.com".to_string(),
            ai_model: "default".to_string(),
            block_ads: true,
            block_javascript: false,
            block_fingerprinting: true,
        }
    }

    pub fn save(&self) {
        // TODO: Zapisz do pliku JSON
        println!("Settings saved: {:?}", self);
    }
}
