// GeoTIFF loader for browser using geotiff.js
import { fromBlob } from 'geotiff';

export interface GeoTIFFMetadata {
  width: number;
  height: number;
  bands: number;
  resolution: [number, number];
  crs: string;
  bounds: [number, number, number, number] | null;
  nodata: number | null;
  dtype: string;
}

export interface GeoTIFFResult {
  image: HTMLImageElement;
  metadata: GeoTIFFMetadata;
}

/**
 * Load a GeoTIFF file from a Blob/File object
 * Handles RGB (3 bands), RGBA (4 bands), multispectral (13 bands), grayscale (1 band)
 * Normalizes uint16 data using percentile stretching
 */
export async function loadGeoTIFF(file: File): Promise<GeoTIFFResult> {
  console.log('🐛 DEBUG GeoTIFF: Starting loadGeoTIFF');
  console.log('🐛 DEBUG GeoTIFF: File name:', file.name);
  console.log('🐛 DEBUG GeoTIFF: File size:', file.size, 'bytes');

  try {
    // Parse the GeoTIFF
    const tiff = await fromBlob(file);
    console.log('🐛 DEBUG GeoTIFF: TIFF parsed successfully');

    const image = await tiff.getImage();
    console.log('🐛 DEBUG GeoTIFF: First image loaded');

    const width = image.getWidth();
    const height = image.getHeight();
    const numBands = image.getSamplesPerPixel();
    
    console.log('🐛 DEBUG GeoTIFF: Dimensions:', width, 'x', height);
    console.log('🐛 DEBUG GeoTIFF: Bands:', numBands);

    // Determine which bands to read
    let bandIndices: number[];
    if (numBands >= 4) {
      // Sentinel-2 multispectral: B4 (red), B3 (green), B2 (blue)
      bandIndices = [3, 2, 1];
      console.log('🐛 DEBUG GeoTIFF: Using Sentinel-2 bands B4, B3, B2');
    } else if (numBands === 3) {
      bandIndices = [0, 1, 2];
      console.log('🐛 DEBUG GeoTIFF: Using RGB bands');
    } else if (numBands === 1) {
      bandIndices = [0, 0, 0];
      console.log('🐛 DEBUG GeoTIFF: Using grayscale (duplicated)');
    } else {
      bandIndices = Array.from({ length: Math.min(3, numBands) }, (_, i) => i);
      console.log('🐛 DEBUG GeoTIFF: Using fallback bands:', bandIndices);
    }

    // Read RGB data using readRasters for better control
    console.log('🐛 DEBUG GeoTIFF: Reading raster data...');
    const rasters = await image.readRasters({
      samples: bandIndices,
      interleave: false, // Get separate arrays for each band
    });

    console.log('🐛 DEBUG GeoTIFF: Rasters read, count:', rasters.length);

    // rasters is an array of typed arrays, one per band
    const rBand = rasters[0];
    const gBand = rasters[1];
    const bBand = rasters[2];

    console.log('🐛 DEBUG GeoTIFF: Band R length:', rBand.length);
    console.log('🐛 DEBUG GeoTIFF: Band G length:', gBand.length);
    console.log('🐛 DEBUG GeoTIFF: Band B length:', bBand.length);

    const totalPixels = width * height;
    console.log('🐛 DEBUG GeoTIFF: Total pixels:', totalPixels);

    // Convert typed arrays to Float32Array for processing
    const rFloat = new Float32Array(rBand);
    const gFloat = new Float32Array(gBand);
    const bFloat = new Float32Array(bBand);

    console.log('🐛 DEBUG GeoTIFF: Bands extracted and converted');

    // Check if data is uint16 (Sentinel-2 typical range: 0-10000)
    const maxVal = Math.max(
      Array.from(rFloat).reduce((max, v) => Math.max(max, v), 0),
      Array.from(gFloat).reduce((max, v) => Math.max(max, v), 0),
      Array.from(bFloat).reduce((max, v) => Math.max(max, v), 0)
    );

    console.log('🐛 DEBUG GeoTIFF: Max value across all bands:', maxVal);

    let normalizedR: Uint8ClampedArray;
    let normalizedG: Uint8ClampedArray;
    let normalizedB: Uint8ClampedArray;

    if (maxVal > 255) {
      // uint16 data - apply percentile stretching
      console.log('🐛 DEBUG GeoTIFF: Applying percentile stretch (2-98%)');
      
      const sortedR = Array.from(rFloat).sort((a, b) => a - b);
      const sortedG = Array.from(gFloat).sort((a, b) => a - b);
      const sortedB = Array.from(bFloat).sort((a, b) => a - b);

      const p2R = sortedR[Math.floor(sortedR.length * 0.02)];
      const p98R = sortedR[Math.floor(sortedR.length * 0.98)];
      const p2G = sortedG[Math.floor(sortedG.length * 0.02)];
      const p98G = sortedG[Math.floor(sortedG.length * 0.98)];
      const p2B = sortedB[Math.floor(sortedB.length * 0.02)];
      const p98B = sortedB[Math.floor(sortedB.length * 0.98)];

      console.log('🐛 DEBUG GeoTIFF: Percentiles - R:', p2R, '-', p98R);
      console.log('🐛 DEBUG GeoTIFF: Percentiles - G:', p2G, '-', p98G);
      console.log('🐛 DEBUG GeoTIFF: Percentiles - B:', p2B, '-', p98B);

      normalizedR = normalizeBand(rFloat, p2R, p98R, totalPixels);
      normalizedG = normalizeBand(gFloat, p2G, p98G, totalPixels);
      normalizedB = normalizeBand(bFloat, p2B, p98B, totalPixels);
    } else {
      // uint8 data - use directly
      console.log('🐛 DEBUG GeoTIFF: Data is uint8, using directly');
      normalizedR = new Uint8ClampedArray(rFloat);
      normalizedG = new Uint8ClampedArray(gFloat);
      normalizedB = new Uint8ClampedArray(bFloat);
    }

    console.log('🐛 DEBUG GeoTIFF: Normalization complete');

    // Create canvas and draw the image
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d')!;

    // Create ImageData
    const imageData = ctx.createImageData(width, height);
    const pixels = imageData.data;

    // Fill the pixel data
    for (let i = 0; i < totalPixels; i++) {
      pixels[i * 4 + 0] = normalizedR[i]; // R
      pixels[i * 4 + 1] = normalizedG[i]; // G
      pixels[i * 4 + 2] = normalizedB[i]; // B
      pixels[i * 4 + 3] = 255;            // A (fully opaque)
    }

    ctx.putImageData(imageData, 0, 0);
    console.log('🐛 DEBUG GeoTIFF: Canvas created and drawn');

    // Convert to HTMLImageElement
    const dataUrl = canvas.toDataURL('image/png');
    const img = new Image();
    
    await new Promise<void>((resolve, reject) => {
      img.onload = () => resolve();
      img.onerror = reject;
      img.src = dataUrl;
    });

    console.log('🐛 DEBUG GeoTIFF: Image element created successfully');

    // Extract metadata
    const bbox = image.getBoundingBox();
    const metadata: GeoTIFFMetadata = {
      width,
      height,
      bands: numBands,
      resolution: [10, 10], // Default, could be extracted from GeoTIFF
      crs: 'EPSG:4326',
      bounds: bbox ? [bbox[0], bbox[1], bbox[2], bbox[3]] : null,
      nodata: image.getGDALNoData(),
      dtype: maxVal > 255 ? 'uint16' : 'uint8',
    };

    console.log('🐛 DEBUG GeoTIFF: Metadata extracted:', metadata);
    console.log('✅ GeoTIFF loaded successfully');

    return { image: img, metadata };
  } catch (error) {
    console.error('❌ Error loading GeoTIFF:', error);
    throw error;
  }
}

/**
 * Normalize a band using percentile stretching
 */
function normalizeBand(
  band: Float32Array,
  p2: number,
  p98: number,
  size: number
): Uint8ClampedArray {
  const normalized = new Uint8ClampedArray(size);
  
  if (p98 <= p2) {
    // Avoid division by zero
    const max = Math.max(...Array.from(band));
    for (let i = 0; i < size; i++) {
      normalized[i] = max > 0 ? Math.round((band[i] / max) * 255) : 0;
    }
  } else {
    // Apply linear stretch
    for (let i = 0; i < size; i++) {
      const value = band[i];
      const clamped = Math.max(p2, Math.min(p98, value));
      normalized[i] = Math.round(((clamped - p2) / (p98 - p2)) * 255);
    }
  }
  
  return normalized;
}
