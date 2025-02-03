import os
import re

def numerique_ordre(fichier):
    # Extraire le numéro du fichier en utilisant une expression régulière
    match = re.search(r'(\d+)', fichier)
    return int(match.group(1)) if match else float('inf')

def generer_html(dossier_html, fichier_liens, nom_fichier="output.html"):
    # Vérifiez si le dossier existe
    if not os.path.exists(dossier_html):
        print(f"Erreur: Le dossier '{dossier_html}' n'existe pas.")
        return
    
    # Lire les liens des images à partir du fichier texte
    try:
        with open(fichier_liens, 'r', encoding='utf-8') as f:
            liens_images = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{fichier_liens}' n'existe pas.")
        return

    # Obtenir la liste des fichiers HTML et les trier numériquement
    fichiers_html = sorted(
        [f for f in os.listdir(dossier_html) if f.endswith('.html')],
        key=numerique_ordre
    )

    # Vérifiez que le nombre de fichiers HTML et de liens d'images est le même
    if len(fichiers_html) != len(liens_images):
        print("Erreur: Le nombre de fichiers HTML et de liens d'images ne correspond pas.")
        return

    # Commencer à construire le contenu HTML
    html_content = """<!DOCTYPE html>
<html lang='fr'>
<head>
    <!-- Inclus Bootstrap CSS pour la barre de navigation -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <link href="/assets/others/Style.css" rel="stylesheet">
    
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vidéo Brooke Tilli</title>
    <link rel="shortcut icon" href="/assets/images/Logo-Head.webp">

    <style>
        /* Mise en page simple */
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            background-color: #0F151E;
            color: white;
        }

        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            margin-top: 50px;
        }

        .image-container {
            width: 350px;
            height: 200px;
        }

        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .image-container img:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }

    </style>
</head>
<body>
    <!--Barre de navigation-->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand">Gentle Leak</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item active">
                    <a class="nav-link" href="/index.html">Accueil </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/pages/bibliothèque.html">Bibliothèque</a>
                </li>
            </ul>
        </div>
    </nav>

    <h1>Retrouvez toutes les vidéos disponibles ci-dessous</h1>
    <p>Cliquez sur les images ci-dessous pour avoir accès à la vidéo.</p>
    
    <div class='container'>"""

    # Générer le contenu HTML pour chaque image et fichier HTML
    for fichier_html, lien_image in zip(fichiers_html, liens_images):
        chemin_html = os.path.join(dossier_html, fichier_html).replace("\\", "/")
        chemin_html = chemin_html.split("passasa.github.io")[1]  # Ajuster pour obtenir le chemin relatif
        html_content += f"""
        <div class='image-container'>
            <a href='{chemin_html}'>
                <img src='{lien_image}' alt='{fichier_html}'>
            </a>
        </div>"""

    html_content += """
    </div>
</body>
</html>"""

    # Écrire le contenu HTML dans un fichier
    with open(nom_fichier, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"Fichier {nom_fichier} généré avec {len(fichiers_html)} images cliquables.")

# Exemple d'utilisation
dossier_html = "C:/Users/test/Documents/GitHub/passasa.github.io/pages/Bibliothèque-Vidéo/Brooke Tilli"
fichier_liens = "C:/Users/test/Desktop/Image et Vidéo Content/Brooke Tilli/Image.txt"  # Remplacez par le chemin de votre fichier texte
generer_html(dossier_html, fichier_liens)
