use serde::{Deserialize, Serialize};
use crate::privacy::PrivacyManager;

#[derive(Serialize, Deserialize)]
pub struct Bookmark {
    url: String,
    title: String,
    folder: String,
}

pub struct BookmarkManager {
    bookmarks: Vec<Bookmark>,
    privacy: PrivacyManager,
}

impl BookmarkManager {
    pub fn new() -> Self {
        BookmarkManager {
            bookmarks: vec![],
            privacy: PrivacyManager::new(),
        }
    }

    pub fn add_bookmark(&mut self, url: String) {
        let encrypted_url = self.privacy.encrypt_data(&url);
        let bookmark = Bookmark {
            url: String::from_utf8(encrypted_url).unwrap(),
            title: "New Bookmark".to_string(), // TODO: Pobierz tytuł strony
            folder: "Default".to_string(),
        };
        self.bookmarks.push(bookmark);
        // TODO: Zapisz do pliku
    }

    pub fn get_bookmarks(&self) -> &Vec<Bookmark> {
        &self.bookmarks
    }
}
