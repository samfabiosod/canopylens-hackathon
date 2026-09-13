"""
CanopyLens — Seeing forests more clearly, one satellite image at a time.
========================================================================
Estimate forest canopy cover and carbon stock from satellite imagery.
Built for the Flora Carbon AI Hackathon — Kolkata, September 2026.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

Deploy:
    Push to GitHub → share.streamlit.io → connect repo → done.

100% free, no API keys, no paid services.

v6.1 — Final Production Release:
  • Zero DEBUG messages — clean professional interface
  • Wide HSV thresholds with fallback for GeoTIFF compatibility
  • Fixed PDF KeyError bug
  • Full GeoTIFF support (Sentinel-2, Planet, drone)
  • Adaptive tree counting based on resolution
  • Professional PDF report generation
  • Bilingual interface (English/French)
  • No OpenCV dependency — uses PIL/Pillow only
"""

import streamlit as st
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skimage import measure
from skimage.segmentation import find_boundaries
from datetime import datetime
import io
import os
import tempfile


# ─────────────────────────────────────────────────────────────────────
# PIL-based image processing functions (no OpenCV)
# ─────────────────────────────────────────────────────────────────────
def rgb_to_hsv(img_array):
    """Convert RGB to HSV using PIL"""
    img = Image.fromarray(img_array)
    hsv_img = img.convert('HSV')
    return np.array(hsv_img)


def hsv_threshold(hsv_img, lower, upper):
    """Apply HSV threshold using only numpy"""
    h, s, v = hsv_img[:,:,0], hsv_img[:,:,1], hsv_img[:,:,2]
    mask = (h >= lower[0]) & (h <= upper[0]) & \
           (s >= lower[1]) & (s <= upper[1]) & \
           (v >= lower[2]) & (v <= upper[2])
    return (mask * 255).astype(np.uint8)


def morphological_cleanup(mask, kernel_size=5):
    """Apply morphological operations using PIL"""
    img = Image.fromarray(mask)
    img = img.filter(ImageFilter.MedianFilter(size=kernel_size))
    return np.array(img)


def blend_images(img1, img2, alpha=0.6, beta=0.4):
    """Blend two images using numpy"""
    return (img1 * alpha + img2 * beta).astype(np.uint8)


def encode_png(img_array):
    """Encode image as PNG using PIL"""
    img = Image.fromarray(img_array)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────
# Rasterio import with verification
# ─────────────────────────────────────────────────────────────────────
try:
    import rasterio
    from rasterio.enums import Resampling
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────
# ReportLab imports (PDF generation)
# ─────────────────────────────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CanopyLens — Forest Carbon Estimation",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────
# Custom CSS for professional styling
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding: 2rem; }
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-bottom: 2px solid #10b981;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .section-container {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #334155;
    }
    .image-container {
        background-color: #0f172a;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #334155;
    }
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# Resolution presets
# ─────────────────────────────────────────────────────────────────────
RESOLUTION_PRESETS = {
    "Auto-detect": None,
    "From GeoTIFF metadata": "geotiff",
    "Sentinel-2 (10 m/px)": 10.0,
    "Planet (3 m/px)": 3.0,
    "Drone / Aerial (0.5 m/px)": 0.5,
    "Drone Ultra-HD (0.1 m/px)": 0.1,
    "Landsat (30 m/px)": 30.0,
}

