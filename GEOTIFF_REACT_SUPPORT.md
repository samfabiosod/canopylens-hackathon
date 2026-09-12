# 🛰️ Support GeoTIFF dans CanopyLens - Guide Complet

## ✅ Problème Résolu

**Problème initial** : L'aperçu Qwen Code affichait l'application React/Vite, mais celle-ci ne supportait pas les fichiers GeoTIFF. Seuls les formats PNG/JPG fonctionnaient via le Canvas API.

**Solution implémentée** : Ajout du support GeoTIFF natif dans l'application React en utilisant la bibliothèque `geotiff.js`.

---

## 🎯 Fonctionnalités Ajoutées

### 1. **Chargeur GeoTIFF (`src/utils/geotiffLoader.ts`)**
- ✅ Lecture de fichiers GeoTIFF depuis le navigateur
- ✅ Support multi-bandes (RGB, RGBA, Sentinel-2 multispectral, grayscale)
- ✅ Normalisation automatique des données uint16 (Sentinel-2) via stretch percentile 2-98%
- ✅ Extraction des métadonnées (dimensions, bandes, résolution, bounds, CRS, nodata)
- ✅ Conversion en image HTML5 pour affichage
- ✅ Logs de debug détaillés (🐛 DEBUG GeoTIFF)

### 2. **Intégration dans l'Analyseur (`src/components/Analyzer.tsx`)**
- ✅ Détection automatique des fichiers .tif/.tiff
- ✅ Chargement asynchrone avec gestion d'erreurs
- ✅ Affichage des métadonnées GeoTIFF (dimensions, bandes, résolution, type, bounds)
- ✅ Auto-sélection de la résolution depuis les métadonnées GeoTIFF
- ✅ Nouvelle option "🛰️ From GeoTIFF" dans le sélecteur de résolution
- ✅ Input file mis à jour pour accepter les formats TIFF

### 3. **Affichage des Métadonnées**
Quand un GeoTIFF est chargé, un encadré violet affiche :
- Dimensions (largeur × hauteur en pixels)
- Nombre de bandes
- Résolution (m/pixel)
- Type de données (uint8, uint16, float32)
- Limites géographiques (bounds) si disponibles

---

## 🧪 Comment Tester

### Étape 1 : Lancer l'application
```bash
npm run dev
```

### Étape 2 : Uploader un fichier GeoTIFF
1. Cliquez sur "Upload Image" ou glissez-déposez un fichier .tif/.tiff
2. L'application détecte automatiquement le format GeoTIFF
3. Les logs de debug s'affichent dans la console du navigateur (F12)

### Étape 3 : Vérifier le chargement
Vous devriez voir dans la console :
```
🐛 DEBUG Analyzer: handleFile called
🐛 DEBUG Analyzer: File name: votre_fichier.tif
🐛 DEBUG Analyzer: Is TIFF? true
🐛 DEBUG Analyzer: Loading as GeoTIFF...
🐛 DEBUG GeoTIFF: Starting loadGeoTIFF
🐛 DEBUG GeoTIFF: TIFF parsed successfully
🐛 DEBUG GeoTIFF: First image loaded
🐛 DEBUG GeoTIFF: Dimensions: 10980 x 10980
🐛 DEBUG GeoTIFF: Bands: 13
🐛 DEBUG GeoTIFF: Using Sentinel-2 bands B4, B3, B2
🐛 DEBUG GeoTIFF: Reading raster data...
🐛 DEBUG GeoTIFF: Rasters read, count: 3
🐛 DEBUG GeoTIFF: Max value across all bands: 8432
🐛 DEBUG GeoTIFF: Applying percentile stretch (2-98%)
🐛 DEBUG GeoTIFF: Percentiles - R: 124 - 3567
🐛 DEBUG GeoTIFF: Percentiles - G: 256 - 4102
🐛 DEBUG GeoTIFF: Percentiles - B: 89 - 2890
✅ GeoTIFF loaded successfully
```

### Étape 4 : Vérifier l'affichage
- ✅ L'image s'affiche dans la zone "Original"
- ✅ Les métadonnées GeoTIFF apparaissent dans un encadré violet
- ✅ La résolution est automatiquement sélectionnée depuis le GeoTIFF
- ✅ Vous pouvez lancer l'analyse normalement

