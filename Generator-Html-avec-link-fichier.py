import os
import re

def numerique_ordre(fichier):
    # Extraire le numéro du fichier en utilisant une expression régulière
    match = re.search(r'(\d+)', fichier)
    return int(match.group(1)) if match else float('inf')

def generer_html(dossier_html, fichier_liens, fichier_infos, nom_fichier="output.html"):
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
    
    # Lire les informations associées aux images à partir du fichier texte
    try:
        with open(fichier_infos, 'r', encoding='utf-8') as f:
            infos_images = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{fichier_infos}' n'existe pas.")
        return
    
    # Obtenir la liste des fichiers HTML et les trier numériquement
    fichiers_html = sorted(
        [f for f in os.listdir(dossier_html) if f.endswith('.html')],
        key=numerique_ordre
    )
    
    # Vérifiez que le nombre de fichiers HTML, de liens d'images et d'infos est le même
    if len(fichiers_html) != len(liens_images) or len(fichiers_html) != len(infos_images):
        print("Erreur: Le nombre de fichiers HTML, de liens d'images et d'infos ne correspond pas.")
        return
    
    # Commencer à construire le contenu HTML
    html_content = """<!DOCTYPE html>
<html lang='fr'>
<head>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <link href="/assets/others/Style.css" rel="stylesheet">

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vidéo Let's Post It</title>
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
            background: #291536;
            border-radius: 10px;
            padding: 10px;
            width: 350px;
            text-align: center;
            transition: transform 0.3s ease-in-out;
        }
        .image-container:hover {
            transform: scale(1.1);
        }
        .image-container img {
            width: 100%;
            border-radius: 10px;
        }
        .info {
            margin-top: 10px;
            font-size: 14px;
        }
        .image-container a {
            text-decoration: none;
            color: inherit;
            display: block;
        }

    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand">Gentle Leak</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="#navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item active"><a class="nav-link" href="/index.html">Accueil </a></li>
                <li class="nav-item"><a class="nav-link" href="/pages/bibliothèque.html">Bibliothèque</a></li>
            </ul>
        </div>
    </nav>
    <h1>Retrouvez toutes les vidéos disponibles ci-dessous</h1>
    <p>Cliquez sur les images ci-dessous pour avoir accès à la vidéo.</p>
    <div class='container'>"""
    
    # Générer le contenu HTML pour chaque image et fichier HTML
    for fichier_html, lien_image, info_image in zip(fichiers_html, liens_images, infos_images):
        chemin_html = os.path.join(dossier_html, fichier_html).replace("\\", "/")
        chemin_html = chemin_html.split("passasa.github.io")[1]  # Ajuster pour obtenir le chemin relatif
        html_content += f"""
        <div class='image-container'>
            <a href='{chemin_html}'>
                <img src='{lien_image}' alt='{fichier_html}'>
                <div class="info">{info_image}</div>
            </a>
        </div>"""
    
    html_content += """
    </div>
    
    <!-- Inclus les scripts Bootstrap JS -->

    <script>
        document.addEventListener("DOMContentLoaded", function () {
            let infoDivs = document.querySelectorAll(".info");
            infoDivs.forEach(div => {
                div.style.fontWeight = "bold";
            });
        });
    </script>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>"""
    
    # Écrire le contenu HTML dans un fichier
    with open(nom_fichier, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"Fichier {nom_fichier} généré avec {len(fichiers_html)} images cliquables.")

# Exemple d'utilisation
dossier_html = "C:/Users/test/Documents/GitHub/passasa.github.io/pages/Bibliothèque-Vidéo/He's Got Rizz"
fichier_liens = "C:/Users/test/Desktop/Image et Vidéo Content/Hes Got Rizz/Image.txt"
fichier_infos = "C:/Users/test/Desktop/Image et Vidéo Content/Hes Got Rizz/Infos.txt"  # Nouveau fichier texte contenant les infos
generer_html(dossier_html, fichier_liens, fichier_infos)
