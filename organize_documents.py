#!pip install transformers torch sentencepiece langchain unstructured
#!pip install tf-keras


import os
import shutil
import transformers
print(transformers.__version__)
from transformers import pipeline
from unstructured.partition.auto import partition
import re

# ========== CONFIGURATION ==========
SOURCE_DIR = "./documents"
DEST_DIR = "./sorted"

# Charger un modèle de classification de texte (multilingue)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Liste de thèmes possibles (tu peux en ajouter)
CATEGORIES = [
    "Physique", "Mathématiques", "Informatique", "Intelligence Artificielle",
    "Philosophie", "Littérature", "Biologie", "Chimie", "Économie", "Sociologie"
]

# ========== EXTRACTION DU TEXTE ==========
def extract_text_from_file(filepath):
    try:
        elements = partition(filename=filepath)
        text = "\n".join([el.text for el in elements if hasattr(el, "text")])
        return text.strip()
    except Exception as e:
        print(f"⚠️ Erreur lors de l’extraction de {filepath} : {e}")
        return ""

# ========== CLASSIFICATION ==========
def detect_category(text):
    if not text or len(text) < 50:
        return "Inconnu"
    result = classifier(text[:1000], CATEGORIES)  # on limite à 1000 caractères
    label = result["labels"][0]
    return label

# ========== RANGEMENT ==========
def move_to_category(filepath, category):
    basename = os.path.basename(filepath)
    dest_folder = os.path.join(DEST_DIR, category)
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, basename)
    shutil.move(filepath, dest_path)
    print(f"✅ {basename} → {category}")

# ========== PIPELINE PRINCIPAL ==========
def organize_documents():
    for filename in os.listdir(SOURCE_DIR):
        filepath = os.path.join(SOURCE_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        print(f"\n🔍 Analyse de {filename}...")
        text = extract_text_from_file(filepath)
        category = detect_category(text)
        move_to_category(filepath, category)

if __name__ == "__main__":
    organize_documents()

