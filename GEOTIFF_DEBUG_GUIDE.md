# 🐛 Guide de Debug GeoTIFF - CanopyLens

## 📋 Problème Identifié

Les fichiers TIF/TIFF ne s'affichent pas correctement dans l'application CanopyLens.

## 🔍 Debugs Ajoutés

### 1. **Dans `load_geotiff()`**

Logs de debug ajoutés à chaque étape critique :

```python
# Entrée dans la fonction
st.write("🐛 DEBUG: Entering load_geotiff()")

# Sauvegarde du fichier temporaire
st.write(f"🐛 DEBUG: Temp file created: {tmp_path}, size: {len(file_data)} bytes")

# Ouverture avec rasterio
st.write(f"🐛 DEBUG: Rasterio opened successfully - width={src.width}, height={src.height}, bands={src.count}")

# Extraction des métadonnées
st.write(f"🐛 DEBUG: Metadata extracted - dtype: {metadata['dtype']}, resolution: {metadata['resolution']}")

# Sélection des bandes
st.write(f"🐛 DEBUG: Multispectral detected, using bands B4, B3, B2")
# ou
st.write(f"🐛 DEBUG: Standard RGB detected")
# ou
st.write(f"🐛 DEBUG: Grayscale detected, duplicating")

# Lecture de chaque bande
st.write(f"🐛 DEBUG: Band {idx} shape: {band.shape}, dtype: {band.dtype}, min: {band.min()}, max: {band.max()}")

# Empilement RGB
st.write(f"🐛 DEBUG: Stacked RGB shape: {rgb.shape}, dtype: {rgb.dtype}")

# Normalisation
st.write(f"🐛 DEBUG: Normalizing based on dtype: {dtype}")
st.write(f"🐛 DEBUG: RGB before normalization - shape: {rgb.shape}, dtype: {rgb.dtype}, min: {rgb.min()}, max: {rgb.max()}")

# Vérification des données vides
if rgb.max() == 0:
    st.write(f"🐛 DEBUG: WARNING: All pixel values are 0!")

# Percentiles par canal
st.write(f"🐛 DEBUG: Channel {i} - p2: {p2}, p98: {p98}")
st.write(f"🐛 DEBUG: Global percentiles - p2: {p2}, p98: {p98}")

# Après normalisation
st.write(f"🐛 DEBUG: After normalization - min: {rgb.min()}, max: {rgb.max()}, dtype: {rgb.dtype}")

# Création de l'image PIL
st.write(f"🐛 DEBUG: Creating PIL Image from array")
st.write(f"🐛 DEBUG: PIL Image created - size: {pil_image.size}, mode: {pil_image.mode}")

# Test d'affichage avant retour
st.write(f"🐛 DEBUG: Testing image display")
st.image(pil_image, caption="DEBUG: Raw GeoTIFF before return", use_container_width=True)

# Sortie de la fonction
st.write(f"🐛 DEBUG: Returning from load_geotiff()")
```

### 2. **Dans le chargement du fichier**

```python
# Fichier uploadé
st.write(f"🐛 DEBUG: File uploaded - name: {uploaded_file.name}, size: {uploaded_file.size} bytes")

# Extension détectée
st.write(f"🐛 DEBUG: Extension detected: '{file_extension}'")

# Détection TIF/TIFF
st.write(f"🐛 DEBUG: Detected TIF/TIFF file")

# Appel de load_geotiff()
st.write(f"🐛 DEBUG: Calling load_geotiff()")

# Retour de load_geotiff()
st.write(f"🐛 DEBUG: load_geotiff() returned - image type: {type(image)}, metadata type: {type(geotiff_metadata)}")
st.write(f"🐛 DEBUG: Image from load_geotiff - size: {image.size}, mode: {image.mode}")

# Stockage dans session_state
st.write(f"🐛 DEBUG: Stored geotiff_metadata in session_state")

# Avant safe_resize
st.write(f"🐛 DEBUG: Before safe_resize - size: {image.size}")

# Après safe_resize
st.write(f"🐛 DEBUG: After safe_resize - size: {image.size}")

# Flag image_uploaded
st.write(f"🐛 DEBUG: Set image_uploaded = True in session_state")
```

