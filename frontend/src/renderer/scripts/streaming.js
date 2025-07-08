function initStreaming() {
  const content = document.getElementById('content');
  content.innerHTML = `
    <h2>Streaming</h2>
    <select id="streaming-service">
      <option value="spotify">Spotify</option>
      <option value="youtube">YouTube Music</option>
    </select>
    <iframe id="streaming-iframe" style="width:100%;height:80%"></iframe>
  `;
  const select = document.getElementById('streaming-service');
  select.addEventListener('change', () => {
    const iframe = document.getElementById('streaming-iframe');
    if (select.value === 'spotify') iframe.src = 'https://open.spotify.com/embed';
    else if (select.value === 'youtube') iframe.src = 'https://music.youtube.com';
  });
}
