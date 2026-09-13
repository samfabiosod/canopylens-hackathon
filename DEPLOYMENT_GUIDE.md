# 🚀 Guide de Déploiement CanopyLens - Version Python/Streamlit

## 📁 Fichiers Nécessaires

Tous les fichiers sont déjà dans le projet :

```
canopylens/
├── app.py                 # Application Streamlit principale (1301 lignes)
├── requirements.txt       # Dépendances Python
├── packages.txt           # Dépendances système (GDAL pour Streamlit Cloud)
├── pitch.md              # Documentation hackathon (FR/EN)
└── README.md             # Documentation générale
```

---

## 🖥️ Option 1 : Exécution Locale

### Prérequis
- Python 3.10 ou supérieur
- pip

### Installation

```bash
# 1. Cloner ou télécharger le projet
cd canopylens

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Sur Linux/Mac:
source venv/bin/activate
# Sur Windows:
venv\Scripts\activate

# 3. Installer les dépendances système (GDAL)
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev python3-gdal

# macOS:
brew install gdal

# Windows:
# Utiliser les binaires précompilés ou installer via conda:
# conda install -c conda-forge gdal

# 4. Installer les dépendances Python
pip install -r requirements.txt

# 5. Lancer l'application
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse :
```
http://localhost:8501
```

---

## ☁️ Option 2 : Déploiement sur Streamlit Cloud (Recommandé)

### Étape 1 : Préparer le Repository GitHub

```bash
# 1. Créer un repository GitHub
# Allez sur https://github.com/new
# Nom : canopylens
# Visibilité : Public (requis pour Streamlit Cloud gratuit)

# 2. Initialiser git dans le projet
cd canopylens
git init

# 3. Ajouter les fichiers
git add app.py requirements.txt packages.txt pitch.md README.md

# 4. Commit
git commit -m "Initial commit: CanopyLens v3.1 with GeoTIFF support"

# 5. Créer le repository distant
git remote add origin https://github.com/VOTRE_USERNAME/canopylens.git

# 6. Push
git branch -M main
git push -u origin main
```

### Étape 2 : Déployer sur Streamlit Cloud

1. **Aller sur Streamlit Cloud**
   - Visitez : https://share.streamlit.io/
   - Connectez-vous avec votre compte GitHub

2. **Déployer l'application**
   - Cliquez sur "New app"
   - Sélectionnez votre repository `canopylens`
   - Branche : `main`
   - Fichier principal : `app.py`
   - Cliquez sur "Deploy!"

3. **Attendre le déploiement**
   - Streamlit Cloud va automatiquement :
     - Lire `packages.txt` et installer GDAL
     - Lire `requirements.txt` et installer les dépendances Python
     - Construire et déployer l'application
   - Temps estimé : 3-5 minutes

4. **Accéder à l'application**
   - Une fois déployée, vous recevrez une URL comme :
   ```
   https://canopylens-votre-username.streamlit.app
   ```
   - Partagez cette URL avec le jury !

### ⚠️ Important pour Streamlit Cloud

Le fichier `packages.txt` est **essentiel** car il permet d'installer GDAL, une dépendance système requise par `rasterio` pour le support GeoTIFF.

Contenu de `packages.txt` :
```
libgdal-dev
gdal-bin
python3-gdal
libspatialindex-dev
```

---

## 🌐 Option 3 : Déploiement sur Autres Plateformes

### Heroku (Alternative)

```bash
# 1. Installer Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Créer un fichier Procfile
echo "web: sh setup.sh && streamlit run --server.port=$PORT app.py" > Procfile

# 3. Créer un script setup.sh
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
EOF

# 4. Déployer
heroku create canopylens
git push heroku main
```

### Render.com (Alternative Gratuite)

1. Créez un compte sur https://render.com
2. Créez un "Web Service"
3. Connectez votre repository GitHub
4. Build Command : `pip install -r requirements.txt`
5. Start Command : `streamlit run --server.port=$PORT --server.address=0.0.0.0 app.py`

---

## 🧪 Tests après Déploiement

### Test 1 : Upload PNG/JPG
1. Uploadez une image satellite PNG ou JPG
2. Vérifiez que l'image s'affiche
3. Cliquez sur "Analyze"
4. Vérifiez les résultats

### Test 2 : Upload GeoTIFF
1. Uploadez un fichier .tif ou .tiff
2. Vérifiez que les métadonnées s'affichent
3. Vérifiez que l'image est correctement normalisée
4. Lancez l'analyse

### Test 3 : Génération PDF
1. Lancez une analyse
2. Cliquez sur "Download Report (PDF)"
3. Vérifiez que le PDF contient toutes les informations

---

## 📊 Fonctionnalités de l'Application

### ✅ Supportées
- Upload d'images PNG, JPG, JPEG
- Upload de fichiers GeoTIFF (.tif, .tiff)
- Support Sentinel-2 (13 bandes) avec normalisation automatique
- Support RGB, RGBA, multispectral, grayscale
- Détection adaptative de la résolution
- Comptage d'arbres adaptatif (direct/ajusté/densité)
- Génération de rapports PDF professionnels
- Interface bilingue (FR/EN)
- Visualisation des contours d'arbres
- Équivalents carbone (voitures, arbres, kg CO₂/jour)

### 🎯 Cas d'Usage
- Forêt tropicale humide (150 tCO₂/ha)
- Forêt tropicale sèche (80 tCO₂/ha)
- Mangrove (200 tCO₂/ha)
- Forêt tempérée (120 tCO₂/ha)

---

## 🐛 Dépannage

### Problème : "Rasterio not installed"
**Solution** :
```bash
# Installer GDAL d'abord
sudo apt-get install gdal-bin libgdal-dev
pip install rasterio
```

### Problème : "GDAL error" sur Streamlit Cloud
**Solution** : Vérifiez que `packages.txt` contient bien :
```
libgdal-dev
gdal-bin
python3-gdal
libspatialindex-dev
```

### Problème : L'application ne démarre pas
**Solution** :
```bash
# Vérifier les logs
streamlit run app.py --logger.level=debug

# Vérifier les dépendances
pip list | grep -E "streamlit|rasterio|reportlab"
```

### Problème : GeoTIFF ne se charge pas
**Solution** :
1. Vérifiez que le fichier est un GeoTIFF valide
2. Testez avec `gdalinfo votre_fichier.tif`
3. Vérifiez les logs de debug dans la console

---

## 📝 Commandes Utiles

```bash
# Lancer localement
streamlit run app.py

# Lancer avec logs debug
streamlit run app.py --logger.level=debug

# Lancer sur un port spécifique
streamlit run app.py --server.port=8080

# Vérifier la version de Streamlit
streamlit --version

# Vérifier les dépendances installées
pip list

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade
```

---

## 🎓 Ressources

- **Streamlit Documentation** : https://docs.streamlit.io/
- **Streamlit Cloud** : https://share.streamlit.io/
- **Rasterio Documentation** : https://rasterio.readthedocs.io/
- **GDAL Documentation** : https://gdal.org/

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs dans la console
2. Consultez le fichier `DEBUG_GUIDE.md`
3. Vérifiez que toutes les dépendances sont installées
4. Testez avec un fichier PNG simple d'abord

---

**Version** : 3.1  
**Dernière mise à jour** : 14 septembre 2026  
**Statut** : ✅ Prêt pour le déploiement
