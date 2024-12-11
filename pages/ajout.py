import os

# Ligne à ajouter
LINE_TO_ADD = '<link href="/assets/others/Style.css" rel="stylesheet">\n'

# Fonction pour vérifier si la ligne est déjà présente
def line_exists(file_path, line):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return line.strip() in content

# Fonction pour insérer une ligne à la ligne 6
def insert_line(file_path, line):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Ajouter la ligne à la position 6 si possible
    if len(lines) >= 6:
        lines.insert(5, line)
    else:
        lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

# Fonction principale pour parcourir les fichiers HTML
def process_html_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if not line_exists(file_path, LINE_TO_ADD):
                    print(f"Modifying: {file_path}")
                    insert_line(file_path, LINE_TO_ADD)
                else:
                    print(f"Already exists: {file_path}")

# Exemple d'utilisation
directory_to_scan = "C:/Users/test/Documents/Site GentleLeak/pages/Bibliothèque-Vidéo"  # Remplacez par votre chemin
process_html_files(directory_to_scan)
