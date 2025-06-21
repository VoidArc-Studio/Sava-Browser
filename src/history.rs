use serde::{Deserialize, Serialize};
use crate::privacy::PrivacyManager;
use std::fs;
use std::io::{self, Write};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct EncryptedField {
    data: Vec<u8>,
    nonce: [u8; 12],
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct HistoryEntry {
    url: EncryptedField,
    timestamp: u64,
}

#[derive(Debug, Clone)]
pub struct HistoryManager {
    history: Vec<HistoryEntry>,
    #[serde(skip)]
    privacy: PrivacyManager,
}

impl HistoryManager {
    pub fn new() -> Self {
        let history = Self::load_from_file().unwrap_or_default();
        HistoryManager {
            history,
            privacy: PrivacyManager::new(),
        }
    }

    pub fn add_entry(&mut self, url: String) {
        let (encrypted_data, nonce) = self.privacy.encrypt_data(&url);
        let entry = HistoryEntry {
            url: EncryptedField { data: encrypted_data, nonce },
            timestamp: chrono::Utc::now().timestamp() as u64,
        };
        self.history.push(entry);
        let _ = self.save_to_file();
    }

    pub fn get_history(&self) -> Vec<String> {
        self.history.iter()
            .map(|h| self.privacy.decrypt_data(&h.url.data, &h.url.nonce))
            .collect()
    }

    fn save_to_file(&self) -> io::Result<()> {
        let serializable = HistoryManagerSer {
            history: self.history.clone(),
        };
        let json = serde_json::to_string_pretty(&serializable)?;
        let mut file = fs::File::create("history.json")?;
        file.write_all(json.as_bytes())?;
        Ok(())
    }

    fn load_from_file() -> Option<Vec<HistoryEntry>> {
        if let Ok(data) = fs::read_to_string("history.json") {
            if let Ok(deserialized) = serde_json::from_str::<HistoryManagerSer>(&data) {
                return Some(deserialized.history);
            }
        }
        None
    }
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
struct HistoryManagerSer {
    history: Vec<HistoryEntry>,
}
