// Dynamic video loader
(function(){
  const params = new URLSearchParams(window.location.search);
  const id = params.get('v');
  const statusEl = document.getElementById('status');
  const titleEl = document.getElementById('videoTitle');
  const thumbnailEl = document.getElementById('videoThumbnail');
  const linkEl = document.getElementById('videoLink');
  const altLinkEl = document.getElementById('videoAltLink');
  const metaEl = document.getElementById('videoMeta');
  const relatedEl = document.getElementById('related');
  const turboContainerEl = document.getElementById('turboContainer');
  const turboEmbedEl = document.getElementById('turboEmbed');

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
      thumbnailEl.src = video.thumbnail;
      thumbnailEl.alt = video.title;

      const primaryUrl = video.iframe || '';
      const secondaryUrl = video.alt_iframe || '';
      const embedUrl = video.embed_url || '';

      // Lien principal (hébergeur n°1)
      if (primaryUrl) {
        linkEl.href = primaryUrl;
      } else if (embedUrl) {
        linkEl.href = embedUrl;
      } else {
        linkEl.removeAttribute('href');
      }
      
      // Si un embed direct existe (Turbo, etc.), on l'affiche
      if (embedUrl){
        turboEmbedEl.src = embedUrl;
        turboContainerEl.style.display = 'block';
        thumbnailEl.style.display = 'none';

        linkEl.style.display = primaryUrl || embedUrl ? 'block' : 'none';
        if (primaryUrl) {
          linkEl.textContent = '⬇ Ouvrir la vidéo (hébergeur principal)';
        } else {
          linkEl.textContent = '⬇ Ouvrir la vidéo dans un nouvel onglet';
        }
      } else {
        // Pas d'embed direct : miniature + simple bouton lien
        turboContainerEl.style.display = 'none';
        thumbnailEl.style.display = 'block';

        if (primaryUrl) {
          linkEl.style.display = 'block';
          linkEl.textContent = '▶ Ouvrir la vidéo (hébergeur principal)';
        } else if (embedUrl) {
          linkEl.style.display = 'block';
          linkEl.textContent = '▶ Ouvrir la vidéo';
        } else {
          linkEl.style.display = 'none';
        }
      }

      // Hébergeur secondaire (ex. Fileditch si union-crax en principal)
      if (altLinkEl) {
        if (secondaryUrl) {
          altLinkEl.style.display = 'block';
          altLinkEl.href = secondaryUrl;
          if (secondaryUrl.toLowerCase().includes('fileditch')) {
            altLinkEl.textContent = 'Voir sur Fileditch (hébergeur secondaire)';
          } else {
            altLinkEl.textContent = 'Voir sur un autre hébergeur';
          }
        } else {
          altLinkEl.style.display = 'none';
          altLinkEl.removeAttribute('href');
        }
      }
      
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
