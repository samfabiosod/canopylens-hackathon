import { useLang } from '../context/LanguageContext';
import { FileText, Terminal, Rocket, Code2 } from 'lucide-react';

export default function Documentation() {
  const { t, lang } = useLang();

  return (
    <section id="docs" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-950">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm mb-6">
            <FileText className="w-4 h-4" />
            {t.docsSubtitle}
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">{t.docsTitle}</h2>
        </div>

        {/* Document sections */}
        <div className="space-y-8">
          {/* Problem */}
          <DocSection title={t.docsProblemTitle} content={t.docsProblem} icon="🌍" />
          
          {/* Approach */}
          <DocSection title={t.docsApproachTitle} content={t.docsApproach} icon="🔬" />
          
          {/* Why it works */}
          <DocSection title={t.docsWhyTitle} content={t.docsWhy} icon="✅" isList />
          
          {/* Tech stack */}
          <DocSection title={t.docsTechTitle} content={t.docsTech} icon="🛠️" isList />

          {/* Deploy */}
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
            <div className="flex items-center gap-3 mb-4">
              <Rocket className="w-5 h-5 text-emerald-400" />
              <h3 className="text-lg font-semibold text-white">{t.docsDeployTitle}</h3>
            </div>
            <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono bg-gray-950 rounded-xl p-4 border border-gray-800">
              {t.docsDeploy}
            </pre>
          </div>

          {/* Run locally */}
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
            <div className="flex items-center gap-3 mb-4">
              <Terminal className="w-5 h-5 text-emerald-400" />
              <h3 className="text-lg font-semibold text-white">{t.docsRunTitle}</h3>
            </div>
            <div className="bg-gray-950 rounded-xl p-4 border border-gray-800 font-mono text-sm">
              <span className="text-emerald-400">$</span> <span className="text-gray-300">npm run dev</span>
              <br />
              <span className="text-gray-500 mt-2 block">→ http://localhost:5173</span>
            </div>
          </div>

          {/* Code structure */}
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
            <div className="flex items-center gap-3 mb-4">
              <Code2 className="w-5 h-5 text-emerald-400" />
              <h3 className="text-lg font-semibold text-white">Project Structure</h3>
            </div>
            <pre className="text-sm text-gray-300 font-mono bg-gray-950 rounded-xl p-4 border border-gray-800">
{`canopylens/
├── src/
│   ├── App.tsx              # Main app component
│   ├── components/
│   │   ├── Header.tsx       # Navigation + language toggle
│   │   ├── Hero.tsx         # Landing section
│   │   ├── Analyzer.tsx     # Image upload + analysis UI
│   │   ├── HowItWorks.tsx   # Algorithm explanation
│   │   └── Documentation.tsx # This page
│   ├── utils/
│   │   ├── imageProcessing.ts  # HSV segmentation + carbon calc
│   │   └── translations.ts     # EN/FR translations
│   └── context/
│       └── LanguageContext.tsx   # i18n state management
├── index.html
├── package.json
└── README.md`}
            </pre>
          </div>
        </div>

        {/* Streamlit version */}
        <div className="mt-12 bg-gray-900 rounded-2xl p-6 border border-gray-800">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-2xl">🐍</span>
            <h3 className="text-lg font-semibold text-white">
              {lang === 'fr' ? 'Version Python/Streamlit' : 'Python/Streamlit Version'}
            </h3>
          </div>
          <p className="text-sm text-gray-300 mb-4">
            {lang === 'fr'
              ? 'CanopyLens est aussi disponible en version Python/Streamlit avec génération de rapports PDF, visualisation des contours d\'arbres, et interface bilingue complète.'
              : 'CanopyLens is also available as a Python/Streamlit app with PDF report generation, tree contour visualization, and full bilingual interface.'}
          </p>
          <div className="bg-gray-950 rounded-xl p-4 border border-gray-800 font-mono text-sm space-y-1">
            <p><span className="text-emerald-400">$</span> <span className="text-gray-300">pip install -r requirements.txt</span></p>
            <p><span className="text-emerald-400">$</span> <span className="text-gray-300">streamlit run app.py</span></p>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-3 text-center">
            <div className="bg-gray-800/50 rounded-lg p-3">
              <p className="text-lg font-bold text-emerald-400">app.py</p>
              <p className="text-xs text-gray-500">{lang === 'fr' ? 'Application complète' : 'Full application'}</p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <p className="text-lg font-bold text-blue-400">PDF</p>
              <p className="text-xs text-gray-500">{lang === 'fr' ? 'Rapports pro' : 'Pro reports'}</p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <p className="text-lg font-bold text-purple-400">FR/EN</p>
              <p className="text-xs text-gray-500">{lang === 'fr' ? 'Bilingue' : 'Bilingual'}</p>
            </div>
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-emerald-500/10 to-green-500/10 rounded-2xl p-8 border border-emerald-500/20">
            <h3 className="text-xl font-bold text-white mb-3">
              {lang === 'fr' ? '🌱 Construit avec honnêteté, livré avec courage.' : '🌱 Built with honesty, shipped with courage.'}
            </h3>
            <p className="text-gray-400 text-sm max-w-xl mx-auto">
              {lang === 'fr'
                ? 'Un outil brut qui admet ses limites l\'emporte sur un outil soigné qui invente des chiffres. CanopyLens est transparent, reproductible, et gratuit.'
                : 'A rough tool that admits its limits beats a polished tool that invents figures. CanopyLens is transparent, reproducible, and free.'}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function DocSection({ title, content, icon, isList }: { title: string; content: string; icon: string; isList?: boolean }) {
  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
        <span>{icon}</span>
        {title.replace(/^[^\s]+\s/, '')}
      </h3>
      {isList ? (
        <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">
          {content.split('\n').map((line, i) => (
            <p key={i} className={line.startsWith('•') ? 'ml-2' : ''}>{line}</p>
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-300 leading-relaxed">{content}</p>
      )}
    </div>
  );
}
