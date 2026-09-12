# 🐛 Guide de Debug CanopyLens

## Problème Signalé
L'utilisateur signale que lorsqu'il upload un fichier TIFF, rien ne se passe - même pas l'aperçu.

## Outils de Debug Disponibles

### 1. Version Debug Complète : `app_debug.py`

Cette version teste chaque étape du chargement d'un fichier TIFF de manière isolée :

```bash
streamlit run app_debug.py
```

**Ce qu'elle fait :**
- ✅ Vérifie les imports (rasterio, cv2)
- ✅ Affiche les informations du fichier uploadé
- ✅ Détecte l'extension
- ✅ Lit le fichier avec rasterio
- ✅ Affiche les métadonnées (bands, dtype, resolution, etc.)
- ✅ Lit chaque bande individuellement
- ✅ Applique la normalisation
- ✅ Crée l'image PIL
- ✅ Affiche l'image

**Utilisation :**
1. Lancez `app_debug.py`
2. Uploadez votre fichier TIFF
3. Regardez les logs qui s'affichent à l'écran
4. Identifiez à quelle étape le processus échoue

### 2. Version Principale avec Logs : `app.py`

J'ai ajouté des logs de debug dans `app.py` (marqués avec 🐛 DEBUG) :

```bash
streamlit run app.py
```

**Logs ajoutés :**
- Au début du chargement du fichier
- Lors de la détection d'extension
- Dans `load_geotiff()` à chaque étape
- Lors du stockage dans session_state
- Lors de l'affichage de l'image

## Étapes de Diagnostic

### Étape 1 : Vérifier les Imports

```bash
python -c "import rasterio; print(rasterio.__version__)"
```

**Résultat attendu :** Numéro de version (ex: 1.3.9)

**Si erreur :**
```bash
pip install rasterio
```

### Étape 2 : Tester avec app_debug.py

```bash
streamlit run app_debug.py
```

Uploadez votre fichier TIFF et regardez les logs :

**Scénarios possibles :**

#### ✅ Tout fonctionne
```
✅ Rasterio importé avec succès
✅ Fichier ouvert avec rasterio
✅ Image PIL créée
✅ Image affichée
```
→ Le problème est ailleurs dans `app.py`

#### ❌ Erreur d'import
```
❌ Erreur import rasterio: No module named 'rasterio'
```
→ Installez rasterio : `pip install rasterio`

#### ❌ Erreur d'ouverture
```
❌ Erreur lors de la lecture: [erreur spécifique]
```
→ Le fichier TIFF est peut-être corrompu ou dans un format non supporté

#### ❌ Erreur de normalisation
```
⚠️ p98 <= p2, normalisation ignorée
```
→ Le fichier a des valeurs inhabituelles, mais devrait quand même fonctionner

### Étape 3 : Tester avec app.py

```bash
streamlit run app.py
```

Uploadez votre fichier TIFF et regardez les logs 🐛 DEBUG :

**Scénarios possibles :**

#### ✅ Logs complets
```
🐛 DEBUG: Fichier uploadé - Nom: test.tif, Taille: 12345678 bytes
🐛 DEBUG: Extension détectée: 'tif'
🐛 DEBUG: C'est un fichier TIFF
🐛 DEBUG: Rasterio disponible, appel de load_geotiff()
🐛 DEBUG load_geotiff: Début de la fonction
🐛 DEBUG load_geotiff: Sauvegarde temporaire du fichier
🐛 DEBUG load_geotiff: Fichier temporaire créé: /tmp/tmpXXXXXX.tif
🐛 DEBUG load_geotiff: Ouverture avec rasterio
🐛 DEBUG load_geotiff: Fichier ouvert - width=1000, height=1000, bands=3
...
🐛 DEBUG: load_geotiff() a retourné - image: <PIL.Image>, metadata: <dict>
🐛 DEBUG: Image size: (1000, 1000)
✅ GeoTIFF loaded: 1000×1000px, 3 bands, uint16
🐛 DEBUG: Image stockée dans session_state - size: (1000, 1000)
🐛 DEBUG: Vérification affichage - image_uploaded: True, image: True
🐛 DEBUG: Conditions d'affichage remplies - affichage de l'image
🐛 DEBUG: Appel de st.image() avec image de taille (1000, 1000)
🐛 DEBUG: Image affichée avec succès
```
→ Tout fonctionne, le problème est résolu

#### ❌ Logs incomplets
Si les logs s'arrêtent à un certain point, cela indique où le problème se situe :

**Exemple 1 : S'arrête avant load_geotiff()**
```
🐛 DEBUG: C'est un fichier TIFF
🐛 DEBUG: RASTERIO_AVAILABLE = False
```
→ Rasterio n'est pas installé

**Exemple 2 : S'arrête dans load_geotiff()**
```
🐛 DEBUG load_geotiff: Ouverture avec rasterio
[plus rien]
```
→ Le fichier ne peut pas être ouvert par rasterio (corrompu ou format non supporté)

**Exemple 3 : S'arrête après load_geotiff()**
```
🐛 DEBUG: load_geotiff() a retourné - image: None, metadata: None
```
→ `load_geotiff()` a échoué silencieusement

**Exemple 4 : S'arrête avant l'affichage**
```
🐛 DEBUG: Image stockée dans session_state - size: (1000, 1000)
🐛 DEBUG: Vérification affichage - image_uploaded: False, image: None
```
→ Problème avec session_state (l'image n'est pas correctement stockée)

## Solutions Possibles

### Solution 1 : Rasterio non installé

```bash
pip install rasterio
```

### Solution 2 : GDAL non installé (dépendance de rasterio)

**Sur Ubuntu/Debian :**
```bash
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev
pip install rasterio
```

**Sur macOS :**
```bash
brew install gdal
pip install rasterio
```

**Sur Windows :**
```bash
# Utiliser les binaires précompilés
pip install rasterio --only-binary :all:
```

### Solution 3 : Fichier TIFF corrompu

Testez avec un autre fichier TIFF pour vérifier si le problème vient du fichier.

### Solution 4 : Format TIFF non supporté

Certains formats TIFF compressés ne sont pas supportés par rasterio. Essayez de convertir :

```bash
gdal_translate -co COMPRESS=NONE input.tif output.tif
```

### Solution 5 : Problème de session_state

Si l'image est chargée mais pas affichée, essayez :
1. Cliquez sur "🔃 Reload App"
2. Uploadez à nouveau le fichier

## Informations à Fournir

Pour mieux vous aider, fournissez :

1. **Les logs complets** affichés par `app_debug.py` ou `app.py`
2. **La sortie de** :
   ```bash
   python -c "import rasterio; print(rasterio.__version__)"
   python -c "import sys; print(sys.version)"
   ```
3. **Les informations du fichier TIFF** (si possible) :
   ```bash
   gdalinfo votre_fichier.tif
   ```
4. **Une capture d'écran** de l'interface Streamlit avec les logs visibles

## Contact

Si le problème persiste après avoir suivi ces étapes, fournissez les informations ci-dessus pour un diagnostic plus précis.
