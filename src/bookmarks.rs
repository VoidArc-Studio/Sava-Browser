use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Serialize, Deserialize)]
pub struct Bookmark {
    url: String,
    title: String,
}

pub struct BookmarkManager {
    bookmarks: Vec<Bookmark>,
}

impl BookmarkManager {
    pub fn new() -> Self {
        BookmarkManager {
            bookmarks: vec![],
        }
    }

    pub fn add_bookmark(&mut self, url: String) {
        self.bookmarks.push(Bookmark {
            url,
            title: "New Bookmark".to_string(), // TODO: Pobierz tytuł strony
        });
        // TODO: Zapisz do pliku
    }

    pub fn get_bookmarks(&self) -> &Vec<Bookmark> {
        &self.bookmarks
    }
}
