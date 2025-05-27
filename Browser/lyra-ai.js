const axios = require('axios');

async function queryLyraAI(query) {
  try {
    // Mock API Gemini
    const geminiResponse = await axios.post('https://api.gemini.mock/v1/completions', {
      prompt: query,
      max_tokens: 100,
    }, {
      headers: { 'Authorization': 'Bearer MOCK_GEMINI_API_KEY' },
    });

    // Mock API Groka (xAI)
    const grokResponse = await axios.post('https://api.x.ai/grok', {
      query,
    }, {
      headers: { 'Authorization': 'Bearer MOCK_XAI_API_KEY' },
    });

    return `Lyra AI: Odpowiedź Gemini: ${geminiResponse.data.choices[0].text || 'Brak odpowiedzi'}\nOdpowiedź Groka: ${grokResponse.data.response || 'Brak odpowiedzi'}`;
  } catch (error) {
    console.error('Błąd Lyra AI:', error.message);
    return 'Lyra AI: Nie udało się uzyskać odpowiedzi. Spróbuj ponownie.';
  }
}

module.exports = { queryLyraAI };
