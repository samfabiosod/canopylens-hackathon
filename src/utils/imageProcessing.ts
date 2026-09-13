// CanopyLens - Real client-side image processing using Canvas API
// Implements HSV-based green channel segmentation for canopy detection
// v2.0 — Adaptive tree counting based on estimated resolution

export interface AnalysisResult {
  canopyPixels: number;
  totalPixels: number;
  canopyPercentage: number;
  canopyAreaHa: number;
  carbonStockTCO2: number;
  treeCount: number | null;
  treeCountRange: [number, number] | null;
  treeMethod: 'direct' | 'adjusted' | 'density';
  treeNoteKey: string;
  resolutionM: number;
  resolutionSource: 'auto' | 'manual';
  maskDataUrl: string;
  originalDataUrl: string;
  width: number;
  height: number;
  gsd: number; // ground sample distance in meters per pixel
}

export interface AnalysisOptions {
  biome: 'tropical' | 'dry' | 'mangrove' | 'temperate';
  gsd: number | null; // meters per pixel, null = auto-detect
  sensitivity: number; // 0-100, green threshold sensitivity
}

// Carbon stock factors (tCO₂/ha) from IPCC defaults
const CARBON_FACTORS: Record<string, number> = {
  tropical: 150,
  dry: 80,
  mangrove: 200,
  temperate: 120,
};

// Tree density factors (trees/ha) by biome
const TREE_DENSITY: Record<string, [number, number]> = {
  tropical: [400, 600],
  dry: [200, 400],
  mangrove: [600, 1000],
  temperate: [300, 500],
};

// Convert RGB to HSV
function rgbToHsv(r: number, g: number, b: number): [number, number, number] {
  r /= 255;
  g /= 255;
  b /= 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const d = max - min;
  let h = 0;
  const s = max === 0 ? 0 : d / max;
  const v = max;

  if (max !== min) {
    if (max === r) {
      h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    } else if (max === g) {
      h = ((b - r) / d + 2) / 6;
    } else {
      h = ((r - g) / d + 4) / 6;
    }
  }
  return [h * 360, s * 100, v * 100];
}

// Estimate resolution from component sizes
function estimateResolution(componentAreas: number[]): number {
  // Filter to crown-like components (20-50000 pixels)
  const crownAreas = componentAreas.filter(a => a >= 20 && a <= 50000);
  
  if (crownAreas.length === 0) return 10.0; // fallback to Sentinel-2
  
  // Sort and get median
  const sorted = [...crownAreas].sort((a, b) => a - b);
  const median = sorted[Math.floor(sorted.length / 2)];
  
  // Assume average crown area ~100 m² (tropical forest)
  // pixel_area_m2 = 100 / median
  // gsd = sqrt(pixel_area_m2)
  if (median > 0) {
    const assumedCrownM2 = 100.0;
    const pixelAreaM2 = assumedCrownM2 / median;
    const gsd = Math.sqrt(pixelAreaM2);
    return Math.max(0.05, Math.min(50.0, gsd));
  }
  return 10.0;
}

