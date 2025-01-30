import os

# Ligne à ajouter pour le script
SCRIPT_TO_ADD = '<script src="https://iamcdn.net/players/replace-domain.js"></script>\n'

# Fonction pour vérifier si le script est déjà présent
def script_exists(file_path, script):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return script.strip() in content

# Fonction pour insérer le script après la ligne contenant Bootstrap
def insert_script_after_bootstrap(file_path, script):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Rechercher la ligne contenant Bootstrap
    bootstrap_line_index = None
    for i, line in enumerate(lines):
        if 'bootstrap' in line.lower():
            bootstrap_line_index = i
            break

    # Si Bootstrap est trouvé, ajouter le script juste après
    if bootstrap_line_index is not None:
        lines.insert(bootstrap_line_index + 1, script)
    else:
        # Si Bootstrap n'est pas trouvé, on ajoute le script à la fin
        lines.append(script)

    # Réécrire le fichier avec la modification
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

# Fonction principale pour parcourir les fichiers HTML
def process_html_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if not script_exists(file_path, SCRIPT_TO_ADD):
                    print(f"Modifying: {file_path}")
                    insert_script_after_bootstrap(file_path, SCRIPT_TO_ADD)
                else:
                    print(f"Script already exists: {file_path}")

# Exemple d'utilisation
directory_to_scan = "C:/Users/DIAG/Documents/passasa.github.io/pages/Bibliothèque-Vidéo"  # Remplacez par votre chemin
process_html_files(directory_to_scan)
