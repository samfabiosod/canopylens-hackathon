# 🌿 CanopyLens

**Seeing forests more clearly, one satellite image at a time.**

> *Flora Carbon AI Hackathon — Kolkata, September 2026*  
> *Built in 48 hours · Zero budget · 100% free & open*

---

## Overview

CanopyLens estimates forest canopy cover and carbon stock from satellite imagery. It comes in **two versions**:

| Version | Tech | Use Case |
|---------|------|----------|
| **Web Demo** (this repo) | React + TypeScript + Tailwind | Live browser demo, no install needed |
| **Python/Streamlit** | Python + Streamlit + ReportLab | Full-featured app with PDF export |

Both versions use the same core algorithm: HSV-based green channel segmentation → morphological cleanup → pixel counting → IPCC carbon factors.

---

## 🌐 Web Demo (React)

A fully functional browser-based version with real client-side image processing using the Canvas API.

### Run locally
```bash
npm install
npm run dev
```
Then open http://localhost:5173

### Deploy
```bash
npm run build
# Deploy the dist/ folder to Netlify, Vercel, or GitHub Pages
```

### Features
- ✅ Upload any RGB satellite/aerial image
- ✅ Real-time HSV-based canopy segmentation
- ✅ Carbon stock estimation (IPCC factors)
- ✅ Tree count estimation
- ✅ Visual canopy mask overlay
- ✅ Bilingual (English / Français)
- ✅ Zero dependencies on external APIs

---

## 🐍 Python/Streamlit Version

The full-featured version with PDF report generation and tree contour visualization.

### Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Deploy to Streamlit Cloud
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → select `app.py` → Deploy
4. Share the URL — done!

### Features
- ✅ Everything in the web demo, plus:
- ✅ **PDF reports** via ReportLab (professional formatting)
- ✅ **Tree contour visualization** (yellow boundaries on processed image)
- ✅ **Progress bar** during analysis
- ✅ **Error handling** for corrupted images
- ✅ **Auto-resize** for images > 2000×2000 px (memory safety)
- ✅ **Reset button** to start fresh
- ✅ **"How It Works" section** with pipeline visualization
- ✅ **Technical specifications** displayed in-app

---

## 🧮 Algorithm

```
RGB Image
    ↓
HSV Conversion
    ↓
Green Threshold (H: 30°–80°, S ≥ 40, V ≥ 40)
    ↓
Morphological Cleanup (close + open, 5×5 kernel)
    ↓
Boundary Extraction (skimage.find_boundaries)
    ↓
Pixel Count → Area (ha) → Carbon (tCO₂)
```

### Carbon Factors (IPCC AR6 WGIII)
| Biome | Factor |
|-------|--------|
| Tropical Moist Forest | 150 tCO₂/ha |
| Tropical Dry Forest | 80 tCO₂/ha |
| Mangrove | 200 tCO₂/ha |
| Temperate Forest | 120 tCO₂/ha |

---

## ⚠️ Limitations

- This is a **proxy estimate** based on RGB pixel thresholding
- Real validation requires **ground truth data** or **LiDAR**
- Cannot distinguish vegetation health (needs NIR band)
- Cloud cover causes underestimation
- Not certified for carbon credit validation (Verra, Gold Standard)

**We prefer a rough tool that admits its limits over a polished tool that invents figures.**

---

## 📁 Project Structure

```
canopylens/
├── app.py                    # Streamlit application (Python)
├── requirements.txt          # Python dependencies
├── pitch.md                  # 2-page hackathon documentation (FR+EN)
├── README.md                 # This file
│
├── src/                      # React web demo
│   ├── App.tsx
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── Hero.tsx
│   │   ├── Stats.tsx
│   │   ├── Analyzer.tsx      # Core analysis UI
│   │   ├── HowItWorks.tsx
│   │   ├── Documentation.tsx
│   │   └── Footer.tsx
│   ├── context/
│   │   └── LanguageContext.tsx
│   └── utils/
│       ├── imageProcessing.ts  # HSV segmentation (Canvas API)
│       └── translations.ts     # EN/FR translations
│
├── index.html
├── package.json
└── vite.config.js
```

---

## 🛠️ Tech Stack

### Web Demo
- React 18 + TypeScript
- Tailwind CSS 4
- Canvas API (image processing)
- Vite (build tool)

### Python/Streamlit
- Python 3.10+
- Streamlit (web interface)
- OpenCV (image processing)
- scikit-image (contour extraction)
- ReportLab (PDF generation)
- Matplotlib (visualization)

**Total cost: $0**

---

## 📄 License

Open source. Built for the Flora Carbon AI Hackathon, Kolkata 2026.

---

*Built with honesty, shipped with courage.* 🌱
