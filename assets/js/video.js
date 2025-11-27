// Dynamic video loader
(function(){
  const params = new URLSearchParams(window.location.search);
  const id = params.get('v');
  const statusEl = document.getElementById('status');
  const titleEl = document.getElementById('videoTitle');
  const iframeEl = document.getElementById('videoIframe');
  const metaEl = document.getElementById('videoMeta');
  const relatedEl = document.getElementById('related');

  function escapeHtml(str){
    return str.replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s]));
  }

  function normTitle(t){
    return (t||'')
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g,'');
  }
  function extractDateFromTitle(title){
    const m = title && title.match(/(\d{4})[-_](\d{2})[-_](\d{2})/);
    if(!m) return null;
    const [_, y, mo, d] = m;
    return `${y}-${mo}-${d}`; // ISO sortable
  }
  function compareDescDateThenTitle(a,b){
    const da = extractDateFromTitle(a.title);
    const db = extractDateFromTitle(b.title);
    if(da && db){
      if(da < db) return 1; // newer first
      if(da > db) return -1;
    } else if(da && !db){
      return -1; // dated before undated
    } else if(!da && db){
      return 1;
    }
    const A = normTitle(a.title);
    const B = normTitle(b.title);
    if(A < B) return 1; // Z->A
    if(A > B) return -1;
    return 0;
  }

  if(!id){
    statusEl.textContent = 'Paramètre manquant ?v=...';
    return;
  }

  fetch('/assets/data/videos.json')
    .then(r => {
      if(!r.ok) throw new Error('Impossible de charger les données');
      return r.json();
    })
    .then(list => {
      const video = list.find(v => v.id === id);
      if(!video){
        statusEl.textContent = 'Vidéo introuvable';
        return;
      }
      statusEl.remove();
      titleEl.textContent = video.title;
      iframeEl.src = video.iframe;
      metaEl.innerHTML = `Artiste: <strong>${escapeHtml(video.artist)}</strong><br>Date: ${escapeHtml(video.date)}<br>Tags: ${video.tags.map(t=>`<span class='tag'>${escapeHtml(t)}</span>`).join(' ')}`;

      // Related videos (same artist, different id) sorted by date (newest first), then title Z->A
      const related = list
        .filter(v => v.artist === video.artist && v.id !== video.id)
        .sort(compareDescDateThenTitle)
        .slice(0,6);
      related.forEach(rVid => {
        const a = document.createElement('a');
        a.href = `/video.html?v=${encodeURIComponent(rVid.id)}`;
        a.className = 'related-item';
        a.innerHTML = `<img loading='lazy' src='${escapeHtml(rVid.thumbnail)}' alt='${escapeHtml(rVid.title)}'><span>${escapeHtml(rVid.title)}</span>`;
        relatedEl.appendChild(a);
      });
    })
    .catch(e => {
      statusEl.textContent = 'Erreur: ' + e.message;
    });
})();
