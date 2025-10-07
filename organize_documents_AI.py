import os
import shutil
import json
import pandas as pd
import plotly.express as px

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
    "GGE","GHD","Lieb-Liniger","Diffusif","sex"
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
def classify_document(filename, text, threshold=0.3, top_k=5):
    if not text or len(text) < 50:
        return {"categories": {"Inconnu": 0.0}}

    # Classification sur les 1000 premiers caractères
    result = classifier(text[:1000], CATEGORIES, multi_label=True)

    # On récupère les catégories dont la probabilité dépasse le seuil
    categories = {
        label: float(score)
        for label, score in zip(result["labels"], result["scores"])
        if score >= threshold
    }

    # Si aucune catégorie ne dépasse le seuil, on garde les top_k
    if not categories:
        categories = {
            label: float(score)
            for label, score in list(zip(result["labels"], result["scores"]))[:top_k]
        }

    return {"categories": categories}

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
    
    # slider avant la boucle
    threshold = st.slider("Seuil de probabilité minimale", 0.0, 1.0, 0.3, 0.05, key="threshold_slider")

    if st.button("Lancer l'analyse"):
        for filename in os.listdir(SOURCE_DIR):
            filepath = os.path.join(SOURCE_DIR, filename)
            if not os.path.isfile(filepath):
                continue

            with st.spinner(f"Analyse de {filename}..."):
                text = extract_text(filepath)
                #threshold = st.slider(
                #    f"Seuil de probabilité minimale pour {filename}",
                #    0.0, 1.0, 0.3, 0.05,
                #    key=f"threshold_{filename}"
                #) ## pour chaque fichier
                prediction = classify_document(filename, text,threshold=threshold)
                results[filename] = {
                    "categories": prediction["categories"],
                    "path": filepath,
                }

        save_results(results)
        st.success("Analyse terminée ✅")

    # --- Section visualisation ---
    if results:
        st.header("🧩 Résultats du classement")
        df = pd.DataFrame([
            {"fichier": f, "catégories": ", ".join([f"{k} ({v:.2f})" for k, v in info["categories"].items()]) , "path": info["path"]}
            for f, info in results.items()
        ])
        st.dataframe(df)

        # --- Sélection d’un fichier pour visualiser les probabilités ---
        st.subheader("📊 Visualisation des probabilités")
        selected_file = st.selectbox("Choisir un fichier :", list(results.keys()))

        if selected_file:
            cat_data = results[selected_file]["categories"]
            chart_df = pd.DataFrame({
                "Catégorie": list(cat_data.keys()),
                "Probabilité": list(cat_data.values())
            }).sort_values("Probabilité", ascending=True)

            fig = px.bar(
                chart_df,
                x="Probabilité",
                y="Catégorie",
                orientation="h",
                text="Probabilité",
                range_x=[0, 1],
                title=f"Probabilités de classification pour : {selected_file}"
            )

            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50))
            st.plotly_chart(fig, use_container_width=True)

        # --- Correction manuelle ---
        st.subheader("✏️ Correction manuelle")
        filename = st.selectbox("Choisir un fichier à corriger :", list(results.keys()), key="correction_select")

        if filename:
            current = results[filename]
            # On prend la catégorie principale actuelle (celle avec la probabilité max)
            current_main = max(current["categories"], key=current["categories"].get)
            new_category = st.selectbox(
                f"Modifier la catégorie principale de {filename} :",
                CATEGORIES + ["Inconnu"],
                index=CATEGORIES.index(current_main) if current_main in CATEGORIES else len(CATEGORIES),
                key="new_category_select"
            )

            if st.button("Valider la correction"):
                # On modifie la catégorie dominante manuellement
                results[filename]["categories"] = {new_category: 1.0}
                save_results(results)
                st.success(f"{filename} → {new_category}")

        # --- 🔎 Recherche multicritère ---
        st.header("🔎 Recherche par catégories")

        selected_categories = st.multiselect(
            "Sélectionner une ou plusieurs catégories à rechercher :",
            CATEGORIES,
            default=[]
        )

        if selected_categories:
            filtered_results = {
                fname: info for fname, info in results.items()
                if any(cat in info["categories"] for cat in selected_categories)
                #if all(cat in info["categories"] for cat in selected_categories) #plus scrit

            }

            if filtered_results:
                st.subheader(f"📄 {len(filtered_results)} document(s) trouvé(s)")
                filtered_df = pd.DataFrame([
                    {
                        "Fichier": f,
                        "Catégories": ", ".join([
                            f"{k} ({v:.2f})" for k, v in info["categories"].items()
                        ]),
                        "Ouvrir": f"[🔗 Ouvrir]({info['path']})"
                    }
                    for f, info in filtered_results.items()
                ])
                st.write(filtered_df.to_markdown(index=False), unsafe_allow_html=True)
            else:
                st.info("Aucun document ne correspond aux catégories sélectionnées.")
        else:
            st.write("➡️ Sélectionnez au moins une catégorie pour lancer la recherche.")


        # Rangement automatique
        if st.button("📂 Ranger les fichiers"):
            for filename, info in results.items():
                if os.path.exists(info["path"]):
                    # Catégorie dominante = celle avec la plus grande probabilité
                    main_category = max(info["categories"], key=info["categories"].get)
                    move_file(info["path"], main_category)
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
