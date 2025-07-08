function initNotes() {
  const content = document.getElementById('content');
  content.innerHTML = '<h2>Notatnik</h2><textarea id="notes" style="width:100%;height:80%"></textarea>';
  const textarea = document.getElementById('notes');
  textarea.value = localStorage.getItem('notes') || '';
  textarea.addEventListener('input', () => {
    localStorage.setItem('notes', textarea.value);
  });
}
