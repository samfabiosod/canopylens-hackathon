"""
CanopyLens v9.1 - Forest Canopy Analysis
=========================================
Analyse d'images satellites pour estimer la canopée forestière,
le nombre d'arbres et le stock de carbone.

Version simplifiée pour déploiement Streamlit Cloud :
- Comptage d'arbres avec composantes connexes (PIL/numpy)
- Sélection manuelle de la résolution (Sentinel-2, Planet, Drone)
- Segmentation par indice ExG (Excess Green) + fallback HSV
- Section "Honnêteté" dynamique selon la source d'image
"""

import streamlit as st
import numpy as np
from PIL import Image
import io
from datetime import datetime

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
# CSS personnalisé - Design professionnel moderne
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Variables CSS */
    :root {
        --primary: #10b981;
        --primary-dark: #059669;
        --primary-darker: #047857;
        --secondary: #0ea5e9;
        --accent: #f59e0b;
        --bg-dark: #030712;
        --bg-medium: #0f172a;
        --bg-light: #1e293b;
        --text-primary: #f9fafb;
        --text-secondary: #d1d5db;
        --text-muted: #9ca3af;
        --border: rgba(51, 65, 85, 0.5);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.4);
        --shadow-glow: 0 0 20px rgba(16, 185, 129, 0.3);
    }
    
    /* Fond global avec animation subtile */
    .stApp {
        background: linear-gradient(135deg, #030712 0%, #0a1628 50%, #030712 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Header avec glassmorphism */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        margin-bottom: 2.5rem;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.04) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(16, 185, 129, 0.2);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
        animation: fadeIn 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .main-header h1 {
        color: var(--primary) !important;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.75rem !important;
        text-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, var(--primary) 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header em {
        color: var(--text-muted) !important;
        font-size: 1.2rem !important;
        font-weight: 300 !important;
        letter-spacing: 0.02em;
    }
    
    /* Conteneurs de section avec glassmorphism */
    .section-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.6) 100%);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-lg);
        animation: fadeIn 0.5s ease-out;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .section-container:hover {
        border-color: rgba(16, 185, 129, 0.3);
        box-shadow: var(--shadow-lg), 0 0 30px rgba(16, 185, 129, 0.15);
        transform: translateY(-2px);
    }
    
    /* Conteneurs d'image avec effet premium */
    .image-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(2, 6, 23, 0.8) 100%);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .image-container:hover {
        border-color: rgba(14, 165, 233, 0.3);
        box-shadow: var(--shadow-lg), 0 0 25px rgba(14, 165, 233, 0.15);
    }
    
    /* Cartes de métriques avec effet premium */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 16px;
        margin: 0.75rem 0;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        transform: scaleX(0);
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover::before {
        transform: scaleX(1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: var(--shadow-lg), 0 0 30px rgba(16, 185, 129, 0.2);
    }
    
    /* Boutons avec effet premium */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2.5rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
        position: relative;
        overflow: hidden;
        letter-spacing: 0.02em;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-darker) 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
    }
    
    .stButton>button:active {
        transform: translateY(-1px) !important;
    }
    
    /* File uploader avec effet premium */
    .stFileUploader {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%) !important;
        backdrop-filter: blur(10px);
        border: 2px dashed rgba(16, 185, 129, 0.3) !important;
        border-radius: 16px !important;
        padding: 3rem 2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stFileUploader:hover {
        border-color: rgba(16, 185, 129, 0.6) !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%) !important;
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.2) !important;
    }
    
    /* Alertes avec design premium */
    .stAlert {
        border-radius: 12px !important;
        border-left-width: 4px !important;
        padding: 1.25rem !important;
        backdrop-filter: blur(10px);
        animation: slideIn 0.4s ease-out;
    }
    
    .stAlert-info {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(2, 132, 199, 0.05) 100%) !important;
        border-left-color: var(--secondary) !important;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.15) !important;
    }
    
    .stAlert-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%) !important;
        border-left-color: var(--accent) !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.15) !important;
    }
    
    .stAlert-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%) !important;
        border-left-color: var(--primary) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15) !important;
    }
    
    .stAlert-error {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%) !important;
        border-left-color: #ef4444 !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.15) !important;
    }
    
    /* Métriques avec typographie premium */
    [data-testid="stMetricValue"] {
        color: var(--primary) !important;
        font-size: 2.75rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
        background: linear-gradient(135deg, var(--primary) 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    
    [data-testid="stMetricDelta"] {
        color: var(--secondary) !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar avec glassmorphism */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(2, 6, 23, 0.95) 100%) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid var(--border) !important;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stSidebar"] h3 {
        color: var(--primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    
    /* Titres avec typographie premium */
    h1, h2, h3, h4 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    h2 {
        font-size: 2rem !important;
        margin-bottom: 1.25rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h4 {
        color: var(--primary) !important;
        font-size: 1.25rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        font-weight: 600 !important;
    }
    
    /* Texte avec typographie premium */
    p, span, li {
        color: var(--text-secondary) !important;
        line-height: 1.7 !important;
        font-weight: 400 !important;
    }
    
    /* Images avec effet premium */
    img {
        border-radius: 12px !important;
        box-shadow: var(--shadow-lg) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    img:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Selectbox avec style premium */
    .stSelectbox > div[data-baseweb="select"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stSelectbox > div[data-baseweb="select"]:hover {
        border-color: rgba(16, 185, 129, 0.4) !important;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.15) !important;
    }
    
    /* Slider avec style premium */
    .stSlider > div[data-baseweb="slider"] > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3) !important;
    }
    
    /* Progress bar avec style premium */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%) !important;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3) !important;
    }
    
    /* Expander avec style premium */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(16, 185, 129, 0.3) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    /* Download button avec style premium */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--secondary) 0%, #0284c7 100%) !important;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4) !important;
    }
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%);
        border-radius: 10px;
        border: 2px solid var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--primary-dark) 0%, var(--primary-darker) 100%);
    }
    
    /* Sélection de texte */
    ::selection {
        background: rgba(16, 185, 129, 0.3);
        color: var(--text-primary);
    }
    
    ::-moz-selection {
        background: rgba(16, 185, 129, 0.3);
        color: var(--text-primary);
    }
    
    /* Focus states */
    input:focus, textarea:focus, select:focus {
        outline: none !important;
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem !important;
        }
        
        .main-header em {
            font-size: 1rem !important;
        }
        
        .section-container {
            padding: 1.5rem !important;
        }
        
        .metric-card {
            padding: 1.5rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
        }
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
# Comptage des arbres avec composantes connexes (numpy/PIL uniquement)
# ─────────────────────────────────────────────────────────────────────
def count_trees_simple(mask, min_area=5):
    """
    Compte les arbres individuels en utilisant une approche simplifiée
    basée sur les composantes connexes avec numpy uniquement.
    
    Args:
        mask: Masque binaire de la canopée
        min_area: Surface minimale pour considérer un composant comme un arbre
    
    Returns:
        num_trees: Nombre d'arbres détectés
    """
    # Convertir le masque en binaire
    binary = mask > 0
    
    if not np.any(binary):
        return 0
    
    # Utiliser une approche simplifiée de labeling avec numpy
    # Créer un tableau de labels
    labels = np.zeros(binary.shape, dtype=np.int32)
    current_label = 1
    
    # Parcourir tous les pixels
    for y in range(binary.shape[0]):
        for x in range(binary.shape[1]):
            if binary[y, x] and labels[y, x] == 0:
                # Nouveau composant connexe trouvé
                # Utiliser un algorithme de flood fill simplifié
                stack = [(y, x)]
                labels[y, x] = current_label
                area = 0
                
                while stack:
                    cy, cx = stack.pop()
                    area += 1
                    
                    # Vérifier les 4 voisins
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = cy + dy, cx + dx
                        if (0 <= ny < binary.shape[0] and 
                            0 <= nx < binary.shape[1] and 
                            binary[ny, nx] and labels[ny, nx] == 0):
                            labels[ny, nx] = current_label
                            stack.append((ny, nx))
                
                current_label += 1
    
    # Compter les composants avec une surface suffisante
    num_trees = 0
    for label in range(1, current_label):
        component_area = np.sum(labels == label)
        if component_area >= min_area:
            num_trees += 1
    
    return num_trees


