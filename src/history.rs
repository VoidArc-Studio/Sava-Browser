use serde::{Deserialize, Serialize};
use crate::privacy::PrivacyManager;

#[derive(Serialize, Deserialize)]
pub struct HistoryEntry {
    url: String,
    timestamp: String,
}

pub struct HistoryManager {
    entries: Vec<HistoryEntry>,
    privacy: PrivacyManager,
}

impl HistoryManager {
    pub fn new() -> Self {
        HistoryManager {
            entries: vec![],
            privacy: PrivacyManager::new(),
        }
    }

    pub fn add_entry(&mut self, url: String) {
        let encrypted_url = self.privacy.encrypt_data(&url);
        self.entries.push(HistoryEntry {
            url: String::from_utf8(encrypted_url).unwrap(),
            timestamp: chrono::Local::now().to_string(),
        });
        // TODO: Zapisz do pliku
    }

    pub fn get_entries(&self) -> &Vec<HistoryEntry> {
        &self.entries
    }
}
