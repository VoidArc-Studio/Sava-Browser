const axios = require('axios');

async function checkAd(url) {
  try {
    const response = await axios.get(`http://localhost:3000/api/adblock/filter/${encodeURIComponent(url)}`);
    return response.data === 'true';
  } catch (error) {
    console.error('Adblock check failed:', error);
    return false;
  }
}

document.getElementById('webview').addEventListener('will-navigate', async (event) => {
  if (await checkAd(event.url)) {
    event.preventDefault();
    console.log(`Blocked ad/tracker: ${event.url}`);
  }
});