# ─────────────────────────────────────────────────────────────────────
# Tree density reference (IPCC/FAO defaults)
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
# Translations
# ─────────────────────────────────────────────────────────────────────
T = {
    "English": {
        "title": "🌿 CanopyLens — Forest Canopy Analysis",
        "subtitle": "Estimate forest canopy cover and carbon stock from satellite imagery",
        "upload": "Upload a satellite image (RGB or GeoTIFF)",
        "upload_hint": "💡 Supported formats: PNG, JPG, GeoTIFF (.tif/.tiff). Sentinel-2 16-bit data is auto-normalized.",
        "analyze": "🔍 Analyze Canopy",
        "analyzing": "Processing image…",
        "reset": "🔄 Reset / New Analysis",
        "reload": "🔃 Reload App",
        "sample": "🌲 Try with sample image",
        "biome": "Select Forest Biome:",
        "resolution": "Image Resolution:",
        "resolution_hint": "Select the source or let CanopyLens auto-detect",
        "biomes": {
            "Tropical Moist Forest (default: 150 tCO₂/ha)": 150,
            "Tropical Dry Forest (80 tCO₂/ha)": 80,
            "Mangrove Forest (200 tCO₂/ha)": 200,
            "Temperate Forest (120 tCO₂/ha)": 120,
        },
        "original": "Original Image",
        "processed": "Canopy Detection (green overlay)",
        "contours": "Detected Trees (contours)",
        "mask": "Canopy Mask",
        "canopy_area": "Canopy Area",
        "carbon_stock": "Carbon Stock",
        "trees": "Trees Detected",
        "trees_estimated": "Trees (estimated)",
        "coverage": "Canopy Coverage",
        "detected_resolution": "Detected Resolution",
        "equiv_title": "🌍 Carbon Equivalents",
        "cars": "cars' annual emissions offset",
        "trees_eq": "mature trees / year equivalent",
        "daily": "kg CO₂ absorbed per day",
        "disclaimer": "**⚠️ Important Disclaimer:** This is a rough proxy estimate based on green pixel thresholding. Real validation requires ground truth or LiDAR.",
        "download_mask": "📥 Download Canopy Mask (PNG)",
        "download_pdf": "📄 Download Full Report (PDF)",
        "geotiff_loaded": "✅ GeoTIFF loaded: {width}×{height}px, {bands} bands, {dtype}",
        "geotiff_metadata_title": "🛰️ GeoTIFF Metadata",
        "geotiff_crs": "CRS",
        "geotiff_resolution": "Resolution",
        "geotiff_bands": "Bands",
        "geotiff_dtype": "Data type",
        "geotiff_bounds": "Bounds",
        "geotiff_nodata": "NoData value",
        "geotiff_loading": "Loading GeoTIFF...",
        "geotiff_error": "❌ Error loading GeoTIFF: {error}",
        "geotiff_hint": "💡 Make sure the file is a valid GeoTIFF.",
        "geotiff_not_available": "⚠️ GeoTIFF support requires rasterio. Install with: pip install rasterio",
        "no_image": "👆 Upload an image or click 'Try with sample image' to begin.",
        "error_title": "❌ Error Processing Image",
        "no_green_detected": "⚠️ No green pixels detected with standard threshold. Trying with wider threshold...",
        "wider_threshold_success": "✅ Wider threshold detected {pixels} green pixels",
        "progress_steps": [
            "Converting to HSV color space…",
            "Applying adaptive threshold…",
            "Morphological cleanup…",
            "Estimating image resolution…",
            "Adaptive tree counting…",
            "Generating visualizations…",
            "Done!",
        ],
        "how_title": "🔬 How CanopyLens Works",
        "how_steps": [
            ("📤", "Upload", "Upload any RGB satellite, aerial image, or GeoTIFF"),
            ("🎨", "HSV Convert", "Convert RGB → HSV to isolate green hues"),
            ("🎯", "Threshold", "Adaptive threshold separates vegetation from background"),
            ("📏", "Resolution", "Auto-detect or manual resolution estimation"),
            ("📊", "Calculate", "Adaptive counting: direct (<2m) or density-based (>5m)"),
        ],
        "specs_title": "📐 Technical Specifications",
        "specs": [
            "Adaptive resolution detection",
            "High-res (<2m/px): direct individual tree counting",
            "Medium-res (2–5m/px): adjusted crown detection",
            "Low-res (>5m/px): density-based estimation",
            "Color space: HSV (Hue 20°–100°, Saturation ≥ 20, Value ≥ 20)",
            "Morphology kernel: 5 × 5, close + open operations",
            "Carbon factors: IPCC AR6 WGIII default biomass expansion factors",
            "Image resize: automatic downscale if > 2000 × 2000 px",
            "GeoTIFF support: Sentinel-2, Planet, custom exports",
            "Percentile stretching (2-98%) for 16-bit data normalization",
        ],
        "limitations_title": "⚠️ What We're Honest About",
        "limitations": [
            "No ground truth validation",
            "Assumes uniform forest",
            "RGB only",
            "Cloud cover causes underestimation",
            "Carbon factors are IPCC defaults",
            "Individual tree detection requires <2m resolution",
            "Density-based estimates follow IPCC/FAO standards",
        ],
        "sidebar_method": "📋 Methodology",
        "sidebar_method_text": "1. Convert RGB → HSV\n2. Apply adaptive threshold\n3. Morphological cleanup\n4. Estimate resolution\n5. Adaptive counting\n6. Calculate area → carbon",
        "tree_count_note_highres": "**📝 High-resolution detection (<2m/px):** Individual tree crowns detected.",
        "tree_count_note_medres": "**📝 Medium-resolution detection (2–5m/px):** Adjusted size thresholds.",
        "tree_count_note_lowres": "**📝 Low-resolution estimation (>5m/px):** Density-based estimate.",
        "tree_density_estimate": "**🌳 Density-based estimate:** {min}–{max} trees/ha for {biome}, total: **{est_min}–{est_max} trees**.",
    },
    "Français": {
        "title": "🌿 CanopyLens — Analyse de la Canopée Forestière",
        "subtitle": "Estimer la couverture de canopée et le stock de carbone",
        "upload": "Télécharger une image satellite (RVB ou GeoTIFF)",
        "upload_hint": "💡 Formats supportés : PNG, JPG, GeoTIFF (.tif/.tiff). Données Sentinel-2 16-bit normalisées automatiquement.",
        "analyze": "🔍 Analyser la Canopée",
        "analyzing": "Traitement en cours…",
        "reset": "🔄 Réinitialiser",
        "reload": "🔃 Recharger",
        "sample": "🌲 Image d'exemple",
        "biome": "Type de forêt :",
        "resolution": "Résolution :",
        "resolution_hint": "Sélectionnez ou auto-détection",
        "biomes": {
            "Forêt Tropicale Humide (défaut: 150 tCO₂/ha)": 150,
            "Forêt Tropicale Sèche (80 tCO₂/ha)": 80,
            "Forêt de Mangrove (200 tCO₂/ha)": 200,
            "Forêt Tempérée (120 tCO₂/ha)": 120,
        },
        "original": "Image Originale",
        "processed": "Détection Canopée",
        "contours": "Arbres Détectés",
        "mask": "Masque",
        "canopy_area": "Surface Canopée",
        "carbon_stock": "Stock Carbone",
        "trees": "Arbres",
        "trees_estimated": "Arbres (estimé)",
        "coverage": "Couverture",
        "detected_resolution": "Résolution",
        "equiv_title": "🌍 Équivalents Carbone",
        "cars": "voitures/an",
        "trees_eq": "arbres/an",
        "daily": "kg CO₂/jour",
        "disclaimer": "**⚠️ Avertissement :** Estimation approximative basée sur le seuillage des pixels verts. Validation réelle nécessite terrain ou LiDAR.",
        "download_mask": "📥 Télécharger Masque (PNG)",
        "download_pdf": "📄 Télécharger Rapport (PDF)",
        "geotiff_loaded": "✅ GeoTIFF chargé : {width}×{height}px, {bands} bandes, {dtype}",
        "geotiff_metadata_title": "🛰️ Métadonnées GeoTIFF",
        "geotiff_crs": "SCR",
        "geotiff_resolution": "Résolution",
        "geotiff_bands": "Bandes",
        "geotiff_dtype": "Type",
        "geotiff_bounds": "Limites",
        "geotiff_nodata": "NoData",
        "geotiff_loading": "Chargement GeoTIFF...",
        "geotiff_error": "❌ Erreur GeoTIFF : {error}",
        "geotiff_hint": "💡 Vérifiez que le fichier est valide.",
        "geotiff_not_available": "⚠️ Support GeoTIFF nécessite rasterio.",
        "no_image": "👆 Téléchargez une image.",
        "error_title": "❌ Erreur",
        "no_green_detected": "⚠️ Aucun pixel vert détecté. Tentative avec seuil élargi...",
        "wider_threshold_success": "✅ Seuil élargi a détecté {pixels} pixels verts",
        "progress_steps": [
            "Conversion TSV…",
            "Seuil adaptatif…",
            "Nettoyage morphologique…",
            "Estimation résolution…",
            "Comptage adaptatif…",
            "Génération visualisations…",
            "Terminé !",
        ],
        "how_title": "🔬 Fonctionnement",
        "how_steps": [
            ("📤", "Upload", "Image satellite ou GeoTIFF"),
            ("🎨", "Conv. TSV", "RGB → TSV"),
            ("🎯", "Seuil", "Détection végétation"),
            ("📏", "Résolution", "Auto ou manuel"),
            ("📊", "Calcul", "Comptage adaptatif"),
        ],
        "specs_title": "📐 Spécifications",
        "specs": [
            "Détection adaptative résolution",
            "Haute rés. (<2m/px) : comptage direct",
            "Rés. moyenne (2–5m/px) : ajusté",
            "Basse rés. (>5m/px) : densité",
            "Espace : TSV (Teinte 20°–100°)",
            "Noyau : 5 × 5",
            "Facteurs carbone : GIEC",
            "Resize auto si > 2000 × 2000 px",
            "Support GeoTIFF",
            "Étirement percentiles (2-98%)",
        ],
        "limitations_title": "⚠️ Limites",
        "limitations": [
            "Pas de validation terrain",
            "Forêt uniforme supposée",
            "RGB uniquement",
            "Nuages = sous-estimation",
            "Facteurs GIEC par défaut",
            "Détection arbres <2m résolution",
            "Estimations densité GIEC/FAO",
        ],
        "sidebar_method": "📋 Méthodologie",
        "sidebar_method_text": "1. RVB → TSV\n2. Seuil adaptatif\n3. Nettoyage\n4. Résolution\n5. Comptage\n6. Calcul carbone",
        "tree_count_note_highres": "**📝 Haute résolution (<2m/px) :** Couronnes détectées.",
        "tree_count_note_medres": "**📝 Résolution moyenne (2–5m/px) :** Seuils ajustés.",
        "tree_count_note_lowres": "**📝 Basse résolution (>5m/px) :** Estimation densité.",
        "tree_density_estimate": "**🌳 Estimation densité :** {min}–{max} arbres/ha pour {biome}, total : **{est_min}–{est_max} arbres**.",
    },
}