# ─────────────────────────────────────────────────────────────────────
# Comptage adaptatif des arbres (version simplifiée)
# ─────────────────────────────────────────────────────────────────────
def adaptive_tree_count(mask, resolution_m, canopy_area_ha, canopy_pct, biome_name):
    """
    Compte les arbres de manière adaptative selon la résolution et la couverture.
    Version simplifiée sans scipy/scikit-image.
    
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
        # Comptage direct avec composantes connexes
        count = count_trees_simple(mask, min_area=5)

        if canopy_pct > 75:
            return {
                "method": "direct" if resolution_m < 2.0 else "adjusted",
                "count": count,
                "count_range": (count, int(count * 1.4)),
                "note_key": "tree_count_note_closedcanopy",
            }

        if resolution_m < 2.0:
            return {
                "method": "direct", "count": count, "count_range": None,
                "note_key": "tree_count_note_highres",
            }
        else:
            estimated = int(count * 1.15)
            return {
                "method": "adjusted", "count": estimated,
                "count_range": (count, int(count * 1.3)),
                "note_key": "tree_count_note_medres",
            }
    else:
        # Estimation par densité pour basse résolution
        est_min = int(canopy_area_ha * min_density)
        est_max = int(canopy_area_ha * max_density)
        return {
            "method": "density", "count": None,
            "count_range": (est_min, est_max),
            "note_key": "tree_count_note_lowres",
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
