const tabs = document.querySelectorAll('#tabs .tab');
const panels = document.querySelectorAll('.panel');

tabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    tabs.forEach((t) => t.classList.remove('active'));
    panels.forEach((panel) => panel.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.target).classList.add('active');
  });
});

async function postJSON(url, data) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || response.statusText);
  }
  return response.json();
}

document.getElementById('chat-send').addEventListener('click', async () => {
  const textarea = document.getElementById('chat-input');
  const output = document.getElementById('chat-response');
  output.textContent = '...';
  try {
    const data = await postJSON('/chat', { message: textarea.value });
    output.textContent = data.response;
  } catch (err) {
    output.textContent = `Error: ${err.message}`;
  }
});

document.getElementById('rag-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const fileInput = document.getElementById('rag-file');
  const results = document.getElementById('rag-results');
  const file = fileInput.files[0];
  if (!file) {
    results.textContent = 'Select a file first.';
    return;
  }
  const form = new FormData();
  form.append('file', file);
  results.textContent = 'Uploading...';
  try {
    const response = await fetch('/rag/ingest', { method: 'POST', body: form });
    results.textContent = JSON.stringify(await response.json(), null, 2);
  } catch (err) {
    results.textContent = `Error: ${err.message}`;
  }
});

document.getElementById('rag-search').addEventListener('click', async () => {
  const queryInput = document.getElementById('rag-query');
  const results = document.getElementById('rag-results');
  results.textContent = 'Searching...';
  try {
    const data = await postJSON('/rag/query', { query: queryInput.value, top_k: 5 });
    results.textContent = JSON.stringify(data.results, null, 2);
  } catch (err) {
    results.textContent = `Error: ${err.message}`;
  }
});

document.getElementById('load-vectors').addEventListener('click', async () => {
  const canvas = document.getElementById('vector-canvas');
  const meta = document.getElementById('vector-meta');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#10b981';
  meta.textContent = 'Loading...';
  try {
    const data = await fetch('/vectors/umap');
    const payload = await data.json();
    ctx.fillStyle = '#10b981';
    payload.points.forEach((point) => {
      const x = (point.x + 5) * (canvas.width / 10);
      const y = (point.y + 5) * (canvas.height / 10);
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fill();
    });
    meta.textContent = JSON.stringify(payload.metadata, null, 2);
  } catch (err) {
    meta.textContent = `Error: ${err.message}`;
  }
});

document.getElementById('ioc-run').addEventListener('click', async () => {
  const input = document.getElementById('ioc-input');
  const output = document.getElementById('ioc-results');
  output.textContent = 'Scanning...';
  try {
    const data = await postJSON('/utils/ioc_extract', { text: input.value });
    output.textContent = JSON.stringify(data.iocs, null, 2);
  } catch (err) {
    output.textContent = `Error: ${err.message}`;
  }
});

document.getElementById('header-run').addEventListener('click', async () => {
  const input = document.getElementById('header-input');
  const output = document.getElementById('header-results');
  output.textContent = 'Parsing...';
  try {
    const data = await postJSON('/utils/headers', { headers: input.value });
    output.textContent = JSON.stringify(data.headers, null, 2);
  } catch (err) {
    output.textContent = `Error: ${err.message}`;
  }
});

document.getElementById('log-run').addEventListener('click', async () => {
  const input = document.getElementById('log-input');
  const output = document.getElementById('log-results');
  output.textContent = 'Summarizing...';
  try {
    const data = await postJSON('/utils/log_summary', { text: input.value });
    output.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    output.textContent = `Error: ${err.message}`;
  }
});

