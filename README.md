# 📚 Organiseur de Documents IA

Analyse et classe automatiquement vos fichiers selon leur thème grâce à l'IA.

---

## 🗂️ Structure du projet

* `organizer/` — Répertoire racine du projet
    * `README.md`
    * `requirements.txt`
    * `environment.yml` # Optionnel pour conda
    * `organize_documents_AI.py`# Script principal
    * `documents/`# Dossier contenant les fichiers à analyser
    * `sorted/`# Dossier où les fichiers seront rangés automatiquement
    * `results.json`# Fichier sauvegardant les résultats de classification
    * `src/`# Code source si projet plus complexe
    * `notebooks/`# Jupyter notebooks
    * `tests/` # Tests unitaires



---

## ⚙️ Installation

### 1️⃣ Avec `venv`

```bash
# Créer l'environnement
python -m venv mon_projet_env

# Activer l'environnement
source mon_projet_env/bin/activate   # macOS / Linux
#mon_projet_env\Scripts\activate      # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 2️⃣ Avec `conda`

```bash
# Créer l'environnement
conda create -n mon_projet_env python=3.11

# Activer l'environnement
conda activate mon_projet_env

# Installer les dépendances
pip install -r requirements.txt
# ou
conda env create -f environment.yml
```

### 3️⃣ `Désactivation`

```bash
deactivate         # venv
conda deactivate   # conda
```


## 📄 Requirements

```makefile
transformers==4.51.3
torch
sentencepiece
streamlit
pandas
unstructured[pdf]
```

> [!IMPORTANT]
> Le [pdf] est nécessaire pour analyser les fichiers PDF avec unstructured.

## 🚀 Lancement
```bash
streamlit run organize_documents_AI.py
```

- L’interface s’ouvre dans le navigateur.
- Tu peux analyser automatiquement tous les documents du dossier `./documents`
- Visualiser les résultats et corriger manuellement si besoin.
- Ranger les fichiers dans des dossiers par thème via le bouton "📂 Ranger les fichiers".

## 🖼️ Aperçu de l’interface

1. Analyse automatique des documents :
2. Résultats et correction manuelle :
3. Rangement des fichiers :

> [!WARNING]
> Les images sont à ajouter dans `docs/` ou remplacer par vos propres captures d’écran.

## 🧠 Thèmes cibles par défaut

- Physique
- Mathématiques
- Informatique
- Intelligence Artificielle
- Philosophie
- Littérature
- Biologie
- Chimie
- Économie
- Sociologie

> [!TIP]
> On peut bien sûr **proposer d’autres thèmes** selon tes besoins.

## 🔄 Workflow Exemple

1. Placer les fichiers à analyser dans `./documents` .
2. Lancer l’application :
```bash
streamlit run organize_documents_AI.py
```
3. Cliquer sur "**Lancer l'analyse**" pour que l'IA classe automatiquement les documents.
4. Vérifier les résultats dans le tableau interactif.
5. Corriger manuellement les classifications si nécessaire.
6. Cliquer sur "**📂 Ranger les fichiers**" pour organiser les documents dans `./sorted`.


## 💡 Remarques

- L’analyse est limitée aux **1000 premiers caractères** pour optimiser la vitesse.
- Possibilité d’ajouter une fonctionnalité pour **rechercher des documents par thème sans les déplacer**.
- On peut créer une interface pour ** trouver tous les fichiers selon le thème** sans forcément les ranger.
- Les fichiers sont analysés automatiquement, mais tu peux **corriger manuellement la catégorie** si l’IA se trompe.
- `@st.cache_resource` est utilisé pour charger le **modèle une seule fois**, optimisant les performances, réduisant le temps de traitement.

## ⚡ Commandes utiles

- Pour réinstaller toutes les dépendances :

```bash
pip install -r requirements.txt
```

- Pour ajouter de nouveaux thèmes :  modifier la liste `CATEGORIES` dans `organize_documents_AI.py`.

- Réinitialiser les résultats :
```bash
rm results.json
```
# organisateur
