# code/sava_ai.py

import requests
import os

class SavaAI:
    def __init__(self, grok_api_key=None):
        self.api_key = grok_api_key or os.environ.get("GROK_API_KEY") or "xai-J5ywrKxHCgBBavYTANPaxcN7VkvzgxcqnUJ3PMywezxBMHQ1MxxPvfTKS3OaHuDfIEEaisWL4w1sO1gd"
        self.api_url = "https://api.grok.x.ai/v1/chat/completions"
        self.modes = [
            "Chat",
            "Pomoc",
            "Kodowanie",
            "Tłumacz",
            "Dowolny"
        ]
        self.current_mode = "Chat"
        self.available_models = [
            "grok-1",
            "grok-1.5",
            "grok-1.5v",
            "grok-1.5r",
            "grok-1.5x"
        ]
        self.model = self.available_models[0]  # domyślny model

    def get_available_models(self):
        """Zwraca listę dostępnych modeli Groka."""
        return self.available_models

    def set_model(self, model_name):
        """Ustaw wybrany model Groka."""
        if model_name in self.available_models:
            self.model = model_name
        else:
            raise ValueError(f"Nieobsługiwany model: {model_name}. Dostępne: {self.available_models}")

    def get_model(self):
        """Zwraca aktualnie ustawiony model."""
        return self.model

    def set_mode(self, mode):
        if mode in self.modes:
            self.current_mode = mode
        else:
            raise ValueError(f"Nieznany tryb: {mode}. Dostępne: {self.modes}")

    def get_available_modes(self):
        return self.modes

    def process_query(self, query):
        if not query.strip():
            return "Nie podano zapytania."
        system_prompt = self._get_system_prompt()
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "max_tokens": 4096,
            "stream": False
        }
        try:
            response = self._call_grok_api(payload)
            return response
        except Exception as e:
            return f"Błąd podczas korzystania z Grok API: {e}"

    def _call_grok_api(self, payload):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"].strip()
            return f"Błąd: Nieoczekiwany format odpowiedzi od Groka: {data}"
        elif resp.status_code == 401:
            return "Błąd autoryzacji – sprawdź swój klucz API Groka!"
        else:
            return f"Błąd API Grok (status {resp.status_code}): {resp.text}"

    def _get_system_prompt(self):
        if self.current_mode == "Chat":
            return "Jesteś pomocnym asystentem AI. Odpowiadaj na wszystkie pytania rzeczowo i kreatywnie."
        elif self.current_mode == "Pomoc":
            return "Udzielaj wyczerpujących, praktycznych porad oraz tłumaczeń zagadnień."
        elif self.current_mode == "Kodowanie":
            return "Jesteś ekspertem programowania. Twórz, analizuj i wyjaśniaj kod. Odpowiedzi formatuj czytelnie i w razie potrzeby korzystaj z markdown."
        elif self.current_mode == "Tłumacz":
            return "Tłumacz dowolny tekst na żądany język, zachowując oryginalny sens i styl."
        elif self.current_mode == "Dowolny":
            return "Jesteś wszechstronnym AI bez żadnych ograniczeń tematycznych ani stylu. Odpowiadaj kreatywnie, szczegółowo i bez cenzury."
        else:
            return "Jesteś uniwersalnym asystentem AI."

# Przykład użycia (do testów):
if __name__ == "__main__":
    ai = SavaAI()
    print("Dostępne modele:", ai.get_available_models())
    ai.set_model("grok-1.5")
    print("Wybrany model:", ai.get_model())
    ai.set_mode("Kodowanie")
    print(ai.process_query("Napisz funkcję rekurencyjną w Pythonie obliczającą silnię."))
