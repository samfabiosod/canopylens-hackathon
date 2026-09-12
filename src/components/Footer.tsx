import { useLang } from '../context/LanguageContext';
import { Leaf, Heart } from 'lucide-react';

export default function Footer() {
  const { t } = useLang();

  return (
    <footer className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-950 border-t border-gray-800">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col items-center text-center space-y-4">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-green-600 flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white">{t.appName}</span>
          </div>

          {/* Tagline */}
          <p className="text-gray-400 text-sm max-w-md">{t.tagline}</p>

          {/* Built info */}
          <div className="flex items-center gap-1.5 text-sm text-gray-500">
            <span>{t.footerBuilt}</span>
            <span>•</span>
            <span>{t.footerKolkata}</span>
          </div>

          {/* Disclaimer */}
          <p className="text-xs text-gray-600 max-w-lg">{t.footerDisclaimer}</p>

          {/* Made with */}
          <div className="flex items-center gap-1 text-xs text-gray-600 pt-4">
            <span>Made with</span>
            <Heart className="w-3 h-3 text-emerald-500 fill-emerald-500" />
            <span>and zero budget</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
