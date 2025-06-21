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
use ui::AppWindowWrapper; // Wrapper, nie ten typ z .slint

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Inicjalizacja Slint UI
    let ui = AppWindowWrapper::new()?; // Wrapper zawiera ui: AppWindow (.slint)
    let ui_handle = ui.as_weak();

    // Inicjalizacja przeglądarki
    let browser = Arc::new(Mutex::new(Browser::new()));
    let browser_clone = Arc::clone(&browser);

    // Callbacki UI
    ui.on_open_url({
        let browser = Arc::clone(&browser_clone);
        move |url| {
            let browser = Arc::clone(&browser);
            tokio::spawn(async move {
                let mut browser = browser.lock().await;
                // Potrzebujesz Window dla WebViewBuilder!
                // browser.navigate(url.to_string(), window);
                browser.navigate(url.to_string());
            });
        }
    });

    ui.on_new_tab({
        let browser = Arc::clone(&browser_clone);
        move || {
            let browser = Arc::clone(&browser);
            tokio::spawn(async move {
                let mut browser = browser.lock().await;
                // browser.new_tab(window);
                browser.new_tab();
            });
        }
    });

    ui.on_close_tab({
        let browser = Arc::clone(&browser_clone);
        move |index| {
            let browser = Arc::clone(&browser);
            tokio::spawn(async move {
                let mut browser = browser.lock().await;
                browser.close_tab(index as usize);
            });
        }
    });

    ui.on_switch_tab({
        let browser = Arc::clone(&browser_clone);
        move |index| {
            let browser = Arc::clone(&browser);
            tokio::spawn(async move {
                let mut browser = browser.lock().await;
                // browser.switch_tab(index as usize, window);
                browser.switch_tab(index as usize);
            });
        }
    });

    ui.on_toggle_incognito({
        let browser = Arc::clone(&browser_clone);
        move || {
            let browser = Arc::clone(&browser);
            tokio::spawn(async move {
                let mut browser = browser.lock().await;
                // browser.toggle_incognito(window);
                browser.toggle_incognito();
            });
        }
    });

    ui.on_add_bookmark({
        let browser = Arc::clone(&browser_clone);
        move |url| {
            let browser = Arc::clone(&browser);
            tokio::spawn(async move {
                let mut browser = browser.lock().await;
                browser.add_bookmark(url.to_string());
            });
        }
    });

    // Inicjalizacja asystenta AI
    let ai = ai_assistant::Assistant::new();
    ui.on_ai_request({
        let ai = ai.clone();
        move |query, mode| {
            let ai = ai.clone();
            tokio::spawn(async move {
                let response = ai.handle_request(query.to_string(), mode).await;
                // TODO: Wyświetl w UI
                println!("Sava AI Response: {}", response);
            });
        }
    });

    ui.on_save_settings({
        let browser = Arc::clone(&browser_clone);
        move |theme, homepage, block_ads, block_js| {
            let browser = Arc::clone(&browser);
            tokio::spawn(async move {
                let mut browser = browser.lock().await;
                browser.update_settings(
                    theme.to_string(),
                    homepage.to_string(),
                    block_ads,
                    block_js,
                );
            });
        }
    });

    // Uruchomienie UI
    ui.run()?;
    Ok(())
}
