use keyring::Entry;
use aes_gcm::{Aes256Gcm, Key, Nonce};
use aes_gcm::aead::{Aead, KeyInit};
use rand::RngCore;
use base64::{engine::general_purpose, Engine as _};

pub struct PrivacyManager {
    keyring: Entry,
    encryption_key: Key<Aes256Gcm>,
}

impl PrivacyManager {
    pub fn new() -> Self {
        let keyring = Entry::new("sava-browser", "user").expect("Failed to initialize keyring");
        // Próbuj pobrać klucz z keyring, jeśli nie ma - generuj i zapisz
        let encryption_key = match keyring.get_password() {
            Ok(stored) => {
                let key_bytes = general_purpose::STANDARD.decode(stored).expect("Failed to decode key from keyring");
                Key::<Aes256Gcm>::from_slice(&key_bytes).clone()
            }
            Err(_) => {
                let mut key_bytes = [0u8; 32];
                rand::thread_rng().fill_bytes(&mut key_bytes);
                // Zapisz klucz do keyring jako base64
                let key_b64 = general_purpose::STANDARD.encode(&key_bytes);
                keyring.set_password(&key_b64).expect("Failed to store key in keyring");
                Key::<Aes256Gcm>::from_slice(&key_bytes).clone()
            }
        };
        PrivacyManager {
            keyring,
            encryption_key,
        }
    }

    pub fn save_password(&self, service: &str, password: &str) -> Result<(), keyring::Error> {
        // Zapisz hasło dla danej usługi do keyring
        let entry = Entry::new("sava-browser", service)?;
        entry.set_password(password)
    }

    pub fn clear_cookies(&self) {
        // TODO: Wyczyść ciasteczka z WebView
        println!("Cookies cleared");
    }

    pub fn encrypt_data(&self, data: &str) -> (Vec<u8>, [u8; 12]) {
        let cipher = Aes256Gcm::new(&self.encryption_key);
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
