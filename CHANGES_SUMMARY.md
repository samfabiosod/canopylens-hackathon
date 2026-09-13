# 📝 Résumé des changements - CanopyLens v9.0

## Changements appliqués

### 1. Suppression d'OpenCV (cv2)
- **Supprimé** : `import cv2`
- **Ajouté** : Imports scikit-image et scipy
  - `from skimage import measure, filters, morphology`
  - `from skimage.segmentation import find_boundaries, watershed`
  - `from skimage.feature import peak_local_max`
  - `from scipy import ndimage as ndi`

### 2. Réécriture des fonctions de segmentation

#### `segment_canopy_exg()`
- **Avant** : Utilisait `cv2.threshold()`
- **Après** : Utilise numpy `(exg > threshold).astype(np.uint8) * 255`

#### `segment_canopy_hsv()`
- **Avant** : Utilisait `cv2.cvtColor()` et `cv2.inRange()`
- **Après** : Utilise PIL pour conversion HSV + numpy pour seuillage

#### `count_trees_connected_components()`
- **Avant** : Utilisait `cv2.connectedComponentsWithStats()`
- **Après** : Utilise `skimage.measure.label()` et `skimage.measure.regionprops()`

#### `create_visualization_overlay()`
- **Avant** : Utilisait `cv2.addWeighted()`
- **Après** : Utilise numpy `(image_rgb * (1 - alpha) + mask_colored * alpha).astype(np.uint8)`

### 3. Ajout de nouvelles fonctions pour le comptage d'arbres

#### `detect_tree_crowns_watershed()`
- **Nouvelle fonction** : Détecte les houppiers individuels avec watershed
- Utilise `scipy.ndimage.distance_transform_edt()` pour calculer la distance
- Utilise `skimage.feature.peak_local_max()` pour trouver les maxima locaux
- Utilise `skimage.segmentation.watershed()` pour séparer les houppiers
- La distance minimale entre pics vient de la densité d'arbres par biome

#### `adaptive_tree_count()`
- **Nouvelle fonction** : Comptage adaptatif selon résolution et couverture
- Pour résolution ≤ 5m : utilise watershed pour séparer les houppiers
- Pour résolution > 5m : utilise estimation par densité (IPCC/FAO)
- Gère le cas de canopée fermée (>75% couverture) avec message d'honnêteté
- Retourne un dictionnaire avec : method, count, count_range, note_key, crown_labels

### 4. Ajout du dictionnaire de référence

#### `TREE_DENSITY_REFERENCE`
- Dictionnaire des densités d'arbres par biome (IPCC/FAO)
- Exemples :
  - "Tropical Moist Forest": (400, 600) arbres/ha
  - "Temperate Forest": (300, 500) arbres/ha
  - "Mangrove Forest": (600, 1000) arbres/ha

### 5. Modification de l'appel dans `main()`

#### Avant :
```python
num_trees, labeled_mask = count_trees_connected_components(mask, min_area=min_tree_area)
metrics = calculate_canopy_metrics(mask, resolution_m_per_pixel, carbon_factor)
```

#### Après :
```python
metrics = calculate_canopy_metrics(mask, resolution_m_per_pixel, carbon_factor)
biome_name = "Tropical Moist Forest"
tree_result = adaptive_tree_count(
    mask, 
    resolution_m_per_pixel, 
    metrics['canopy_area_ha'], 
    metrics['canopy_coverage_pct'], 
    biome_name
)
num_trees = tree_result['count'] if tree_result['count'] is not None else 0
```

## Corrections de bugs

### Bug 1 : Comptage d'arbres incorrect
- **Problème** : `count_trees_connected_components` comptait les composantes connexes, mais en cas de canopée fermée (>60-70% de couverture), les houppiers fusionnaient en un seul gros blob
- **Solution** : Utilisation de watershed pour séparer les houppiers individuels avant le comptage

### Bug 2 : Contradiction entre détection de type d'image et estimation de résolution
- **Problème** : `detect_image_type()` pouvait classer l'image comme 'sentinel2' (10m/px), mais `estimate_resolution_from_components()` calculait une résolution différente (0.42m/px)
- **Solution** : Suppression de `estimate_resolution_from_components()` et utilisation directe de la résolution sélectionnée par l'utilisateur

## Améliorations

### 1. Comptage plus précis
- Watershed sépare les houppiers qui se chevauchent
- Filtrage par surface minimale et maximale selon la résolution
- Estimation adaptative selon le type de résolution

### 2. Transparence améliorée
- Messages d'honnêteté pour canopée fermée (>75% couverture)
- Distinction entre méthodes : direct, adjusted, density
- Plage de confiance (count_range) pour les estimations

### 3. Compatibilité
- Suppression de la dépendance OpenCV
- Utilisation exclusive de scikit-image et scipy (déjà dans le stack imposé)
- Code plus portable et maintenable

## Fichiers modifiés

- `app.py` : Réécriture complète pour supprimer OpenCV et ajouter watershed
- `requirements.txt` : Non modifié (les dépendances scikit-image et scipy sont déjà présentes)

## Validation

Le code devrait maintenant :
1. ✅ Compiler sans erreur (`python -m py_compile app.py`)
2. ✅ Compter les arbres correctement même en canopée fermée
3. ✅ Utiliser la résolution sélectionnée par l'utilisateur
4. ✅ Afficher des messages d'honnêteté appropriés
5. ✅ Fonctionner sans OpenCV

## Notes techniques

- `tree_result["crown_labels"]` n'est pas ajouté au dict `metrics` (trop volumineux)
- `carbon_stock_tco2` ne dépend que de `canopy_area_ha`, pas du comptage d'arbres
- Le style et les commentaires existants sont conservés
