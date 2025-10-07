#!pip install transformers==4.51.3 torch sentencepiece unstructured streamlit pandas


import os
import shutil
import json
import pandas as pd

#import transformers
#print(transformers.__file__)

from transformers import pipeline
from unstructured.partition.auto import partition
import streamlit as st

# ======================
# 🔧 CONFIGURATION
# ======================
SOURCE_DIR = "./documents"
DEST_DIR = "./sorted"
RESULTS_FILE = "./results.json"

# Thèmes cibles
CATEGORIES = [
    "GGE", "Mathématiques", "GHD", "Intelligence Artificielle", "1D",
    "Philosophie", "Littérature", "Biologie", "Chimie", "Économie", "Sociologie"
]

# ======================
# 🧠 CHARGEMENT DU MODÈLE
# ======================
@st.cache_resource
def load_model():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

classifier = load_model()

# ======================
# 📖 EXTRACTION TEXTE
# ======================
def extract_text(filepath):
    try:
        elements = partition(filename=filepath)
        text = "\n".join([el.text for el in elements if hasattr(el, "text")])
        return text.strip()
    except Exception as e:
        st.warning(f"Erreur lecture {filepath} : {e}")
        return ""

# ======================
# 🔍 CLASSIFICATION
# ======================
def classify_document(filename, text):
    if not text or len(text) < 50:
        return {"label": "Inconnu", "score": 0.0}

    result = classifier(text[:1000], CATEGORIES)
    return {"label": result["labels"][0], "score": float(result["scores"][0])}

# ======================
# 📦 SAUVEGARDE JSON
# ======================
def save_results(results):
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    return {}

# ======================
# 📂 RANGEMENT FICHIER
# ======================
def move_file(filepath, category):
    basename = os.path.basename(filepath)
    dest_folder = os.path.join(DEST_DIR, category)
    os.makedirs(dest_folder, exist_ok=True)
    shutil.move(filepath, os.path.join(dest_folder, basename))

# ======================
# 🖥️ INTERFACE STREAMLIT
# ======================
def app():
    st.set_page_config(page_title="Organiseur de Documents IA", layout="wide")
    st.title("📚 Organiseur de Documents IA")
    st.markdown("Analyse et classe automatiquement vos fichiers selon leur thème.")

    results = load_results()

    # --- Section analyse automatique ---
    st.header("🔍 Analyse automatique des documents")
    if st.button("Lancer l'analyse"):
        for filename in os.listdir(SOURCE_DIR):
            filepath = os.path.join(SOURCE_DIR, filename)
            if not os.path.isfile(filepath):
                continue

            with st.spinner(f"Analyse de {filename}..."):
                text = extract_text(filepath)
                prediction = classify_document(filename, text)
                results[filename] = {
                    "category": prediction["label"],
                    "confidence": prediction["score"],
                    "path": filepath,
                }

        save_results(results)
        st.success("Analyse terminée ✅")

    # --- Section visualisation ---
    if results:
        df = pd.DataFrame.from_dict(results, orient="index")
        st.header("🧩 Résultats du classement")
        st.dataframe(df)

        # Correction manuelle
        filename = st.selectbox("Choisir un fichier à corriger :", list(results.keys()))
        if filename:
            current = results[filename]
            new_category = st.selectbox(
                f"Modifier la catégorie de {filename} :",
                CATEGORIES + ["Inconnu"],
                index=CATEGORIES.index(current["category"]) if current["category"] in CATEGORIES else len(CATEGORIES),
            )
            if st.button("Valider la correction"):
                results[filename]["category"] = new_category
                save_results(results)
                st.success(f"{filename} → {new_category}")

        # Rangement automatique
        if st.button("📂 Ranger les fichiers"):
            for filename, info in results.items():
                if os.path.exists(info["path"]):
                    move_file(info["path"], info["category"])
            st.success("Tous les fichiers ont été rangés dans leurs dossiers respectifs ✅")

# ======================
# 🚀 LANCEMENT
# ======================
if __name__ == "__main__":
    app()
    
#conda env create -f environment.yml
#conda activate mon_projet_env

# ou

#conda create -n mon_projet_env python=3.11
#conda activate mon_projet_env
#pip install -r requirements.txt

#pour desactiver

#deactivate   # venv
#conda deactivate  # conda

# run
#streamlit run organize_documents_AI.py
