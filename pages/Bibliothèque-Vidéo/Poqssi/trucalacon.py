import os
import re

def remove_style_tags(file_path):
    """Lit un fichier HTML, supprime les balises <style> et leur contenu, et sauvegarde le résultat."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Expression régulière pour capturer les balises <style> et leur contenu
        cleaned_content = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL)

        # Écriture du contenu nettoyé dans le fichier d'origine
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)

        print(f"Fichier traité avec succès : {file_path}")

    except Exception as e:
        print(f"Erreur lors du traitement du fichier {file_path} : {e}")

def process_html_files(directory):
    """Parcourt un répertoire pour traiter tous les fichiers HTML."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.html'):
                file_path = os.path.join(root, file)
                remove_style_tags(file_path)

if __name__ == "__main__":
    directory = input("Entrez le chemin du répertoire contenant les fichiers HTML : ").strip()
    if os.path.isdir(directory):
        process_html_files(directory)
    else:
        print("Le chemin spécifié n'est pas un répertoire valide.")