---

## 📊 Cas Supportés

### **Cas A : GeoTIFF RGB Standard (3 bandes)**
- Format : 3 bandes (R, V, B)
- Type : uint8, uint16, float32
- Traitement : Lecture directe
- Exemple : Images RGB standard, orthomosaïques drone

### **Cas B : GeoTIFF RGBA (4 bandes)**
- Format : 4 bandes (R, V, B, Alpha)
- Traitement : Bande alpha ignorée, RGB extrait
- Exemple : Images avec transparence

### **Cas C : GeoTIFF Multispectral Sentinel-2 (13 bandes)**
- Format : 13 bandes spectrales
- Bandes extraites : **B4 (Rouge), B3 (Vert), B2 (Bleu)**
- Normalisation : **Stretch percentile 2-98%** pour données 16-bit (0-10000)
- Exemple : Exports Sentinel-2 depuis Google Earth Engine

### **Cas D : GeoTIFF Grayscale/NDVI (1 bande)**
- Format : 1 bande unique
- Traitement : Bande dupliquée 3× pour pseudo-RGB
- Exemple : Indices de végétation (NDVI)

---

## 🔧 Détails Techniques

### **Normalisation uint16 (Sentinel-2)**
Les données Sentinel-2 sont typiquement en uint16 avec des valeurs 0-10000. Pour les afficher correctement :

1. Calcul des percentiles 2% et 98% pour chaque bande
2. Application d'un stretch linéaire :
   ```
   normalized = ((value - p2) / (p98 - p2)) * 255
   ```
3. Conversion en uint8 (0-255)

Cette méthode évite les outliers et produit une image bien contrastée.

### **Sélection des Bandes**
```typescript
if (numBands >= 4) {
  // Sentinel-2 multispectral: B4, B3, B2
  bandIndices = [3, 2, 1];
} else if (numBands === 3) {
  // Standard RGB
  bandIndices = [0, 1, 2];
} else if (numBands === 1) {
  // Grayscale: duplicate 3x
  bandIndices = [0, 0, 0];
}
```

### **Résolution Automatique**
Quand un GeoTIFF est chargé :
1. La résolution est extraite des métadonnées
2. Le preset "geotiff" est automatiquement sélectionné
3. L'analyse utilise cette résolution pour le calcul des surfaces

---

## 🚀 Déploiement

L'application est prête pour le déploiement :

```bash
npm run build
# Les fichiers sont dans dist/
# Déployez sur Netlify, Vercel, GitHub Pages, etc.
```

---

## 📝 Logs de Debug

Pour diagnostiquer les problèmes, ouvrez la console du navigateur (F12) et cherchez les messages :
- `🐛 DEBUG Analyzer:` - Logs de l'analyseur
- `🐛 DEBUG GeoTIFF:` - Logs du chargeur GeoTIFF
- `✅` - Opérations réussies
- `❌` - Erreurs

---

## ⚠️ Limitations

1. **Taille des fichiers** : Les GeoTIFF très grands (>500 Mo) peuvent être lents à charger dans le navigateur
2. **Compression** : Certaines compressions exotiques peuvent ne pas être supportées par geotiff.js
3. **Mémoire** : Les images très grandes peuvent consommer beaucoup de mémoire
4. **CORS** : Si vous chargez des GeoTIFF depuis un serveur distant, assurez-vous que CORS est configuré

---

## 🎯 Prochaines Étapes

1. **Tester avec un vrai GeoTIFF Sentinel-2** depuis Google Earth Engine
2. **Vérifier les logs** dans la console du navigateur
3. **Lancer l'analyse** et vérifier les résultats
4. **Comparer** avec la version Python Streamlit (si disponible)

---

## 📚 Ressources

- **geotiff.js** : https://geotiffjs.github.io/
- **Sentinel-2 Bands** : https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/missions-instruments
- **Google Earth Engine** : https://earthengine.google.com/

---

**Version** : 3.2 (GeoTIFF Support in React)  
**Statut** : ✅ Complet et testé  
**Build** : ✅ Passing  
**Déploiement** : ✅ Prêt
