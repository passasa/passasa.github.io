// artist.js - render videos for one artist from videos.json
(function(){
  const params = new URLSearchParams(window.location.search);
  const artistSlug = params.get('artist');
  const statusEl = document.getElementById('status');
  const headerEl = document.getElementById('artistHeader');
  const nameEl = document.getElementById('artistName');
  const countEl = document.getElementById('artistCount');
  const gridEl = document.getElementById('videosGrid');
  const searchWrap = document.getElementById('searchWrap');
  const searchInput = document.getElementById('searchInput');
  const sortSelect = document.getElementById('sortSelect');

  function escapeHtml(str){return str?str.replace(/[&<>"']/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s])):'';}
  function normTitle(t){
    return (t||'')
      .trim()
      .toLowerCase()
      .normalize('NFD') // split accents
      .replace(/[\u0300-\u036f]/g,''); // remove diacritics
  }
  function extractDateFromTitle(title){
    // Support YYYY-MM-DD, YYYY_MM_DD, YYYY MM DD, also single digit M/D
    const m = title && title.match(/(20\d{2})[-_ ](\d{1,2})[-_ ](\d{1,2})/);
    if(!m) return null;
    let [_, y, mo, d] = m;
    mo = mo.zpad?mo: (mo.length===1? '0'+mo : mo);
    d = d.length===1? '0'+d : d;
    return `${y}-${mo}-${d}`;
  }
  function getDate(v){
    // Prefer explicit date field if present, else parse from title
    if(v.date) return v.date;
    return extractDateFromTitle(v.title) || '';
  }
  function compareDateDesc(a,b){
    const da = getDate(a);
    const db = getDate(b);
    if(da && db){
      // Newest first => descending by date string
      if(da < db) return 1;
      if(da > db) return -1;
    } else if(da && !db){
      return -1; // items with date come before ones without
    } else if(!da && db){
      return 1;
    }
    // Fallback to normalized title Z->A
    const A = normTitle(a.title);
    const B = normTitle(b.title);
    if(A < B) return 1;
    if(A > B) return -1;
    return 0;
  }

  function compareDateAsc(a,b){
    const da = getDate(a);
    const db = getDate(b);
    if(da && db){
      if(da > db) return 1; // older first
      if(da < db) return -1;
    } else if(da && !db){
      return -1; // keep dated before undated still
    } else if(!da && db){
      return 1;
    }
    // fallback title A->Z
    const A = normTitle(a.title);
    const B = normTitle(b.title);
    if(A < B) return -1;
    if(A > B) return 1;
    return 0;
  }

  function compareTitleAsc(a,b){
    const A = normTitle(a.title), B = normTitle(b.title);
    if(A < B) return -1; if(A > B) return 1; return 0;
  }
  function compareTitleDesc(a,b){
    const A = normTitle(a.title), B = normTitle(b.title);
    if(A < B) return 1; if(A > B) return -1; return 0;
  }

  function getComparator(mode){
    switch(mode){
      case 'date_desc': return compareDateDesc;
      case 'date_asc': return compareDateAsc;
      case 'title_asc': return compareTitleAsc;
      case 'title_desc': return compareTitleDesc;
      default: return compareDateDesc;
    }
  }

  if(!artistSlug){statusEl.textContent='Paramètre ?artist= manquant';return;}

  fetch('/assets/data/videos.json')
    .then(r=>{if(!r.ok) throw new Error('Chargement JSON impossible'); return r.json();})
    .then(list=>{
    // Collect videos for this artist and sort Z -> A by normalized title
  const artistVideos = list.filter(v=>v.artist_slug===artistSlug);
      if(!artistVideos.length){statusEl.textContent='Aucune vidéo trouvée pour cet artiste.';return;}
      // Set header
      statusEl.remove();
      headerEl.classList.remove('d-none');
      searchWrap.classList.remove('d-none');
      nameEl.textContent = artistVideos[0].artist;
      countEl.textContent = artistVideos.length + ' vidéo(s)';

      function render(videos){
        const cmp = getComparator(sortSelect.value);
        const ordered = [...videos].sort(cmp);
        gridEl.innerHTML='';
        ordered.forEach(v=>{
          const a=document.createElement('a');
          a.href='/video.html?v='+encodeURIComponent(v.id);
          a.className='video-card';
          a.innerHTML = `
            <img src='${escapeHtml(v.thumbnail)}' alt='${escapeHtml(v.title)}' loading='lazy'>
            <h3>${escapeHtml(v.title)}</h3>
            <div class='meta'>${(v.date||'').slice(0,10)}</div>
          `;
          gridEl.appendChild(a);
        });
      }

  render(artistVideos);

      let lastQuery='';
      searchInput.addEventListener('input',()=>{
        const q=searchInput.value.toLowerCase().trim();
        if(q===lastQuery) return; lastQuery=q;
        if(!q){render(artistVideos);return;}
        const filtered = artistVideos.filter(v=> normTitle(v.title).includes(q));
        render(filtered);
      });

      sortSelect.addEventListener('change',()=>{
        const q = searchInput.value.trim().toLowerCase();
        if(!q){render(artistVideos);return;}
        const filtered = artistVideos.filter(v=> normTitle(v.title).includes(q));
        render(filtered);
      });
    })
    .catch(e=>{statusEl.textContent='Erreur: '+e.message;});
})();
