use slint::SlintWeak;
use std::sync::Arc;
use tokio::sync::Mutex;

mod browser;
mod ui;
mod ai_assistant;
mod integrations;
mod settings;
mod privacy;
mod bookmarks;
mod history;
mod plugins;

use browser::Browser;
use ui::AppWindow;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Inicjalizacja Slint
    let ui = AppWindow::new()?;
    let ui_handle: SlintWeak<AppWindow> = ui.as_weak();

    // Inicjalizacja przeglądarki
    let browser = Arc::new(Mutex::new(Browser::new()));
    let browser_clone = Arc::clone(&browser);

    // Callbacki dla UI
    ui.on_open_url(move |url| {
        let browser = Arc::clone(&browser_clone);
        tokio::spawn(async move {
            let mut browser = browser.lock().await;
            browser.navigate(url.to_string());
        });
    });

    ui.on_new_tab(move || {
        let browser = Arc::clone(&browser_clone);
        tokio::spawn(async move {
            let mut browser = browser.lock().await;
            browser.new_tab();
        });
    });

    ui.on_close_tab(move |index| {
        let browser = Arc::clone(&browser_clone);
        tokio::spawn(async move {
            let mut browser = browser.lock().await;
            browser.close_tab(index as usize);
        });
    });

    ui.on_toggle_incognito(move || {
        let browser = Arc::clone(&browser_clone);
        tokio::spawn(async move {
            let mut browser = browser.lock().await;
            browser.toggle_incognito();
        });
    });

    ui.on_add_bookmark(move |url| {
        let browser = Arc::clone(&browser_clone);
        tokio::spawn(async move {
            let mut browser = browser.lock().await;
            browser.add_bookmark(url.to_string());
        });
    });

    // Inicjalizacja asystenta AI
    let ai = ai_assistant::Assistant::new();
    ui.on_ai_request(move |query, mode| {
        let ai = ai.clone();
        tokio::spawn(async move {
            let response = ai.handle_request(query.to_string(), mode).await;
            // TODO: Wyświetl w UI
            println!("Sava AI Response: {}", response);
        });
    });

    // Uruchomienie UI
    ui.run()?;
    Ok(())
}