### 3. **Dans le stockage session_state**

```python
# Stockage de l'image
st.write(f"🐛 DEBUG: Stored image in session_state['loaded_image'] - size: {image.size}")

# État du session_state
st.write(f"🐛 DEBUG: Current session_state keys: {list(st.session_state.keys())}")
st.write(f"🐛 DEBUG: image_uploaded: {st.session_state.get('image_uploaded')}")
st.write(f"🐛 DEBUG: loaded_image exists: {'loaded_image' in st.session_state}")

# Image récupérée
if 'loaded_image' in st.session_state:
    st.write(f"🐛 DEBUG: loaded_image size: {st.session_state.loaded_image.size}")
```

### 4. **Section de test d'affichage**

```python
# Test Preview
st.write("### 🧪 Test: Loaded Image Preview")
st.write(f"Image type: {type(image)}")
st.write(f"Image size: {image.size}")
st.write(f"Image mode: {image.mode}")

# Conversion en numpy array
img_array = np.array(image)
st.write(f"Array shape: {img_array.shape}")
st.write(f"Array dtype: {img_array.dtype}")
st.write(f"Array min: {img_array.min()}, max: {img_array.max()}")

# Affichage de l'image
st.image(image, caption="Test Preview: Image before analysis", use_container_width=True)

# Statistiques par canal
st.write("### Channel Statistics")
# Red, Green, Blue channels avec min, max, mean
```

### 5. **Dans l'affichage de l'image**

```python
# Entrée dans la section d'affichage
st.write(f"🐛 DEBUG: Entering image display section - image_uploaded: {st.session_state.get('image_uploaded')}, image: {image is not None}")

# Avant affichage
st.write(f"🐛 DEBUG: About to display image - size: {image.size}, mode: {image.mode}")

# Après affichage
st.write(f"🐛 DEBUG: Image displayed successfully")
```

### 6. **Dans le bouton Analyser**

```python
# Bouton visible
st.write(f"🐛 DEBUG: About to show Analyze button")

# Clic sur le bouton
st.write(f"🐛 DEBUG: Analyze button clicked!")

# Début du traitement
st.write(f"🐛 DEBUG: Starting image processing")

# Résolution GeoTIFF
st.write(f"🐛 DEBUG: Using GeoTIFF resolution: {geotiff_res}")

# Appel de process_image()
st.write(f"🐛 DEBUG: Calling process_image() with image size: {image.size}")

# Fin du traitement
st.write(f"🐛 DEBUG: process_image() completed successfully")

# Stockage des résultats
st.write(f"🐛 DEBUG: Storing results in session_state")
st.write(f"🐛 DEBUG: analysis_done set to True")
```

### 7. **Dans la récupération depuis session_state**

```python
# Récupération
st.write(f"🐛 DEBUG: Retrieving image from session_state")
st.write(f"🐛 DEBUG: Retrieved image: {image is not None}, metadata: {geotiff_metadata is not None}")

# Image récupérée
if image is not None:
    st.write(f"🐛 DEBUG: Retrieved image size: {image.size}, mode: {image.mode}")
```

### 8. **Dans la gestion des erreurs**

```python
# Erreur
st.write(f"🐛 DEBUG: ERROR in file loading: {str(e)}")
st.write(f"🐛 DEBUG: Full traceback: {traceback.format_exc()}")
```

## 🎯 Améliorations de la Normalisation

### 1. **Vérification des données vides**
```python
if rgb.max() == 0:
    st.write(f"🐛 DEBUG: WARNING: All pixel values are 0!")
    st.warning("⚠️ All pixel values are 0. The image may be empty or corrupted.")
```

