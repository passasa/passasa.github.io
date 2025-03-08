import os
import re

# Configuration
dossier_cible = "C:/Users/test/Documents/passasa.github.io/pages/Bibliothèque-Vidéo/Eva Elfie"
fichier_liens = "C:/Users/test/Desktop/Image et Vidéo Content/Eva Elfie/Filemoon.txt"

# Lire les liens depuis le fichier en conservant l'ordre
with open(fichier_liens, "r", encoding="utf-8") as f:
    liens = [ligne.strip() for ligne in f.readlines() if ligne.strip()]

# Fonction pour extraire un numéro d'un fichier
def extraire_numero(nom_fichier):
    nombres = re.findall(r'\d+', nom_fichier)  # Trouve tous les nombres
    return int(nombres[-1]) if nombres else float('inf')  # Prend le dernier nombre

# Lister et trier les fichiers HTML en conservant l'ordre naturel
fichiers_html = sorted(
    [f for f in os.listdir(dossier_cible) if f.endswith(".html")],
    key=extraire_numero
)

# Vérifier si on a assez de liens
if len(liens) != len(fichiers_html):
    print("Erreur: Le nombre de liens et de fichiers HTML ne correspond pas.")
else:
    # Associer chaque fichier au lien dans l'ordre
    for fichier, lien in zip(fichiers_html, liens):
        chemin_fichier = os.path.join(dossier_cible, fichier)
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            contenu = f.read()
        
        # Remplacement uniquement des liens Filemoon
        nouveau_contenu = re.sub(
            r"onclick=\"changeIframe\('https://filemoon\.to/d/[^']*'\)\"",
            f"onclick=\"changeIframe('{lien}')('https://filemoon\.to/d/[^']*'\)\"",
            contenu
        )
        
        # Modification des boutons Filemoon vides
        nouveau_contenu = re.sub(
            r"onclick=\"changeIframe\(''\)\">Filemoon</button>",
            f"onclick=\"changeIframe('{lien}')\">Filemoon</button>",
            nouveau_contenu
        )
        
        # Écriture du fichier modifié
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            f.write(nouveau_contenu)
        
        print(f"Lien remplacé ou ajouté dans {fichier}")
