slint::include_modules!();

pub struct AppWindow {
    ui: slint::Window,
}

impl AppWindow {
    pub fn new() -> Result<Self, slint::PlatformError> {
        let ui = AppWindow::new()?;
        Ok(AppWindow { ui })
    }

    pub fn run(&self) -> Result<(), slint::PlatformError> {
        self.ui.run()
    }

    pub fn as_weak(&self) -> slint::Weak<AppWindow> {
        self.ui.as_weak()
    }

    pub fn on_open_url<F: Fn(String) + 'static>(&self, callback: F) {
        self.ui.on_open_url(callback);
    }

    pub fn on_new_tab<F: Fn() + 'static>(&self, callback: F) {
        self.ui.on_new_tab(callback);
    }

    pub fn on_close_tab<F: Fn(i32) + 'static>(&self, callback: F) {
        self.ui.on_close_tab(callback);
    }

    pub fn on_toggle_incognito<F: Fn() + 'static>(&self, callback: F) {
        self.ui.on_toggle_incognito(callback);
    }

    pub fn on_add_bookmark<F: Fn(String) + 'static>(&self, callback: F) {
        self.ui.on_add_bookmark(callback);
    }

    pub fn on_ai_request<F: Fn(String, i32) + 'static>(&self, callback: F) {
        self.ui.on_ai_request(callback);
    }
}
