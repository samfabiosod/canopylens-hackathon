"""
CanopyLens v9.0 - Forest Canopy Analysis
=========================================
Analyse d'images satellites pour estimer la canopée forestière,
le nombre d'arbres et le stock de carbone.

Corrections apportées :
- Comptage d'arbres avec watershed (séparation des houppiers)
- Sélection manuelle de la résolution (Sentinel-2, Planet, Drone)
- Segmentation par indice ExG (Excess Green) + fallback HSV
- Section "Honnêteté" dynamique selon la source d'image
"""

import streamlit as st
import numpy as np
from PIL import Image
import io
from datetime import datetime
from skimage import measure, filters, morphology
from skimage.segmentation import find_boundaries, watershed
from skimage.feature import peak_local_max
from scipy import ndimage as ndi

# ─────────────────────────────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CanopyLens - Forest Canopy Analysis",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────
# CSS personnalisé - Design sombre et professionnel
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fond global */
    .stApp {
        background: linear-gradient(180deg, #030712 0%, #0a1628 50%, #030712 100%);
    }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
        border-radius: 16px;
        border: 1px solid rgba(16, 185, 129, 0.2);
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.1);
    }
    
    .main-header h1 {
        color: #10b981 !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
    }
    
    .main-header em {
        color: #9ca3af !important;
        font-size: 1.1rem !important;
    }
    
    /* Conteneurs de section */
    .section-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        border: 1px solid rgba(51, 65, 85, 0.5);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Conteneurs d'image */
    .image-container {
        background: linear-gradient(135deg, #0f172a 0%, #020617 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid rgba(51, 65, 85, 0.5);
    }
    
    /* Cartes de métriques */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid rgba(51, 65, 85, 0.5);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.15);
    }
    
    /* Boutons */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%) !important;
        border: 2px dashed rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
    }
    
    /* Alertes */
    .stAlert {
        border-radius: 12px !important;
        border-left-width: 4px !important;
    }
    
    .stAlert-info {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(2, 132, 199, 0.05) 100%) !important;
        border-left-color: #0ea5e9 !important;
    }
    
    .stAlert-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%) !important;
        border-left-color: #f59e0b !important;
    }
    
    .stAlert-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%) !important;
        border-left-color: #10b981 !important;
    }
    
    /* Métriques */
    [data-testid="stMetricValue"] {
        color: #10b981 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-size: 0.9rem !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #020617 100%) !important;
        border-right: 1px solid rgba(51, 65, 85, 0.5) !important;
    }
    
    /* Titres */
    h1, h2, h3, h4 {
        color: #f3f4f6 !important;
    }
    
    h4 {
        color: #10b981 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Texte */
    p, span, li {
        color: #d1d5db !important;
    }
    
    /* Images */
    img {
        border-radius: 8px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# Fonctions de traitement d'image
# ─────────────────────────────────────────────────────────────────────

def calculate_exg_index(image_rgb):
    """
    Calcule l'indice ExG (Excess Green Index) pour la segmentation de végétation.
    Formule: ExG = 2*G - R - B
    
    Args:
        image_rgb: Image RGB en numpy array (H, W, 3)
    
    Returns:
        exg: Indice ExG normalisé (H, W)
    """
    # Séparer les canaux
    r = image_rgb[:, :, 0].astype(float)
    g = image_rgb[:, :, 1].astype(float)
    b = image_rgb[:, :, 2].astype(float)
    
    # Calculer ExG
    exg = 2 * g - r - b
    
    # Normaliser entre 0 et 255
    exg_min = exg.min()
    exg_max = exg.max()
    
    if exg_max > exg_min:
        exg_normalized = ((exg - exg_min) / (exg_max - exg_min) * 255).astype(np.uint8)
    else:
        exg_normalized = np.zeros_like(exg, dtype=np.uint8)
    
    return exg_normalized


def segment_canopy_exg(image_rgb, threshold=50):
    """
    Segmente la canopée en utilisant l'indice ExG.
    
    Args:
        image_rgb: Image RGB en numpy array
        threshold: Seuil pour binariser l'indice ExG (0-255)
    
    Returns:
        mask: Masque binaire de la canopée
        exg_normalized: Indice ExG normalisé
    """
    exg = calculate_exg_index(image_rgb)
    
    # Appliquer le seuil
    mask = (exg > threshold).astype(np.uint8) * 255
    
    return mask, exg


def segment_canopy_hsv(image_rgb, lower_bound=(35, 40, 40), upper_bound=(85, 255, 255)):
    """
    Segmente la canopée en utilisant l'espace couleur HSV (fallback).
    
    Args:
        image_rgb: Image RGB en numpy array
        lower_bound: Bornes inférieures HSV
        upper_bound: Bornes supérieures HSV
    
    Returns:
        mask: Masque binaire de la canopée
    """
    # Convertir en HSV en utilisant PIL
    image_pil = Image.fromarray(image_rgb)
    hsv_pil = image_pil.convert('HSV')
    hsv = np.array(hsv_pil)
    
    # Appliquer le seuil
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for i in range(3):
        if i == 0:  # Hue
            mask[(hsv[:,:,i] >= lower_bound[i]) & (hsv[:,:,i] <= upper_bound[i])] = 255
        else:  # Saturation et Value
            mask[(hsv[:,:,i] >= lower_bound[i]) & (hsv[:,:,i] <= upper_bound[i]) & (mask == 255)] = 255
    
    # Simplification : appliquer les seuils sur les 3 canaux
    h_mask = (hsv[:,:,0] >= lower_bound[0]) & (hsv[:,:,0] <= upper_bound[0])
    s_mask = (hsv[:,:,1] >= lower_bound[1]) & (hsv[:,:,1] <= upper_bound[1])
    v_mask = (hsv[:,:,2] >= lower_bound[2]) & (hsv[:,:,2] <= upper_bound[2])
    mask = (h_mask & s_mask & v_mask).astype(np.uint8) * 255
    
    return mask


def count_trees_connected_components(mask, min_area=5):
    """
    Compte les arbres individuels en utilisant skimage.measure.label.
    
    Args:
        mask: Masque binaire de la canopée
        min_area: Surface minimale pour considérer un composant comme un arbre
    
    Returns:
        num_trees: Nombre d'arbres détectés
        labeled_mask: Masque avec les composants étiquetés
    """
    # Appliquer label pour trouver les composantes connexes
    labeled = measure.label(mask > 0, connectivity=2)
    regions = measure.regionprops(labeled)
    
    # Filtrer par surface minimale
    valid_labels = []
    for region in regions:
        if region.area >= min_area:
            valid_labels.append(region.label)
    
    # Créer un masque avec uniquement les composants valides
    labeled_mask = np.zeros_like(labeled)
    for idx, label in enumerate(valid_labels, start=1):
        labeled_mask[labeled == label] = idx
    
    num_trees = len(valid_labels)
    
    return num_trees, labeled_mask


def calculate_canopy_metrics(mask, resolution_m_per_pixel, carbon_factor=150):
    """
    Calcule les métriques de canopée : surface, stock de carbone.
    
    Args:
        mask: Masque binaire de la canopée
        resolution_m_per_pixel: Résolution en mètres par pixel
        carbon_factor: Facteur de carbone en tCO₂/ha (défaut: 150 pour forêt tropicale)
    
    Returns:
        metrics: Dictionnaire avec les métriques calculées
    """
    # Compter les pixels de canopée
    canopy_pixels = np.sum(mask > 0)
    total_pixels = mask.shape[0] * mask.shape[1]
    
    # Calculer la couverture en pourcentage
    canopy_coverage_pct = (canopy_pixels / total_pixels) * 100 if total_pixels > 0 else 0
    
    # Calculer la surface en hectares
    # 1 pixel = resolution_m_per_pixel² m²
    # 1 hectare = 10,000 m²
    canopy_area_m2 = canopy_pixels * (resolution_m_per_pixel ** 2)
    canopy_area_ha = canopy_area_m2 / 10000
    
    # Calculer le stock de carbone
    carbon_stock_tco2 = canopy_area_ha * carbon_factor
    
    # Équivalents environnementaux
    cars_offset = carbon_stock_tco2 / 4.6  # ~4.6 tCO₂ par voiture/an
    trees_equivalent = carbon_stock_tco2 / 0.022  # ~22 kg CO₂ par arbre/an
    
    return {
        'canopy_pixels': canopy_pixels,
        'total_pixels': total_pixels,
        'canopy_coverage_pct': canopy_coverage_pct,
        'canopy_area_ha': canopy_area_ha,
        'carbon_stock_tco2': carbon_stock_tco2,
        'cars_offset': cars_offset,
        'trees_equivalent': trees_equivalent
    }


def create_visualization_overlay(image_rgb, mask, alpha=0.5):
    """
    Crée une visualisation superposée de l'image originale et du masque.
    
    Args:
        image_rgb: Image RGB originale
        mask: Masque binaire de la canopée
        alpha: Transparence du masque
    
    Returns:
        overlay: Image superposée
    """
    # Créer une image colorée pour le masque (vert)
    mask_colored = np.zeros_like(image_rgb)
    mask_colored[mask > 0] = [0, 255, 0]  # Vert pour la canopée
    
    # Superposer en utilisant numpy
    overlay = (image_rgb * (1 - alpha) + mask_colored * alpha).astype(np.uint8)
    
    return overlay


# ─────────────────────────────────────────────────────────────────────
# Dictionnaire de référence pour la densité d'arbres (IPCC/FAO)
# ─────────────────────────────────────────────────────────────────────
TREE_DENSITY_REFERENCE = {
    "Tropical Moist Forest": (400, 600),
    "Forêt Tropicale Humide": (400, 600),
    "Tropical Dry Forest": (200, 400),
    "Forêt Tropicale Sèche": (200, 400),
    "Mangrove Forest": (600, 1000),
    "Forêt de Mangrove": (600, 1000),
    "Temperate Forest": (300, 500),
    "Forêt Tempérée": (300, 500),
}

# ─────────────────────────────────────────────────────────────────────
# Détection des houppiers avec watershed
# ─────────────────────────────────────────────────────────────────────
def detect_tree_crowns_watershed(mask, resolution_m, biome_name):
    """
    Détecte les houppiers individuels en utilisant watershed contrôlé par marqueurs.
    La distance minimale entre pics vient de la densité d'arbres par biome.
    
    Args:
        mask: Masque binaire de la canopée
        resolution_m: Résolution en mètres par pixel
        biome_name: Nom du biome pour obtenir la densité d'arbres
    
    Returns:
        crown_labels: Masque avec les houppiers étiquetés
        regions: Liste des régions détectées
    """
    binary = mask > 0
    if not np.any(binary):
        return np.zeros(mask.shape, dtype=np.int32), []

    min_density, max_density = TREE_DENSITY_REFERENCE.get(biome_name, (400, 600))
    avg_density = (min_density + max_density) / 2.0
    avg_crown_area_m2 = 10000.0 / avg_density
    crown_diameter_m = float(np.sqrt(avg_crown_area_m2))
    crown_diameter_px = max(2.0, crown_diameter_m / max(resolution_m, 1e-6))

    distance = ndi.distance_transform_edt(binary)
    min_distance_px = max(1, int(round(crown_diameter_px * 0.6)))
    coords = peak_local_max(distance, min_distance=min_distance_px,
                             labels=binary, exclude_border=False)

    if len(coords) == 0:
        labeled = measure.label(binary, connectivity=2)
        return labeled, measure.regionprops(labeled)

    markers_mask = np.zeros(binary.shape, dtype=bool)
    markers_mask[tuple(coords.T)] = True
    markers, _ = ndi.label(markers_mask)

    crown_labels = watershed(-distance, markers, mask=binary)
    regions = measure.regionprops(crown_labels)
    return crown_labels, regions


# ─────────────────────────────────────────────────────────────────────
# Comptage adaptatif des arbres
# ─────────────────────────────────────────────────────────────────────
def adaptive_tree_count(mask, resolution_m, canopy_area_ha, canopy_pct, biome_name):
    """
    Compte les arbres de manière adaptative selon la résolution et la couverture.
    
    Args:
        mask: Masque binaire de la canopée
        resolution_m: Résolution en mètres par pixel
        canopy_area_ha: Surface de canopée en hectares
        canopy_pct: Pourcentage de couverture
        biome_name: Nom du biome
    
    Returns:
        dict: Dictionnaire avec les résultats du comptage
    """
    min_density, max_density = TREE_DENSITY_REFERENCE.get(biome_name, (400, 600))

    if resolution_m <= 5.0:
        crown_labels, regions = detect_tree_crowns_watershed(mask, resolution_m, biome_name)

        if resolution_m < 2.0:
            min_crown_px = max(3, int(0.5 / (resolution_m ** 2)))
            max_crown_px = int(300.0 / (resolution_m ** 2))
        else:
            min_crown_px = max(5, int(5.0 / (resolution_m ** 2)))
            max_crown_px = int(400.0 / (resolution_m ** 2))

        tree_candidates = [r for r in regions if min_crown_px <= r.area <= max_crown_px]
        count = len(tree_candidates)

        if canopy_pct > 75:
            return {
                "method": "direct" if resolution_m < 2.0 else "adjusted",
                "count": count,
                "count_range": (count, int(count * 1.4)),
                "note_key": "tree_count_note_closedcanopy",
                "crown_labels": crown_labels,
            }

        if resolution_m < 2.0:
            return {
                "method": "direct", "count": count, "count_range": None,
                "note_key": "tree_count_note_highres", "crown_labels": crown_labels,
            }
        else:
            estimated = int(count * 1.15)
            return {
                "method": "adjusted", "count": estimated,
                "count_range": (count, int(count * 1.3)),
                "note_key": "tree_count_note_medres", "crown_labels": crown_labels,
            }
    else:
        est_min = int(canopy_area_ha * min_density)
        est_max = int(canopy_area_ha * max_density)
        return {
            "method": "density", "count": None,
            "count_range": (est_min, est_max),
            "note_key": "tree_count_note_lowres", "crown_labels": None,
        }


# ─────────────────────────────────────────────────────────────────────
# Interface utilisateur
# ─────────────────────────────────────────────────────────────────────

def main():
    """Fonction principale de l'application Streamlit."""
    
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🌿 CanopyLens - Forest Canopy Analysis")
    st.markdown("*Estimation de la canopée forestière et du stock de carbone à partir d'images satellites*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────
    # Sidebar - Configuration
    # ─────────────────────────────────────────────────────────────────
    st.sidebar.markdown("### ⚙️ Configuration")
    
    # Sélection de la source d'image
    image_source = st.sidebar.selectbox(
        "Source de l'image",
        options=["Sentinel-2 (10m)", "Planet (3m)", "Drone (0.1m)", "Inconnu (Saisie manuelle)"],
        index=0,
        help="Sélectionnez la source de votre image pour une estimation précise de la résolution"
    )
    
    # Résolution en mètres par pixel
    resolution_map = {
        "Sentinel-2 (10m)": 10.0,
        "Planet (3m)": 3.0,
        "Drone (0.1m)": 0.1
    }
    
    if image_source == "Inconnu (Saisie manuelle)":
        resolution_m_per_pixel = st.sidebar.number_input(
            "Résolution (m/pixel)",
            min_value=0.01,
            max_value=100.0,
            value=1.0,
            step=0.1,
            help="Entrez la résolution de votre image en mètres par pixel"
        )
    else:
        resolution_m_per_pixel = resolution_map[image_source]
        st.sidebar.info(f"📏 Résolution automatique : {resolution_m_per_pixel} m/pixel")
    
    # Facteur de carbone
    carbon_factor = st.sidebar.number_input(
        "Facteur de carbone (tCO₂/ha)",
        min_value=50,
        max_value=300,
        value=150,
        step=10,
        help="Facteur de stockage de carbone selon le type de forêt (IPCC defaults: Tropical=150, Tempéré=120, Boréal=80)"
    )
    
    # Paramètres de segmentation
    st.sidebar.markdown("### 🎯 Segmentation")
    
    segmentation_method = st.sidebar.radio(
        "Méthode de segmentation",
        options=["ExG (Excess Green)", "HSV (Fallback)"],
        index=0,
        help="ExG est plus robuste pour la végétation. HSV en fallback si l'image est trop sombre."
    )
    
    if segmentation_method == "ExG (Excess Green)":
        exg_threshold = st.sidebar.slider(
            "Seuil ExG",
            min_value=0,
            max_value=255,
            value=50,
            step=5,
            help="Seuil pour binariser l'indice ExG. Plus élevé = moins de végétation détectée."
        )
    else:
        st.sidebar.info("💡 HSV utilise des seuils par défaut optimisés pour la végétation verte.")
    
    # Paramètres de comptage
    min_tree_area = st.sidebar.slider(
        "Surface minimale d'un arbre (pixels)",
        min_value=1,
        max_value=50,
        value=5,
        step=1,
        help="Surface minimale pour considérer un composant comme un arbre individuel"
    )
    
    # ─────────────────────────────────────────────────────────────────
    # Upload d'image
    # ─────────────────────────────────────────────────────────────────
    st.markdown("### 📤 Upload d'image")
    
    uploaded_file = st.file_uploader(
        "Téléchargez une image satellite (JPG, PNG)",
        type=['jpg', 'jpeg', 'png'],
        help="Formats supportés : JPG, PNG. Taille recommandée : < 5000x5000 pixels"
    )
    
    if uploaded_file is not None:
        try:
            # Charger l'image
            image = Image.open(uploaded_file)
            image_rgb = np.array(image.convert('RGB'))
            
            # Vérifier la taille
            if image_rgb.shape[0] > 5000 or image_rgb.shape[1] > 5000:
                st.warning("⚠️ Image très grande. Le traitement peut être lent.")
            
            # Afficher l'image originale
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.subheader("🖼️ Image originale")
                st.image(image_rgb, use_column_width=True)
                st.markdown(f"*Dimensions : {image_rgb.shape[1]} × {image_rgb.shape[0]} pixels*")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # ─────────────────────────────────────────────────────────
            # Traitement de l'image
            # ─────────────────────────────────────────────────────────
            if st.button("🔍 Analyser la canopée", type="primary"):
                with st.spinner("Analyse en cours..."):
                    
                    # Étape 1 : Segmentation
                    if segmentation_method == "ExG (Excess Green)":
                        mask, exg_normalized = segment_canopy_exg(image_rgb, threshold=exg_threshold)
                        
                        # Vérifier si le masque est vide
                        if np.sum(mask > 0) == 0:
                            st.warning("⚠️ Aucune végétation détectée avec ExG. Passage en mode HSV...")
                            mask = segment_canopy_hsv(image_rgb)
                            segmentation_method_used = "HSV (Fallback)"
                        else:
                            segmentation_method_used = "ExG"
                    else:
                        mask = segment_canopy_hsv(image_rgb)
                        segmentation_method_used = "HSV"
                    
                    # Étape 2 : Calcul des métriques de base
                    metrics = calculate_canopy_metrics(mask, resolution_m_per_pixel, carbon_factor)
                    
                    # Étape 3 : Comptage adaptatif des arbres
                    # Déterminer le biome (par défaut "Tropical Moist Forest")
                    biome_name = "Tropical Moist Forest"
                    tree_result = adaptive_tree_count(
                        mask, 
                        resolution_m_per_pixel, 
                        metrics['canopy_area_ha'], 
                        metrics['canopy_coverage_pct'], 
                        biome_name
                    )
                    num_trees = tree_result['count'] if tree_result['count'] is not None else 0
                    
                    # Étape 4 : Créer la visualisation
                    overlay = create_visualization_overlay(image_rgb, mask, alpha=0.5)
                    
                    # ─────────────────────────────────────────────────
                    # Affichage des résultats
                    # ─────────────────────────────────────────────────
                    st.success("✅ Analyse terminée !")
                    
                    # Afficher la segmentation
                    with col2:
                        st.markdown('<div class="image-container">', unsafe_allow_html=True)
                        st.subheader("🌳 Canopée détectée")
                        st.image(overlay, use_column_width=True)
                        st.markdown(f"*Méthode : {segmentation_method_used}*")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Métriques principales
                    st.markdown("### 📊 Résultats")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("🌳 Arbres détectés", f"{num_trees:,}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("📏 Surface de canopée", f"{metrics['canopy_area_ha']:.2f} ha")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("💨 Stock de carbone", f"{metrics['carbon_stock_tco2']:.1f} tCO₂")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("📊 Couverture", f"{metrics['canopy_coverage_pct']:.1f}%")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Équivalents environnementaux
                    st.markdown("### 🌍 Équivalents environnementaux")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("🚗 Voitures compensées/an", f"{metrics['cars_offset']:.1f}")
                        st.markdown('*~4.6 tCO₂ par voiture/an*')
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("🌳 Arbres équivalents", f"{metrics['trees_equivalent']:.0f}")
                        st.markdown('*~22 kg CO₂ par arbre/an*')
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("📅 Absorption quotidienne", f"{metrics['carbon_stock_tco2'] * 1000 / 365:.1f} kg CO₂/jour")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # ─────────────────────────────────────────────────
                    # Section "Honnêteté" dynamique
                    # ─────────────────────────────────────────────────
                    st.markdown("### ⚠️ Ce dont nous sommes honnêtes")
                    
                    st.markdown('<div class="section-container">', unsafe_allow_html=True)
                    
                    # Messages dynamiques selon la source d'image
                    if image_source == "Drone (0.1m)":
                        st.success("✅ **Haute précision** : Résolution de 0.1m permet une détection fiable des arbres individuels.")
                    elif image_source == "Sentinel-2 (10m)":
                        st.warning("⚠️ **Résolution de 10m** : L'estimation des arbres individuels est limitée. La surface de canopée est plus fiable que le comptage d'arbres.")
                    elif image_source == "Planet (3m)":
                        st.info("ℹ️ **Résolution intermédiaire (3m)** : Détection d'arbres possible mais avec une précision modérée.")
                    else:
                        st.info("ℹ️ **Résolution inconnue** : Les résultats sont des estimations. Vérifiez la résolution réelle de votre image.")
                    
                    # Avertissements généraux
                    st.warning("⚠️ **Indice ExG** : Sensible aux ombres denses et aux surfaces non-végétales vertes (toits, peintures).")
                    
                    st.info("💡 **Limitations générales** :")
                    st.markdown("""
                    - Les estimations sont basées sur des facteurs IPCC par défaut
                    - La validation terrain est nécessaire pour des applications critiques
                    - Les nuages, ombres et surfaces artificielles peuvent fausser les résultats
                    - Le comptage d'arbres est une approximation basée sur la segmentation
                    """)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # ─────────────────────────────────────────────────
                    # Téléchargements
                    # ─────────────────────────────────────────────────
                    st.markdown("### 📥 Téléchargements")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Télécharger le masque
                        mask_pil = Image.fromarray(mask)
                        buffer = io.BytesIO()
                        mask_pil.save(buffer, format="PNG")
                        buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Télécharger le masque de canopée",
                            data=buffer,
                            file_name="canopy_mask.png",
                            mime="image/png"
                        )
                    
                    with col2:
                        # Télécharger le rapport
                        report = f"""
# CanopyLens - Rapport d'analyse
Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Configuration
- Source de l'image : {image_source}
- Résolution : {resolution_m_per_pixel} m/pixel
- Facteur de carbone : {carbon_factor} tCO₂/ha
- Méthode de segmentation : {segmentation_method_used}

## Résultats
- Arbres détectés : {num_trees}
- Surface de canopée : {metrics['canopy_area_ha']:.2f} ha
- Stock de carbone : {metrics['carbon_stock_tco2']:.1f} tCO₂
- Couverture : {metrics['canopy_coverage_pct']:.1f}%

## Équivalents environnementaux
- Voitures compensées/an : {metrics['cars_offset']:.1f}
- Arbres équivalents : {metrics['trees_equivalent']:.0f}
- Absorption quotidienne : {metrics['carbon_stock_tco2'] * 1000 / 365:.1f} kg CO₂/jour

## Limitations
- Estimation basée sur des facteurs IPCC par défaut
- Validation terrain nécessaire pour applications critiques
- Sensible aux ombres et surfaces non-végétales
"""
                        
                        st.download_button(
                            label="📥 Télécharger le rapport (Markdown)",
                            data=report,
                            file_name="canopylens_report.md",
                            mime="text/markdown"
                        )
        
        except Exception as e:
            st.error(f"❌ Erreur lors du traitement de l'image : {str(e)}")
            st.info("💡 Vérifiez que l'image est au format JPG ou PNG et n'est pas corrompue.")
    
    else:
        # Message d'accueil
        st.info("👆 Téléchargez une image satellite pour commencer l'analyse.")
        
        st.markdown("### 🎯 Comment utiliser CanopyLens")
        
        st.markdown("""
        1. **Sélectionnez la source** de votre image dans la barre latérale (Sentinel-2, Planet, Drone, ou manuel)
        2. **Ajustez les paramètres** de segmentation si nécessaire
        3. **Téléchargez une image** satellite (JPG, PNG)
        4. **Cliquez sur "Analyser"** pour lancer le traitement
        5. **Consultez les résultats** : nombre d'arbres, surface, stock de carbone
        6. **Téléchargez** le masque et le rapport si nécessaire
        
        💡 **Conseil** : Pour Sentinel-2, la détection de surface est plus fiable que le comptage d'arbres individuels.
        """)
        
        st.markdown("### 📚 Ressources")
        
        st.markdown("""
        - **Sentinel-2** : https://sentinel-hub.com/ (gratuit, 10m de résolution)
        - **Planet** : https://www.planet.com/ (payant, 3m de résolution)
        - **Facteurs IPCC** : https://www.ipcc-nggip.iges.or.jp/
        """)


if __name__ == "__main__":
    main()