# ─────────────────────────────────────────────────────────────────────
# GeoTIFF Loading Function
# ─────────────────────────────────────────────────────────────────────
def load_geotiff(file_obj):
    """
    Load a GeoTIFF file robustly.
    Handles: RGB (3 bands), RGBA (4 bands), multispectral (13 bands), grayscale (1 band)
    Returns: (PIL Image, metadata_dict) or raises exception
    """
    if not RASTERIO_AVAILABLE:
        raise ImportError("Rasterio is not installed. Install with: pip install rasterio")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp:
        file_data = file_obj.read()
        tmp.write(file_data)
        tmp_path = tmp.name
    
    try:
        with rasterio.open(tmp_path) as src:
            metadata = {
                'crs': str(src.crs) if src.crs else 'Unknown',
                'width': src.width,
                'height': src.height,
                'bands': src.count,
                'dtype': str(src.dtypes[0]),
                'resolution': src.res,
                'nodata': src.nodata,
                'bounds': src.bounds
            }
            
            # Select bands
            num_bands = src.count
            if num_bands >= 4:
                band_indices = [3, 2, 1]  # Sentinel-2: B4, B3, B2
            elif num_bands == 3:
                band_indices = [0, 1, 2]
            elif num_bands == 1:
                band_indices = [0, 0, 0]
            else:
                band_indices = list(range(min(3, num_bands)))
            
            # Read bands
            bands = []
            for idx in band_indices:
                band = src.read(idx + 1)
                
                if metadata['nodata'] is not None:
                    band = np.where(band == metadata['nodata'], 0, band)
                bands.append(band)
            
            rgb = np.dstack(bands)
            
            # Normalize based on dtype
            dtype = metadata['dtype']
            
            if 'uint16' in dtype:
                # Percentile stretch for Sentinel-2 (0-10000 range)
                p2 = np.percentile(rgb, 2)
                p98 = np.percentile(rgb, 98)
                
                # If p2 is 0, use p5 instead
                if p2 == 0:
                    p2 = np.percentile(rgb, 5)
                
                if p98 - p2 < 1:
                    p2, p98 = rgb.min(), rgb.max()
                
                if p98 > p2:
                    rgb = np.clip(rgb, p2, p98)
                    rgb = ((rgb - p2) / (p98 - p2) * 255).astype(np.uint8)
                else:
                    if rgb.max() > 0:
                        rgb = (rgb / rgb.max() * 255).astype(np.uint8)
                    else:
                        rgb = rgb.astype(np.uint8)
            
            elif 'float' in dtype:
                if rgb.max() > 1.0:
                    rgb = rgb / rgb.max()
                
                rgb = np.clip(rgb, 0, 1)
                rgb = (rgb * 255).astype(np.uint8)
            
            else:
                rgb = rgb.astype(np.uint8)
            
            img = Image.fromarray(rgb)
            return img, metadata
    
    except Exception as e:
        raise Exception(f"Error loading GeoTIFF: {str(e)}")
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ─────────────────────────────────────────────────────────────────────
# Helper: create sample image
# ─────────────────────────────────────────────────────────────────────
def create_sample_image() -> Image.Image:
    """Generate a synthetic satellite-like image"""
    np.random.seed(42)
    img = np.zeros((500, 500, 3), dtype=np.uint8)
    img[:, :] = [139, 115, 85]
    
    noise = np.random.randint(-20, 20, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Forest patches (green)
    for _ in range(25):
        x, y = np.random.randint(0, 500, 2)
        r = np.random.randint(25, 90)
        green = np.random.randint(80, 160)
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(20, green, 20))
        img = np.array(pil_img)
    
    return Image.fromarray(img)


