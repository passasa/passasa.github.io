import os

# Script à insérer
SCRIPT_TO_ADD = '<script src="https://iamcdn.net/players/replace-domain.js"></script>\n'

def script_exists(file_path, script):
    """Vérifie si le script est déjà présent dans le fichier."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return script.strip().lower() in content.lower()
    except Exception as e:
        print(f"Erreur de lecture du fichier {file_path}: {e}")
        return False

def insert_or_move_script_after_jquery(file_path, script):
    """Ajoute ou déplace le script juste après jQuery."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        jquery_index = None
        script_index = None

        # Trouver la dernière occurrence de jQuery et l'emplacement du script existant
        for i, line in enumerate(lines):
            if 'jquery' in line.lower():
                jquery_index = i
            if script.strip().lower() in line.lower():
                script_index = i

        # Si jQuery est trouvé
        if jquery_index is not None:
            # Si le script existe déjà mais n'est pas après jQuery, le déplacer
            if script_index is not None and script_index != jquery_index + 1:
                lines.pop(script_index)  # Supprimer l'ancienne occurrence
                jquery_index = max(0, jquery_index - (1 if script_index < jquery_index else 0))  # Ajuster l'index
                lines.insert(jquery_index + 1, script)
                print(f"Script déplacé après jQuery : {file_path}")
            # Si le script n'existe pas, l'ajouter après jQuery
            elif script_index is None:
                lines.insert(jquery_index + 1, script)
                print(f"Script ajouté après jQuery : {file_path}")
        else:
            # Si jQuery n'est pas trouvé, ajouter le script à la fin
            if script_index is None:
                lines.append(script)
                print(f"Script ajouté en fin de fichier (jQuery non trouvé) : {file_path}")

        # Réécriture du fichier
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    except Exception as e:
        print(f"Erreur lors de la modification de {file_path}: {e}")

def process_html_files(directory):
    """Parcourt tous les fichiers HTML d'un répertoire et applique les modifications."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                insert_or_move_script_after_jquery(file_path, SCRIPT_TO_ADD)

# Exécution
directory_to_scan = r"C:/Users/DIAG/Documents/passasa.github.io/pages/Bibliothèque-Vidéo"
process_html_files(directory_to_scan)
