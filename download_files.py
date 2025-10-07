import os
import requests

def download_files(urls, directories):
    """
    Télécharge des fichiers à partir d'une liste d'URLs dans les répertoires correspondants.
    
    Args:
        urls (list[str]): liste des URLs à télécharger
        directories (list[str]): liste des répertoires correspondants
    """
    if len(urls) != len(directories):
        raise ValueError("Les deux listes doivent avoir la même longueur.")
    
    for url, directory in zip(urls, directories):
        # Créer le dossier s'il n'existe pas
        os.makedirs(directory, exist_ok=True)
        
        # Nom du fichier local
        filename = os.path.basename(url.split("?")[0])  # ignore les paramètres d'URL
        file_path = os.path.join(directory, filename)
        
        # Vérifie si le fichier existe déjà
        if os.path.exists(file_path):
            print(f"✅ Déjà présent : {file_path}")
            continue
        
        # Téléchargement
        try:
            print(f"⬇️ Téléchargement de {url} vers {file_path}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Sauvegarde du fichier
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"✅ Fichier téléchargé : {file_path}")
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors du téléchargement de {url} : {e}")


urls = [
    "https://arxiv.org/pdf/2408.04502.pdf",
    "https://arxiv.org/pdf/2506.05279.pdf",
    "https://arxiv.org/pdf/2505.05839.pdf",
    "https://arxiv.org/pdf/2312.15344.pdf",
    "https://arxiv.org/pdf/1309.3471.pdf",
    "https://arxiv.org/pdf/2406.17569.pdf",
    "https://www.numdam.org/item/AST_2013__350__R1_0.pdf",
    "https://www.imo.universite-paris-saclay.fr/~frederic.paulin/notescours/cours18sep23TESD.pdf",
    "https://images.math.cnrs.fr/wp-content/uploads/2024/10/10.60868ey52-3C40.pdf",
    "https://univ-scholarvox-com.ezproxy.universite-paris-saclay.fr/reader/docid/45006579/page/54?searchterm=M%20theory",
]

directories = [
    "./documents",
    "./documents",
    "./documents",
    "./documents",
    "./documents",
    "./documents",
    "./documents",
    "./documents",
    "./documents",
    "./documents"
]

download_files(urls, directories)

