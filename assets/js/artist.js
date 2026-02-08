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

  Promise.all([
    fetch('./assets/data/videos.json').then(r=>{if(!r.ok) throw new Error('Chargement JSON impossible'); return r.json();}),
    fetch('./assets/data/creators.json').then(r=>{if(!r.ok) throw new Error('Chargement creators impossible'); return r.json();})
  ])
  .then(([list, creatorsMap]) => {
    // Collect videos for this artist and sort Z -> A by normalized title
    const artistVideos = list.filter(v=>v.artist_slug===artistSlug);
    // Also find child categories (slugs that begin with artistSlug + '-')
    const childVideos = list.filter(v=> v.artist_slug && v.artist_slug.startsWith(artistSlug + '-'));
    // Group child videos by their exact artist_slug
    const childGroups = {};
    childVideos.forEach(v=>{
      if(!childGroups[v.artist_slug]) childGroups[v.artist_slug]=[];
      childGroups[v.artist_slug].push(v);
    });
    const childSlugs = Object.keys(childGroups).sort();

    if(!artistVideos.length && childSlugs.length===0){statusEl.textContent='Aucune vidéo trouvée pour cet artiste.';return;}
      // Set header
      statusEl.remove();
      headerEl.classList.remove('d-none');
      searchWrap.classList.remove('d-none');
      // If there are direct videos, use that artist name; otherwise derive from slug
      const displayName = artistVideos.length ? artistVideos[0].artist : (artistSlug.replace(/-/g,' ').replace(/\b\w/g,c=>c.toUpperCase()));
      nameEl.textContent = displayName;
      // Count: direct videos if present, else sum of child videos
      const totalCount = artistVideos.length ? artistVideos.length : childSlugs.reduce((s,slug)=> s + childGroups[slug].length, 0);
      countEl.textContent = totalCount + ' vidéo(s)';

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

  // If there are child categories and no direct videos, render children as category cards
  function renderChildrenAsCategories(){
    gridEl.innerHTML = '';
    childSlugs.forEach(slug => {
      const vids = childGroups[slug];
      const v0 = vids[0];
      // Use creators.json first, fallback to first video thumbnail or placeholder
      let thumb = creatorsMap[slug] || (v0 && v0.thumbnail && v0.thumbnail !== '/assets/images/placeholder.svg' ? v0.thumbnail : '/assets/images/placeholder.svg');
      
      // Derive a nice display name from slug (remove parent prefix)
      function titleize(s){
        const parts = s.split('-');
        if(parts.length>1) parts.shift();
        const base = parts.join(' ').replace(/[_]+/g,' ');
        return base.replace(/\b\w/g, ch => ch.toUpperCase());
      }
      const displayTitle = (v0 && v0.artist && !v0.artist.toLowerCase().startsWith(slug)) ? v0.artist : titleize(slug);

      const a = document.createElement('a');
      a.href = '/artist.html?artist='+encodeURIComponent(slug);
      a.className = 'video-card';
      a.innerHTML = `\n        <img src='${escapeHtml(thumb)}' alt='${escapeHtml(displayTitle)}' loading='lazy'>\n        <h3>${escapeHtml(displayTitle)}</h3>\n        <div class='meta'>${vids.length} vidéo(s)</div>\n      `;
      gridEl.appendChild(a);
    });
  }

  if(childSlugs.length>0 && artistVideos.length===0){
    // Show child categories
    renderChildrenAsCategories();
  } else {
    render(artistVideos);
  }

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
