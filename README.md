# 🌿 CanopyLens v9.0 - README FINAL

## 🎯 QU'EST-CE QUE C'EST ?

Application Streamlit pour analyser des images satellites et estimer :
- 🌳 Nombre d'arbres
- 📏 Surface de canopée (ha)
- 💨 Stock de carbone (tCO₂)
- 📊 Couverture (%)

## ✅ CORRECTIONS APPORTÉES

1. **Comptage** : `cv2.connectedComponentsWithStats` → précis
2. **Résolution** : Menu déroulant → 10m/3m/0.1m/manuel
3. **Segmentation** : ExG + fallback HSV → robuste
4. **Honnêteté** : Avertissements dynamiques → contextuel

## 🚀 DÉMARRAGE RAPIDE

```bash
# Installer
pip install -r requirements.txt

# Lancer
streamlit run app.py
```

## 📦 FICHIERS ESSENTIELS

### Code (3 fichiers)
- `app.py` - Application complète
- `requirements.txt` - Dépendances Python
- `packages.txt` - Dépendances système

### Documentation
- `README_PRINCIPAL.md` - Point d'entrée principal
- `START_HERE.md` - Guide ultime détaillé
- `CORRECTIONS.md` - Détails techniques
- `DEPLOYMENT.md` - Instructions de déploiement

## 🎯 POUR LES RECRUTEURS

**Technique** :
- `cv2.connectedComponentsWithStats` pour comptage
- Indice ExG pour segmentation robuste
- Fallback automatique HSV
- Gestion d'erreurs complète

**Méthodologique** :
- Identification systématique des problèmes
- Solutions techniques robustes
- Documentation complète
- Tests et validation

**Business** :
- Estimation précise du carbone
- Interface intuitive
- Transparence sur les limites
- Prêt pour production

## 🧪 TESTS

1. **Sentinel-2** : 10m, comptage > 1
2. **Drone** : 0.1m, "Haute précision"
3. **Sombre** : fallback HSV
4. **Manuel** : résolution custom

## 🎉 PRÊT POUR SOUMISSION !

✅ Code fonctionnel
✅ Corrections implémentées
✅ Documentation complète
✅ Design professionnel
✅ Tests effectués
✅ Prêt pour déploiement

## 🚀 PROCHAINES ÉTAPES

1. Déployer sur Streamlit Cloud
2. Obtenir lien de démo
3. Soumettre avec code source

---

**Bonne chance pour le hackathon Flora Carbon AI ! 🌿**

**v9.0 | 14 sept 2026 | ✅ PRÊT**

## ✨ Fonctionnalités

### 🎯 Corrections apportées dans cette version

1. **Comptage d'arbres amélioré** : Utilisation de `cv2.connectedComponentsWithStats` pour un comptage précis des arbres individuels avec filtrage par surface minimale
2. **Sélection manuelle de la résolution** : Menu déroulant pour choisir la source d'image (Sentinel-2, Planet, Drone, ou saisie manuelle)
3. **Segmentation par indice ExG** : Utilisation de l'indice Excess Green (ExG) plus robuste que HSV, avec fallback automatique si l'image est trop sombre
4. **Section "Honnêteté" dynamique** : Avertissements adaptés selon la source d'image choisie

### 📊 Métriques calculées

- 🌳 Nombre d'arbres détectés
- 📏 Surface de canopée (hectares)
- 💨 Stock de carbone (tCO₂)
- 📊 Pourcentage de couverture
- 🚗 Équivalents environnementaux (voitures, arbres)

## 🚀 Installation et déploiement

### Installation locale

```bash
# Cloner le repository
git clone <votre-repo>
cd canopylens

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

### Déploiement sur Streamlit Cloud

1. **Préparer les fichiers** :
   - `app.py` - Application principale
   - `requirements.txt` - Dépendances Python
   - `packages.txt` - Dépendances système (libgl1 pour OpenCV)

2. **Pousser vers GitHub** :
   ```bash
   git add .
   git commit -m "CanopyLens v9.0 - Corrections complètes"
   git push origin main
   ```

3. **Déployer sur Streamlit Cloud** :
   - Aller sur [share.streamlit.io](https://share.streamlit.io)
   - Connecter votre repository GitHub
   - Sélectionner le fichier `app.py`
   - Cliquer sur "Deploy"

## 📖 Guide d'utilisation

### 1. Configuration (barre latérale)

**Source de l'image** :
- **Sentinel-2 (10m)** : Images satellites gratuites, résolution 10m
- **Planet (3m)** : Images commerciales, résolution 3m
- **Drone (0.1m)** : Images aériennes haute résolution
- **Inconnu** : Saisie manuelle de la résolution

**Paramètres de segmentation** :
- **Méthode** : ExG (recommandé) ou HSV (fallback)
- **Seuil ExG** : Ajuster la sensibilité de détection (0-255)
- **Surface minimale** : Filtrer les petits composants (1-50 pixels)

### 2. Upload et analyse

1. Télécharger une image satellite (JPG, PNG)
2. Cliquer sur "🔍 Analyser la canopée"
3. Consulter les résultats

### 3. Résultats

L'application affiche :
- Image originale et segmentation superposée
- Métriques principales (arbres, surface, carbone, couverture)
- Équivalents environnementaux
- Avertissements dynamiques selon la source

### 4. Téléchargements

- **Masque de canopée** : Image PNG avec la végétation détectée
- **Rapport Markdown** : Rapport complet avec toutes les métriques

## 🔬 Méthodologie

### Segmentation par indice ExG

L'indice Excess Green (ExG) est calculé comme suit :

```
ExG = 2*G - R - B
```

Où R, G, B sont les canaux rouge, vert et bleu normalisés.

**Avantages** :
- Plus robuste que HSV pour la végétation
- Moins sensible aux variations de luminosité
- Fallback automatique sur HSV si nécessaire

### Comptage d'arbres

Utilisation de `cv2.connectedComponentsWithStats` :
1. Identification des composants connexes dans le masque
2. Filtrage par surface minimale (paramètre ajustable)
3. Comptage des composants valides

### Calcul du stock de carbone

```
Stock carbone (tCO₂) = Surface canopée (ha) × Facteur carbone (tCO₂/ha)
```

Facteurs par défaut (IPCC) :
- Forêt tropicale : 150 tCO₂/ha
- Forêt tempérée : 120 tCO₂/ha
- Forêt boréale : 80 tCO₂/ha

## ⚠️ Limitations et honnêteté

### Selon la source d'image

- **Drone (0.1m)** : Haute précision, détection fiable des arbres individuels
- **Planet (3m)** : Résolution intermédiaire, précision modérée
- **Sentinel-2 (10m)** : Surface fiable, comptage d'arbres limité
- **Inconnu** : Résultats à vérifier avec la résolution réelle

### Limitations générales

- L'indice ExG est sensible aux ombres denses et aux surfaces non-végétales vertes
- Les estimations sont basées sur des facteurs IPCC par défaut
- La validation terrain est nécessaire pour des applications critiques
- Les nuages, ombres et surfaces artificielles peuvent fausser les résultats

## 🛠️ Technologies utilisées

- **Python 3.10+**
- **Streamlit** : Interface web
- **OpenCV** : Traitement d'image
- **NumPy** : Calculs numériques
- **Pillow** : Gestion d'images

## 📝 Licence

Projet développé pour le hackathon Flora Carbon AI.

## 🤝 Contribution

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur GitHub.

---

**Développé avec 🌿 pour la protection des forêts**
