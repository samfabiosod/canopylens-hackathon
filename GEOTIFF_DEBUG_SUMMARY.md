# 🐛 Résumé des Debugs Ajoutés - CanopyLens GeoTIFF

## 📋 Fichier Modifié

**`app.py`** - Version avec debugs complets pour GeoTIFF

## ✅ Debugs Ajoutés

### 1. **Dans la fonction `load_geotiff()`** (25+ logs)

```python
# Entrée et initialisation
st.write("🐛 DEBUG: Entering load_geotiff()")
st.write(f"🐛 DEBUG: Saving file to temp location")
st.write(f"🐛 DEBUG: Temp file created: {tmp_path}, size: {len(file_data)} bytes")

# Ouverture rasterio
st.write("🐛 DEBUG: Opening with rasterio")
st.write(f"🐛 DEBUG: Rasterio opened successfully - width={src.width}, height={src.height}, bands={src.count}")

# Métadonnées
st.write(f"🐛 DEBUG: Metadata extracted - dtype: {metadata['dtype']}, resolution: {metadata['resolution']}")

# Sélection des bandes
st.write(f"🐛 DEBUG: Multispectral detected, using bands B4, B3, B2")
# ou
st.write(f"🐛 DEBUG: Standard RGB detected")
# ou
st.write(f"🐛 DEBUG: Grayscale detected, duplicating")

# Lecture des bandes
st.write(f"🐛 DEBUG: Reading bands {band_indices}")
st.write(f"🐛 DEBUG: Band {idx} shape: {band.shape}, dtype: {band.dtype}, min: {band.min()}, max: {band.max()}")

# Empilement
st.write(f"🐛 DEBUG: Stacked RGB shape: {rgb.shape}, dtype: {rgb.dtype}")

# Normalisation
st.write(f"🐛 DEBUG: Normalizing based on dtype: {dtype}")
st.write(f"🐛 DEBUG: RGB before normalization - shape: {rgb.shape}, dtype: {rgb.dtype}, min: {rgb.min()}, max: {rgb.max()}")

# Vérification données vides
if rgb.max() == 0:
    st.write(f"🐛 DEBUG: WARNING: All pixel values are 0!")

# Percentiles par canal
st.write(f"🐛 DEBUG: Channel {i} - p2: {p2}, p98: {p98}")
st.write(f"🐛 DEBUG: Global percentiles - p2: {p2}, p98: {p98}")

# Après normalisation
st.write(f"🐛 DEBUG: After normalization - min: {rgb.min()}, max: {rgb.max()}, dtype: {rgb.dtype}")

# Gestion cas particuliers
st.write(f"🐛 DEBUG: WARNING: p98 <= p2, using simple conversion")
st.write(f"🐛 DEBUG: Converting float to uint8")
st.write(f"🐛 DEBUG: Using uint8 directly")

# Création PIL Image
st.write(f"🐛 DEBUG: Creating PIL Image from array")
st.write(f"🐛 DEBUG: PIL Image created - size: {pil_image.size}, mode: {pil_image.mode}")

# Test d'affichage
st.write(f"🐛 DEBUG: Testing image display")
st.image(pil_image, caption="DEBUG: Raw GeoTIFF before return", use_container_width=True)

# Sortie
st.write(f"🐛 DEBUG: Returning from load_geotiff()")

# Gestion erreurs
st.write(f"🐛 DEBUG: ERROR in load_geotiff: {str(e)}")
st.write(f"🐛 DEBUG: Traceback: {traceback.format_exc()}")

# Nettoyage
st.write(f"🐛 DEBUG: Temp file cleaned up")
```

### 2. **Dans le chargement du fichier** (15+ logs)

