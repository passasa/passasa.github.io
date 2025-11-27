import json, os, re, sys

# Configuration
CONTENT_DIR = os.path.join(os.path.dirname(__file__), 'content')
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), 'assets', 'data', 'videos.json')
THUMB_ROOT = '/assets/images/videos'

slug_cache = {}

def slugify(name: str) -> str:
    base = name.lower().strip()
    base = re.sub(r'\.[^.]+$', '', base)  # remove extension
    base = re.sub(r'[^a-z0-9]+', '-', base)
    base = re.sub(r'-{2,}', '-', base).strip('-')
    return base


def build_entries():
    entries = []
    seen_ids = set()
    duplicate_counter = {}
    if not os.path.isdir(CONTENT_DIR):
        print(f"CONTENT_DIR '{CONTENT_DIR}' introuvable", file=sys.stderr)
        return entries

    for creator in sorted(os.listdir(CONTENT_DIR)):
        c_path = os.path.join(CONTENT_DIR, creator)
        if not os.path.isdir(c_path):
            continue
        creator_slug = slugify(creator)
        created_count = 0
        skipped_count = 0
        for fname in sorted(os.listdir(c_path)):
            if not fname.lower().endswith('.txt'):
                continue
            file_path = os.path.join(c_path, fname)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    embed_url = f.read().strip()
            except Exception as e:
                print(f"Erreur lecture {file_path}: {e}", file=sys.stderr)
                continue
            title_raw = re.sub(r'\.[^.]+$', '', fname)
            title = title_raw.replace('-', ' ').replace('_', ' ').strip()
            video_slug = slugify(title_raw)
            vid_id_base = f"{creator_slug}-{video_slug}"
            vid_id = vid_id_base
            # Ensure uniqueness: append incremental suffix if collision
            suffix = 2
            while vid_id in seen_ids:
                vid_id = f"{vid_id_base}-{suffix}"
                suffix += 1
            if suffix > 2:
                duplicate_counter[vid_id_base] = suffix - 1
            # Extract date (YYYY-MM-DD or YYYY_MM_DD) from filename if present
            date_match = re.search(r'(20\d{2})[-_ ](\d{2})[-_ ](\d{2})', title_raw)
            detected_date = ''
            if date_match:
                y, m, d = date_match.group(1), date_match.group(2), date_match.group(3)
                # Basic validation: month/day ranges
                if '01' <= m <= '12' and '01' <= d <= '31':
                    detected_date = f"{y}-{m}-{d}"
            # Thumbnail discovery priority:
            # 1. Image colocated avec le fichier .txt dans le dossier du creator (même base + extension)
            # 2. Image dans assets/images/videos/<creator_slug>/
            # 3. Fallback placeholder
            thumb_rel = None
            for ext in ('webp','jpg','jpeg','png'):
                colocated = os.path.join(c_path, f"{title_raw}.{ext}")
                if os.path.isfile(colocated):
                    # Accessible directement via /content/<folder>/<file>
                    # On utilise le nom réel du dossier creator (pas le slug) pour construire l'URL publique.
                    thumb_rel = f"/content/{creator}/{title_raw}.{ext}"
                    break
            if thumb_rel is None:
                thumb_dir = os.path.join(os.path.dirname(__file__), 'assets', 'images', 'videos', creator_slug)
                if os.path.isdir(thumb_dir):
                    for ext in ('webp','jpg','jpeg','png'):
                        candidate = os.path.join(thumb_dir, f"{title_raw}.{ext}")
                        if os.path.isfile(candidate):
                            thumb_rel = f"{THUMB_ROOT}/{creator_slug}/{title_raw}.{ext}"
                            break
            if thumb_rel is None:
                thumb_rel = '/assets/images/placeholder.svg'
            entry = {
                'id': vid_id,
                'artist': creator.replace('-', ' ').title(),
                'artist_slug': creator_slug,
                'title': title,
                'iframe': embed_url,
                'thumbnail': thumb_rel,
                'tags': [],
                'date': detected_date
            }
            entries.append(entry)
            seen_ids.add(vid_id)
            created_count += 1
        print(f"Creator '{creator}' -> {created_count} vidéos (collisions résolues: {len(duplicate_counter)})")
    return entries


def main():
    entries = build_entries()
    # Optional: merge with existing if present (preserve manual metadata)
    existing = []
    if os.path.isfile(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []
    # Index existing by id
    existing_map = {e['id']: e for e in existing if 'id' in e}
    for e in entries:
        if e['id'] in existing_map:
            old = existing_map[e['id']]
            # Decide thumbnail: prefer newly detected if old is placeholder or missing
            new_thumb = e.get('thumbnail')
            old_thumb = old.get('thumbnail')
            if old_thumb and old_thumb != '/assets/images/placeholder.svg':
                # keep old custom thumbnail
                e['thumbnail'] = old_thumb
            elif new_thumb and new_thumb != '/assets/images/placeholder.svg':
                # use newly detected
                e['thumbnail'] = new_thumb
            else:
                # fallback to whichever exists
                e['thumbnail'] = new_thumb or old_thumb or '/assets/images/placeholder.svg'
            # Preserve tags/date if they already exist (and non-empty)
            # Preserve tags if already present; for date keep existing only if new detection empty
            if 'tags' in old and old['tags']:
                e['tags'] = old['tags']
            if (not e.get('date')) and old.get('date'):
                e['date'] = old['date']
            # Prefer richer title: if old title shorter keep new, else keep old
            if len(old.get('title','')) > len(e.get('title','')):
                e['title'] = old['title']
            existing_map[e['id']] = e
        else:
            existing_map[e['id']] = e
    merged = list(existing_map.values())
    merged.sort(key=lambda x: (x.get('artist_slug',''), x.get('id','')))
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Ecrit {len(merged)} entrées dans {OUTPUT_JSON}")

if __name__ == '__main__':
    main()
