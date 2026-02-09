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
    
    if not os.path.isdir(CONTENT_DIR):
        print(f"CONTENT_DIR '{CONTENT_DIR}' introuvable", file=sys.stderr)
        return entries

    def process_creator(c_path, creator_name, parent_slug=None):
        creator_slug = slugify(creator_name)
        if parent_slug:
            creator_slug = f"{parent_slug}-{creator_slug}"
        
        created_count = 0
        skipped_count = 0
        
        for fname in sorted(os.listdir(c_path)):
            item_path = os.path.join(c_path, fname)
            
            # Si c'est un dossier, le traiter comme un sous-créateur
            if os.path.isdir(item_path):
                process_creator(item_path, fname, creator_slug)
                continue
            
            if not fname.lower().endswith('.txt'):
                continue
            
            try:
                with open(item_path, 'r', encoding='utf-8') as f:
                    embed_url = f.read().strip()
            except Exception as e:
                print(f"Erreur lecture {item_path}: {e}", file=sys.stderr)
                continue
            
            # Validate that it's a proper .mp4 URL
            if not embed_url or not embed_url.startswith(('http://', 'https://')):
                print(f"Avertissement: {fname} ne contient pas une URL valide", file=sys.stderr)
                skipped_count += 1
                continue
            if not embed_url.lower().endswith('.mp4'):
                print(f"Avertissement: {fname} n'est pas une URL .mp4 ({embed_url})", file=sys.stderr)
            
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
            # Extract date (YYYY-MM-DD or YYYY_MM_DD) from filename if present
            date_match = re.search(r'(20\d{2})[-_ ](\d{2})[-_ ](\d{2})', title_raw)
            detected_date = ''
            if date_match:
                y, m, d = date_match.group(1), date_match.group(2), date_match.group(3)
                # Basic validation: month/day ranges
                if '01' <= m <= '12' and '01' <= d <= '31':
                    detected_date = f"{y}-{m}-{d}"
            # Thumbnail discovery for VIDEO entries (videos thumbnails should come
            # from assets/images/videos first, then fallback to colocated in content):
            # 1. image in assets/images/videos/<creator_slug>/<image>
            # 2. image colocated with the .txt file in the creator's folder -> /content/<rel-folder>/<image>
            # 3. fallback placeholder
            thumb_rel = None
            
            # First, check dedicated assets/images/videos/<creator_slug>/ folder (GitHub Pages compatible)
            thumb_dir = os.path.join(os.path.dirname(__file__), 'assets', 'images', 'videos', creator_slug)
            if os.path.isdir(thumb_dir):
                for ext in ('webp', 'jpg', 'jpeg', 'png'):
                    candidate = os.path.join(thumb_dir, f"{title_raw}.{ext}")
                    if os.path.isfile(candidate):
                        thumb_rel = f"{THUMB_ROOT}/{creator_slug}/{title_raw}.{ext}"
                        break

            # If not found in assets, check colocated with the .txt file in the creator's folder
            if thumb_rel is None:
                rel_folder = os.path.relpath(c_path, CONTENT_DIR).replace('\\', '/')
                for ext in ('webp', 'jpg', 'jpeg', 'png'):
                    colocated = os.path.join(c_path, f"{title_raw}.{ext}")
                    if os.path.isfile(colocated):
                        thumb_rel = f"/content/{rel_folder}/{title_raw}.{ext}"
                        break

            # Final fallback is the site placeholder
            if thumb_rel is None:
                thumb_rel = '/assets/images/placeholder.svg'
            entry = {
                'id': vid_id,
                'artist': creator_name.replace('-', ' ').title(),
                'artist_slug': creator_slug,
                'title': title,
                'iframe': embed_url,  # Direct .mp4 URL
                'thumbnail': thumb_rel,
                'tags': [],
                'date': detected_date
            }
            entries.append(entry)
            seen_ids.add(vid_id)
            created_count += 1
        
        if created_count > 0 or skipped_count > 0:
            print(f"Creator '{creator_name}' -> {created_count} vidéos")

    for creator in sorted(os.listdir(CONTENT_DIR)):
        c_path = os.path.join(CONTENT_DIR, creator)
        if not os.path.isdir(c_path):
            continue
        process_creator(c_path, creator)
    
    return entries


def main():
    entries = build_entries()
    # Build creators -> thumbnail mapping (folders use images from /assets/images)
    creators_map = {}
    images_root = os.path.join(os.path.dirname(__file__), 'assets', 'images')
    # Walk content folders to discover folder slugs
    for dirpath, dirnames, filenames in os.walk(CONTENT_DIR):
        # compute slug based on path relative to CONTENT_DIR
        rel = os.path.relpath(dirpath, CONTENT_DIR)
        if rel == '.':
            continue
        parts = rel.split(os.sep)
        slug_parts = [slugify(p) for p in parts]
        slug = '-'.join(slug_parts)
        # candidate bases: full slug, last part, capitalized last part, underscore variant
        last = slug_parts[-1] if slug_parts else slug
        cand_bases = [slug, last, '-'.join([p.capitalize() for p in re.sub(r'[^a-z0-9-]', ' ', last).split()]), last.replace('-', '_')]
        # Add singular variants (remove trailing 's' if present)
        for b in list(cand_bases):
            if b.endswith('s') and len(b) > 1:
                cand_bases.append(b[:-1])
        seen = set(); candidates = []
        for b in cand_bases:
            if not b or b in seen: continue
            seen.add(b); candidates.append(b)
        thumb = None
        for base in candidates:
            for ext in ('webp','jpg','jpeg','png'):
                candidate = os.path.join(images_root, f"{base}.{ext}")
                if os.path.isfile(candidate):
                    thumb = f"/assets/images/{base}.{ext}"
                    break
            if thumb:
                break
        if not thumb:
            thumb = '/assets/images/placeholder.svg'
        creators_map[slug] = thumb
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
            # Decide thumbnail: prefer newly detected thumbnails (they include
            # correct /content/ or /assets/images paths). Only fall back to the
            # existing thumbnail if the new one is a placeholder.
            new_thumb = e.get('thumbnail')
            old_thumb = old.get('thumbnail')
            if new_thumb and new_thumb != '/assets/images/placeholder.svg':
                e['thumbnail'] = new_thumb
            elif old_thumb and old_thumb != '/assets/images/placeholder.svg':
                e['thumbnail'] = old_thumb
            else:
                e['thumbnail'] = new_thumb or old_thumb or '/assets/images/placeholder.svg'
            # Preserve tags/date if they already exist (and non-empty)
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
    # Write creators map
    creators_json_path = os.path.join(os.path.dirname(__file__), 'assets', 'data', 'creators.json')
    os.makedirs(os.path.dirname(creators_json_path), exist_ok=True)
    with open(creators_json_path, 'w', encoding='utf-8') as f:
        json.dump(creators_map, f, ensure_ascii=False, indent=2)
    print(f"Ecrit {len(creators_map)} créateurs dans {creators_json_path}")

if __name__ == '__main__':
    main()
