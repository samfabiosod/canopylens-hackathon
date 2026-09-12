# 🌿 CanopyLens — Pitch Document
### *Seeing forests more clearly, one satellite image at a time*

**Flora Carbon AI Hackathon — Kolkata, September 2026**  
**Built in 48 hours · Zero budget · 100% free & open**

---

## 🇫🇷 Version Française

### 🌍 Le Problème

La comptabilité du carbone forestier est essentielle pour l'action climatique. Les forêts tropicales de la région de Kolkata — Sundarbans, mangroves du Bengale, forêts humides — stockent des centaines de millions de tonnes de CO₂. Pourtant, mesurer ce stock reste difficile :

- **Les méthodes traditionnelles** (inventaires terrain, LiDAR aérien) sont **coûteuses** (plusieurs milliers d'euros par hectare) et **lentes** (semaines de travail).
- **Les outils logiciels existants** (QGIS + plugins, Google Earth Engine) demandent une **expertise technique** que n'ont pas les ONG locales, les petits agriculteurs ou les décideurs municipaux.
- **Les APIs cloud** (AWS, GCP) imposent des coûts récurrents et une dépendance à Internet — inacceptable pour beaucoup de terrains en Inde rurale.

**Résultat** : des millions d'hectares de forêts ne sont jamais comptabilisés dans les bilans carbone, simplement parce que l'outil pour les estimer est hors de portée.

### 💡 Notre Solution : CanopyLens

CanopyLens est un **outil web minimaliste** qui estime la couverture de canopée et le stock de carbone à partir de n'importe quelle image satellite RGB.

**Fonctionnement en 3 clics :**
1. L'utilisateur télécharge une image (Sentinel-2, drone, photo aérienne…)
2. Il clique sur "Analyser"
3. Il obtient instantanément : surface de canopée (ha), stock de carbone (tCO₂), nombre d'arbres estimés, masque visuel, et rapport PDF téléchargeable.

**Caractéristiques clés :**
- ✅ **100% gratuit** — aucune clé API, aucun compte cloud, aucun abonnement
- ✅ **Fonctionne hors-ligne** — tout le traitement est côté client (navigateur) ou local (Streamlit)
- ✅ **Bilingue** — interface complète en anglais et français
- ✅ **Adaptatif** — détection automatique de la résolution, comptage adapté
- ✅ **Transparent** — affiche ses limites clairement, ne prétend pas à une précision qu'il n'a pas
- ✅ **Reproductible** — code open-source, hypothèses documentées

### 🔬 Approche Technique

Le pipeline est volontairement simple et explicable :

```
Image RGB → Conversion HSV → Seuil vert (H:30-80°, S≥40, V≥40)
         → Nettoyage morphologique (close + open, kernel 5×5)
         → Estimation de résolution (taille médiane des couronnes)
         → Comptage adaptatif :
             • Haute rés. (<2m) : détection directe d'arbres individuels
             • Rés. moyenne (2-5m) : détection ajustée + correction
             • Basse rés. (>5m) : estimation par densité (IPCC/FAO)
         → Calcul surface (ha) → carbone (tCO₂)
```

**Logique adaptative de comptage d'arbres :**

| Résolution | Méthode | Précision |
|-----------|---------|-----------|
| < 2 m/px | Comptage direct (composantes connexes) | Haute — couronnes séparables |
| 2–5 m/px | Détection ajustée + facteur de correction | Moyenne — certains arbres manqués |
| > 5 m/px | Estimation par densité (IPCC/FAO) | Ordre de grandeur seulement |

**Facteurs de carbone (IPCC AR6 WGIII) :**
- Forêt tropicale humide : 150 tCO₂/ha *(défaut, région Kolkata)*
- Forêt tropicale sèche : 80 tCO₂/ha
- Mangrove : 200 tCO₂/ha
- Forêt tempérée : 120 tCO₂/ha

**Stack technique (100% gratuit) :**
- Python 3.10 + Streamlit (interface web)
- OpenCV + scikit-image (traitement d'image)
- ReportLab (génération PDF)
- Déploiement : Streamlit Cloud (gratuit) ou local

### ⚠️ Limites et Honnêteté

**Ce que CanopyLens FAIT :**
- Donne une estimation rapide et gratuite de la couverture forestière
- Identifie visuellement les zones de canopée sur une image
- Fournit un ordre de grandeur du stock de carbone
- S'adapte automatiquement à la résolution de l'image source

**Ce que CanopyLens NE FAIT PAS :**
- ❌ Ne remplace pas une validation terrain ou LiDAR
- ❌ Ne distingue pas les essences d'arbres ou la santé de la végétation (nécessite bande NIR)
- ❌ Ne gère pas la couverture nuageuse (sous-estimation possible)
- ❌ N'est PAS certifié pour les crédits carbone (Verra, Gold Standard)
- ❌ Suppose une forêt homogène — les paysages mixtes réduisent la précision
- ❌ La détection d'arbres individuels nécessite une résolution <2m. Sentinel-2 (10m) est trop grossier pour cette tâche.
- ❌ Pour le comptage individuel, utilisez des images drone/aériennes (<1m de résolution) avec des outils comme DeepForest.
- ❌ Les estimations par densité suivent les normes GIEC/FAO lorsque des données haute résolution ne sont pas disponibles.

**Notre engagement :** Nous préférons un outil brut qui admet ses limites à un outil soigné qui invente des chiffres. Chaque estimation est accompagnée d'un disclaimer clair.

### ✅ Pourquoi Ça Marche

1. **Utilisable par tous** — upload → clic → résultat. Pas de formation requise.
2. **Reproductible** — tout le code est ouvert, toutes les hypothèses sont documentées.
3. **Honnête** — nous montrons l'incertitude, pas une fausse précision.
4. **Adaptatif** — la méthode de comptage s'adapte à la résolution disponible.
5. **Gratuit** — zéro infrastructure, zéro coût récurrent.
6. **Éducatif** — démontre les concepts de base de la télédétection pour le carbone.
7. **Déployable en 5 minutes** — `pip install -r requirements.txt && streamlit run app.py`

**Pour le jury :** CanopyLens prouve qu'une personne seule, avec zéro budget et 48 heures, peut livrer un outil fonctionnel qui répond à un vrai besoin. Ce n'est pas un SOTA académique — c'est un outil pratique, honnête, et déployable dès maintenant.

---

## 🇬🇧 English Version

### 🌍 The Problem

Forest carbon accounting is critical for climate action. The tropical forests around Kolkata — the Sundarbans, Bengal mangroves, moist forests — store hundreds of millions of tonnes of CO₂. Yet measuring this stock remains difficult:

- **Traditional methods** (field inventories, airborne LiDAR) are **expensive** (thousands of euros per hectare) and **slow** (weeks of work).
- **Existing software tools** (QGIS + plugins, Google Earth Engine) require **technical expertise** that local NGOs, small farmers, and municipal decision-makers don't have.
- **Cloud APIs** (AWS, GCP) impose recurring costs and Internet dependency — unacceptable for many rural Indian field sites.

**Result:** Millions of hectares of forest go uncounted in carbon inventories, simply because the tool to estimate them is out of reach.

### 💡 Our Solution: CanopyLens

CanopyLens is a **minimalist web tool** that estimates canopy cover and carbon stock from any RGB satellite image.

**3-click workflow:**
1. User uploads an image (Sentinel-2, drone, aerial photo…)
2. Clicks "Analyze"
3. Instantly gets: canopy area (ha), carbon stock (tCO₂), estimated tree count, visual mask, and downloadable PDF report.

**Key features:**
- ✅ **100% free** — no API keys, no cloud accounts, no subscriptions
- ✅ **Works offline** — all processing is client-side (browser) or local (Streamlit)
- ✅ **Bilingual** — full English and French interface
- ✅ **Adaptive** — automatic resolution detection, adapted counting
- ✅ **Transparent** — clearly states its limitations, doesn't claim precision it doesn't have
- ✅ **Reproducible** — open-source code, documented assumptions

### 🔬 Technical Approach

The pipeline is deliberately simple and explainable:

```
RGB Image → HSV Conversion → Green Threshold (H:30-80°, S≥40, V≥40)
          → Morphological Cleanup (close + open, 5×5 kernel)
          → Resolution Estimation (median crown size)
          → Adaptive Counting:
              • High-res (<2m): direct individual tree detection
              • Medium-res (2-5m): adjusted detection + correction
              • Low-res (>5m): density-based estimation (IPCC/FAO)
          → Calculate area (ha) → carbon (tCO₂)
```

**Adaptive Tree Counting Logic:**

| Resolution | Method | Accuracy |
|-----------|--------|----------|
| < 2 m/px | Direct counting (connected components) | High — crowns are separable |
| 2–5 m/px | Adjusted detection + correction factor | Medium — some trees missed |
| > 5 m/px | Density-based estimation (IPCC/FAO) | Order of magnitude only |

**Carbon factors (IPCC AR6 WGIII):**
- Tropical moist forest: 150 tCO₂/ha *(default, Kolkata region)*
- Tropical dry forest: 80 tCO₂/ha
- Mangrove: 200 tCO₂/ha
- Temperate forest: 120 tCO₂/ha

**Tech stack (100% free):**
- Python 3.10 + Streamlit (web interface)
- OpenCV + scikit-image (image processing)
- ReportLab (PDF generation)
- Deployment: Streamlit Cloud (free) or local

### ⚠️ Limitations & Honesty

**What CanopyLens DOES:**
- Gives a fast, free estimate of forest cover
- Visually identifies canopy areas on an image
- Provides an order-of-magnitude carbon stock estimate
- Automatically adapts to source image resolution

**What CanopyLens DOES NOT:**
- ❌ Replace field validation or LiDAR
- ❌ Distinguish tree species or vegetation health (needs NIR band)
- ❌ Handle cloud cover (may underestimate)
- ❌ Be certified for carbon credits (Verra, Gold Standard)
- ❌ Assume homogeneous forest — mixed landscapes reduce accuracy
- ❌ Individual tree detection requires <2m resolution. Sentinel-2 (10m) is too coarse for this task.
- ❌ For individual counting, use drone/aerial imagery (<1m resolution) with tools like DeepForest.
- ❌ Density-based estimates follow IPCC/FAO standards when high-resolution data is unavailable.

**Our commitment:** We prefer a rough tool that admits its limits over a polished tool that invents figures. Every estimate comes with a clear disclaimer.

### ✅ Why It Works

1. **Usable by anyone** — upload → click → result. No training required.
2. **Reproducible** — all code is open, all assumptions are documented.
3. **Honest** — we show uncertainty, not false precision.
4. **Adaptive** — counting method adapts to available resolution.
5. **Free** — zero infrastructure, zero recurring cost.
6. **Educational** — demonstrates core remote sensing concepts for carbon.
7. **Deployable in 5 minutes** — `pip install -r requirements.txt && streamlit run app.py`

**For the jury:** CanopyLens proves that one person, with zero budget and 48 hours, can deliver a functional tool that addresses a real need. This isn't academic SOTA — it's a practical, honest, immediately deployable tool.

---

## 📦 Deliverables Checklist

- [x] `app.py` — Complete Streamlit application (bilingual, PDF export, adaptive counting)
- [x] `requirements.txt` — All dependencies listed
- [x] `pitch.md` — This document (FR + EN)
- [x] Live demo — Deployable on Streamlit Cloud in < 5 minutes
- [x] Zero cost — No paid APIs, no cloud credits, no subscriptions

## 🚀 Deployment (5 minutes)

```bash
# Local
pip install -r requirements.txt
streamlit run app.py

# Streamlit Cloud
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect repo → select app.py → Deploy
4. Share URL — done!
```

---

**Built with honesty, shipped with courage.** 🌱  
*Kolkata, September 2026 — Flora Carbon AI Hackathon*