// Adaptive tree counting based on resolution
function adaptiveTreeCount(
  componentAreas: number[],
  resolutionM: number,
  canopyAreaHa: number,
  biome: string
): { count: number | null; range: [number, number] | null; method: 'direct' | 'adjusted' | 'density'; noteKey: string } {
  const [minDensity, maxDensity] = TREE_DENSITY[biome] || [400, 600];
  
  if (resolutionM < 2.0) {
    // HIGH RESOLUTION: direct individual tree counting
    const minCrownPx = Math.max(5, Math.floor(1.0 / (resolutionM ** 2)));
    const maxCrownPx = Math.floor(200.0 / (resolutionM ** 2));
    const candidates = componentAreas.filter(a => a >= minCrownPx && a <= maxCrownPx);
    return {
      count: candidates.length,
      range: null,
      method: 'direct',
      noteKey: 'tree_count_note_highres',
    };
  } else if (resolutionM <= 5.0) {
    // MEDIUM RESOLUTION: adjusted crown detection
    const minCrownPx = Math.max(10, Math.floor(10.0 / (resolutionM ** 2)));
    const maxCrownPx = Math.floor(300.0 / (resolutionM ** 2));
    const candidates = componentAreas.filter(a => a >= minCrownPx && a <= maxCrownPx);
    const correction = 1.3; // ~30% undercount correction
    const estimated = Math.round(candidates.length * correction);
    return {
      count: estimated,
      range: [Math.round(candidates.length * 1.0), Math.round(candidates.length * 1.6)],
      method: 'adjusted',
      noteKey: 'tree_count_note_medres',
    };
  } else {
    // LOW RESOLUTION: density-based estimation
    const estMin = Math.round(canopyAreaHa * minDensity);
    const estMax = Math.round(canopyAreaHa * maxDensity);
    return {
      count: null,
      range: [estMin, estMax],
      method: 'density',
      noteKey: 'tree_count_note_lowres',
    };
  }
}

// Main canopy segmentation function
export function analyzeCanopy(
  imageData: ImageData,
  options: AnalysisOptions
): AnalysisResult {
  const { width, height } = imageData;
  const data = imageData.data;
  const totalPixels = width * height;
  
  // Create mask canvas
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = width;
  maskCanvas.height = height;
  const maskCtx = maskCanvas.getContext('2d')!;
  const maskImageData = maskCtx.createImageData(width, height);
  const maskData = maskImageData.data;

  // WIDER HSV threshold for better GeoTIFF compatibility (matches Python v5.0)
  // Base thresholds: Hue 25-90°, Saturation ≥ 30, Value ≥ 30
  // Sensitivity adjusts these ranges
  const hueMin = 25 - (options.sensitivity * 0.05); // Wider range for GeoTIFF
  const hueMax = 90 + (options.sensitivity * 0.1);
  const satMin = 30 - (options.sensitivity * 0.1);
  const valMin = 30 - (options.sensitivity * 0.1);

  let canopyPixels = 0;
  const canopyMask = new Array(totalPixels).fill(false);

  // First pass: classify pixels
  for (let i = 0; i < totalPixels; i++) {
    const r = data[i * 4];
    const g = data[i * 4 + 1];
    const b = data[i * 4 + 2];

    const [h, s, v] = rgbToHsv(r, g, b);
    const isCanopy = h >= hueMin && h <= hueMax && s >= satMin && v >= valMin;

    if (isCanopy) {
      canopyPixels++;
      canopyMask[i] = true;
    }
  }

  // If no green detected, try with wider threshold (fallback for GeoTIFF)
  if (canopyPixels === 0) {
    const widerHueMin = 20;
    const widerHueMax = 100;
    const widerSatMin = 20;
    const widerValMin = 20;
    
    for (let i = 0; i < totalPixels; i++) {
      const r = data[i * 4];
      const g = data[i * 4 + 1];
      const b = data[i * 4 + 2];

      const [h, s, v] = rgbToHsv(r, g, b);
      const isCanopy = h >= widerHueMin && h <= widerHueMax && s >= widerSatMin && v >= widerValMin;

      if (isCanopy) {
        canopyPixels++;
        canopyMask[i] = true;
      }
    }
  }

  // Morphological cleanup - remove small noise
  const cleaned = new Array(totalPixels).fill(false);
  const kernelSize = 3;
  const halfKernel = Math.floor(kernelSize / 2);

  for (let y = halfKernel; y < height - halfKernel; y++) {
    for (let x = halfKernel; x < width - halfKernel; x++) {
      const idx = y * width + x;
      if (!canopyMask[idx]) continue;
      
      let neighbors = 0;
      for (let dy = -halfKernel; dy <= halfKernel; dy++) {
        for (let dx = -halfKernel; dx <= halfKernel; dx++) {
          if (canopyMask[(y + dy) * width + (x + dx)]) {
            neighbors++;
          }
        }
      }
      if (neighbors >= 4) {
        cleaned[idx] = true;
      }
    }
  }

  // Recount after cleanup
  canopyPixels = 0;
  for (let i = 0; i < totalPixels; i++) {
    if (cleaned[i]) {
      canopyPixels++;
      maskData[i * 4] = 34;
      maskData[i * 4 + 1] = 197;
      maskData[i * 4 + 2] = 94;
      maskData[i * 4 + 3] = 200;
    } else {
      maskData[i * 4] = 30;
      maskData[i * 4 + 1] = 30;
      maskData[i * 4 + 2] = 30;
      maskData[i * 4 + 3] = 100;
    }
  }

  // Estimate resolution and count trees adaptively
  const componentAreas = findComponentAreas(cleaned, width, height);
  
  let resolutionM: number;
  let resolutionSource: 'auto' | 'manual';
  
  if (options.gsd !== null) {
    resolutionM = options.gsd;
    resolutionSource = 'manual';
  } else {
    resolutionM = estimateResolution(componentAreas);
    resolutionSource = 'auto';
  }

  // Calculate area with actual resolution
  const pixelAreaM2 = resolutionM * resolutionM;
  const canopyAreaM2 = canopyPixels * pixelAreaM2;
  const canopyAreaHa = canopyAreaM2 / 10000;
  const canopyPercentage = (canopyPixels / totalPixels) * 100;
  const carbonStockTCO2 = canopyAreaHa * CARBON_FACTORS[options.biome];

  // Adaptive tree counting
  const treeResult = adaptiveTreeCount(componentAreas, resolutionM, canopyAreaHa, options.biome);

  // Generate mask data URL
  maskCtx.putImageData(maskImageData, 0, 0);
  const maskDataUrl = maskCanvas.toDataURL('image/png');

  // Generate original data URL
  const origCanvas = document.createElement('canvas');
  origCanvas.width = width;
  origCanvas.height = height;
  const origCtx = origCanvas.getContext('2d')!;
  origCtx.putImageData(imageData, 0, 0);
  const originalDataUrl = origCanvas.toDataURL('image/png');

  return {
    canopyPixels,
    totalPixels,
    canopyPercentage,
    canopyAreaHa,
    carbonStockTCO2,
    treeCount: treeResult.count,
    treeCountRange: treeResult.range,
    treeMethod: treeResult.method,
    treeNoteKey: treeResult.noteKey,
    resolutionM,
    resolutionSource,
    maskDataUrl,
    originalDataUrl,
    width,
    height,
    gsd: resolutionM,
  };
}

