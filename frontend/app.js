// Mock data: replace these variables with real API responses when available
const MOCK_USERS = [
  // each item: { avatar, username, name, emotions: {joy:.., sadness:.., anger:.., fear:.., surprise:..}, tweets: [], words: [], summary: '' }
  {
    avatar: 'https://pbs.twimg.com/profile_images/141508325/joe_400x400.jpg',
    username: 'user_one',
    name: 'User One',
    emotions: { Joy: 0.45, Sadness: 0.2, Anger: 0.15, Fear: 0.1, Surprise: 0.1 },
    tweets: ['Tweet ejemplo A', 'Tweet ejemplo B'],
    words: ['ejemplo', 'prueba', 'shameless'],
    summary: 'Tendente a compartir opiniones personales y contenido multimedia.'
  },
  // repeat mock items to simulate up to 10
];

// fill up to 10 mock users if needed
while (MOCK_USERS.length < 10) {
  const i = MOCK_USERS.length + 1;
  MOCK_USERS.push({
    avatar: `https://i.pravatar.cc/150?img=${i}`,
    username: `ejemplo_${i}`,
    name: `Ejemplo ${i}`,
    emotions: { Joy: Math.random(), Sadness: Math.random(), Anger: Math.random(), Fear: Math.random(), Surprise: Math.random() },
    tweets: [`Ultimo tweet ${i}`, `Otro tweet ${i}`],
    words: ['palabra1', 'palabra2'],
    summary: 'Usuario activo con mezcla de contenido.'
  });
}

// normalize emotion distributions to sum to 1
function normalizeEmotions(e) {
  const keys = Object.keys(e);
  const sum = keys.reduce((s, k) => s + e[k], 0) || 1;
  const out = {};
  for (const k of keys) out[k] = e[k] / sum;
  return out;
}

// Render users grid
const grid = document.getElementById('users-grid');
const title = document.getElementById('project-title');
const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-input');
const themeToggle = document.getElementById('theme-toggle');

function createBubble(user, idx) {
  const el = document.createElement('button');
  el.className = 'bubble';
  el.setAttribute('data-idx', idx);
  el.title = `Ver ${user.username}`;

  const av = document.createElement('div');
  av.className = 'avatar';
  const img = document.createElement('img');
  img.src = user.avatar;
  img.alt = `${user.username} avatar`;
  av.appendChild(img);

  const uname = document.createElement('div');
  uname.className = 'username';
  uname.textContent = '@' + user.username;

  // only avatar and username are appended to keep minimal look
  el.appendChild(av);
  el.appendChild(uname);

  // hover effect for avatar circle
  el.addEventListener('mouseover', () => {
    av.style.transform = 'scale(1.06)';
    av.style.boxShadow = '0 8px 20px rgba(0,0,0,0.5)';
  });
  el.addEventListener('mouseout', () => {
    av.style.transform = '';
    av.style.boxShadow = '';
  });

  el.addEventListener('click', () => openDetail(idx));

  return el;
}

function renderGrid(users) {
  grid.innerHTML = '';
  users.slice(0, 10).forEach((u, i) => grid.appendChild(createBubble(u, i)));
}

// Detail panel logic
const detail = document.getElementById('detail');
const closeBtn = document.getElementById('close-detail');
const detailAvatar = document.getElementById('detail-avatar');
const detailName = document.getElementById('detail-name');
const detailUsername = document.getElementById('detail-username');
const detailTweets = document.getElementById('detail-tweets');
const detailWords = document.getElementById('detail-words');
const detailSummary = document.getElementById('detail-summary');
const legendArea = document.getElementById('chart-legend');

let currentChart = null;

function openDetail(idx) {
  const user = USERS[idx];
  detailAvatar.src = user.avatar;
  detailName.textContent = user.name;
  detailUsername.textContent = '@' + user.username;
  detailTweets.innerHTML = '';
  user.tweets.forEach(t => {
    const li = document.createElement('li');
    li.textContent = t;
    detailTweets.appendChild(li);
  });
  detailWords.innerHTML = '';
  user.words.forEach(w => {
    const s = document.createElement('span');
    s.className = 'word';
    s.textContent = w;
    detailWords.appendChild(s);
  });
  detailSummary.textContent = user.summary;

  // chart
  const ctx = document.getElementById('emotion-chart').getContext('2d');
  const emo = normalizeEmotions(user.emotions);
  const labels = Object.keys(emo);
  const data = labels.map(l => Math.round(emo[l] * 100));
  const colors = ['#4ade80', '#60a5fa', '#f97316', '#f43f5e', '#a78bfa'];
  if (currentChart) {
    currentChart.destroy();
    legendArea.innerHTML = '';
  }
  currentChart = new Chart(ctx, {
    type: 'doughnut',
    data: {labels, datasets:[{data, backgroundColor:colors, borderWidth:0}]},
    options: {plugins:{legend:{display:false}}, cutout: '40%'}
  });

  // legend
  labels.forEach((lab, i) => {
    const it = document.createElement('div');
    it.className = 'legend-item';
    const sw = document.createElement('div');
    sw.className = 'legend-swatch';
    sw.style.background = colors[i % colors.length];
    const txt = document.createElement('div');
    txt.textContent = `${lab} — ${data[i]}%`;
    it.appendChild(sw);
    it.appendChild(txt);
    legendArea.appendChild(it);
  });

  detail.classList.remove('hidden');
  detail.setAttribute('aria-hidden', 'false');
}

function closeDetail() {
  detail.classList.add('hidden');
  detail.setAttribute('aria-hidden', 'true');
}

closeBtn.addEventListener('click', closeDetail);
detail.addEventListener('click', (e) => { if (e.target === detail) closeDetail(); });

