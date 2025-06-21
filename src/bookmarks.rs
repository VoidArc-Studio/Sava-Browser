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
pub struct Bookmark {
    url: EncryptedField,
    title: String,
    folder: String,
}

#[derive(Debug, Clone)]
pub struct BookmarkManager {
    bookmarks: Vec<Bookmark>,
    #[serde(skip)]
    privacy: PrivacyManager,
}

impl BookmarkManager {
    pub fn new() -> Self {
        let bookmarks = Self::load_from_file().unwrap_or_default();
        BookmarkManager {
            bookmarks,
            privacy: PrivacyManager::new(),
        }
    }

    pub fn add_bookmark(&mut self, url: String) {
        let (encrypted_data, nonce) = self.privacy.encrypt_data(&url);
        let bookmark = Bookmark {
            url: EncryptedField { data: encrypted_data, nonce },
            title: "New Bookmark".to_string(),
            folder: "Default".to_string(),
        };
        self.bookmarks.push(bookmark);
        let _ = self.save_to_file();
    }

    pub fn get_bookmarks(&self) -> Vec<String> {
        self.bookmarks.iter()
            .map(|b| self.privacy.decrypt_data(&b.url.data, &b.url.nonce))
            .collect()
    }

    fn save_to_file(&self) -> io::Result<()> {
        let serializable = BookmarkManagerSer {
            bookmarks: self.bookmarks.clone(),
        };
        let json = serde_json::to_string_pretty(&serializable)?;
        let mut file = fs::File::create("bookmarks.json")?;
        file.write_all(json.as_bytes())?;
        Ok(())
    }

    fn load_from_file() -> Option<Vec<Bookmark>> {
        if let Ok(data) = fs::read_to_string("bookmarks.json") {
            if let Ok(deserialized) = serde_json::from_str::<BookmarkManagerSer>(&data) {
                return Some(deserialized.bookmarks);
            }
        }
        None
    }
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
struct BookmarkManagerSer {
    bookmarks: Vec<Bookmark>,
}