// Find connected component areas (simplified BFS)
function findComponentAreas(mask: boolean[], width: number, height: number): number[] {
  const visited = new Array(mask.length).fill(false);
  const areas: number[] = [];
  
  // Sample for performance
  const step = Math.max(1, Math.floor(Math.sqrt(width * height / 30000)));
  
  for (let y = 0; y < height; y += step) {
    for (let x = 0; x < width; x += step) {
      const idx = y * width + x;
      if (!mask[idx] || visited[idx]) continue;

      // BFS
      const queue: number[] = [idx];
      visited[idx] = true;
      let size = 0;

      while (queue.length > 0 && size < 50000) {
        const current = queue.shift()!;
        size++;
        const cx = current % width;
        const cy = Math.floor(current / width);

        const neighbors = [
          [cx - 1, cy], [cx + 1, cy],
          [cx, cy - 1], [cx, cy + 1],
        ];

        for (const [nx, ny] of neighbors) {
          if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
            const nIdx = ny * width + nx;
            if (mask[nIdx] && !visited[nIdx]) {
              visited[nIdx] = true;
              queue.push(nIdx);
            }
          }
        }
      }

      if (size >= 20) {
        areas.push(size);
      }
    }
  }

  return areas;
}

// Generate plain-language explanation
export function generateExplanation(
  result: AnalysisResult,
  biome: string,
  lang: 'en' | 'fr'
): string {
  const carsOffset = Math.round(result.carbonStockTCO2 / 4.6);
  const treesEquivalent = Math.round(result.carbonStockTCO2 / 0.022);

  // Tree count display
  let treeDisplay: string;
  if (result.treeCount !== null) {
    treeDisplay = `${result.treeCount.toLocaleString()} (${result.treeMethod} method)`;
  } else if (result.treeCountRange) {
    treeDisplay = `${result.treeCountRange[0].toLocaleString()}–${result.treeCountRange[1].toLocaleString()} (density-based)`;
  } else {
    treeDisplay = 'N/A';
  }

  // Resolution note
  const resNote = lang === 'fr'
    ? `📏 Résolution : ${result.resolutionM.toFixed(2)} m/pixel (${result.resolutionSource === 'auto' ? 'auto-détectée' : 'sélectionnée'})`
    : `📏 Resolution: ${result.resolutionM.toFixed(2)} m/pixel (${result.resolutionSource === 'auto' ? 'auto-detected' : 'user-selected'})`;

  // Tree counting note
  let treeNote: string;
  if (lang === 'fr') {
    if (result.treeMethod === 'direct') {
      treeNote = '📝 Détection haute résolution (<2m/px) : couronnes individuelles détectées directement.';
    } else if (result.treeMethod === 'adjusted') {
      treeNote = '📝 Détection résolution moyenne (2–5m/px) : détection ajustée avec facteur de correction.';
    } else {
      treeNote = '📝 Estimation basse résolution (>5m/px) : estimation par densité (IPCC/FAO).';
    }
  } else {
    if (result.treeMethod === 'direct') {
      treeNote = '📝 High-resolution detection (<2m/px): individual crowns detected directly.';
    } else if (result.treeMethod === 'adjusted') {
      treeNote = '📝 Medium-resolution detection (2–5m/px): adjusted detection with correction factor.';
    } else {
      treeNote = '📝 Low-resolution estimation (>5m/px): density-based estimation (IPCC/FAO).';
    }
  }

  if (lang === 'fr') {
    return `📊 Résultats de l'analyse CanopyLens :

${resNote}

Sur cette image satellite, nous avons détecté une couverture de canopée de ${result.canopyPercentage.toFixed(1)}%.

🌳 Surface de canopée estimée : ${result.canopyAreaHa.toFixed(2)} hectare(s)
💨 Stock de carbone estimé : ${result.carbonStockTCO2.toFixed(1)} tonnes de CO₂
🌲 Arbres : ${treeDisplay}

${treeNote}

🚗 Équivalent : cela pourrait compenser les émissions d'environ ${carsOffset} voitures pendant un an.
🌱 Ou l'équivalent du carbone absorbé par ${treesEquivalent} arbres matures en un an.

⚠️ Note importante : Ceci est une estimation approximative basée sur le seuillage des pixels verts. La validation réelle nécessite des données de terrain ou LiDAR. Notre outil est transparent sur ses limites.`;
  }

  return `📊 CanopyLens Analysis Results:

${resNote}

On this satellite image, we detected ${result.canopyPercentage.toFixed(1)}% canopy coverage.

🌳 Estimated canopy area: ${result.canopyAreaHa.toFixed(2)} hectare(s)
💨 Estimated carbon stock: ${result.carbonStockTCO2.toFixed(1)} tonnes of CO₂
🌲 Trees: ${treeDisplay}

${treeNote}

🚗 Equivalent: this could offset the emissions of about ${carsOffset} average cars for one year.
🌱 Or the carbon absorbed by ${treesEquivalent} mature trees in one year.

⚠️ Important note: This is a rough estimate based on green pixel thresholding. Real validation requires ground truth data or LiDAR. Our tool is transparent about its limitations.`;
}

export { CARBON_FACTORS, TREE_DENSITY };