```python
# Upload
st.write(f"🐛 DEBUG: File uploaded - name: {uploaded_file.name}, size: {uploaded_file.size} bytes")

# Extension
st.write(f"🐛 DEBUG: Extension detected: '{file_extension}'")

# Détection TIF
st.write(f"🐛 DEBUG: Detected TIF/TIFF file")

# Appel load_geotiff
st.write(f"🐛 DEBUG: Calling load_geotiff()")

# Retour
st.write(f"🐛 DEBUG: load_geotiff() returned - image type: {type(image)}, metadata type: {type(geotiff_metadata)}")
st.write(f"🐛 DEBUG: Image from load_geotiff - size: {image.size}, mode: {image.mode}")

# Stockage
st.write(f"🐛 DEBUG: Stored geotiff_metadata in session_state")

# Resize
st.write(f"🐛 DEBUG: Before safe_resize - size: {image.size}")
st.write(f"🐛 DEBUG: After safe_resize - size: {image.size}")

# Flag
st.write(f"🐛 DEBUG: Set image_uploaded = True in session_state")
```

### 3. **Dans le stockage session_state** (5+ logs)

```python
# Stockage
st.write(f"🐛 DEBUG: Stored image in session_state['loaded_image'] - size: {image.size}")

# État
st.write(f"🐛 DEBUG: Current session_state keys: {list(st.session_state.keys())}")
st.write(f"🐛 DEBUG: image_uploaded: {st.session_state.get('image_uploaded')}")
st.write(f"🐛 DEBUG: loaded_image exists: {'loaded_image' in st.session_state}")

# Récupération
if 'loaded_image' in st.session_state:
    st.write(f"🐛 DEBUG: loaded_image size: {st.session_state.loaded_image.size}")
```

### 4. **Section de test d'affichage** (10+ logs)

```python
# Test Preview
st.write("### 🧪 Test: Loaded Image Preview")
st.write(f"Image type: {type(image)}")
st.write(f"Image size: {image.size}")
st.write(f"Image mode: {image.mode}")

# Conversion numpy
img_array = np.array(image)
st.write(f"Array shape: {img_array.shape}")
st.write(f"Array dtype: {img_array.dtype}")
st.write(f"Array min: {img_array.min()}, max: {img_array.max()}")

# Affichage
st.image(image, caption="Test Preview: Image before analysis", use_container_width=True)

# Statistiques par canal
st.write("### Channel Statistics")
# Red, Green, Blue channels avec min, max, mean
```

### 5. **Dans l'affichage de l'image** (3+ logs)

```python
# Entrée
st.write(f"🐛 DEBUG: Entering image display section - image_uploaded: {st.session_state.get('image_uploaded')}, image: {image is not None}")

# Avant affichage
st.write(f"🐛 DEBUG: About to display image - size: {image.size}, mode: {image.mode}")

# Après affichage
st.write(f"🐛 DEBUG: Image displayed successfully")
```

### 6. **Dans le bouton Analyser** (5+ logs)

```python
# Bouton visible
st.write(f"🐛 DEBUG: About to show Analyze button")

# Clic
st.write(f"🐛 DEBUG: Analyze button clicked!")

# Début traitement
st.write(f"🐛 DEBUG: Starting image processing")

# Résolution GeoTIFF
st.write(f"🐛 DEBUG: Using GeoTIFF resolution: {geotiff_res}")

# Appel process_image
st.write(f"🐛 DEBUG: Calling process_image() with image size: {image.size}")

# Fin traitement
st.write(f"🐛 DEBUG: process_image() completed successfully")

# Stockage résultats
st.write(f"🐛 DEBUG: Storing results in session_state")
st.write(f"🐛 DEBUG: analysis_done set to True")
```

### 7. **Dans la récupération session_state** (3+ logs)

```python
# Récupération
st.write(f"🐛 DEBUG: Retrieving image from session_state")
st.write(f"🐛 DEBUG: Retrieved image: {image is not None}, metadata: {geotiff_metadata is not None}")

# Image récupérée
if image is not None:
    st.write(f"🐛 DEBUG: Retrieved image size: {image.size}, mode: {image.mode}")
```

### 8. **Dans la gestion des erreurs** (2+ logs)

