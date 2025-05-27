async function enableVPN() {
  try {
    console.log('VPN włączony (mock)');
    return { status: 'enabled', message: 'VPN aktywny (mock)' };
  } catch (error) {
    console.error('Błąd VPN:', error);
    return { status: 'error', message: 'Nie udało się włączyć VPN' };
  }
}

async function disableVPN() {
  try {
    console.log('VPN wyłączony (mock)');
    return { status: 'disabled', message: 'VPN nieaktywny' };
  } catch (error) {
    console.error('Błąd VPN:', error);
    return { status: 'error', message: 'Nie udało się wyłączyć VPN' };
  }
}

module.exports = { enableVPN, disableVPN };