// Title hover effect (tiny animation)
title.addEventListener('mouseover', () => title.style.letterSpacing = '2px');
title.addEventListener('mouseout', () => title.style.letterSpacing = '0.6px');

// Initialize
let USERS = MOCK_USERS.slice().reverse(); // most recent first (fallback)

// Try to load stored users from server. If the server or endpoint is unavailable,
// we fall back to the MOCK_USERS defined above.
async function loadStoredUsers() {
  try {
    const res = await fetch('/api/stored_users');
    if (!res.ok) throw new Error('Server returned ' + res.status);
    const data = await res.json();
    if (Array.isArray(data) && data.length) {
      // Expecting data entries to match the structure used in the frontend
      USERS = data.slice(0, 10);
    }
  } catch (e) {
    console.warn('Could not load stored users from server, using mock data:', e);
  }
  renderGrid(USERS);
}

loadStoredUsers();

// Search handling - uses sentiment analysis endpoint
searchForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = searchInput.value && searchInput.value.trim();
  if (!q) return;

  const handle = q.replace(/^@/, '');
  
  // Show loading state
  searchInput.disabled = true;
  searchInput.placeholder = 'Analizando...';
  
  try {
    // Use sentiment analysis endpoint
    const res = await fetch(`/api/analyze/bluesky/user/${encodeURIComponent(handle)}?limit=10`);
    if (!res.ok) throw new Error('Server returned ' + res.status);
    const data = await res.json();

    // Map sentiment analysis result to UI structure
    // Calculate emotion distribution from sentiment analysis
    const totalPosts = data.total_analyzed || 1;
    const positiveRatio = (data.positive_count || 0) / totalPosts;
    const negativeRatio = (data.negative_count || 0) / totalPosts;
    const neutralRatio = 1 - positiveRatio - negativeRatio;
    
    // Map to emotion categories (adjust as needed)
    const emotions = {
      Joy: positiveRatio * 0.6,          // Most positive → Joy
      Surprise: positiveRatio * 0.4,     // Some positive → Surprise
      Sadness: negativeRatio * 0.5,      // Most negative → Sadness
      Anger: negativeRatio * 0.3,        // Some negative → Anger
      Fear: negativeRatio * 0.2 + neutralRatio  // Remaining negative + neutral
    };
    
    const mapped = {
      avatar: data.user_avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(handle)}`,
      username: data.user_handle || handle,
      name: data.user_name || handle,
      emotions: emotions,
      tweets: (data.posts || []).map(p => p.text || p.content || '').slice(0, 10),
      words: extractTopWords(data.posts || []),
      summary: generateSummary(data)
    };

    // update local list and re-render
    USERS.unshift(mapped);
    USERS = USERS.slice(0, 10);
    renderGrid(USERS);
    
    console.log('✅ Análisis completado para', handle);
  } catch (e) {
    console.error('Failed to fetch sentiment analysis:', e);
    alert(`Error al analizar @${handle}. Por favor intenta de nuevo.`);
  } finally {
    searchInput.disabled = false;
    searchInput.placeholder = 'Buscar usuario (ej: elonmusk)';
    searchInput.value = '';
  }
});

// Helper function to extract top words from posts
function extractTopWords(posts) {
  const words = {};
  posts.forEach(post => {
    const text = post.text || post.content || '';
    const tokens = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 3); // words longer than 3 chars
    
    tokens.forEach(word => {
      words[word] = (words[word] || 0) + 1;
    });
  });
  
  return Object.entries(words)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([word]) => word);
}

// Helper function to generate summary from sentiment data
function generateSummary(data) {
  const total = data.total_analyzed || 0;
  const positive = data.positive_count || 0;
  const negative = data.negative_count || 0;
  const avgConf = (data.average_confidence || 0) * 100;
  
  let sentiment = 'neutral';
  if (positive > negative * 1.5) sentiment = 'muy positivo';
  else if (positive > negative) sentiment = 'positivo';
  else if (negative > positive * 1.5) sentiment = 'muy negativo';
  else if (negative > positive) sentiment = 'negativo';
  
  return `Analizados ${total} posts. Sentimiento general: ${sentiment}. Confianza promedio: ${avgConf.toFixed(1)}%.`;
}

// Theme toggle
function setLightMode(on) {
  document.documentElement.classList.toggle('light', on);
  document.body.classList.toggle('light', on);
  themeToggle.setAttribute('aria-pressed', String(on));
  // update bulb svg
  themeToggle.innerHTML = on ? bulbSvg(true) : bulbSvg(false);
  themeToggle.classList.toggle('on', !!on);
  try { localStorage.setItem('shameless:light', on ? '1' : '0'); } catch (e) {}
}

// bulb svg helper
function bulbSvg(on) {
  if (on) {
    return `
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M9 21h6v-1H9v1zm3-19a6 6 0 00-6 6c0 2.21 1.46 3.98 2.5 4.93L9.5 13h5l.999-.07C15.54 11.98 17 10.21 17 8a6 6 0 00-6-6z" fill="#facc15"/>
      </svg>`;
  }
  return `
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M9 21h6v-1H9v1zm3-19a6 6 0 00-6 6c0 2.21 1.46 3.98 2.5 4.93L9.5 13h5l.999-.07C15.54 11.98 17 10.21 17 8a6 6 0 00-6-6z" fill="currentColor"/>
    </svg>`;
}

themeToggle.addEventListener('click', () => {
  const isLight = !document.documentElement.classList.contains('light');
  setLightMode(isLight);
});

// initialize bulb icon based on current mode (default dark)
// initialize from localStorage if present
const saved = (function(){ try { return localStorage.getItem('shameless:light'); } catch(e){ return null }})();
if (saved === '1') setLightMode(true);
else setLightMode(false);
