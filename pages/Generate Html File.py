import os
import shutil

def creer_fichiers_html(source_html, nombre_fichiers, dossier_sortie):
    """
    Crée plusieurs fichiers HTML à partir d'un fichier source en conservant l'extension d'origine.
    
    :param source_html: Chemin du fichier source
    :param nombre_fichiers: Nombre de fichiers à générer
    :param dossier_sortie: Dossier où stocker les fichiers générés
    """
    
    if not os.path.exists(source_html):
        print("Le fichier source n'existe pas.")
        return
    
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)
    
    extension = os.path.splitext(source_html)[1]  # Récupérer l'extension du fichier source
    
    for i in range(1, nombre_fichiers + 1):
        destination = os.path.join(dossier_sortie, f"{i}{extension}")
        shutil.copy(source_html, destination)
        print(f"Fichier généré : {destination}")

# Exemple d'utilisation
source_html = "C:/Users/test/Documents/Html Source/1.html"  # Remplacez par le chemin de votre fichier source
nombre_fichiers = 121          # Nombre de fichiers à générer
dossier_sortie = "C:/Users/test/Documents/GitHub/passasa.github.io/pages/Bibliothèque-Vidéo/Eva Elfie"  # Dossier de sortie

creer_fichiers_html(source_html, nombre_fichiers, dossier_sortie)