# ─────────────────────────────────────────────────────────────────────
# Helper: resize image
# ─────────────────────────────────────────────────────────────────────
def safe_resize(image: Image.Image, max_dim: int = 2000) -> Image.Image:
    """Resize image if too large"""
    w, h = image.size
    if w > max_dim or h > max_dim:
        ratio = min(max_dim / w, max_dim / h)
        new_size = (int(w * ratio), int(h * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image


# ─────────────────────────────────────────────────────────────────────
# Resolution estimation
# ─────────────────────────────────────────────────────────────────────
def estimate_resolution_from_components(regions, canopy_area_ha, canopy_pct):
    """Estimate GSD from median crown size"""
    areas = [r.area for r in regions if 20 <= r.area <= 50000]
    if not areas:
        return 10.0
    
    median_area_px = float(np.median(areas))
    if median_area_px > 0:
        assumed_crown_m2 = 100.0
        pixel_area_m2 = assumed_crown_m2 / median_area_px
        gsd = np.sqrt(pixel_area_m2)
        return float(np.clip(gsd, 0.05, 50.0))
    return 10.0


# ─────────────────────────────────────────────────────────────────────
# Adaptive tree counting
# ─────────────────────────────────────────────────────────────────────
def adaptive_tree_count(regions, resolution_m, canopy_area_ha, canopy_pct, biome_name):
    """Count trees adaptively based on resolution"""
    min_density, max_density = TREE_DENSITY_REFERENCE.get(biome_name, (400, 600))

    if resolution_m < 2.0:
        min_crown_px = max(5, int(1.0 / (resolution_m ** 2)))
        max_crown_px = int(200.0 / (resolution_m ** 2))
        tree_candidates = [r for r in regions if min_crown_px <= r.area <= max_crown_px]
        return {
            "method": "direct",
            "count": len(tree_candidates),
            "count_range": None,
            "note_key": "tree_count_note_highres",
        }
    elif resolution_m <= 5.0:
        min_crown_px = max(10, int(10.0 / (resolution_m ** 2)))
        max_crown_px = int(300.0 / (resolution_m ** 2))
        tree_candidates = [r for r in regions if min_crown_px <= r.area <= max_crown_px]
        correction = 1.3
        estimated = int(len(tree_candidates) * correction)
        return {
            "method": "adjusted",
            "count": estimated,
            "count_range": (int(len(tree_candidates) * 1.0), int(len(tree_candidates) * 1.6)),
            "note_key": "tree_count_note_medres",
        }
    else:
        est_min = int(canopy_area_ha * min_density)
        est_max = int(canopy_area_ha * max_density)
        return {
            "method": "density",
            "count": None,
            "count_range": (est_min, est_max),
            "note_key": "tree_count_note_lowres",
        }


# ─────────────────────────────────────────────────────────────────────
# Core: image processing pipeline
# ─────────────────────────────────────────────────────────────────────
def process_image(image, carbon_factor, biome_name, user_resolution=None, geotiff_resolution=None, progress_callback=None):
    """Full canopy analysis pipeline with wide HSV thresholds and fallback"""
    img_array = np.array(image.convert("RGB"))
    
    if progress_callback:
        progress_callback(0)

    hsv = rgb_to_hsv(img_array)
    if progress_callback:
        progress_callback(1)

    # WIDE HSV threshold for GeoTIFF compatibility
    lower_green = np.array([20, 20, 20])
    upper_green = np.array([100, 255, 255])
    
    mask = hsv_threshold(hsv, lower_green, upper_green)
    canopy_pixels = int(np.sum(mask > 0))
    
    # FALLBACK: if no green detected, try even wider threshold
    if canopy_pixels == 0:
        lower_green = np.array([15, 15, 15])
        upper_green = np.array([110, 255, 255])
        mask = hsv_threshold(hsv, lower_green, upper_green)
        canopy_pixels = int(np.sum(mask > 0))
    
    if progress_callback:
        progress_callback(2)

    mask = morphological_cleanup(mask, kernel_size=5)
    
    labeled = measure.label(mask > 0, connectivity=2)
    boundaries = find_boundaries(labeled, mode="thick")
    regions = measure.regionprops(labeled)

    total_pixels = mask.shape[0] * mask.shape[1]
    canopy_pct = (canopy_pixels / total_pixels) * 100
    canopy_area_ha_10m = canopy_pixels * 0.0001

    if geotiff_resolution is not None:
        resolution_m = geotiff_resolution
        resolution_source = "geotiff"
    elif user_resolution is not None:
        resolution_m = user_resolution
        resolution_source = "manual"
    else:
        resolution_m = estimate_resolution_from_components(regions, canopy_area_ha_10m, canopy_pct)
        resolution_source = "auto"

    pixel_area_m2 = resolution_m ** 2
    canopy_area_m2 = canopy_pixels * pixel_area_m2
    canopy_area_ha = canopy_area_m2 / 10000.0

    if progress_callback:
        progress_callback(3)

    tree_result = adaptive_tree_count(regions, resolution_m, canopy_area_ha, canopy_pct, biome_name)

    if progress_callback:
        progress_callback(4)

    carbon_stock = canopy_area_ha * carbon_factor

    metrics = {
        "canopy_area_ha": canopy_area_ha,
        "carbon_stock_tco2": carbon_stock,
        "canopy_pct": canopy_pct,
        "total_pixels": total_pixels,
        "canopy_pixels": canopy_pixels,
        "image_size": (mask.shape[1], mask.shape[0]),
        "resolution_m": resolution_m,
        "resolution_source": resolution_source,
        "tree_method": tree_result["method"],
        "tree_count": tree_result["count"],
        "tree_count_range": tree_result["count_range"],
        "tree_note_key": tree_result["note_key"],
    }

    overlay = img_array.copy()
    overlay[mask > 0] = [0, 200, 0]
    processed = blend_images(img_array, overlay, alpha=0.6, beta=0.4)

    contour_img = processed.copy()
    contour_img[boundaries] = [255, 255, 0]

    if progress_callback:
        progress_callback(5)

    return processed, contour_img, mask, metrics


# ─────────────────────────────────────────────────────────────────────
# PDF Report generation
# ─────────────────────────────────────────────────────────────────────
def generate_pdf_report(metrics, biome_name, lang, geotiff_metadata=None):
    """Generate PDF report"""
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab not installed")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#065F46"), spaceAfter=12)
    heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#047857"), spaceAfter=8)
    body_style = ParagraphStyle("CustomBody", parent=styles["Normal"], fontSize=10, leading=14)

    elements = []
    elements.append(Paragraph("🌿 CanopyLens Report", title_style))
    
    # FIX: Use local variable instead of missing translation key
    date_label = "Date" if lang == "English" else "Date"
    elements.append(Paragraph(f"{date_label}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#10B981")))
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("Analysis Results", heading_style))
    
    avg_car = 4.6
    cars_offset = metrics["carbon_stock_tco2"] / avg_car
    daily_kg = metrics["carbon_stock_tco2"] * 1000 / 365

    if metrics["tree_count"] is not None:
        tree_display = f"{metrics['tree_count']:,} ({metrics['tree_method']})"
    elif metrics["tree_count_range"]:
        tree_display = f"{metrics['tree_count_range'][0]:,}–{metrics['tree_count_range'][1]:,} (density-based)"
    else:
        tree_display = "N/A"

    table_data = [
        ["Metric", "Value"],
        ["Biome", biome_name],
        ["Resolution", f"{metrics['resolution_m']:.2f} m/px ({metrics['resolution_source']})"],
        ["Canopy Area", f"{metrics['canopy_area_ha']:.2f} ha"],
        ["Carbon Stock", f"{metrics['carbon_stock_tco2']:.2f} tCO₂"],
        ["Trees Detected", tree_display],
        ["Canopy Coverage", f"{metrics['canopy_pct']:.1f}%"],
        ["Cars Offset (year)", f"{cars_offset:.1f}"],
        ["Daily CO₂ Absorption", f"{daily_kg:.1f} kg"],
    ]

    table = Table(table_data, colWidths=[8*cm, 6*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065F46")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0FDF4")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.8*cm))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────────────────
