use wasm_bindgen::prelude::*;

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
        // TODO: Wczytywanie wtyczek WebAssembly
        self.plugins.push(path.to_string());
        println!("Loaded plugin: {}", path);
    }
}
