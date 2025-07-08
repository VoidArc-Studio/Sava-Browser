const axios = require('axios');

async function askAI() {
  const input = document.getElementById('ai-input').value;
  try {
    const response = await axios.post('http://localhost:3000/api/ai/query', { prompt: input });
    const content = document.getElementById('content');
    content.innerHTML += `<p><strong>AI Response:</strong> ${response.data}</p>`;
  } catch (error) {
    console.error('AI query failed:', error);
    document.getElementById('content').innerHTML += '<p>Error: Could not reach AI service</p>';
  }
}
