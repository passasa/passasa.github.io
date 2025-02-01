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
