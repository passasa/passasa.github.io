def generer_html(nombre_images, nom_fichier="output.html"):
    html_content = """<!DOCTYPE html>
<html lang='fr'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Galerie d'Images</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            background-color: #0F151E;
            color: white;
        }

        .container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }

        .image-container {
            background: #291536;
            border-radius: 15px;
            padding: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
        }

        .image-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        }

        .image-container img {
            width: 100%;
            height: auto;
            border-radius: 10px;
            margin-bottom: 1rem;
            object-fit: contain; /* Afficher l'image en entier */
            aspect-ratio: 16/9; /* Garde le format 16:9 */
            background-color: black; /* Optionnel : remplit l'espace vide */
        }

        .info {
            padding: 0.5rem;
            font-size: 0.9rem;
            font-weight: 500;
            color: #ffffff;
            margin-top: auto;
        }

        .image-container a {
            text-decoration: none;
            color: inherit;
            display: block;
            height: 100%;
        }

        h1 {
            margin: 2rem 0;
            font-size: 2rem;
            font-weight: bold;
        }

        p {
            margin-bottom: 2rem;
            color: #cccccc;
        }

        @media (max-width: 768px) {
            .container {
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 1rem;
                padding: 1rem;
            }

            h1 {
                font-size: 1.5rem;
                margin: 1rem 0;
            }
        }
    </style>
</head>
<body>
    <h1>Galerie d'Images</h1>
    <div class='container'>"""
    
    for i in range(1, nombre_images + 1):
        html_content += f"""
        <div class='image-container'>
            <a href=''>
                <img src='' alt='Image {i}'>
            </a>
        </div>"""
    
    html_content += """
    </div>
</body>
</html>"""
    
    with open(nom_fichier, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"Fichier {nom_fichier} généré avec {nombre_images} images cliquables.")

# Modifier le nombre d'images ici
generer_html(521)
