use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Serialize, Deserialize)]
pub struct HistoryEntry {
    url: String,
    timestamp: String,
}

pub struct HistoryManager {
    entries: Vec<HistoryEntry>,
}

impl HistoryManager {
    pub fn new() -> Self {
        HistoryManager {
            entries: vec![],
        }
    }

    pub fn add_entry(&mut self, url: String) {
        self.entries.push(HistoryEntry {
            url,
            timestamp: chrono::Local::now().to_string(),
        });
        // TODO: Zapisz do pliku
    }

    pub fn get_entries(&self) -> &Vec<HistoryEntry> {
        &self.entries
    }
}