### 2. **Percentiles par canal**
```python
# Calculate percentiles per channel for better results
p2_values = []
p98_values = []
for i in range(3):
    channel = rgb[:, :, i]
    p2 = np.percentile(channel, 2)
    p98 = np.percentile(channel, 98)
    p2_values.append(p2)
    p98_values.append(p98)
    st.write(f"🐛 DEBUG: Channel {i} - p2: {p2}, p98: {p98}")
```

### 3. **Gestion du cas p98 <= p2**
```python
if p98 > p2:  # Normal case
    rgb = np.clip(rgb, p2, p98)
    rgb = ((rgb - p2) / (p98 - p2) * 255).astype(np.uint8)
else:
    st.write(f"🐛 DEBUG: WARNING: p98 <= p2, using simple conversion")
    # Try simple min-max normalization
    if rgb.max() > 0:
        rgb = (rgb / rgb.max() * 255).astype(np.uint8)
    else:
        rgb = rgb.astype(np.uint8)
```

### 4. **Détection automatique de la plage float**
```python
if rgb.max() > 1.0:
    st.write(f"🐛 DEBUG: Values > 1.0, assuming 0-255 range")
    rgb = np.clip(rgb, 0, 255)
    rgb = rgb.astype(np.uint8)
else:
    st.write(f"🐛 DEBUG: Values in 0-1 range, scaling to 0-255")
    rgb = np.clip(rgb, 0, 1)
    rgb = (rgb * 255).astype(np.uint8)
```

## 📊 Comment Utiliser les Debugs

### Étape 1 : Lancer l'application
```bash
streamlit run app.py
```

### Étape 2 : Uploader un fichier TIF
- Uploadez votre fichier TIF/TIFF
- Observez les messages 🐛 DEBUG qui s'affichent

### Étape 3 : Analyser les logs
Cherchez les messages dans l'ordre :

1. **Fichier uploadé** :
   ```
   🐛 DEBUG: File uploaded - name: xxx.tif, size: xxx bytes
   🐛 DEBUG: Extension detected: 'tif'
   🐛 DEBUG: Detected TIF/TIFF file
   ```

2. **Chargement GeoTIFF** :
   ```
   🐛 DEBUG: Calling load_geotiff()
   🐛 DEBUG: Entering load_geotiff()
   🐛 DEBUG: Temp file created: /tmp/xxx.tif, size: xxx bytes
   🐛 DEBUG: Rasterio opened successfully - width=xxx, height=xxx, bands=xxx
   ```

3. **Extraction des bandes** :
   ```
   🐛 DEBUG: Metadata extracted - dtype: uint16, resolution: (10.0, 10.0)
   🐛 DEBUG: Multispectral detected, using bands B4, B3, B2
   🐛 DEBUG: Band 0 shape: (xxx, xxx), dtype: uint16, min: xxx, max: xxx
   ```

4. **Normalisation** :
   ```
   🐛 DEBUG: Normalizing based on dtype: uint16
   🐛 DEBUG: RGB before normalization - shape: (xxx, xxx, 3), dtype: uint16, min: xxx, max: xxx
   🐛 DEBUG: Channel 0 - p2: xxx, p98: xxx
   🐛 DEBUG: Global percentiles - p2: xxx, p98: xxx
   🐛 DEBUG: After normalization - min: 0, max: 255, dtype: uint8
   ```

5. **Création de l'image PIL** :
   ```
   🐛 DEBUG: Creating PIL Image from array
   🐛 DEBUG: PIL Image created - size: (xxx, xxx), mode: RGB
   🐛 DEBUG: Testing image display
   ```

6. **Stockage dans session_state** :
   ```
   🐛 DEBUG: Returning from load_geotiff()
   🐛 DEBUG: load_geotiff() returned - image type: <class 'PIL.Image.Image'>, metadata type: <class 'dict'>
   🐛 DEBUG: Stored geotiff_metadata in session_state
   ```

