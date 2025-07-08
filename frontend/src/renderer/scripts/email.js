function initEmail() {
  const content = document.getElementById('content');
  content.innerHTML = `
    <h2>Poczta</h2>
    <input id="email-user" placeholder="Email">
    <input id="email-pass" type="password" placeholder="Hasło">
    <button onclick="checkEmail()">Sprawdź pocztę</button>
    <div id="email-content"></div>
  `;
}

async function checkEmail() {
  const user = document.getElementById('email-user').value;
  const pass = document.getElementById('email-pass').value;
  const content = document.getElementById('email-content');
  content.innerHTML = 'Ładowanie...';
  // Tu można dodać komunikację z backendem (email_service.cr)
  content.innerHTML = '<p>Funkcja poczty niezaimplementowana w pełni</p>';
}