```python
# Erreur
st.write(f"🐛 DEBUG: ERROR in file loading: {str(e)}")
st.write(f"🐛 DEBUG: Full traceback: {traceback.format_exc()}")
```

## 🎯 Améliorations de la Normalisation

### 1. **Vérification des données vides**
```python
if rgb.max() == 0:
    st.warning("⚠️ All pixel values are 0. The image may be empty or corrupted.")
```

### 2. **Percentiles par canal**
```python
for i in range(3):
    channel = rgb[:, :, i]
    p2 = np.percentile(channel, 2)
    p98 = np.percentile(channel, 98)
    # Logs pour chaque canal
```

### 3. **Gestion du cas p98 <= p2**
```python
if p98 > p2:
    # Normalisation normale
else:
    # Simple min-max normalization
    if rgb.max() > 0:
        rgb = (rgb / rgb.max() * 255).astype(np.uint8)
```

### 4. **Détection automatique de la plage float**
```python
if rgb.max() > 1.0:
    # Assuming 0-255 range
else:
    # Values in 0-1 range, scaling to 0-255
```

## 📊 Total des Logs Ajoutés

- **load_geotiff()** : ~25 logs
- **Chargement fichier** : ~15 logs
- **session_state** : ~5 logs
- **Test Preview** : ~10 logs
- **Affichage image** : ~3 logs
- **Bouton Analyser** : ~5 logs
- **Récupération** : ~3 logs
- **Gestion erreurs** : ~2 logs

**Total : ~68 logs de debug**

## 🚀 Comment Tester

### 1. Lancer l'application
```bash
streamlit run app.py
```

### 2. Uploader un fichier TIF
- Uploadez votre fichier TIF/TIFF
- Observez les messages 🐛 DEBUG

### 3. Analyser les logs
Cherchez les messages dans l'ordre chronologique :

1. **Upload** → Extension → Détection TIF
2. **load_geotiff()** → Rasterio → Métadonnées → Bandes
3. **Normalisation** → Percentiles → Conversion
4. **PIL Image** → Test affichage
5. **session_state** → Stockage → Récupération
6. **Affichage** → Image visible
7. **Bouton Analyser** → Traitement → Résultats

### 4. Identifier le problème
Si l'image ne s'affiche pas, cherchez :
- `WARNING: All pixel values are 0!` → Données vides
- `WARNING: p98 <= p2` → Données uniformes
- `ERROR in load_geotiff` → Fichier corrompu
- `loaded_image exists: False` → Problème session_state

## 📝 Checklist de Debug

- [ ] Fichier uploadé correctement
- [ ] Extension détectée
- [ ] Rasterio ouvre le fichier
- [ ] Métadonnées extraites
- [ ] Bandes sélectionnées
- [ ] Données lues (min/max valides)
- [ ] Normalisation fonctionne
- [ ] PIL Image créée
- [ ] Image stockée dans session_state
- [ ] Image récupérée depuis session_state
- [ ] Image affichée
- [ ] Bouton Analyser visible
- [ ] Traitement fonctionne

## 📄 Documentation

- **`GEOTIFF_DEBUG_GUIDE.md`** : Guide complet d'utilisation des debugs
- **`GEOTIFF_DEBUG_SUMMARY.md`** : Ce fichier (résumé)

## 🎯 Prochaines Étapes

1. **Tester avec différents types de TIF** :
   - Sentinel-2 (13 bandes, uint16)
   - RGB standard (3 bandes, uint8)
   - Grayscale (1 bande)
   - Fichiers corrompus

2. **Analyser les logs** pour identifier le problème exact

3. **Corriger le problème** une fois identifié

4. **Retirer les debugs** une fois que tout fonctionne

---

**Version** : Debug v1.0  
**Date** : 14 septembre 2026  
**Statut** : 🐛 Prêt pour diagnostic  
**Logs ajoutés** : ~68  
**Améliorations normalisation** : 4
