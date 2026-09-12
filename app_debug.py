"""
CanopyLens — Version DEBUG avec logs
"""

import streamlit as st
import numpy as np
from PIL import Image
import os
import tempfile

st.set_page_config(page_title="CanopyLens DEBUG", page_icon="🐛", layout="wide")

st.title("🐛 CanopyLens - Mode Debug")

# Test 1: Vérifier les imports
st.header("1. Vérification des imports")
try:
    import rasterio
    st.success("✅ Rasterio importé avec succès")
    st.write(f"Version: {rasterio.__version__}")
except ImportError as e:
    st.error(f"❌ Erreur import rasterio: {e}")

try:
    import cv2
    st.success("✅ OpenCV importé avec succès")
except ImportError as e:
    st.error(f"❌ Erreur import cv2: {e}")

# Test 2: Upload de fichier
st.header("2. Upload de fichier")
uploaded_file = st.file_uploader("Upload un fichier TIFF", type=["tif", "tiff"])

if uploaded_file is not None:
    st.write(f"**Nom du fichier:** {uploaded_file.name}")
    st.write(f"**Taille:** {uploaded_file.size} bytes")
    st.write(f"**Type:** {uploaded_file.type}")
    
    # Test 3: Détection d'extension
    st.header("3. Détection d'extension")
    _, file_extension = os.path.splitext(uploaded_file.name)
    file_extension = file_extension.lower().lstrip('.')
    st.write(f"**Extension détectée:** '{file_extension}'")
    st.write(f"**Est un TIFF?** {file_extension in ['tif', 'tiff']}")
    
    # Test 4: Essayer de lire avec rasterio
    st.header("4. Lecture avec rasterio")
    try:
        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        
        st.write(f"**Fichier temporaire:** {tmp_path}")
        
        # Ouvrir avec rasterio
        with rasterio.open(tmp_path) as src:
            st.success("✅ Fichier ouvert avec rasterio")
            st.write(f"**Largeur:** {src.width}")
            st.write(f"**Hauteur:** {src.height}")
            st.write(f"**Nombre de bandes:** {src.count}")
            st.write(f"**Type de données:** {src.dtypes[0]}")
            st.write(f"**CRS:** {src.crs}")
            st.write(f"**Résolution:** {src.res}")
            st.write(f"**NoData:** {src.nodata}")
            st.write(f"**Bounds:** {src.bounds}")
            
            # Lire les bandes
            st.header("5. Lecture des bandes")
            num_bands = src.count
            
            if num_bands >= 4:
                band_indices = [3, 2, 1]  # B4, B3, B2
                st.write(f"**Bandes sélectionnées:** B4, B3, B2 (indices {band_indices})")
            elif num_bands == 3:
                band_indices = [0, 1, 2]
                st.write(f"**Bandes sélectionnées:** RGB (indices {band_indices})")
            elif num_bands == 1:
                band_indices = [0, 0, 0]
                st.write(f"**Bandes sélectionnées:** Grayscale dupliqué (indices {band_indices})")
            else:
                band_indices = list(range(min(3, num_bands)))
                st.write(f"**Bandes sélectionnées:** {band_indices}")
            
            # Lire et empiler
            bands = []
            for i, idx in enumerate(band_indices):
                band = src.read(idx + 1)  # rasterio is 1-indexed
                st.write(f"**Bande {i+1} (index {idx}):** shape={band.shape}, dtype={band.dtype}, min={band.min()}, max={band.max()}")
                
                # Gestion nodata
                if src.nodata is not None:
                    band = np.where(band == src.nodata, 0, band)
                
                bands.append(band)
            
            rgb = np.dstack(bands)
            st.write(f"**Image RGB empilée:** shape={rgb.shape}, dtype={rgb.dtype}")
            
            # Normalisation
            st.header("6. Normalisation")
            dtype = str(src.dtypes[0])
            st.write(f"**Type de données:** {dtype}")
            
            if 'uint16' in dtype:
                st.write("→ Application du stretch percentile 2-98%")
                p2, p98 = np.percentile(rgb, (2, 98))
                st.write(f"**Percentiles:** p2={p2}, p98={p98}")
                
                if p98 > p2:
                    rgb = np.clip(rgb, p2, p98)
                    rgb = ((rgb - p2) / (p98 - p2) * 255).astype(np.uint8)
                    st.write(f"**Après normalisation:** dtype={rgb.dtype}, min={rgb.min()}, max={rgb.max()}")
                else:
                    st.warning("⚠️ p98 <= p2, normalisation ignorée")
                    rgb = rgb.astype(np.uint8)
            elif 'float' in dtype:
                st.write("→ Conversion float32 → uint8")
                rgb = np.clip(rgb, 0, 1)
                rgb = (rgb * 255).astype(np.uint8)
                st.write(f"**Après conversion:** dtype={rgb.dtype}, min={rgb.min()}, max={rgb.max()}")
            else:
                st.write("→ Conversion directe en uint8")
                rgb = rgb.astype(np.uint8)
            
            # Créer l'image PIL
            st.header("7. Création de l'image PIL")
            try:
                image = Image.fromarray(rgb)
                st.success(f"✅ Image PIL créée: {image.size[0]}x{image.size[1]}")
                
                # Afficher l'image
                st.header("8. Affichage de l'image")
                st.image(image, caption="Image chargée depuis GeoTIFF", use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Erreur création image PIL: {e}")
                import traceback
                st.code(traceback.format_exc())
        
        # Nettoyer
        os.remove(tmp_path)
        st.success("✅ Fichier temporaire supprimé")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture: {e}")
        import traceback
        st.code(traceback.format_exc())

else:
    st.info("👆 Upload un fichier TIFF pour commencer le debug")
