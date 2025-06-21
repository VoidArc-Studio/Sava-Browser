use keyring::Entry;
use aes_gcm::{Aes256Gcm, Key, Nonce}; // OrKey, OrNonce
use aes_gcm::aead::{Aead, KeyInit}; // Używaj KeyInit zamiast NewAead
use rand::RngCore;

pub struct PrivacyManager {
    keyring: Entry,
    encryption_key: Key<Aes256Gcm>,
}

impl PrivacyManager {
    pub fn new() -> Self {
        let keyring = Entry::new("sava-browser", "user").expect("Failed to initialize keyring");
        // Wygeneruj losowy 256-bitowy klucz (32 bajty)
        let mut key_bytes = [0u8; 32];
        rand::thread_rng().fill_bytes(&mut key_bytes);
        let encryption_key = Key::<Aes256Gcm>::from_slice(&key_bytes);
        PrivacyManager {
            keyring,
            encryption_key: *encryption_key,
        }
    }

    pub fn save_password(&self, service: &str, password: &str) -> Result<(), keyring::Error> {
        self.keyring.set_password(&format!("{}:{}", service, password))?;
        Ok(())
    }

    pub fn clear_cookies(&self) {
        // TODO: Wyczyść ciasteczka z WebView
        println!("Cookies cleared");
    }

    pub fn encrypt_data(&self, data: &str) -> (Vec<u8>, [u8; 12]) {
        let cipher = Aes256Gcm::new(&self.encryption_key);
        // Wygeneruj losowy nonce (12 bajtów)
        let mut nonce_bytes = [0u8; 12];
        rand::thread_rng().fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);
        let encrypted = cipher.encrypt(nonce, data.as_bytes()).expect("Encryption failed");
        (encrypted, nonce_bytes)
    }

    pub fn decrypt_data(&self, encrypted: &[u8], nonce_bytes: &[u8; 12]) -> String {
        let cipher = Aes256Gcm::new(&self.encryption_key);
        let nonce = Nonce::from_slice(nonce_bytes);
        let decrypted = cipher.decrypt(nonce, encrypted).expect("Decryption failed");
        String::from_utf8(decrypted).expect("Invalid UTF-8")
    }

    pub fn block_javascript(&self, _url: &str) -> bool {
        // TODO: Sprawdź ustawienia dla domeny
        false
    }

    pub fn block_fingerprinting(&self) -> bool {
        true
    }
}
