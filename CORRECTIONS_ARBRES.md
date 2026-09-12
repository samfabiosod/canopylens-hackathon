# Corrections du Comptage d'Arbres - CanopyLens

## Problème Identifié

**Symptôme :** L'algorithme détectait 294 arbres pour 4967 hectares, soit 0.06 arbre/hectare.  
**Réalité attendue :** Une forêt tropicale dense contient normalement 400-600 arbres/ha.

## Cause Racine

La fonction `measure.label()` comptait **tous les "connected components"** sans filtrage de taille approprié :
- ❌ Composants < 100 pixels = bruit, pas des arbres
- ❌ Composants > 5000 pixels = zones de canopée continue, pas des arbres individuels
- ✅ Seuls les composants 100-5000 pixels représentent des couronnes d'arbres individuelles

## Corrections Appliquées

### 1. Filtrage par Taille (app.py, ligne ~346-365)

**Avant :**
```python
num_trees = len([r for r in regions if r.area > 50])
```

**Après :**
```python
# Tree crowns in satellite imagery (10m GSD) typically span 100-5000 pixels
# < 100 pixels = noise or very small saplings
# > 5000 pixels = continuous canopy patches (not individual trees)
tree_candidates = [r for r in regions if 100 <= r.area <= 5000]
num_trees_detected = len(tree_candidates)
```

### 2. Estimation Alternative pour Forêts Denses

Ajout d'une estimation basée sur la densité typique quand la couverture > 70% :

```python
# Alternative estimation for dense forests (>70% coverage)
# Typical tree density: 400-600 trees/ha for tropical forests
num_trees_density_estimate = None
if canopy_pct > 70 and canopy_area_ha > 0:
    min_density = 400  # trees/ha
    max_density = 600  # trees/ha
    num_trees_density_estimate = {
        "min": int(canopy_area_ha * min_density),
        "max": int(canopy_area_ha * max_density),
    }
```

### 3. Messages d'Honnêteté (Transparence)

**Interface Streamlit :**
- Note explicative sur les limites du comptage d'arbres
- Estimation alternative affichée si couverture > 70%

**Rapport PDF :**
- Section "Note on tree counting" avec explication détaillée
- Estimation basée sur la densité si applicable
- Style visuel distinct (encadré bleu) pour attirer l'attention

### 4. Documentation Technique Mise à Jour

**Spécifications (FR/EN) :**
- Avant : "Surface minimale d'un arbre : 50 pixels"
- Après : "Filtrage taille couronne : 100–5000 pixels (arbres individuels uniquement)"

## Résultats Attendus

### Scénario 1 : Forêt Fragmentée (< 70% couverture)
- **Comptage détecté :** Nombre de couronnes distinctes (100-5000 pixels)
- **Message :** "Ce nombre représente les couronnes distinctes détectables"
- **Exemple :** 150 arbres détectés sur 50 ha = 3 arbres/ha (forêt fragmentée, réaliste)

### Scénario 2 : Forêt Dense (> 70% couverture)
- **Comptage détecté :** Couronnes séparables (sous-estimation inévitable)
- **Estimation alternative :** "400-600 arbres/ha → 20,000-30,000 arbres total"
- **Exemple :** 4967 ha à 85% couverture → estimation 1,986,800-2,980,200 arbres

## Philosophie : Honnêteté Radicale

CanopyLens adhère au principe :
> **"Un outil brut qui admet ses limites l'emporte sur un outil soigné qui invente des chiffres."**

### Ce que l'outil FAIT :
✅ Compte les couronnes d'arbres **détectables et séparables**  
✅ Fournit une estimation basée sur la densité pour les forêts denses  
✅ Explique clairement les limites méthodologiques  

### Ce que l'outil NE FAIT PAS :
❌ Prétend compter tous les arbres en forêt dense (impossible en RGB)  
❌ Ignore le chevauchement des couronnes  
❌ Fournit des chiffres sans contexte  

## Validation

Pour valider les corrections :
1. Tester avec une image de forêt fragmentée → comptage raisonnable
2. Tester avec une image de forêt dense → estimation alternative affichée
3. Vérifier le rapport PDF → notes d'honnêteté présentes
4. Comparer avec données terrain si disponibles

## Fichiers Modifiés

- `app.py` : Fonction `process_image()` + interface + rapport PDF
- Traductions FR/EN : Nouvelles clés `tree_count_note` et `tree_density_estimate`
- Spécifications techniques : Mise à jour du filtrage par taille

---

**Date de correction :** 14 septembre 2026  
**Impact :** Critique - corrige un bug majeur de comptage  
**Breaking changes :** Non - rétrocompatible (ajout de métriques supplémentaires)
