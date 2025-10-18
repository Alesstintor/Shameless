// Render users grid
const grid = document.getElementById('users-grid');
const emptyState = document.getElementById('empty-state');
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
  
  if (users.length === 0) {
    // Mostrar empty state
    emptyState.classList.add('visible');
    grid.style.display = 'none';
  } else {
    // Mostrar grid con usuarios
    emptyState.classList.remove('visible');
    grid.style.display = 'grid';
    users.slice(0, 10).forEach((u, i) => grid.appendChild(createBubble(u, i)));
  }
}

// Detail panel logic
const detail = document.getElementById('detail');
const closeBtn = document.getElementById('close-detail');
const detailAvatar = document.getElementById('detail-avatar');
const detailName = document.getElementById('detail-name');
const detailUsername = document.getElementById('detail-username');
const detailSummary = document.getElementById('detail-summary');
const legendArea = document.getElementById('chart-legend');
const mostPositivePost = document.getElementById('most-positive-post');
const mostNegativePost = document.getElementById('most-negative-post');

let currentChart = null;

function openDetail(idx) {
  const user = USERS[idx];
  detailAvatar.src = user.avatar;
  detailName.textContent = user.name;
  detailUsername.textContent = '@' + user.username;
  detailSummary.textContent = user.summary;
  
  // Show most positive post
  if (user.most_positive) {
    const posText = mostPositivePost.querySelector('.post-text');
    const posMeta = mostPositivePost.querySelector('.post-confidence');
    posText.textContent = user.most_positive.text || user.most_positive;
    if (typeof user.most_positive === 'object' && user.most_positive.confidence) {
      posMeta.textContent = `Confianza: ${(user.most_positive.confidence * 100).toFixed(1)}%`;
    } else {
      posMeta.textContent = '';
    }
  } else {
    const posText = mostPositivePost.querySelector('.post-text');
    posText.textContent = 'No disponible';
    mostPositivePost.querySelector('.post-confidence').textContent = '';
  }
  
  // Show most negative post
  if (user.most_negative) {
    const negText = mostNegativePost.querySelector('.post-text');
    const negMeta = mostNegativePost.querySelector('.post-confidence');
    negText.textContent = user.most_negative.text || user.most_negative;
    if (typeof user.most_negative === 'object' && user.most_negative.confidence) {
      negMeta.textContent = `Confianza: ${(user.most_negative.confidence * 100).toFixed(1)}%`;
    } else {
      negMeta.textContent = '';
    }
  } else {
    const negText = mostNegativePost.querySelector('.post-text');
    negText.textContent = 'No disponible';
    mostNegativePost.querySelector('.post-confidence').textContent = '';
  }

  // chart - mostrar solo sentimientos reales
  const ctx = document.getElementById('emotion-chart').getContext('2d');
  const sentiments = user.sentiments || {};
  
  // Filtrar sentimientos con valor > 0 para el gráfico
  const labels = [];
  const data = [];
  const colors = [];
  
  const colorMap = {
    'Positivo': '#10b981',  // Verde esmeralda
    'Negativo': '#ef4444',  // Rojo
    'Neutral': '#06b6d4'    // Cyan
  };
  
  Object.entries(sentiments).forEach(([label, count]) => {
    if (count > 0) {
      labels.push(label);
      data.push(count);
      colors.push(colorMap[label] || '#9aa4b2');
    }
  });
  
  if (currentChart) {
    currentChart.destroy();
    legendArea.innerHTML = '';
  }
  
  currentChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels, 
      datasets: [{
        data, 
        backgroundColor: colors, 
        borderWidth: 0
      }]
    },
    options: {
      plugins: {
        legend: {display: false}
      }, 
      cutout: '40%'
    }
  });

  // legend - mostrar cantidad de posts
  labels.forEach((lab, i) => {
    const it = document.createElement('div');
    it.className = 'legend-item';
    const sw = document.createElement('div');
    sw.className = 'legend-swatch';
    sw.style.background = colors[i];
    const txt = document.createElement('div');
    const total = data.reduce((a, b) => a + b, 0);
    const percentage = Math.round((data[i] / total) * 100);
    txt.textContent = `${lab} — ${data[i]} posts (${percentage}%)`;
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

// Initialize - empty users list
let USERS = [];

// Load stored users from database
async function loadStoredUsers() {
  try {
    const res = await fetch('/api/users');
    if (!res.ok) throw new Error('Server returned ' + res.status);
    const data = await res.json();
    
    if (Array.isArray(data) && data.length) {
      // Map database format to UI format
      USERS = data.map(user => mapAnalysisToUI(user));
      console.log(`✅ Loaded ${USERS.length} saved analyses from database`);
    } else {
      console.log('ℹ️ No saved analyses found. Search for a user to start!');
    }
  } catch (e) {
    console.error('Could not load saved users from server:', e);
  }
  renderGrid(USERS);
}

// Map analysis result from database to UI format
function mapAnalysisToUI(analysis) {
  const totalPosts = analysis.total_analyzed || 1;
  const positiveCount = analysis.positive_count || 0;
  const negativeCount = analysis.negative_count || 0;
  const neutralCount = totalPosts - positiveCount - negativeCount;
  
  // Sentimientos reales del análisis
  const sentiments = {
    Positivo: positiveCount,
    Negativo: negativeCount,
    Neutral: neutralCount
  };
  
  return {
    avatar: analysis.user_avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(analysis.user_handle)}`,
    username: analysis.user_handle || 'unknown',
    name: analysis.user_name || analysis.user_handle || 'Unknown',
    sentiments: sentiments,
    summary: generateSummary(analysis),
    most_positive: analysis.most_positive || null,
    most_negative: analysis.most_negative || null
  };
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
    const res = await fetch(`/api/analyze/bluesky/user/${encodeURIComponent(handle)}?limit=25`);
    if (!res.ok) throw new Error('Server returned ' + res.status);
    const analysis = await res.json();

    // Map to UI format using shared function
    const mapped = mapAnalysisToUI(analysis);

    // Update local list and re-render
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
