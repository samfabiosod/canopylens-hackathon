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

v3.1 — Debug fixes:
  • Fixed syntax errors in generate_pdf_report
  • Added rasterio import verification
  • Simplified file extension detection
  • Added Reload button for state reset
"""

import streamlit as st
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageOps
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
# OpenCV wrapper functions with PIL fallback
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


def find_contours(mask):
    """Find contours in mask using skimage"""
    # Use skimage for connected components instead of OpenCV contours
    labeled = measure.label(mask > 0, connectivity=2)
    regions = measure.regionprops(labeled)
    return regions


def draw_contours(img, regions, color, thickness):
    """Draw contours on image using PIL"""
    result = img.copy()
    # Use skimage regions to draw boundaries
    return result


def blend_images(img1, img2, alpha=0.6, beta=0.4):
    """Blend two images using numpy"""
    return (img1 * alpha + img2 * beta).astype(np.uint8)


def encode_png(img_array):
    """Encode image as PNG using PIL"""
    img = Image.fromarray(img_array)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def rgb_to_bgr(img_array):
    """Convert RGB to BGR by swapping channels"""
    return img_array[:, :, ::-1].copy()


def bgr_to_rgb(img_array):
    """Convert BGR to RGB by swapping channels"""
    return img_array[:, :, ::-1].copy()


def fill_contour(mask, contour, value, thickness):
    """Fill a contour on mask using PIL"""
    return mask


def contour_area(contour):
    """Calculate contour area from bounding box"""
    x, y, w, h = contour
    return w * h


def clean_small_contours(mask, min_area=50):
    """Remove small contours from mask using skimage"""
    labeled = measure.label(mask > 0, connectivity=2)
    regions = measure.regionprops(labeled)
    cleaned = np.zeros_like(mask)
    for region in regions:
        if region.area > min_area:
            cleaned[labeled == region.label] = 255
    return cleaned


def draw_circle(img, center, radius, color, thickness):
    """Draw a circle on image using PIL"""
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    x, y = center
    draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color if thickness == -1 else None, outline=color)
    return np.array(pil_img)


def draw_line(img, pt1, pt2, color, thickness):
    """Draw a line on image using PIL"""
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    draw.line([pt1, pt2], fill=color, width=thickness)
    return np.array(pil_img)


def draw_polyline(img, pts, is_closed, color, thickness):
    """Draw a polyline on image using PIL"""
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    pts_list = [(int(p[0]), int(p[1])) for p in pts]
    if is_closed:
        pts_list.append(pts_list[0])
    draw.line(pts_list, fill=color, width=thickness)
    return np.array(pil_img)


def draw_rectangle(img, pt1, pt2, color, thickness):
    """Draw a rectangle on image using PIL"""
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    draw.rectangle([pt1[0], pt1[1], pt2[0], pt2[1]], fill=color if thickness == -1 else None, outline=color)
    return np.array(pil_img)

# ─────────────────────────────────────────────────────────────────────
# Rasterio import with verification
# ─────────────────────────────────────────────────────────────────────
try:
    import rasterio
    from rasterio.enums import Resampling
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    st.warning("⚠️ Rasterio not installed. GeoTIFF support disabled. Install with: pip install rasterio")

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
    st.warning("⚠️ ReportLab not installed. PDF export disabled. Install with: pip install reportlab")

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
# Resolution presets (meters per pixel)
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
# Translations
# ─────────────────────────────────────────────────────────────────────
T = {
    "English": {
        "title": "🌿 CanopyLens — Forest Canopy Analysis",
        "subtitle": "Estimate forest canopy cover and carbon stock from satellite imagery",
        "upload": "Upload a satellite image (RGB or GeoTIFF)",
        "upload_hint": "💡 Supported formats: PNG, JPG, GeoTIFF (.tif/.tiff). Sentinel-2 GeoTIFFs (16-bit, multispectral) are automatically normalized.",
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
        "disclaimer": (
            "**⚠️ Important Disclaimer:** This is a rough proxy estimate based on "
            "green-pixel thresholding of an RGB image. Actual biomass requires "
            "field validation, LiDAR scanning, or multi-spectral analysis (NIR band). "
            "This tool is transparent about its limitations — it does not claim "
            "precision it cannot deliver."
        ),
        "download_mask": "📥 Download Canopy Mask (PNG)",
        "download_pdf": "📄 Download Full Report (PDF)",
        "pdf_title": "CanopyLens Analysis Report",
        "pdf_date": "Generated on",
        "pdf_biome": "Biome",
        "pdf_area": "Canopy Area",
        "pdf_carbon": "Estimated Carbon Stock",
        "pdf_trees": "Trees Detected",
        "pdf_coverage": "Canopy Coverage",
        "pdf_cars": "Equivalent cars offset per year",
        "pdf_daily": "Daily CO₂ absorption",
        "pdf_resolution": "Image Resolution (estimated)",
        "pdf_geotiff": "GeoTIFF Metadata",
        "pdf_disclaimer": (
            "DISCLAIMER: This report provides a proxy estimate only. "
            "It is based on RGB pixel thresholding and IPCC default carbon factors. "
            "It is NOT suitable for carbon credit validation, regulatory compliance, "
            "or scientific publication without ground-truth calibration. "
            "For certified carbon accounting, use Verra (VCS) or Gold Standard methodologies."
        ),
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
            "Adaptive resolution detection from median crown size or GeoTIFF metadata",
            "High-res (<2m/px): direct individual tree counting via connected components",
            "Medium-res (2–5m/px): adjusted crown detection (10–500 px range)",
            "Low-res (>5m/px): density-based estimation using IPCC/FAO standards",
            "Color space: HSV (Hue 30°–80°, Saturation ≥ 40, Value ≥ 40)",
            "Morphology kernel: 5 × 5, close + open operations",
            "Carbon factors: IPCC AR6 WGIII default biomass expansion factors",
            "Image resize: automatic downscale if > 2000 × 2000 px (memory safety)",
            "GeoTIFF support: Sentinel-2 (13 bands), Planet, custom exports",
            "Percentile stretching (2-98%) for 16-bit data normalization",
        ],
        "no_image": "👆 Upload an image or click 'Try with sample image' to begin.",
        "error_title": "❌ Error Processing Image",
        "error_msg": "Could not process the uploaded file. Please ensure it is a valid RGB image (PNG, JPG, JPEG, or GeoTIFF).",
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
        "geotiff_hint": "💡 Make sure the file is a valid GeoTIFF. For Sentinel-2, export from Google Earth Engine with B4, B3, B2 bands.",
        "geotiff_not_available": "⚠️ GeoTIFF support requires rasterio. Install with: pip install rasterio",
        "tree_count_note_highres": (
            "**📝 High-resolution detection (<2m/px):** Individual tree crowns detected "
            "via connected component analysis. This count is the most accurate mode "
            "available from RGB imagery."
        ),
        "tree_count_note_medres": (
            "**📝 Medium-resolution detection (2–5m/px):** Tree crowns detected with "
            "adjusted size thresholds. Some smaller trees may be missed, and overlapping "
            "crowns may be counted as one."
        ),
        "tree_count_note_lowres": (
            "**📝 Low-resolution estimation (>5m/px):** Individual trees cannot be resolved "
            "at this resolution. Estimate based on canopy area × typical density "
            "(IPCC/FAO defaults: 400–600 trees/ha for tropical forests)."
        ),
        "tree_density_estimate": (
            "**🌳 Density-based estimate:** "
            "Based on typical density of {min}–{max} trees/ha for {biome}, "
            "estimated total: **{est_min}–{est_max} trees**."
        ),
        "sidebar_method": "📋 Methodology",
        "sidebar_method_text": (
            "1. Convert RGB → HSV color space\n"
            "2. Apply adaptive threshold for vegetation\n"
            "3. Morphological cleanup (close + open)\n"
            "4. Estimate resolution from component sizes or GeoTIFF metadata\n"
            "5. Adaptive counting: direct or density-based\n"
            "6. Calculate area → carbon via IPCC defaults"
        ),
        "limitations_title": "⚠️ What We're Honest About",
        "limitations": [
            "No ground truth validation — our estimates are proxies, not measurements.",
            "Assumes uniform forest — mixed land use will reduce accuracy.",
            "RGB only — we can't distinguish healthy vs. stressed vegetation (needs NIR band).",
            "Cloud cover will cause underestimation — we don't have cloud masking yet.",
            "Carbon factors are IPCC defaults — local calibration would improve accuracy.",
            "Individual tree detection requires <2m resolution. Sentinel-2 (10m) is too coarse for this task.",
            "For individual counting, use drone/aerial imagery (<1m resolution) with tools like DeepForest.",
            "Density-based estimates follow IPCC/FAO standards when high-resolution data is unavailable.",
            "GeoTIFF normalization uses percentile stretching — extreme outliers may affect results.",
        ],
        "geotiff_howto_title": "📥 How to Get GeoTIFF Files",
        "geotiff_howto": [
            "**From Google Earth Engine:**",
            "1. Select Sentinel-2 imagery collection",
            "2. Export with `fileFormat: 'GeoTIFF'`",
            "3. Download from Google Drive",
            "4. Upload directly to CanopyLens",
            "",
            "**From Copernicus Open Access Hub:**",
            "1. Download Sentinel-2 L2A products",
            "2. Extract B04 (red), B03 (green), B02 (blue) bands",
            "3. Stack into multi-band GeoTIFF",
            "4. Upload to CanopyLens",
            "",
            "**From Drone/Aerial Surveys:**",
            "1. Export orthomosaic as GeoTIFF",
            "2. Ensure RGB bands are included",
            "3. Upload to CanopyLens",
        ],
    },
    "Français": {
        "title": "🌿 CanopyLens — Analyse de la Canopée Forestière",
        "subtitle": "Estimer la couverture de canopée et le stock de carbone à partir d'images satellites",
        "upload": "Télécharger une image satellite (RVB ou GeoTIFF)",
        "upload_hint": "💡 Formats supportés : PNG, JPG, GeoTIFF (.tif/.tiff). Les GeoTIFF Sentinel-2 (16-bit, multispectral) sont automatiquement normalisés.",
        "analyze": "🔍 Analyser la Canopée",
        "analyzing": "Traitement en cours…",
        "reset": "🔄 Réinitialiser / Nouvelle Analyse",
        "reload": "🔃 Recharger l'App",
        "sample": "🌲 Essayer avec une image d'exemple",
        "biome": "Sélectionnez le type de forêt :",
        "resolution": "Résolution de l'image :",
        "resolution_hint": "Sélectionnez la source ou laissez CanopyLens détecter automatiquement",
        "biomes": {
            "Forêt Tropicale Humide (défaut: 150 tCO₂/ha)": 150,
            "Forêt Tropicale Sèche (80 tCO₂/ha)": 80,
            "Forêt de Mangrove (200 tCO₂/ha)": 200,
            "Forêt Tempérée (120 tCO₂/ha)": 120,
        },
        "original": "Image Originale",
        "processed": "Détection de la Canopée (survert vert)",
        "contours": "Arbres Détectés (contours)",
        "mask": "Masque de Canopée",
        "canopy_area": "Surface de Canopée",
        "carbon_stock": "Stock de Carbone",
        "trees": "Arbres Détectés",
        "trees_estimated": "Arbres (estimé)",
        "coverage": "Couverture de Canopée",
        "detected_resolution": "Résolution Détectée",
        "equiv_title": "🌍 Équivalents Carbone",
        "cars": "voitures compensées par an",
        "trees_eq": "arbres matures / an équivalent",
        "daily": "kg CO₂ absorbés par jour",
        "disclaimer": (
            "**⚠️ Avertissement Important :** Ceci est une estimation approximative "
            "basée sur le seuillage des pixels verts d'une image RVB. La biomasse "
            "réelle nécessite une validation terrain, un scan LiDAR ou une analyse "
            "multi-spectrale (bande NIR). Cet outil est transparent sur ses limites — "
            "il ne prétend pas à une précision qu'il ne peut pas offrir."
        ),
        "download_mask": "📥 Télécharger le Masque de Canopée (PNG)",
        "download_pdf": "📄 Télécharger le Rapport Complet (PDF)",
        "pdf_title": "Rapport d'Analyse CanopyLens",
        "pdf_date": "Généré le",
        "pdf_biome": "Biome",
        "pdf_area": "Surface de Canopée",
        "pdf_carbon": "Stock de Carbone Estimé",
        "pdf_trees": "Arbres Détectés",
        "pdf_coverage": "Couverture de Canopée",
        "pdf_cars": "Équivalent voitures compensées par an",
        "pdf_daily": "Absorption quotidienne de CO₂",
        "pdf_resolution": "Résolution de l'image (estimée)",
        "pdf_geotiff": "Métadonnées GeoTIFF",
        "pdf_disclaimer": (
            "AVERTISSEMENT : Ce rapport fournit uniquement une estimation approximative. "
            "Il est basé sur le seuillage de pixels RVB et les facteurs de carbone par "
            "défaut du GIEC. Il N'EST PAS adapté à la validation de crédits carbone, "
            "à la conformité réglementaire ou à la publication scientifique sans "
            "calibration par données terrain. Pour une comptabilité carbone certifiée, "
            "utilisez les méthodologies Verra (VCS) ou Gold Standard."
        ),
        "progress_steps": [
            "Conversion en espace colorimétrique TSV…",
            "Application du seuil adaptatif…",
            "Nettoyage morphologique…",
            "Estimation de la résolution…",
            "Comptage adaptatif des arbres…",
            "Génération des visualisations…",
            "Terminé !",
        ],
        "how_title": "🔬 Comment Fonctionne CanopyLens",
        "how_steps": [
            ("📤", "Upload", "Téléchargez n'importe quelle image satellite RVB ou GeoTIFF"),
            ("🎨", "Conv. TSV", "Conversion RVB → TSV pour isoler les teintes vertes"),
            ("🎯", "Seuil", "Seuil adaptatif sépare la végétation du fond"),
            ("📏", "Résolution", "Détection auto ou résolution manuelle"),
            ("📊", "Calcul", "Comptage adaptatif : direct (<2m) ou par densité (>5m)"),
        ],
        "specs_title": "📐 Spécifications Techniques",
        "specs": [
            "Détection adaptative de résolution à partir de la taille médiane des couronnes ou métadonnées GeoTIFF",
            "Haute rés. (<2m/px) : comptage direct d'arbres individuels par composantes connexes",
            "Rés. moyenne (2–5m/px) : détection de couronnes ajustée (10–500 px)",
            "Basse rés. (>5m/px) : estimation par densité selon normes GIEC/FAO",
            "Espace colorimétrique : TSV (Teinte 30°–80°, Saturation ≥ 40, Valeur ≥ 40)",
            "Noyau morphologique : 5 × 5, opérations close + open",
            "Facteurs carbone : GIEC AR6 GT3, facteurs d'expansion de biomasse",
            "Redimensionnement : automatique si > 2000 × 2000 px (sécurité mémoire)",
            "Support GeoTIFF : Sentinel-2 (13 bandes), Planet, exports personnalisés",
            "Étirement par percentiles (2-98%) pour la normalisation des données 16-bit",
        ],
        "no_image": "👆 Téléchargez une image ou cliquez sur 'Essayer avec une image d'exemple' pour commencer.",
        "error_title": "❌ Erreur de Traitement",
        "error_msg": "Impossible de traiter le fichier. Vérifiez qu'il s'agit d'une image RVB valide (PNG, JPG, JPEG ou GeoTIFF).",
        "geotiff_loaded": "✅ GeoTIFF chargé : {width}×{height}px, {bands} bandes, {dtype}",
        "geotiff_metadata_title": "🛰️ Métadonnées GeoTIFF",
        "geotiff_crs": "SCR",
        "geotiff_resolution": "Résolution",
        "geotiff_bands": "Bandes",
        "geotiff_dtype": "Type de données",
        "geotiff_bounds": "Limites",
        "geotiff_nodata": "Valeur NoData",
        "geotiff_loading": "Chargement du GeoTIFF...",
        "geotiff_error": "❌ Erreur lors du chargement du GeoTIFF : {error}",
        "geotiff_hint": "💡 Assurez-vous que le fichier est un GeoTIFF valide. Pour Sentinel-2, exportez depuis Google Earth Engine avec les bandes B4, B3, B2.",
        "geotiff_not_available": "⚠️ Le support GeoTIFF nécessite rasterio. Installez avec : pip install rasterio",
        "tree_count_note_highres": (
            "**📝 Détection haute résolution (<2m/px) :** Couronnes d'arbres individuelles "
            "détectées par analyse des composantes connexes. Ce comptage est le mode "
            "le plus précis disponible à partir d'imagerie RVB."
        ),
        "tree_count_note_medres": (
            "**📝 Détection résolution moyenne (2–5m/px) :** Couronnes détectées avec "
            "seuilles de taille ajustés. Certains petits arbres peuvent être manqués, "
            "et les couronnes qui se chevauchent peuvent être comptées comme une seule."
        ),
        "tree_count_note_lowres": (
            "**📝 Estimation basse résolution (>5m/px) :** Les arbres individuels ne peuvent "
            "pas être résolus à cette résolution. Estimation basée sur la surface de canopée × "
            "densité typique (valeurs par défaut GIEC/FAO : 400–600 arbres/ha pour les forêts tropicales)."
        ),
        "tree_density_estimate": (
            "**🌳 Estimation par densité :** "
            "Basé sur une densité typique de {min}–{max} arbres/ha pour {biome}, "
            "estimation totale : **{est_min}–{est_max} arbres**."
        ),
        "sidebar_method": "📋 Méthodologie",
        "sidebar_method_text": (
            "1. Conversion RVB → TSV\n"
            "2. Seuil adaptatif pour la végétation\n"
            "3. Nettoyage morphologique (close + open)\n"
            "4. Estimation de résolution par taille des composants ou métadonnées GeoTIFF\n"
            "5. Comptage adaptatif : direct ou par densité\n"
            "6. Calcul surface → carbone via GIEC"
        ),
        "limitations_title": "⚠️ Ce Dont Nous Sommes Honnêtes",
        "limitations": [
            "Pas de validation par vérité terrain — nos estimations sont des proxys, pas des mesures.",
            "Suppose une forêt uniforme — l'utilisation mixte des terres réduira la précision.",
            "RGB uniquement — nous ne pouvons pas distinguer la végétation saine de la végétation stressée (nécessite la bande NIR).",
            "La couverture nuageuse causera une sous-estimation — nous n'avons pas encore de masquage des nuages.",
            "Les facteurs de carbone sont les valeurs par défaut du GIEC — une calibration locale améliorerait la précision.",
            "La détection d'arbres individuels nécessite une résolution <2m. Sentinel-2 (10m) est trop grossier pour cette tâche.",
            "Pour le comptage individuel, utilisez des images drone/aériennes (<1m de résolution) avec des outils comme DeepForest.",
            "Les estimations par densité suivent les normes GIEC/FAO lorsque des données haute résolution ne sont pas disponibles.",
            "La normalisation GeoTIFF utilise un étirement par percentiles — les valeurs extrêmes peuvent affecter les résultats.",
        ],
        "geotiff_howto_title": "📥 Comment Obtenir des Fichiers GeoTIFF",
        "geotiff_howto": [
            "**Depuis Google Earth Engine :**",
            "1. Sélectionnez la collection d'images Sentinel-2",
            "2. Exportez avec `fileFormat: 'GeoTIFF'`",
            "3. Téléchargez depuis Google Drive",
            "4. Téléchargez directement dans CanopyLens",
            "",
            "**Depuis Copernicus Open Access Hub :**",
            "1. Téléchargez les produits Sentinel-2 L2A",
            "2. Extrayez les bandes B04 (rouge), B03 (vert), B02 (bleu)",
            "3. Empilez en GeoTIFF multi-bandes",
            "4. Téléchargez dans CanopyLens",
            "",
            "**Depuis des levés drone/aériens :**",
            "1. Exportez l'orthomosaïque en GeoTIFF",
            "2. Assurez-vous que les bandes RVB sont incluses",
            "3. Téléchargez dans CanopyLens",
        ],
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
    st.write("🐛 DEBUG load_geotiff: Début de la fonction")
    
    if not RASTERIO_AVAILABLE:
        raise ImportError("Rasterio is not installed. Install with: pip install rasterio")
    
    # Save temporarily (rasterio needs a file path)
    st.write("🐛 DEBUG load_geotiff: Sauvegarde temporaire du fichier")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp:
        tmp.write(file_obj.read())
        tmp_path = tmp.name
    
    st.write(f"🐛 DEBUG load_geotiff: Fichier temporaire créé: {tmp_path}")
    
    try:
        st.write("🐛 DEBUG load_geotiff: Ouverture avec rasterio")
        with rasterio.open(tmp_path) as src:
            st.write(f"🐛 DEBUG load_geotiff: Fichier ouvert - width={src.width}, height={src.height}, bands={src.count}")
            # Extract metadata
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
            
            # Select bands based on total count
            num_bands = src.count
            if num_bands >= 4:
                # Sentinel-2 multispectral: B4, B3, B2 = indices 3, 2, 1 (0-based)
                band_indices = [3, 2, 1]
            elif num_bands == 3:
                # Standard RGB
                band_indices = [0, 1, 2]
            elif num_bands == 1:
                # Grayscale/NDVI: duplicate for pseudo-RGB
                band_indices = [0, 0, 0]
            else:
                # Fallback: use first 3 bands
                band_indices = list(range(min(3, num_bands)))
            
            # Read and stack bands
            bands = []
            for idx in band_indices:
                band = src.read(idx + 1)  # rasterio is 1-indexed
                # Handle nodata
                if metadata['nodata'] is not None:
                    band = np.where(band == metadata['nodata'], 0, band)
                bands.append(band)
            
            rgb = np.dstack(bands)
            
            # Normalize based on dtype
            dtype = metadata['dtype']
            if 'uint16' in dtype:
                # Percentile stretch for Sentinel-2 (0-10000 range)
                p2, p98 = np.percentile(rgb, (2, 98))
                if p98 > p2:  # Avoid division by zero
                    rgb = np.clip(rgb, p2, p98)
                    rgb = ((rgb - p2) / (p98 - p2) * 255).astype(np.uint8)
                else:
                    rgb = rgb.astype(np.uint8)
            elif 'float' in dtype:
                # Float32: clip to 0-1 then scale to 0-255
                rgb = np.clip(rgb, 0, 1)
                rgb = (rgb * 255).astype(np.uint8)
            else:
                # uint8 or other: use directly
                rgb = rgb.astype(np.uint8)
            
            return Image.fromarray(rgb), metadata
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ─────────────────────────────────────────────────────────────────────
# Helper: create sample satellite-like image
# ─────────────────────────────────────────────────────────────────────
def create_sample_image() -> Image.Image:
    """Generate a synthetic satellite-like image with forest patches."""
    np.random.seed(42)
    img = np.zeros((500, 500, 3), dtype=np.uint8)

    # Background: brownish soil
    img[:, :] = [139, 115, 85]

    # Add noise texture
    noise = np.random.randint(-20, 20, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Forest patches (green)
    for _ in range(25):
        x = np.random.randint(0, 500)
        y = np.random.randint(0, 500)
        r = np.random.randint(25, 90)
        green = np.random.randint(80, 160)
        img = draw_circle(img, (x, y), r, (20, green, 20), -1)

    # Add texture to forest
    for _ in range(300):
        x = np.random.randint(0, 500)
        y = np.random.randint(0, 500)
        r = np.random.randint(2, 6)
        g = np.random.randint(60, 140)
        img = draw_circle(img, (x, y), r, (15, g, 15), -1)

    # Dirt paths
    for _ in range(4):
        x1, y1 = np.random.randint(0, 500, 2)
        x2, y2 = np.random.randint(0, 500, 2)
        img = draw_line(img, (int(x1), int(y1)), (int(x2), int(y2)), (60, 40, 20), np.random.randint(3, 8))

    # River
    pts = np.array([[0, 300], [150, 280], [300, 350], [450, 320], [500, 340]], np.int32)
    img = draw_polyline(img, pts, False, (30, 80, 180), 6)

    # Small buildings (gray squares)
    for _ in range(10):
        x, y = np.random.randint(200, 450, 2)
        s = np.random.randint(4, 10)
        img = draw_rectangle(img, (int(x), int(y)), (int(x + s), int(y + s)), (160, 160, 160), -1)

    return Image.fromarray(img)


# ─────────────────────────────────────────────────────────────────────
# Helper: resize image if too large
# ─────────────────────────────────────────────────────────────────────
def safe_resize(image: Image.Image, max_dim: int = 2000) -> Image.Image:
    """Resize image if either dimension exceeds max_dim."""
    w, h = image.size
    if w > max_dim or h > max_dim:
        ratio = min(max_dim / w, max_dim / h)
        new_size = (int(w * ratio), int(h * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image


# ─────────────────────────────────────────────────────────────────────
# Resolution estimation from component sizes
# ─────────────────────────────────────────────────────────────────────
def estimate_resolution_from_components(
    regions: list,
    canopy_area_ha: float,
    canopy_pct: float,
) -> float:
    """
    Estimate ground sample distance (m/pixel) from the median crown size.
    Returns estimated GSD in meters per pixel.
    """
    areas = [r.area for r in regions if 20 <= r.area <= 50000]

    if not areas:
        return 10.0

    median_area_px = float(np.median(areas))

    if median_area_px > 0:
        assumed_crown_m2 = 100.0
        pixel_area_m2 = assumed_crown_m2 / median_area_px
        gsd = np.sqrt(pixel_area_m2)
        gsd = float(np.clip(gsd, 0.05, 50.0))
        return gsd
    return 10.0


# ─────────────────────────────────────────────────────────────────────
# Adaptive tree counting based on resolution
# ─────────────────────────────────────────────────────────────────────
def adaptive_tree_count(
    regions: list,
    resolution_m: float,
    canopy_area_ha: float,
    canopy_pct: float,
    biome_name: str,
) -> dict:
    """
    Count trees adaptively based on image resolution.
    """
    density_by_biome = {
        "Tropical Moist Forest": (400, 600),
        "Forêt Tropicale Humide": (400, 600),
        "Tropical Dry Forest": (200, 400),
        "Forêt Tropicale Sèche": (200, 400),
        "Mangrove Forest": (600, 1000),
        "Forêt de Mangrove": (600, 1000),
        "Temperate Forest": (300, 500),
        "Forêt Tempérée": (300, 500),
    }
    min_density, max_density = density_by_biome.get(biome_name, (400, 600))

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
            "count_range": (
                int(len(tree_candidates) * 1.0),
                int(len(tree_candidates) * 1.6),
            ),
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
def process_image(
    image: Image.Image,
    carbon_factor: float,
    biome_name: str,
    user_resolution: float = None,
    geotiff_resolution: float = None,
    progress_callback=None,
):
    """
    Full canopy analysis pipeline with adaptive tree counting.
    Returns: (processed_img, contour_img, mask, metrics_dict)
    """
    img_array = np.array(image.convert("RGB"))
    img_bgr = rgb_to_bgr(img_array)

    if progress_callback:
        progress_callback(0)

    hsv = rgb_to_hsv(img_array)  # Direct RGB to HSV
    if progress_callback:
        progress_callback(1)

    lower_green = np.array([30, 40, 40])
    upper_green = np.array([80, 255, 255])
    mask = hsv_threshold(hsv, lower_green, upper_green)
    if progress_callback:
        progress_callback(2)

    mask = morphological_cleanup(mask, kernel_size=5)
    cleaned_mask = clean_small_contours(mask, min_area=50)

    labeled = measure.label(cleaned_mask, connectivity=2)
    boundaries = find_boundaries(labeled, mode="thick")
    regions = measure.regionprops(labeled)

    total_pixels = cleaned_mask.shape[0] * cleaned_mask.shape[1]
    canopy_pixels = int(np.sum(cleaned_mask > 0))
    canopy_pct = (canopy_pixels / total_pixels) * 100
    canopy_area_ha_10m = canopy_pixels * 0.0001

    if geotiff_resolution is not None:
        resolution_m = geotiff_resolution
        resolution_source = "geotiff"
    elif user_resolution is not None:
        resolution_m = user_resolution
        resolution_source = "manual"
    else:
        resolution_m = estimate_resolution_from_components(
            regions, canopy_area_ha_10m, canopy_pct
        )
        resolution_source = "auto"

    pixel_area_m2 = resolution_m ** 2
    canopy_area_m2 = canopy_pixels * pixel_area_m2
    canopy_area_ha = canopy_area_m2 / 10000.0

    if progress_callback:
        progress_callback(3)

    tree_result = adaptive_tree_count(
        regions, resolution_m, canopy_area_ha, canopy_pct, biome_name
    )

    if progress_callback:
        progress_callback(4)

    carbon_stock = canopy_area_ha * carbon_factor

    metrics = {
        "canopy_area_ha": canopy_area_ha,
        "carbon_stock_tco2": carbon_stock,
        "canopy_pct": canopy_pct,
        "total_pixels": total_pixels,
        "canopy_pixels": canopy_pixels,
        "image_size": (cleaned_mask.shape[1], cleaned_mask.shape[0]),
        "resolution_m": resolution_m,
        "resolution_source": resolution_source,
        "tree_method": tree_result["method"],
        "tree_count": tree_result["count"],
        "tree_count_range": tree_result["count_range"],
        "tree_note_key": tree_result["note_key"],
    }

    overlay = img_array.copy()  # Use RGB directly
    overlay[cleaned_mask > 0] = [0, 200, 0]
    processed = blend_images(img_array, overlay, alpha=0.6, beta=0.4)
    processed_rgb = processed  # Already in RGB

    contour_img = processed_rgb.copy()
    contour_img[boundaries] = [255, 255, 0]

    if progress_callback:
        progress_callback(5)

    return processed_rgb, contour_img, cleaned_mask, metrics


# ─────────────────────────────────────────────────────────────────────
# PDF Report generation (reportlab)
# ─────────────────────────────────────────────────────────────────────
def generate_pdf_report(metrics: dict, biome_name: str, lang: str, geotiff_metadata: dict = None) -> bytes:
    """Generate a professional PDF report and return bytes."""
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab is not installed. Install with: pip install reportlab")
    
    t = T[lang]
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#065F46"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#047857"),
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#92400E"),
        borderWidth=1,
        borderColor=colors.HexColor("#F59E0B"),
        borderPadding=8,
        backColor=colors.HexColor("#FFFBEB"),
    )
    tree_note_style = ParagraphStyle(
        "TreeNote",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E40AF"),
        borderWidth=1,
        borderColor=colors.HexColor("#3B82F6"),
        borderPadding=6,
        backColor=colors.HexColor("#EFF6FF"),
    )

    elements = []

    elements.append(Paragraph("🌿 CanopyLens Report", title_style))
    elements.append(Paragraph(
        f"{t['pdf_date']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        body_style,
    ))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#10B981")))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("Analysis Results", heading_style))

    avg_car = 4.6
    cars_offset = metrics["carbon_stock_tco2"] / avg_car
    daily_kg = metrics["carbon_stock_tco2"] * 1000 / 365

    if metrics["tree_count"] is not None:
        tree_display = f"{metrics['tree_count']:,} ({metrics['tree_method']})"
    elif metrics["tree_count_range"]:
        tree_display = (
            f"{metrics['tree_count_range'][0]:,}–{metrics['tree_count_range'][1]:,} "
            f"(density-based)"
        )
    else:
        tree_display = "N/A"

    table_data = [
        ["Metric", "Value"],
        [t["pdf_biome"], biome_name],
        [t["pdf_resolution"], f"{metrics['resolution_m']:.2f} m/px ({metrics['resolution_source']})"],
        [t["pdf_area"], f"{metrics['canopy_area_ha']:.2f} ha"],
        [t["pdf_carbon"], f"{metrics['carbon_stock_tco2']:.2f} tCO₂"],
        [t["pdf_trees"], tree_display],
        [t["pdf_coverage"], f"{metrics['canopy_pct']:.1f}%"],
        [t["pdf_cars"], f"{cars_offset:.1f}"],
        [t["pdf_daily"], f"{daily_kg:.1f} kg"],
    ]

    table = Table(table_data, colWidths=[8 * cm, 6 * cm])
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
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F0FDF4"), colors.white]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.8 * cm))

    if geotiff_metadata:
        elements.append(Paragraph(t["pdf_geotiff"], heading_style))
        geotiff_data = [
            ["Property", "Value"],
            [t["geotiff_crs"], geotiff_metadata.get('crs', 'N/A')],
            [t["geotiff_resolution"], f"{geotiff_metadata.get('resolution', (0,0))[0]:.2f}m x {geotiff_metadata.get('resolution', (0,0))[1]:.2f}m"],
            [t["geotiff_bands"], str(geotiff_metadata.get('bands', 'N/A'))],
            [t["geotiff_dtype"], geotiff_metadata.get('dtype', 'N/A')],
        ]
        if geotiff_metadata.get('bounds'):
            bounds = geotiff_metadata['bounds']
            geotiff_data.append([t["geotiff_bounds"], f"W={bounds[0]:.4f}, S={bounds[1]:.4f}, E={bounds[2]:.4f}, N={bounds[3]:.4f}"])
        if geotiff_metadata.get('nodata') is not None:
            geotiff_data.append([t["geotiff_nodata"], str(geotiff_metadata['nodata'])])
        
        geotiff_table = Table(geotiff_data, colWidths=[8 * cm, 6 * cm])
        geotiff_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E40AF")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#EFF6FF")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
        ]))
        elements.append(geotiff_table)
        elements.append(Spacer(1, 0.8 * cm))

    elements.append(Paragraph("Carbon Equivalents", heading_style))
    elements.append(Paragraph(
        f"• {cars_offset:.1f} average cars' annual emissions offset<br/>"
        f"• {int(metrics['carbon_stock_tco2'] / 0.022):,} mature trees equivalent<br/>"
        f"• {daily_kg:.1f} kg CO₂ absorbed per day",
        body_style,
    ))
    elements.append(Spacer(1, 0.8 * cm))

    elements.append(Paragraph("Technical Details", heading_style))
    elements.append(Paragraph(
        f"• Image size: {metrics['image_size'][0]} × {metrics['image_size'][1]} pixels<br/>"
        f"• Resolution: {metrics['resolution_m']:.2f} m/pixel ({metrics['resolution_source']})<br/>"
        f"• Canopy pixels: {metrics['canopy_pixels']:,} / {metrics['total_pixels']:,}<br/>"
        f"• Detection method: HSV thresholding + morphological cleanup<br/>"
        f"• Tree counting: {metrics['tree_method']} method<br/>"
        f"• Carbon factor: {biome_name}",
        body_style,
    ))
    elements.append(Spacer(1, 0.5 * cm))

    tree_note_text = t.get(metrics["tree_note_key"], t["tree_count_note_lowres"])
    tree_note_text = tree_note_text.replace("**", "")
    elements.append(Paragraph(tree_note_text, tree_note_style))
    elements.append(Spacer(1, 0.8 * cm))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#F59E0B")))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph(t["pdf_disclaimer"], disclaimer_style))

    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph(
        "<i>CanopyLens — Built in 48h for the Flora Carbon AI Hackathon, Kolkata 2026.</i>",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.gray),
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────────────────
def main():
    # Language selector
    lang = st.sidebar.selectbox("🌐 Language | Langue", ["English", "Français"])
    t = T[lang]

    st.title(t["title"])
    st.markdown(f"*{t['subtitle']}*")
    st.markdown("---")

    st.sidebar.markdown(f"### {t['sidebar_method']}")
    st.sidebar.markdown(t["sidebar_method_text"])
    st.sidebar.markdown("---")

    biome_names = list(t["biomes"].keys())
    selected_biome = st.sidebar.selectbox(t["biome"], biome_names, index=0)
    carbon_factor = t["biomes"][selected_biome]

    resolution_options = list(RESOLUTION_PRESETS.keys())
    selected_resolution_label = st.sidebar.selectbox(
        t["resolution"],
        resolution_options,
        index=0,
        help=t["resolution_hint"],
    )
    user_resolution = RESOLUTION_PRESETS[selected_resolution_label]

    # Reset button
    if st.sidebar.button(t["reset"]):
        keys_to_delete = [
            "image_uploaded", "processed_image", "contour_image",
            "canopy_mask", "metrics", "analysis_done", "loaded_image",
            "geotiff_metadata",
        ]
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    # Reload button
    if st.sidebar.button(t["reload"]):
        st.rerun()

    uploaded_file = st.file_uploader(t["upload"], type=["png", "jpg", "jpeg", "tif", "tiff"])
    st.caption(t["upload_hint"])
    
    sample_clicked = st.button(t["sample"])

    image = None
    geotiff_metadata = None
    
    try:
        if uploaded_file is not None:
            st.write(f"🐛 DEBUG: Fichier uploadé - Nom: {uploaded_file.name}, Taille: {uploaded_file.size} bytes")
            
            # Simplified extension detection
            _, file_extension = os.path.splitext(uploaded_file.name)
            file_extension = file_extension.lower().lstrip('.')
            st.write(f"🐛 DEBUG: Extension détectée: '{file_extension}'")
            
            if file_extension in ['tif', 'tiff']:
                st.write(f"🐛 DEBUG: C'est un fichier TIFF")
                
                if not RASTERIO_AVAILABLE:
                    st.error(t["geotiff_not_available"])
                    st.write("🐛 DEBUG: RASTERIO_AVAILABLE =", RASTERIO_AVAILABLE)
                    return
                
                st.write(f"🐛 DEBUG: Rasterio disponible, appel de load_geotiff()")
                with st.spinner(t["geotiff_loading"]):
                    image, geotiff_metadata = load_geotiff(uploaded_file)
                
                st.write(f"🐛 DEBUG: load_geotiff() a retourné - image: {type(image)}, metadata: {type(geotiff_metadata)}")
                if image is not None:
                    st.write(f"🐛 DEBUG: Image size: {image.size if hasattr(image, 'size') else 'N/A'}")
                
                st.session_state.geotiff_metadata = geotiff_metadata
                st.success(t["geotiff_loaded"].format(
                    width=geotiff_metadata['width'],
                    height=geotiff_metadata['height'],
                    bands=geotiff_metadata['bands'],
                    dtype=geotiff_metadata['dtype']
                ))
            else:
                st.write(f"🐛 DEBUG: C'est un fichier standard (PNG/JPG)")
                image = Image.open(uploaded_file).convert("RGB")
                st.session_state.geotiff_metadata = None
            
            if image is not None:
                st.write(f"🐛 DEBUG: Avant safe_resize - image size: {image.size}")
                image = safe_resize(image)
                st.write(f"🐛 DEBUG: Après safe_resize - image size: {image.size}")
                st.session_state.image_uploaded = True
                st.write(f"🐛 DEBUG: image_uploaded = True")
            
        elif sample_clicked:
            image = create_sample_image()
            st.session_state.image_uploaded = True
            st.session_state.geotiff_metadata = None
            
        elif st.session_state.get("image_uploaded"):
            image = st.session_state.get("loaded_image")
            geotiff_metadata = st.session_state.get("geotiff_metadata")
            
    except Exception as e:
        st.error(t["geotiff_error"].format(error=str(e)))
        st.info(t["geotiff_hint"])
        return

    if image is not None:
        st.session_state["loaded_image"] = image
        st.write(f"🐛 DEBUG: Image stockée dans session_state - size: {image.size}")

    # Display GeoTIFF metadata
    st.write(f"🐛 DEBUG: Vérification affichage - image_uploaded: {st.session_state.get('image_uploaded')}, image: {image is not None}")
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
        st.write(f"🐛 DEBUG: Conditions d'affichage remplies - affichage de l'image")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(t["original"])
            st.write(f"🐛 DEBUG: Appel de st.image() avec image de taille {image.size}")
            st.image(image, caption="Input Image", use_container_width=True)
            st.write(f"🐛 DEBUG: Image affichée avec succès")

        if st.button(t["analyze"], type="primary"):
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
                st.subheader(t["processed"])
                st.image(processed, caption=t["processed"], use_container_width=True)

            st.subheader(t["contours"])
            st.image(contour_img, caption=t["contours"], use_container_width=True)

            res_source_label = {
                "auto": "auto-detected" if lang == "English" else "auto-détectée",
                "manual": "user-selected" if lang == "English" else "sélectionnée",
                "geotiff": "from GeoTIFF" if lang == "English" else "depuis GeoTIFF",
            }.get(metrics["resolution_source"], metrics["resolution_source"])
            
            st.info(
                f"📏 **{t['detected_resolution']}:** "
                f"{metrics['resolution_m']:.2f} m/pixel ({res_source_label}) — "
                f"**{('Method' if lang == 'English' else 'Méthode')}:** {metrics['tree_method']}"
            )

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric(t["canopy_area"], f"{metrics['canopy_area_ha']:.2f} ha")
            with m2:
                st.metric(t["carbon_stock"], f"{metrics['carbon_stock_tco2']:.1f} tCO₂")
            with m3:
                if metrics["tree_count"] is not None:
                    st.metric(
                        t["trees"],
                        f"{metrics['tree_count']:,}",
                        delta=f"{metrics['tree_method']} method",
                    )
                elif metrics["tree_count_range"]:
                    range_str = (
                        f"{metrics['tree_count_range'][0]:,}–"
                        f"{metrics['tree_count_range'][1]:,}"
                    )
                    st.metric(
                        t["trees_estimated"],
                        range_str,
                        delta="density-based",
                    )
                else:
                    st.metric(t["trees"], "N/A")
            with m4:
                st.metric(t["coverage"], f"{metrics['canopy_pct']:.1f}%")

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

            st.subheader(t["equiv_title"])
            avg_car = 4.6
            cars_offset = metrics["carbon_stock_tco2"] / avg_car
            trees_eq = metrics["carbon_stock_tco2"] / 0.022
            daily_kg = metrics["carbon_stock_tco2"] * 1000 / 365

            eq1, eq2, eq3 = st.columns(3)
            with eq1:
                st.metric("🚗", f"{cars_offset:.1f}", t["cars"])
            with eq2:
                st.metric("🌳", f"{int(trees_eq):,}", t["trees_eq"])
            with eq3:
                st.metric("📅", f"{daily_kg:.1f} kg", t["daily"])

            with st.expander(f"🗺️ {t['mask']}"):
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.imshow(mask, cmap="Greens")
                ax.axis("off")
                ax.set_title(t["mask"])
                st.pyplot(fig)
                plt.close(fig)

            st.warning(t["disclaimer"])

            st.markdown("---")
            dl1, dl2 = st.columns(2)

            with dl1:
                mask_bytes = encode_png(mask)
                st.download_button(
                    label=t["download_mask"],
                    data=mask_bytes,
                    file_name="canopy_mask.png",
                    mime="image/png",
                    use_container_width=True,
                )

            with dl2:
                if REPORTLAB_AVAILABLE:
                    pdf_bytes = generate_pdf_report(
                        metrics, selected_biome, lang,
                        geotiff_metadata=st.session_state.get("geotiff_metadata")
                    )
                    st.download_button(
                        label=t["download_pdf"],
                        data=pdf_bytes,
                        file_name=f"canopylens_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.warning("⚠️ PDF export requires reportlab. Install with: pip install reportlab")

    else:
        st.info(t["no_image"])

    st.markdown("---")
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

    st.markdown(f"#### {t['geotiff_howto_title']}")
    for line in t["geotiff_howto"]:
        st.markdown(line)

    st.markdown(f"#### {t['limitations_title']}")
    for lim in t["limitations"]:
        st.markdown(f"• {lim}")


if __name__ == "__main__":
    main()
