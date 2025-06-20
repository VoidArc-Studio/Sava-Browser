pub struct PluginManager {
    plugins: Vec<String>,
}

impl PluginManager {
    pub fn new() -> Self {
        PluginManager {
            plugins: vec![],
        }
    }

    pub fn load_plugin(&mut self, path: &str) {
        // TODO: Wczytywanie wtyczek (np. WebAssembly)
        self.plugins.push(path.to_string());
    }
}
