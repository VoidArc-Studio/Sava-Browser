use serde::{Deserialize, Serialize};
use std::fs;
use std::io::{self, Write};

#[derive(Serialize, Deserialize, Debug, Clone)]
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
        let path = "settings.json";
        if let Ok(data) = fs::read_to_string(path) {
            if let Ok(settings) = serde_json::from_str(&data) {
                return settings;
            }
        }
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
        let path = "settings.json";
        match serde_json::to_string_pretty(self) {
            Ok(json) => {
                if let Err(e) = fs::File::create(path).and_then(|mut f| f.write_all(json.as_bytes())) {
                    eprintln!("Błąd zapisu ustawień: {e}");
                } else {
                    println!("Settings saved: {:?}", self);
                }
            }
            Err(e) => eprintln!("Błąd serializacji ustawień: {e}"),
        }
    }
}
