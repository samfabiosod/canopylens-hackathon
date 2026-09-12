import { useLang } from '../context/LanguageContext';
import { Leaf, Globe } from 'lucide-react';

export default function Header() {
  const { lang, setLang, t } = useLang();

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-gray-950/80 backdrop-blur-xl border-b border-emerald-900/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-green-600 flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white">{t.appName}</span>
          </div>

          {/* Nav */}
          <nav className="hidden md:flex items-center gap-6">
            <button onClick={() => scrollTo('analyzer')} className="text-sm text-gray-300 hover:text-emerald-400 transition-colors">
              {t.navTool}
            </button>
            <button onClick={() => scrollTo('how-it-works')} className="text-sm text-gray-300 hover:text-emerald-400 transition-colors">
              {t.navHow}
            </button>
            <button onClick={() => scrollTo('docs')} className="text-sm text-gray-300 hover:text-emerald-400 transition-colors">
              {t.navDocs}
            </button>
          </nav>

          {/* Language Toggle */}
          <button
            onClick={() => setLang(lang === 'en' ? 'fr' : 'en')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-800 border border-gray-700 text-sm text-gray-300 hover:border-emerald-500 hover:text-emerald-400 transition-all"
          >
            <Globe className="w-3.5 h-3.5" />
            <span className="font-medium">{lang === 'en' ? 'FR' : 'EN'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
