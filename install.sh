#!/bin/bash

# Skrypt instalacyjny dla Sava Browser
# Wymagania: Node.js, npm, Crystal, shards, Electron

set -e

echo "Rozpoczynanie instalacji Sava Browser..."

# 1. Sprawdzenie wymaganych narzędzi
if ! command -v node &> /dev/null; then
  echo "Node.js nie jest zainstalowany. Instalowanie..."
  sudo apt update
  sudo apt install -y nodejs npm
fi

if ! command -v crystal &> /dev/null; then
  echo "Crystal nie jest zainstalowany. Instalowanie..."
  curl -sSL https://dist.crystal-lang.org/apt/setup.sh | sudo bash
  sudo apt install -y crystal
fi

if ! command -v shards &> /dev/null; then
  echo "Shards nie jest zainstalowany. Instalowanie..."
  sudo apt install -y shards
fi

# 2. Instalacja zależności frontendu
echo "Instalowanie zależności frontendu..."
cd frontend
npm install
cd ..

# 3. Instalacja zależności backendu
echo "Instalowanie zależności backendu..."
cd backend
shards install
cd ..

# 4. Budowanie aplikacji Electron
echo "Budowanie aplikacji Electron..."
cd frontend
npm run build
cd ..

# 5. Kopiowanie plików do /opt/sava-browser
echo "Kopiowanie plików do /opt/sava-browser..."
sudo mkdir -p /opt/sava-browser
sudo cp -r frontend/dist/* /opt/sava-browser/
sudo cp -r backend /opt/sava-browser/backend
sudo cp -r frontend/src/renderer/assets /opt/sava-browser/assets
sudo chmod -R 755 /opt/sava-browser

# 6. Kopiowanie pliku .desktop
echo "Kopiowanie pliku .desktop do /usr/share/applications..."
sudo cp install-files/sava-browser.desktop /usr/share/applications/
sudo chmod 644 /usr/share/applications/sava-browser.desktop

# 7. Aktualizacja cache ikon
echo "Aktualizowanie cache ikon..."
sudo update-desktop-database

echo "Instalacja zakończona! Możesz uruchomić Sava Browser z menu aplikacji."
