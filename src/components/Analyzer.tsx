import { useState, useRef, useCallback } from 'react';
import { useLang } from '../context/LanguageContext';
import { analyzeCanopy, generateExplanation, AnalysisResult, AnalysisOptions } from '../utils/imageProcessing';
import { Upload, Settings, Download, AlertTriangle, TreePine, Droplets, Wind, Ruler, ImageIcon } from 'lucide-react';

export default function Analyzer() {
  const { t, lang } = useLang();
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [explanation, setExplanation] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [geoTIFFMetadata, setGeoTIFFMetadata] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Options
  const [biome, setBiome] = useState<AnalysisOptions['biome']>('tropical');
  const [gsdPreset, setGsdPreset] = useState<string>('auto');
  const [sensitivity, setSensitivity] = useState(50);

  // Resolution presets
  const resolutionPresets: Record<string, number | null> = {
    'auto': null,
    'geotiff': null, // Will be set from GeoTIFF metadata
    'sentinel2': 10,
    'planet': 3,
    'drone': 0.5,
    'drone-hd': 0.1,
    'landsat': 30,
  };
  const gsd = gsdPreset === 'geotiff' && geoTIFFMetadata 
    ? geoTIFFMetadata.resolution[0] 
    : resolutionPresets[gsdPreset];

  const handleFile = useCallback(async (file: File) => {
    console.log('🐛 DEBUG Analyzer: handleFile called');
    console.log('🐛 DEBUG Analyzer: File name:', file.name);
    console.log('🐛 DEBUG Analyzer: File type:', file.type);
    console.log('🐛 DEBUG Analyzer: File size:', file.size);

    // Check if it's a GeoTIFF
    const isTiff = file.name.toLowerCase().endsWith('.tif') || 
                   file.name.toLowerCase().endsWith('.tiff') ||
                   file.type === 'image/tiff';

    console.log('🐛 DEBUG Analyzer: Is TIFF?', isTiff);

    if (isTiff) {
      console.log('🐛 DEBUG Analyzer: Loading as GeoTIFF...');
      try {
        const { loadGeoTIFF } = await import('../utils/geotiffLoader');
        const result = await loadGeoTIFF(file);
        console.log('🐛 DEBUG Analyzer: GeoTIFF loaded successfully');
        console.log('🐛 DEBUG Analyzer: Image size:', result.image.width, 'x', result.image.height);
        
        setImage(result.image);
        setImageUrl(result.image.src);
        setResult(null);
        setExplanation('');
        
        // Store GeoTIFF metadata
        setGeoTIFFMetadata(result.metadata);
        
        // Auto-set resolution from GeoTIFF metadata
        if (result.metadata.resolution[0] > 0) {
          setGsdPreset('geotiff');
          console.log('🐛 DEBUG Analyzer: Auto-set GSD preset to geotiff, resolution:', result.metadata.resolution[0]);
        }
      } catch (error) {
        console.error('❌ Error loading GeoTIFF:', error);
        alert(`Error loading GeoTIFF: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    } else {
      // Standard image (PNG, JPG, etc.)
      console.log('🐛 DEBUG Analyzer: Loading as standard image...');
      if (!file.type.startsWith('image/')) {
        console.error('❌ Not an image file');
        return;
      }
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        console.log('🐛 DEBUG Analyzer: Standard image loaded');
        setImage(img);
        setImageUrl(url);
        setResult(null);
        setExplanation('');
        setGeoTIFFMetadata(null);
      };
      img.src = url;
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  // Generate a synthetic satellite-like forest image for demo
  const loadSampleImage = useCallback(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d')!;
    
    // Background: brown soil / urban mix
    ctx.fillStyle = '#8B7355';
    ctx.fillRect(0, 0, 512, 512);
    
    // Add some noise/texture to background
    for (let i = 0; i < 5000; i++) {
      const x = Math.random() * 512;
      const y = Math.random() * 512;
      const shade = 80 + Math.random() * 60;
      ctx.fillStyle = `rgb(${shade + 40}, ${shade + 20}, ${shade - 10})`;
      ctx.fillRect(x, y, 2, 2);
    }
    
    // Draw forest patches (green areas)
    const drawForestPatch = (cx: number, cy: number, radius: number, density: number) => {
      for (let i = 0; i < density; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = Math.random() * radius;
        const x = cx + Math.cos(angle) * r;
        const y = cy + Math.sin(angle) * r;
        const size = 3 + Math.random() * 8;
        
        // Vary green shades (like real canopy)
        const g = 80 + Math.random() * 100;
        const rb = 20 + Math.random() * 40;
        ctx.fillStyle = `rgb(${rb}, ${g}, ${rb - 10})`;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
      }
    };
    
    // Large forest area (top-left)
    drawForestPatch(150, 150, 120, 400);
    // Medium patch (center-right)
    drawForestPatch(380, 280, 80, 250);
    // Small patches scattered
    drawForestPatch(250, 400, 50, 150);
    drawForestPatch(100, 350, 40, 100);
    drawForestPatch(420, 120, 60, 180);
    
    // Add a river (blue line)
    ctx.strokeStyle = '#2563EB';
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.moveTo(0, 300);
    ctx.quadraticCurveTo(200, 280, 300, 350);
    ctx.quadraticCurveTo(400, 420, 512, 400);
    ctx.stroke();
    
    // Add some "roads" (gray lines)
    ctx.strokeStyle = '#6B7280';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(256, 0);
    ctx.lineTo(256, 512);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, 200);
    ctx.lineTo(512, 200);
    ctx.stroke();
    
    // Add a few "buildings" (small gray squares)
    for (let i = 0; i < 15; i++) {
      const x = 260 + Math.random() * 100;
      const y = 50 + Math.random() * 120;
      const size = 5 + Math.random() * 10;
      ctx.fillStyle = '#9CA3AF';
      ctx.fillRect(x, y, size, size);
    }
    
    canvas.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const img = new Image();
      img.onload = () => {
        setImage(img);
        setImageUrl(url);
        setResult(null);
        setExplanation('');
      };
      img.src = url;
    });
  }, []);

  const handleAnalyze = useCallback(() => {
    if (!image || !canvasRef.current) return;
    setIsAnalyzing(true);

    // Use setTimeout to allow UI to update
    setTimeout(() => {
      const canvas = canvasRef.current!;
      // Scale down large images for performance
      const maxDim = 800;
      const origW = image.width;
      const origH = image.height;
      let w = origW;
      let h = origH;
      let scale = 1;
      if (w > maxDim || h > maxDim) {
        scale = maxDim / Math.max(w, h);
        w = Math.round(w * scale);
        h = Math.round(h * scale);
      }
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(image, 0, 0, w, h);
      const imageData = ctx.getImageData(0, 0, w, h);

      // Adjust GSD for scaled image (each pixel now covers more ground)
      // If gsd is null (auto-detect), pass null to let the algorithm decide
      const adjustedGsd = gsd !== null ? gsd / scale : null;

      const analysisResult = analyzeCanopy(imageData, { biome, gsd: adjustedGsd, sensitivity });
      setResult(analysisResult);
      setExplanation(generateExplanation(analysisResult, biome, lang));
      setIsAnalyzing(false);
    }, 100);
  }, [image, biome, gsd, sensitivity, lang]);

  const downloadMask = () => {
    if (!result) return;
    const a = document.createElement('a');
    a.href = result.maskDataUrl;
    a.download = 'canopy-mask.png';
    a.click();
  };

  const downloadResults = () => {
    if (!result) return;
    const content = `${explanation}\n\n---\nTechnical Details:\n- Image: ${result.width}×${result.height} px\n- GSD: ${result.gsd} m/pixel\n- Canopy pixels: ${result.canopyPixels} / ${result.totalPixels}\n- Canopy %: ${result.canopyPercentage.toFixed(2)}%\n- Area: ${result.canopyAreaHa.toFixed(4)} ha\n- Carbon: ${result.carbonStockTCO2.toFixed(2)} tCO₂\n- Biome: ${biome}\n- Sensitivity: ${sensitivity}%`;
    const blob = new Blob([content], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'canopylens-results.txt';
    a.click();
  };

  return (
    <section id="analyzer" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-950">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl sm:text-4xl font-bold text-white text-center mb-4">
          {t.uploadTitle}
        </h2>
        <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
          {t.uploadHint}
        </p>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left: Upload & Options */}
          <div className="lg:col-span-1 space-y-6">
            {/* Upload Area */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative rounded-2xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-300 ${
                dragOver
                  ? 'border-emerald-400 bg-emerald-500/10 scale-[1.02]'
                  : imageUrl
                  ? 'border-emerald-600/50 bg-gray-900'
                  : 'border-gray-700 bg-gray-900/50 hover:border-emerald-500/50 hover:bg-gray-900'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,.tif,.tiff"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              />
              
              {imageUrl ? (
                <div className="space-y-3">
                  <img src={imageUrl} alt="Uploaded" className="w-full h-40 object-cover rounded-lg" />
                  <p className="text-sm text-emerald-400">✓ Image loaded — click to change</p>
                </div>
              ) : (
                <div className="space-y-3">
                  <Upload className="w-10 h-10 text-gray-500 mx-auto" />
                  <p className="text-gray-300 font-medium">{t.uploadDrop}</p>
                  <p className="text-xs text-gray-500">{t.uploadFormats}</p>
                </div>
              )}
              
              {/* Sample image button */}
              <button
                onClick={(e) => { e.stopPropagation(); loadSampleImage(); }}
                className="mt-3 flex items-center justify-center gap-2 w-full px-3 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-400 hover:bg-emerald-500/20 transition-all"
              >
                <ImageIcon className="w-4 h-4" />
                {lang === 'fr' ? '🌲 Essayer avec un exemple' : '🌲 Try with sample image'}
              </button>
            </div>

            {/* Options */}
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 space-y-5">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-300">
                <Settings className="w-4 h-4 text-emerald-400" />
                Parameters
              </div>

              {/* Biome */}
              <div>
                <label className="text-xs text-gray-400 mb-1.5 block">{t.biomeLabel}</label>
                <select
                  value={biome}
                  onChange={(e) => setBiome(e.target.value as AnalysisOptions['biome'])}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
                >
                  <option value="tropical">{t.biomeTropical} (150 tCO₂/ha)</option>
                  <option value="dry">{t.biomeDry} (80 tCO₂/ha)</option>
                  <option value="mangrove">{t.biomeMangrove} (200 tCO₂/ha)</option>
                  <option value="temperate">{t.biomeTemperate} (120 tCO₂/ha)</option>
                </select>
              </div>

              {/* Resolution Preset */}
              <div>
                <label className="text-xs text-gray-400 mb-1.5 block">{t.gsdLabel}</label>
                <select
                  value={gsdPreset}
                  onChange={(e) => setGsdPreset(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
                >
                  <option value="auto">{lang === 'fr' ? '🔍 Auto-détection' : '🔍 Auto-detect'}</option>
                  <option value="geotiff" disabled={!geoTIFFMetadata}>
                    {lang === 'fr' ? '🛰️ Depuis GeoTIFF' : '🛰️ From GeoTIFF'}
                    {!geoTIFFMetadata && (lang === 'fr' ? ' (non disponible)' : ' (not available)')}
                  </option>
                  <option value="sentinel2">Sentinel-2 (10 m/px)</option>
                  <option value="planet">Planet (3 m/px)</option>
                  <option value="drone">{lang === 'fr' ? 'Drone (0.5 m/px)' : 'Drone (0.5 m/px)'}</option>
                  <option value="drone-hd">{lang === 'fr' ? 'Drone HD (0.1 m/px)' : 'Drone HD (0.1 m/px)'}</option>
                  <option value="landsat">Landsat (30 m/px)</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">{t.gsdHint}</p>
              </div>

              {/* Sensitivity */}
              <div>
                <label className="text-xs text-gray-400 mb-1.5 block">{t.sensitivityLabel}</label>
                <input
                  type="range"
                  value={sensitivity}
                  onChange={(e) => setSensitivity(Number(e.target.value))}
                  min={0}
                  max={100}
                  className="w-full accent-emerald-500"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{t.sensitivityLow}</span>
                  <span>{sensitivity}%</span>
                  <span>{t.sensitivityHigh}</span>
                </div>
              </div>

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={!image || isAnalyzing}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-emerald-500/25 transition-all"
              >
                {isAnalyzing ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    {t.analyzing}
                  </span>
                ) : t.analyzeBtn}
              </button>
            </div>
          </div>

          {/* Right: Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Hidden canvas for processing */}
            <canvas ref={canvasRef} className="hidden" />

            {result ? (
              <>
                {/* Side by side images */}
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="bg-gray-900 rounded-2xl p-4 border border-gray-800">
                    <p className="text-xs text-gray-400 mb-2 font-medium">Original</p>
                    <img src={result.originalDataUrl} alt="Original" className="w-full rounded-lg" />
                  </div>
                  <div className="bg-gray-900 rounded-2xl p-4 border border-gray-800">
                    <p className="text-xs text-emerald-400 mb-2 font-medium">Canopy Mask</p>
                    <img src={result.maskDataUrl} alt="Mask" className="w-full rounded-lg" />
                  </div>
                </div>

                {/* Resolution & Method Badge */}
                <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl p-3">
                  <p className="text-sm text-blue-300">
                    📏 <strong>{lang === 'fr' ? 'Résolution' : 'Resolution'}:</strong> {result.resolutionM.toFixed(2)} m/px
                    ({result.resolutionSource === 'auto' ? (lang === 'fr' ? 'auto-détectée' : 'auto-detected') : (lang === 'fr' ? 'sélectionnée' : 'user-selected')}) — 
                    <strong> {lang === 'fr' ? 'Méthode' : 'Method'}:</strong> {result.treeMethod}
                  </p>
                </div>

                {/* GeoTIFF Metadata Display */}
                {geoTIFFMetadata && (
                  <div className="bg-purple-500/5 border border-purple-500/20 rounded-xl p-4">
                    <p className="text-sm font-semibold text-purple-300 mb-2">
                      🛰️ {lang === 'fr' ? 'Métadonnées GeoTIFF' : 'GeoTIFF Metadata'}
                    </p>
                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-300">
                      <div><strong>{lang === 'fr' ? 'Dimensions' : 'Dimensions'}:</strong> {geoTIFFMetadata.width} × {geoTIFFMetadata.height} px</div>
                      <div><strong>{lang === 'fr' ? 'Bandes' : 'Bands'}:</strong> {geoTIFFMetadata.bands}</div>
                      <div><strong>{lang === 'fr' ? 'Résolution' : 'Resolution'}:</strong> {geoTIFFMetadata.resolution[0].toFixed(2)} m/px</div>
                      <div><strong>{lang === 'fr' ? 'Type' : 'Type'}:</strong> {geoTIFFMetadata.dtype}</div>
                      {geoTIFFMetadata.bounds && (
                        <div className="col-span-2">
                          <strong>{lang === 'fr' ? 'Limites' : 'Bounds'}:</strong> [{geoTIFFMetadata.bounds.map((b: number) => b.toFixed(4)).join(', ')}]
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <MetricCard
                    icon={<TreePine className="w-5 h-5 text-emerald-400" />}
                    label={t.canopyArea}
                    value={result.canopyAreaHa.toFixed(2)}
                    unit={t.hectares}
                  />
                  <MetricCard
                    icon={<Wind className="w-5 h-5 text-blue-400" />}
                    label={t.carbonStock}
                    value={result.carbonStockTCO2.toFixed(1)}
                    unit={t.tonnesCO2}
                  />
                  <MetricCard
                    icon={<Droplets className="w-5 h-5 text-cyan-400" />}
                    label={result.treeCount !== null ? t.treeCount : (lang === 'fr' ? 'Arbres (estimé)' : 'Trees (estimated)')}
                    value={result.treeCount !== null ? result.treeCount.toLocaleString() : (result.treeCountRange ? `${result.treeCountRange[0].toLocaleString()}–${result.treeCountRange[1].toLocaleString()}` : 'N/A')}
                    unit={t.trees}
                  />
                  <MetricCard
                    icon={<Ruler className="w-5 h-5 text-purple-400" />}
                    label={t.coverage}
                    value={result.canopyPercentage.toFixed(1)}
                    unit={t.percent}
                  />
                </div>

                {/* Coverage Bar */}
                <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">{lang === 'fr' ? 'Couverture de Canopée' : 'Canopy Coverage'}</span>
                    <span className="text-sm font-bold text-emerald-400">{result.canopyPercentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full h-4 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 to-green-400 rounded-full transition-all duration-1000 ease-out"
                      style={{ width: `${Math.min(result.canopyPercentage, 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-2 text-xs text-gray-500">
                    <span>{lang === 'fr' ? 'Non-canopée' : 'Non-canopy'}</span>
                    <span>{lang === 'fr' ? 'Canopée détectée' : 'Detected canopy'}</span>
                  </div>
                </div>

                {/* Carbon Equivalents */}
                <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
                  <h3 className="text-sm font-medium text-gray-400 mb-3">
                    {lang === 'fr' ? '🌍 Équivalents Carbone' : '🌍 Carbon Equivalents'}
                  </h3>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-blue-400">{Math.round(result.carbonStockTCO2 / 4.6)}</p>
                      <p className="text-xs text-gray-500">{lang === 'fr' ? 'voitures/an' : 'cars/year'}</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-emerald-400">{Math.round(result.carbonStockTCO2 / 0.022)}</p>
                      <p className="text-xs text-gray-500">{lang === 'fr' ? 'arbres/an' : 'trees/year'}</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-amber-400">{(result.carbonStockTCO2 * 1000 / 365).toFixed(0)}</p>
                      <p className="text-xs text-gray-500">{lang === 'fr' ? 'kg CO₂/jour' : 'kg CO₂/day'}</p>
                    </div>
                  </div>
                </div>

                {/* Explanation */}
                <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
                  <h3 className="text-lg font-semibold text-white mb-3">{t.explanationTitle}</h3>
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">
                    {explanation}
                  </pre>
                </div>

                {/* Download buttons */}
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={downloadMask}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-sm text-gray-300 hover:border-emerald-500 hover:text-emerald-400 transition-all"
                  >
                    <Download className="w-4 h-4" />
                    {t.downloadMask}
                  </button>
                  <button
                    onClick={downloadResults}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-sm text-gray-300 hover:border-emerald-500 hover:text-emerald-400 transition-all"
                  >
                    <Download className="w-4 h-4" />
                    {t.downloadResults}
                  </button>
                </div>

                {/* Disclaimer */}
                <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
                  <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-amber-200/80">
                    {lang === 'fr'
                      ? 'Ceci est une estimation approximative basée sur le seuillage des pixels. La validation réelle nécessite des données de terrain ou LiDAR.'
                      : 'This is a rough estimate based on pixel thresholding. Real validation requires ground truth data or LiDAR.'}
                  </p>
                </div>
              </>
            ) : (
              /* Placeholder */
              <div className="flex items-center justify-center h-96 bg-gray-900/50 rounded-2xl border border-gray-800 border-dashed">
                <div className="text-center space-y-3">
                  <div className="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mx-auto">
                    <TreePine className="w-8 h-8 text-gray-600" />
                  </div>
                  <p className="text-gray-500 text-sm">
                    {lang === 'fr'
                      ? 'Téléchargez une image et cliquez sur Analyser pour voir les résultats'
                      : 'Upload an image and click Analyze to see results'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function MetricCard({ icon, label, value, unit }: { icon: React.ReactNode; label: string; value: string; unit: string }) {
  return (
    <div className="bg-gray-900 rounded-xl p-4 border border-gray-800 text-center">
      <div className="flex justify-center mb-2">{icon}</div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-xs text-gray-400">{unit}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}
