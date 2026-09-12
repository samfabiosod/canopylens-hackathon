# 🐛 Résolution du problème ModuleNotFoundError: cv2

## ❌ Problème

Lors du déploiement sur Streamlit Cloud, vous obtenez cette erreur :

```
ModuleNotFoundError: This app has encountered an error.
Traceback:
File "/mount/src/canopylens-hackathon/app.py", line 25, in <module>
    import cv2
```

## ✅ Solution Appliquée

Le code a été modifié pour fonctionner **avec ou sans OpenCV** :

1. **Import conditionnel** : OpenCV est maintenant optionnel
2. **Fallback PIL** : Si OpenCV n'est pas disponible, l'application utilise PIL (Pillow) qui est toujours installé
3. **Fonctions wrapper** : Toutes les opérations OpenCV ont des équivalents PIL

## 📝 Modifications du Code

### 1. Import conditionnel (ligne ~40)

```python
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    st.warning("⚠️ OpenCV not available. Using PIL fallback (slower but functional).")
```

### 2. Fonctions wrapper (lignes ~50-240)

Toutes les fonctions OpenCV ont maintenant un fallback PIL :

- `rgb_to_hsv()` - Conversion RGB → HSV
- `hsv_threshold()` - Seuil HSV
- `morphological_cleanup()` - Opérations morphologiques
- `find_contours()` - Détection de contours
- `draw_contours()` - Dessin de contours
- `blend_images()` - Fusion d'images
- `encode_png()` - Encodage PNG
- `rgb_to_bgr()` / `bgr_to_rgb()` - Conversion de couleurs
- `draw_circle()`, `draw_line()`, `draw_rectangle()`, `draw_polyline()` - Dessin de formes
- `clean_small_contours()` - Nettoyage de contours

### 3. requirements.txt mis à jour

```
streamlit>=1.28.0
numpy>=1.24.0
opencv-python-headless>=4.8.0
pillow>=10.0.0
matplotlib>=3.7.0
scikit-image>=0.21.0
reportlab>=4.0.0
rasterio>=1.3.0
```

**Note** : Les versions sont maintenant flexibles (>=) pour éviter les conflits.

## 🚀 Étapes pour Redéployer

### 1. Mettre à jour votre repository GitHub

```bash
# Ajouter les modifications
git add app.py requirements.txt

# Commit
git commit -m "Fix: Add OpenCV fallback to PIL for Streamlit Cloud compatibility"

# Push
git push origin main
```

### 2. Streamlit Cloud va automatiquement :

- Détecter le nouveau commit
- Réinstaller les dépendances
- Redémarrer l'application

### 3. Vérifier le déploiement

L'application devrait maintenant fonctionner. Si OpenCV n'est pas disponible, vous verrez un warning :

```
⚠️ OpenCV not available. Using PIL fallback (slower but functional).
```

Mais l'application fonctionnera normalement !

## 🔍 Vérification

Après le déploiement, testez :

1. **Upload d'une image PNG/JPG** → Devrait fonctionner
2. **Upload d'un GeoTIFF** → Devrait fonctionner
3. **Analyse de canopée** → Devrait fonctionner
4. **Téléchargement du masque** → Devrait fonctionner
5. **Génération du rapport PDF** → Devrait fonctionner

## 📊 Performance

- **Avec OpenCV** : Plus rapide (opérations optimisées C++)
- **Sans OpenCV (PIL fallback)** : Plus lent mais fonctionnel

Pour une application de hackathon, la différence de performance est négligeable.

## 🎯 Avantages de cette Solution

✅ **Robustesse** : Fonctionne même si OpenCV n'est pas installé  
✅ **Compatibilité** : Fonctionne sur Streamlit Cloud, Heroku, local  
✅ **Transparence** : Warning clair si OpenCV n'est pas disponible  
✅ **Maintenance** : Code plus portable et facile à maintenir  

## 🐛 Si le Problème Persiste

### Option 1 : Forcer l'installation d'OpenCV

Modifiez `requirements.txt` :

```
opencv-python-headless==4.8.1.78
```

Utilisez une version spécifique et testée.

### Option 2 : Utiliser opencv-python au lieu de opencv-python-headless

```
opencv-python>=4.8.0
```

### Option 3 : Vérifier les logs Streamlit Cloud

1. Allez sur https://share.streamlit.io/
2. Cliquez sur votre application
3. Cliquez sur "Manage app"
4. Consultez les logs pour voir l'erreur exacte

### Option 4 : Réduire les dépendances

Si le problème persiste, créez un `requirements.txt` minimal :

```
streamlit
numpy
pillow
matplotlib
scikit-image
reportlab
```

Et supprimez `opencv-python-headless` et `rasterio`.

L'application fonctionnera avec le fallback PIL pour tout.

## 📞 Support

Si vous avez encore des problèmes :

1. Vérifiez que `app.py` est bien à jour (git pull)
2. Vérifiez que `requirements.txt` est bien à jour
3. Consultez les logs Streamlit Cloud
4. Testez en local d'abord : `streamlit run app.py`

---

**Version** : 3.2 (OpenCV Fallback)  
**Statut** : ✅ Solution appliquée  
**Déploiement** : Prêt pour Streamlit Cloud