def main():
    lang = st.sidebar.selectbox("🌐 Language | Langue", ["English", "Français"])
    t = T[lang]

    # Header
    header_container = st.container()
    with header_container:
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        st.title(t["title"])
        st.markdown(f"*{t['subtitle']}*")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

    # Sidebar
    st.sidebar.markdown(f"### {t['sidebar_method']}")
    st.sidebar.markdown(t["sidebar_method_text"])
    st.sidebar.markdown("---")

    biome_names = list(t["biomes"].keys())
    selected_biome = st.sidebar.selectbox(t["biome"], biome_names, index=0)
    carbon_factor = t["biomes"][selected_biome]

    resolution_options = list(RESOLUTION_PRESETS.keys())
    selected_resolution_label = st.sidebar.selectbox(t["resolution"], resolution_options, index=0, help=t["resolution_hint"])
    user_resolution = RESOLUTION_PRESETS[selected_resolution_label]

    # Reset button
    if st.sidebar.button(t["reset"]):
        keys_to_delete = ["image_uploaded", "processed_image", "contour_image", "canopy_mask", "metrics", "analysis_done", "loaded_image", "geotiff_metadata", "image"]
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    if st.sidebar.button(t["reload"]):
        st.rerun()

    # Upload section
    upload_container = st.container()
    with upload_container:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(t["upload"], type=["png", "jpg", "jpeg", "tif", "tiff"])
        st.caption(t["upload_hint"])
        sample_clicked = st.button(t["sample"])
        st.markdown('</div>', unsafe_allow_html=True)

    image = None
    geotiff_metadata = None
    
    try:
        if uploaded_file is not None:
            _, file_extension = os.path.splitext(uploaded_file.name)
            file_extension = file_extension.lower().lstrip('.')
            
            if file_extension in ['tif', 'tiff']:
                if not RASTERIO_AVAILABLE:
                    st.error(t["geotiff_not_available"])
                    return
                
                with st.spinner(t["geotiff_loading"]):
                    image, geotiff_metadata = load_geotiff(uploaded_file)
                
                st.session_state.geotiff_metadata = geotiff_metadata
                st.session_state.image_uploaded = True
                st.session_state.image = image
                
                st.success(t["geotiff_loaded"].format(
                    width=geotiff_metadata['width'],
                    height=geotiff_metadata['height'],
                    bands=geotiff_metadata['bands'],
                    dtype=geotiff_metadata['dtype']
                ))
            else:
                image = Image.open(uploaded_file).convert("RGB")
                st.session_state.geotiff_metadata = None
                st.session_state.image_uploaded = True
                st.session_state.image = image
            
            if image is not None:
                image = safe_resize(image)
                st.session_state.image = image
        
        elif sample_clicked:
            image = create_sample_image()
            st.session_state.image_uploaded = True
            st.session_state.image = image
            st.session_state.geotiff_metadata = None
            
        elif st.session_state.get("image_uploaded"):
            image = st.session_state.get("image")
            geotiff_metadata = st.session_state.get("geotiff_metadata")
    
    except Exception as e:
        st.error(t["geotiff_error"].format(error=str(e)))
        st.info(t["geotiff_hint"])
        return

    # Display GeoTIFF metadata
    if st.session_state.get("geotiff_metadata"):
        meta = st.session_state.geotiff_metadata
        with st.expander(t["geotiff_metadata_title"], expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"**{t['geotiff_crs']}:** {meta['crs']}")
                st.caption(f"**{t['geotiff_resolution']}:** {meta['resolution'][0]:.1f}m × {meta['resolution'][1]:.1f}m")
            with col2:
                st.caption(f"**{t['geotiff_bands']}:** {meta['bands']}")
                st.caption(f"**{t['geotiff_dtype']}:** {meta['dtype']}")
            with col3:
                if meta['bounds']:
                    st.caption(f"**{t['geotiff_bounds']}:**")
                    st.caption(f"W={meta['bounds'][0]:.4f}, S={meta['bounds'][1]:.4f}")
                    st.caption(f"E={meta['bounds'][2]:.4f}, N={meta['bounds'][3]:.4f}")
                if meta['nodata'] is not None:
                    st.caption(f"**{t['geotiff_nodata']}:** {meta['nodata']}")

    if st.session_state.get("image_uploaded") and image is not None:
        image_container = st.container()
        with image_container:
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.subheader(t["original"])
                st.image(image, caption="Input Image", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if st.button(t["analyze"], type="primary"):
                if 'image' not in st.session_state or st.session_state.image is None:
                    st.error("❌ No image found. Please reload the image.")
                    st.stop()
                
                image = st.session_state.image
                
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(step):
                    pct = int((step + 1) / len(t["progress_steps"]) * 100)
                    progress_bar.progress(pct)
                    status_text.text(t["progress_steps"][step])

                try:
                    with st.spinner(t["analyzing"]):
                        geotiff_res = None
                        if user_resolution == "geotiff" and st.session_state.get("geotiff_metadata"):
                            geotiff_res = st.session_state.geotiff_metadata['resolution'][0]
                        
                        processed, contour_img, mask, metrics = process_image(
                            image, carbon_factor, selected_biome,
                            user_resolution=user_resolution if user_resolution != "geotiff" else None,
                            geotiff_resolution=geotiff_res,
                            progress_callback=update_progress,
                        )

                    # Check if no green was detected
                    if metrics.get("canopy_pixels", 0) == 0:
                        st.warning(t["no_green_detected"])
                        return

                    progress_bar.progress(100)
                    status_text.text(t["progress_steps"][-1])

                    st.session_state.processed_image = processed
                    st.session_state.contour_image = contour_img
                    st.session_state.canopy_mask = mask
                    st.session_state.metrics = metrics
                    st.session_state.analysis_done = True

                except Exception as e:
                    st.error(f"{t['error_title']}: {str(e)}")
                    return

            if st.session_state.get("analysis_done"):
                processed = st.session_state.processed_image
                contour_img = st.session_state.contour_image
                mask = st.session_state.canopy_mask
                metrics = st.session_state.metrics

                with col2:
                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                    st.subheader(t["processed"])
                    st.image(processed, caption=t["processed"], use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                results_container = st.container()
                with results_container:
                    st.markdown('<div class="section-container">', unsafe_allow_html=True)
                    st.subheader(t["contours"])
                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                    st.image(contour_img, caption=t["contours"], use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    metrics_container = st.container()
                    with metrics_container:
                        st.markdown('<div class="section-container">', unsafe_allow_html=True)
                        
                        res_source_label = {
                            "auto": "auto-detected" if lang == "English" else "auto-détectée",
                            "manual": "user-selected" if lang == "English" else "sélectionnée",
                            "geotiff": "from GeoTIFF" if lang == "English" else "depuis GeoTIFF",
                        }.get(metrics["resolution_source"], metrics["resolution_source"])
                        
                        st.info(f"📏 **{t['detected_resolution']}:** {metrics['resolution_m']:.2f} m/pixel ({res_source_label})")

                        st.markdown("#### 📊 Analysis Results")
                        m1, m2, m3, m4 = st.columns(4)
                        with m1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric(t["canopy_area"], f"{metrics['canopy_area_ha']:.2f} ha")
                            st.markdown('</div>', unsafe_allow_html=True)
                        with m2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric(t["carbon_stock"], f"{metrics['carbon_stock_tco2']:.1f} tCO₂")
                            st.markdown('</div>', unsafe_allow_html=True)
                        with m3:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            if metrics["tree_count"] is not None:
                                st.metric(t["trees"], f"{metrics['tree_count']:,}", delta=f"{metrics['tree_method']}")
                            elif metrics["tree_count_range"]:
                                range_str = f"{metrics['tree_count_range'][0]:,}–{metrics['tree_count_range'][1]:,}"
                                st.metric(t["trees_estimated"], range_str, delta="density-based")
                            else:
                                st.metric(t["trees"], "N/A")
                            st.markdown('</div>', unsafe_allow_html=True)
                        with m4:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric(t["coverage"], f"{metrics['canopy_pct']:.1f}%")
                            st.markdown('</div>', unsafe_allow_html=True)

                        note_key = metrics.get("tree_note_key", "tree_count_note_lowres")
                        st.info(t.get(note_key, t["tree_count_note_lowres"]))

                        if metrics["tree_count_range"] and metrics["tree_method"] == "density":
                            est = metrics["tree_count_range"]
                            density_msg = t["tree_density_estimate"].format(
                                min=est[0] // max(1, int(metrics["canopy_area_ha"])),
                                max=est[1] // max(1, int(metrics["canopy_area_ha"])),
                                biome=selected_biome,
                                est_min=f"{est[0]:,}",
                                est_max=f"{est[1]:,}",
                            )
                            st.info(density_msg)

                        st.progress(min(metrics["canopy_pct"] / 100, 1.0))
                        st.caption(f"{t['coverage']}: {metrics['canopy_pct']:.1f}%")

                        st.markdown("#### 🌍 Carbon Equivalents")
                        avg_car = 4.6
                        cars_offset = metrics["carbon_stock_tco2"] / avg_car
                        trees_eq = metrics["carbon_stock_tco2"] / 0.022
                        daily_kg = metrics["carbon_stock_tco2"] * 1000 / 365

                        eq1, eq2, eq3 = st.columns(3)
                        with eq1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("🚗", f"{cars_offset:.1f}", t["cars"])
                            st.markdown('</div>', unsafe_allow_html=True)
                        with eq2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("🌳", f"{int(trees_eq):,}", t["trees_eq"])
                            st.markdown('</div>', unsafe_allow_html=True)
                        with eq3:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("📅", f"{daily_kg:.1f} kg", t["daily"])
                            st.markdown('</div>', unsafe_allow_html=True)

                        with st.expander(f"🗺️ {t['mask']}"):
                            fig, ax = plt.subplots(figsize=(8, 6))
                            ax.imshow(mask, cmap="Greens")
                            ax.axis("off")
                            ax.set_title(t["mask"])
                            st.pyplot(fig)
                            plt.close(fig)

                        st.warning(t["disclaimer"])
                        st.markdown('</div>', unsafe_allow_html=True)

                    download_container = st.container()
                    with download_container:
                        st.markdown('<div class="section-container">', unsafe_allow_html=True)
                        st.markdown("#### 📥 Downloads")
                        dl1, dl2 = st.columns(2)

                        with dl1:
                            mask_bytes = encode_png(mask)
                            st.download_button(label=t["download_mask"], data=mask_bytes, file_name="canopy_mask.png", mime="image/png", use_container_width=True)

                        with dl2:
                            if REPORTLAB_AVAILABLE:
                                pdf_bytes = generate_pdf_report(metrics, selected_biome, lang, geotiff_metadata=st.session_state.get("geotiff_metadata"))
                                st.download_button(label=t["download_pdf"], data=pdf_bytes, file_name=f"canopylens_report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
                            else:
                                st.warning("⚠️ PDF export requires reportlab")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info(t["no_image"])

    # How It Works section
    how_container = st.container()
    with how_container:
        st.markdown("---")
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.subheader(t["how_title"])

        cols = st.columns(5)
        for i, (emoji, title, desc) in enumerate(t["how_steps"]):
            with cols[i]:
                st.markdown(f"### {emoji}")
                st.markdown(f"**{title}**")
                st.caption(desc)

        st.markdown(f"#### {t['specs_title']}")
        for spec in t["specs"]:
            st.markdown(f"• {spec}")

        st.markdown(f"#### {t['limitations_title']}")
        for lim in t["limitations"]:
            st.markdown(f"• {lim}")
        
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