7. **Affichage de l'image** :
   ```
   🐛 DEBUG: Entering image display section - image_uploaded: True, image: True
   🐛 DEBUG: About to display image - size: (xxx, xxx), mode: RGB
   🐛 DEBUG: Image displayed successfully
   ```

### Étape 4 : Identifier le problème

**Si l'image ne s'affiche pas, cherchez :**

1. **Données vides** :
   ```
   🐛 DEBUG: WARNING: All pixel values are 0!
   ```
   → Le fichier est corrompu ou vide

2. **Percentiles invalides** :
   ```
   🐛 DEBUG: WARNING: p98 <= p2, using simple conversion
   ```
   → Les données sont uniformes ou corrompues

3. **Erreur rasterio** :
   ```
   🐛 DEBUG: ERROR in load_geotiff: xxx
   🐛 DEBUG: Traceback: xxx
   ```
   → Le fichier n'est pas un GeoTIFF valide

4. **Image non stockée** :
   ```
   🐛 DEBUG: loaded_image exists: False
   ```
   → Problème de stockage dans session_state

5. **Image non récupérée** :
   ```
   🐛 DEBUG: Retrieved image: False, metadata: False
   ```
   → Problème de récupération depuis session_state

## 🎯 Scénarios de Test

### Test 1 : GeoTIFF Sentinel-2 (13 bandes, uint16)
```
Attendu :
- bands=13
- dtype=uint16
- Bandes B4, B3, B2 extraites
- Normalisation percentile 2-98%
- Image RGB affichée correctement
```

### Test 2 : GeoTIFF RGB standard (3 bandes, uint8)
```
Attendu :
- bands=3
- dtype=uint8
- Bandes 0, 1, 2 utilisées
- Pas de normalisation nécessaire
- Image RGB affichée correctement
```

### Test 3 : GeoTIFF grayscale (1 bande)
```
Attendu :
- bands=1
- Bande dupliquée 3 fois
- Image grayscale affichée
```

### Test 4 : Fichier corrompu
```
Attendu :
- Message d'erreur clair
- Traceback affiché
- Pas de crash
```

## 📝 Checklist de Debug

- [ ] Le fichier est bien uploadé
- [ ] L'extension est correctement détectée
- [ ] Rasterio ouvre le fichier
- [ ] Les métadonnées sont extraites
- [ ] Les bandes sont sélectionnées correctement
- [ ] Les données sont lues (min/max valides)
- [ ] La normalisation fonctionne (min=0, max=255)
- [ ] L'image PIL est créée
- [ ] L'image est stockée dans session_state
- [ ] L'image est récupérée depuis session_state
- [ ] L'image est affichée
- [ ] Le bouton Analyser est visible
- [ ] Le traitement fonctionne

## 🔧 Solutions Potentielles

### Problème 1 : Image noire
**Cause** : Données uint16 non normalisées
**Solution** : Vérifier la normalisation percentile

### Problème 2 : Image complètement blanche
**Cause** : Données float non converties
**Solution** : Vérifier la conversion float → uint8

### Problème 3 : Image avec des bandes de couleur
**Cause** : Mauvaise sélection des bandes
**Solution** : Vérifier band_indices

### Problème 4 : Erreur "cannot identify image file"
**Cause** : Fichier corrompu ou non-GeoTIFF
**Solution** : Vérifier avec `gdalinfo`

### Problème 5 : Image ne s'affiche pas
**Cause** : Problème de session_state
**Solution** : Vérifier les logs de stockage/récupération

## 📞 Support

Si les debugs ne suffisent pas :

1. Copiez tous les messages 🐛 DEBUG
2. Notez le type de fichier TIF (Sentinel-2, drone, etc.)
3. Notez les dimensions et le nombre de bandes
4. Fournissez un échantillon du fichier si possible

---

**Version** : Debug v1.0  
**Date** : 14 septembre 2026  
**Statut** : 🐛 En cours de diagnostic
