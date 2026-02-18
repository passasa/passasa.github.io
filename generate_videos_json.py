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

    def process_dir_for_creator(c_path, creator_name, parent_slug=None, recurse_subfolders=True):
        """Process files in c_path as videos for creator_name.
        If recurse_subfolders is True, any subdirectory will be treated as a nested creator
        and processed with parent slugging. If False, subdirectories are ignored.
        """
        creator_slug = slugify(creator_name)
        if parent_slug:
            creator_slug = f"{parent_slug}-{creator_slug}"

        created_count = 0
        skipped_count = 0

        for fname in sorted(os.listdir(c_path)):
            item_path = os.path.join(c_path, fname)

            # If recursion is allowed and it's a folder, treat it as a sub-creator
            if recurse_subfolders and os.path.isdir(item_path):
                process_dir_for_creator(item_path, fname, creator_slug, recurse_subfolders=True)
                continue

            # Only process .txt files here
            if not os.path.isfile(item_path) or not fname.lower().endswith('.txt'):
                continue

            try:
                with open(item_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
            except Exception as e:
                print(f"Erreur lecture {item_path}: {e}", file=sys.stderr)
                continue

            # Parse all URLs from the file (one per line)
            lines = [line.strip() for line in content.split('\n') if line.strip()]

            # Separate Fileditch and Turbo URLs
            fileditch_url = None
            turbo_url = None

            for line in lines:
                if not line.startswith(('http://', 'https://')):
                    continue

                if 'fileditch' in line.lower():
                    if line.lower().endswith('.mp4'):
                        fileditch_url = line
                    else:
                        print(f"Avertissement: {fname} Fileditch URL n'est pas .mp4 ({line})", file=sys.stderr)
                if 'turbo' in line.lower():
                    turbo_url = line

            # Skip if no valid links found
            if not fileditch_url and not turbo_url:
                print(f"Avertissement: {fname} ne contient pas de lien Fileditch ou Turbo valide (skipped)", file=sys.stderr)
                skipped_count += 1
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
            # Extract date (YYYY-MM-DD or YYYY_MM_DD) from filename if present
            date_match = re.search(r'(20\d{2})[-_ ](\d{2})[-_ ](\d{2})', title_raw)
            detected_date = ''
            if date_match:
                y, m, d = date_match.group(1), date_match.group(2), date_match.group(3)
                # Basic validation: month/day ranges
                if '01' <= m <= '12' and '01' <= d <= '31':
                    detected_date = f"{y}-{m}-{d}"

            # Thumbnail discovery for VIDEO entries:
            thumb_rel = None

            # 1) Check colocated with the .txt file in the creator's folder (primary)
            rel_folder = os.path.relpath(c_path, CONTENT_DIR).replace('\\', '/')
            for ext in ('webp', 'jpg', 'jpeg', 'png'):
                colocated = os.path.join(c_path, f"{title_raw}.{ext}")
                if os.path.isfile(colocated):
                    thumb_rel = f"/content/{rel_folder}/{title_raw}.{ext}"
                    break

            # 2) If not found in content, check assets/images/videos/<creator_slug>/ as fallback
            if thumb_rel is None:
                thumb_dir = os.path.join(os.path.dirname(__file__), 'assets', 'images', 'videos', creator_slug)
                if os.path.isdir(thumb_dir):
                    for ext in ('webp', 'jpg', 'jpeg', 'png'):
                        candidate = os.path.join(thumb_dir, f"{title_raw}.{ext}")
                        if os.path.isfile(candidate):
                            thumb_rel = f"{THUMB_ROOT}/{creator_slug}/{title_raw}.{ext}"
                            break

            # Final fallback is the site placeholder
            if thumb_rel is None:
                thumb_rel = '/assets/images/placeholder.svg'

            entry = {
                'id': vid_id,
                'artist': creator_name.replace('-', ' ').title(),
                'artist_slug': creator_slug,
                'title': title,
                'thumbnail': thumb_rel,
                'tags': [],
                'date': detected_date
            }

            # Add Fileditch link as 'iframe' (redirect to watch on fileditch)
            if fileditch_url:
                entry['iframe'] = fileditch_url

            # Add Turbo link as 'embed_url' (direct embed on page)
            if turbo_url:
                entry['embed_url'] = turbo_url

            entries.append(entry)
            seen_ids.add(vid_id)
            created_count += 1

        if created_count > 0 or skipped_count > 0:
            print(f"Creator '{creator_name}' -> {created_count} vidéos")

    # New layout support:
    # - content/creator/<creator_name>/  => flat creators (no parent slugging)
    # - content/studio/<studio_name>/<child_creator>/ => parent-child slugging only inside studios
    # If neither 'creator' nor 'studio' folders exist, fall back to legacy behavior (top-level folders as creators).
    dir_entries = sorted(os.listdir(CONTENT_DIR))
    if 'creator' in dir_entries or 'studio' in dir_entries:
        # Process creators in content/creator (flat)
        creator_dir = os.path.join(CONTENT_DIR, 'creator')
        if os.path.isdir(creator_dir):
            for creator in sorted(os.listdir(creator_dir)):
                c_path = os.path.join(creator_dir, creator)
                if not os.path.isdir(c_path):
                    continue
                # Do not recurse into subfolders for creators: they should be simple slugs
                process_dir_for_creator(c_path, creator, parent_slug=None, recurse_subfolders=False)

        # Process studios in content/studio
        studio_dir = os.path.join(CONTENT_DIR, 'studio')
        if os.path.isdir(studio_dir):
            for studio in sorted(os.listdir(studio_dir)):
                s_path = os.path.join(studio_dir, studio)
                if not os.path.isdir(s_path):
                    continue
                studio_slug = slugify(studio)
                # Process only child creators inside the studio and prefix them with studio slug
                # (do NOT process files directly in the studio folder)
                for child in sorted(os.listdir(s_path)):
                    child_path = os.path.join(s_path, child)
                    if os.path.isdir(child_path):
                        process_dir_for_creator(child_path, child, parent_slug=studio_slug, recurse_subfolders=False)
    else:
        # Legacy behavior: treat each top-level folder in CONTENT_DIR as a creator and allow nested subfolders
        for creator in dir_entries:
            c_path = os.path.join(CONTENT_DIR, creator)
            if not os.path.isdir(c_path):
                continue
            process_dir_for_creator(c_path, creator, parent_slug=None, recurse_subfolders=True)
    
    return entries


def main():
    entries = build_entries()
    # Build creators -> thumbnail mapping (creator covers live in `assets/images/`)
    creators_map = {}
    images_root = os.path.join(os.path.dirname(__file__), 'assets', 'images')
    
    def find_thumb_for_slug(slug: str) -> str:
        """Search for an image in assets/images/ whose slugified basename matches the given slug.
        For studio-prefixed slugs (e.g., 'nubiles-porn-bratty-sis'), also try the child name alone (e.g., 'bratty-sis')."""
        if not os.path.isdir(images_root):
            return '/assets/images/placeholder.svg'
        
        # First try exact match
        for existing_file in os.listdir(images_root):
            name_wo_ext = re.sub(r'\.[^.]+$', '', existing_file)
            if slugify(name_wo_ext) == slug:
                return f"/assets/images/{existing_file}"
        
        # For studio-prefixed slugs, try the child name alone
        # e.g., if slug is "nubiles-porn-bratty-sis", try "bratty-sis"
        if '-' in slug:
            parts = slug.split('-')
            # Try progressively removing prefixes
            for i in range(1, len(parts)):
                child_slug = '-'.join(parts[i:])
                for existing_file in os.listdir(images_root):
                    name_wo_ext = re.sub(r'\.[^.]+$', '', existing_file)
                    if slugify(name_wo_ext) == child_slug:
                        return f"/assets/images/{existing_file}"
        
        return '/assets/images/placeholder.svg'
    
    # Build creators_map respecting the new layout rules:
    # - content/creator/<creator_name>/  => simple slugs
    # - content/studio/<studio>/<child>/ => slugs like 'studio-child'
    # Fallback: if neither 'creator' nor 'studio' exists, process legacy top-level folders recursively.
    if os.path.isdir(CONTENT_DIR):
        top_level = sorted(os.listdir(CONTENT_DIR))
        if 'creator' in top_level or 'studio' in top_level:
            # content/creator: simple slugs
            creator_dir = os.path.join(CONTENT_DIR, 'creator')
            if os.path.isdir(creator_dir):
                for creator in sorted(os.listdir(creator_dir)):
                    c_path = os.path.join(creator_dir, creator)
                    if not os.path.isdir(c_path):
                        continue
                    slug = slugify(creator)
                    creators_map[slug] = find_thumb_for_slug(slug)

            # content/studio: only child creators with studio prefix
            studio_dir = os.path.join(CONTENT_DIR, 'studio')
            if os.path.isdir(studio_dir):
                for studio in sorted(os.listdir(studio_dir)):
                    s_path = os.path.join(studio_dir, studio)
                    if not os.path.isdir(s_path):
                        continue
                    studio_slug = slugify(studio)
                    # Process only child creators (not the studio itself)
                    for child in sorted(os.listdir(s_path)):
                        child_path = os.path.join(s_path, child)
                        if not os.path.isdir(child_path):
                            continue
                        child_slug = slugify(child)
                        combined = f"{studio_slug}-{child_slug}"
                        creators_map[combined] = find_thumb_for_slug(combined)
        else:
            # Legacy recursive behavior for top-level folders
            def process_creators_recursive(dirpath: str, parent_slug: str = None):
                for creator in sorted(os.listdir(dirpath)):
                    c_path = os.path.join(dirpath, creator)
                    if not os.path.isdir(c_path):
                        continue
                    slug = slugify(creator)
                    if parent_slug:
                        slug = f"{parent_slug}-{slug}"
                    creators_map[slug] = find_thumb_for_slug(slug)
                    process_creators_recursive(c_path, slug)

            process_creators_recursive(CONTENT_DIR)
    else:
        # content dir not present, no creators to map
        pass
    
    # Auto-generate parent entries in creators_map ONLY for studio children
    # Only if we're using the new layout (content/creator/ and content/studio/)
    if os.path.isdir(CONTENT_DIR):
        top_level = sorted(os.listdir(CONTENT_DIR))
        if 'studio' in top_level:
            studio_dir = os.path.join(CONTENT_DIR, 'studio')
            # Iterate through studios and ensure parent entries exist for each
            for studio in sorted(os.listdir(studio_dir)):
                s_path = os.path.join(studio_dir, studio)
                if os.path.isdir(s_path):
                    studio_slug = slugify(studio)
                    # Ensure the studio parent exists in creators_map
                    if studio_slug not in creators_map:
                        creators_map[studio_slug] = find_thumb_for_slug(studio_slug)
                        print(f"Auto-created studio parent slug: {studio_slug}")
    
    # Écriture directe sans fusion : écrase les fichiers à chaque exécution
    entries.sort(key=lambda x: (x.get('artist_slug',''), x.get('id','')))
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Ecrit {len(entries)} entrées dans {OUTPUT_JSON}")
    
    # Write creators.json with auto-generated parents
    CREATORS_JSON = os.path.join(os.path.dirname(__file__), 'assets', 'data', 'creators.json')
    with open(CREATORS_JSON, 'w', encoding='utf-8') as f:
        json.dump(creators_map, f, ensure_ascii=False, indent=2)
    print(f"Ecrit {len(creators_map)} créateurs dans {CREATORS_JSON}")


if __name__ == '__main__':
    main()
