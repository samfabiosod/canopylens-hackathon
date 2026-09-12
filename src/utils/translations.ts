export type Lang = 'en' | 'fr';

export const translations = {
  en: {
    // Header
    appName: 'CanopyLens',
    tagline: 'Seeing forests more clearly, one satellite image at a time',
    navTool: 'Analyze',
    navHow: 'How It Works',
    navDocs: 'Documentation',
    
    // Hero
    heroTitle: 'Estimate Forest Carbon from Space',
    heroSubtitle: 'Upload any satellite or aerial image. Get instant canopy cover analysis and carbon stock estimates. Free, open, and honest about its limits.',
    heroCta: 'Try the Analyzer',
    heroOpenSource: '100% Free & Open Source',
    heroNoApi: 'No API Keys Required',
    heroBrowser: 'Runs in Your Browser',
    
    // Analyzer
    uploadTitle: 'Upload Satellite Image',
    uploadDrop: 'Drag & drop an image here, or click to browse',
    uploadFormats: 'Supports: JPG, PNG, TIFF (RGB satellite/aerial imagery)',
    uploadHint: 'For best results, use Sentinel-2 or similar 10m resolution imagery',
    analyzeBtn: '🔍 Analyze Canopy',
    analyzing: 'Processing...',
    
    // Options
    biomeLabel: 'Biome Type',
    biomeTropical: 'Tropical Moist Forest',
    biomeDry: 'Tropical Dry Forest',
    biomeMangrove: 'Mangrove Forest',
    biomeTemperate: 'Temperate Forest',
    gsdLabel: 'Resolution (m/pixel)',
    gsdHint: 'Sentinel-2 = 10m, Planet = 3m, Drone = 0.1m',
    sensitivityLabel: 'Detection Sensitivity',
    sensitivityLow: 'Conservative',
    sensitivityHigh: 'Aggressive',
    
    // Results
    resultsTitle: 'Analysis Results',
    canopyArea: 'Canopy Area',
    carbonStock: 'Carbon Stock',
    treeCount: 'Estimated Trees',
    coverage: 'Coverage',
    hectares: 'hectares',
    tonnesCO2: 'tCO₂',
    percent: '%',
    trees: 'trees',
    
    // Explanation
    explanationTitle: 'Plain-Language Explanation',
    downloadMask: 'Download Mask',
    downloadResults: 'Download Results',
    
    // How it works
    howTitle: 'How CanopyLens Works',
    howSubtitle: 'Simple computer vision, transparent assumptions, honest limitations.',
    step1Title: '1. You Upload an Image',
    step1Desc: 'Any RGB satellite or aerial image works. We assume 10m/pixel (Sentinel-2) by default, but you can adjust.',
    step2Title: '2. Green Channel Segmentation',
    step2Desc: 'We convert the image to HSV color space and isolate pixels in the green hue range (60°–160°) with sufficient saturation. This separates vegetation from soil, water, and buildings.',
    step3Title: '3. Morphological Cleanup',
    step3Desc: 'We remove noise (isolated pixels) using a simple neighbor-counting filter. This eliminates false positives from green roofs, parks, or sensor noise.',
    step4Title: '4. Area & Carbon Calculation',
    step4Desc: 'We count canopy pixels, multiply by pixel area (GSD²), convert to hectares, then apply IPCC carbon stock factors (e.g., 150 tCO₂/ha for tropical forest).',
    step5Title: '5. Honest Output',
    step5Desc: 'We show you the mask, the numbers, and a plain-language explanation. We also tell you what we can\'t know without ground truth data.',
    
    // Limitations
    limitationsTitle: 'What We\'re Honest About',
    lim1: 'No ground truth validation — our estimates are proxies, not measurements.',
    lim2: 'Assumes uniform forest — mixed land use will reduce accuracy.',
    lim3: 'RGB only — we can\'t distinguish healthy vs. stressed vegetation (needs NIR band).',
    lim4: 'Cloud cover will cause underestimation — we don\'t have cloud masking yet.',
    lim5: 'Carbon factors are IPCC defaults — local calibration would improve accuracy.',
    
    // Documentation
    docsTitle: 'Project Documentation',
    docsSubtitle: 'A weekend hackathon project built by one person, with zero budget.',
    docsProblemTitle: '🌍 The Problem',
    docsProblem: 'Forest carbon accounting is critical for climate action, but traditional methods (field surveys, LiDAR) are expensive and slow. Satellite-based estimation could democratize access — but most tools require expensive software, cloud computing, or expert knowledge.',
    docsApproachTitle: '🔬 Our Approach',
    docsApproach: 'CanopyLens uses basic computer vision (HSV color thresholding + morphological operations) to estimate canopy cover from any RGB satellite image. We pair this with IPCC default carbon stock factors to estimate stored carbon. The entire pipeline runs in your browser — no server, no API keys, no cost.',
    docsWhyTitle: '✅ Why It Works',
    docsWhy: '• Usable by anyone: upload image → click → see results\n• Reproducible: all code is open, all assumptions are stated\n• Honest: we show uncertainty, not false precision\n• Free: runs entirely in the browser, zero infrastructure cost\n• Educational: demonstrates the core concepts of remote sensing for carbon',
    docsTechTitle: '🛠️ Technical Stack',
    docsTech: '• Frontend: React + TypeScript + Tailwind CSS\n• Image Processing: Canvas API (HSV conversion, thresholding, morphology)\n• Carbon Estimation: IPCC default factors (AR6 WGIII)\n• Hosting: Static site (GitHub Pages / Netlify free tier)\n• Total cost: $0',
    docsDeployTitle: '🚀 Deploy in 5 Minutes',
    docsDeploy: '1. Clone the repository\n2. npm install\n3. npm run build\n4. Deploy the dist/ folder to any static host (Netlify, Vercel, GitHub Pages)\n5. Share the URL — done!',
    docsRunTitle: '💻 Run Locally',
    docsRun: 'npm run dev\n\nThen open http://localhost:5173 in your browser.',
    
    // Footer
    footerBuilt: 'Built in 48 hours for the Flora Carbon AI hackathon',
    footerKolkata: 'Kolkata, September 2026',
    footerDisclaimer: 'This tool provides estimates, not measurements. For carbon credit validation, use certified methodologies (Verra, Gold Standard).',
  },
  fr: {
    // Header
    appName: 'CanopyLens',
    tagline: 'Voir les forêts plus clairement, une image satellite à la fois',
    navTool: 'Analyser',
    navHow: 'Fonctionnement',
    navDocs: 'Documentation',
    
    // Hero
    heroTitle: 'Estimer le Carbone Forestier depuis l\'Espace',
    heroSubtitle: 'Téléchargez n\'importe quelle image satellite ou aérienne. Obtenez instantanément une analyse de couverture de canopée et une estimation du stock de carbone. Gratuit, ouvert, et honnête sur ses limites.',
    heroCta: 'Essayer l\'Analyseur',
    heroOpenSource: '100% Gratuit & Open Source',
    heroNoApi: 'Aucune Clé API Requise',
    heroBrowser: 'Fonctionne dans Votre Navigateur',
    
    // Analyzer
    uploadTitle: 'Télécharger une Image Satellite',
    uploadDrop: 'Glissez-déposez une image ici, ou cliquez pour parcourir',
    uploadFormats: 'Supporte : JPG, PNG, TIFF (imagerie satellite/aérienne RGB)',
    uploadHint: 'Pour de meilleurs résultats, utilisez une imagerie Sentinel-2 ou similaire (résolution 10m)',
    analyzeBtn: '🔍 Analyser la Canopée',
    analyzing: 'Traitement en cours...',
    
    // Options
    biomeLabel: 'Type de Biome',
    biomeTropical: 'Forêt Tropicale Humide',
    biomeDry: 'Forêt Tropicale Sèche',
    biomeMangrove: 'Forêt de Mangrove',
    biomeTemperate: 'Forêt Tempérée',
    gsdLabel: 'Résolution (m/pixel)',
    gsdHint: 'Sentinel-2 = 10m, Planet = 3m, Drone = 0.1m',
    sensitivityLabel: 'Sensibilité de Détection',
    sensitivityLow: 'Conservatrice',
    sensitivityHigh: 'Agressive',
    
    // Results
    resultsTitle: 'Résultats de l\'Analyse',
    canopyArea: 'Surface de Canopée',
    carbonStock: 'Stock de Carbone',
    treeCount: 'Arbres Estimés',
    coverage: 'Couverture',
    hectares: 'hectares',
    tonnesCO2: 'tCO₂',
    percent: '%',
    trees: 'arbres',
    
    // Explanation
    explanationTitle: 'Explication en Langage Clair',
    downloadMask: 'Télécharger le Masque',
    downloadResults: 'Télécharger les Résultats',
    
    // How it works
    howTitle: 'Comment Fonctionne CanopyLens',
    howSubtitle: 'Vision par ordinateur simple, hypothèses transparentes, limites honnêtes.',
    step1Title: '1. Vous Téléchargez une Image',
    step1Desc: 'N\'importe quelle image satellite ou aérienne RGB fonctionne. Nous supposons 10m/pixel (Sentinel-2) par défaut, mais vous pouvez ajuster.',
    step2Title: '2. Segmentation du Canal Vert',
    step2Desc: 'Nous convertissons l\'image en espace colorimétrique HSV et isolons les pixels dans la plage de teinte verte (60°–160°) avec une saturation suffisante. Cela sépare la végétation du sol, de l\'eau et des bâtiments.',
    step3Title: '3. Nettoyage Morphologique',
    step3Desc: 'Nous supprimons le bruit (pixels isolés) à l\'aide d\'un filtre simple de comptage de voisins. Cela élimine les faux positifs provenant de toits verts, de parcs ou de bruit de capteur.',
    step4Title: '4. Calcul de Surface & Carbone',
    step4Desc: 'Nous comptons les pixels de canopée, multiplions par la surface du pixel (GSD²), convertissons en hectares, puis appliquons les facteurs de stock de carbone du GIEC (ex: 150 tCO₂/ha pour la forêt tropicale).',
    step5Title: '5. Résultat Honnête',
    step5Desc: 'Nous vous montrons le masque, les chiffres, et une explication en langage clair. Nous vous disons aussi ce que nous ne pouvons pas savoir sans données de terrain.',
    
    // Limitations
    limitationsTitle: 'Ce Dont Nous Sommes Honnêtes',
    lim1: 'Pas de validation par vérité terrain — nos estimations sont des proxys, pas des mesures.',
    lim2: 'Suppose une forêt uniforme — l\'utilisation mixte des terres réduira la précision.',
    lim3: 'RGB uniquement — nous ne pouvons pas distinguer la végétation saine de la végétation stressée (nécessite la bande NIR).',
    lim4: 'La couverture nuageuse causera une sous-estimation — nous n\'avons pas encore de masquage des nuages.',
    lim5: 'Les facteurs de carbone sont les valeurs par défaut du GIEC — une calibration locale améliorerait la précision.',
    
    // Documentation
    docsTitle: 'Documentation du Projet',
    docsSubtitle: 'Un projet de hackathon de week-end construit par une seule personne, avec zéro budget.',
    docsProblemTitle: '🌍 Le Problème',
    docsProblem: 'La comptabilité du carbone forestier est essentielle pour l\'action climatique, mais les méthodes traditionnelles (enquêtes de terrain, LiDAR) sont coûteuses et lentes. L\'estimation par satellite pourrait démocratiser l\'accès — mais la plupart des outils nécessitent des logiciels coûteux, du cloud computing ou des connaissances expertes.',
    docsApproachTitle: '🔬 Notre Approche',
    docsApproach: 'CanopyLens utilise la vision par ordinateur de base (seuillage de couleur HSV + opérations morphologiques) pour estimer la couverture de canopée à partir de n\'importe quelle image satellite RGB. Nous associons cela aux facteurs de stock de carbone par défaut du GIEC pour estimer le carbone stocké. Tout le pipeline fonctionne dans votre navigateur — pas de serveur, pas de clés API, pas de coût.',
    docsWhyTitle: '✅ Pourquoi Ça Marche',
    docsWhy: '• Utilisable par tous : télécharger une image → cliquer → voir les résultats\n• Reproductible : tout le code est ouvert, toutes les hypothèses sont énoncées\n• Honnête : nous montrons l\'incertitude, pas une fausse précision\n• Gratuit : fonctionne entièrement dans le navigateur, coût d\'infrastructure zéro\n• Éducatif : démontre les concepts de base de la télédétection pour le carbone',
    docsTechTitle: '🛠️ Stack Technique',
    docsTech: '• Frontend : React + TypeScript + Tailwind CSS\n• Traitement d\'image : Canvas API (conversion HSV, seuillage, morphologie)\n• Estimation carbone : Facteurs par défaut du GIEC (AR6 WGIII)\n• Hébergement : Site statique (GitHub Pages / Netlify gratuit)\n• Coût total : 0€',
    docsDeployTitle: '🚀 Déployer en 5 Minutes',
    docsDeploy: '1. Cloner le dépôt\n2. npm install\n3. npm run build\n4. Déployer le dossier dist/ sur n\'importe quel hôte statique (Netlify, Vercel, GitHub Pages)\n5. Partager l\'URL — terminé !',
    docsRunTitle: '💻 Exécuter Localement',
    docsRun: 'npm run dev\n\nPuis ouvrir http://localhost:5173 dans votre navigateur.',
    
    // Footer
    footerBuilt: 'Construit en 48 heures pour le hackathon Flora Carbon AI',
    footerKolkata: 'Kolkata, Septembre 2026',
    footerDisclaimer: 'Cet outil fournit des estimations, pas des mesures. Pour la validation de crédits carbone, utilisez des méthodologies certifiées (Verra, Gold Standard).',
  },
};
