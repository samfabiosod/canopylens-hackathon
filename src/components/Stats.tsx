import { useLang } from '../context/LanguageContext';
import { Zap, Globe, Clock, DollarSign } from 'lucide-react';

export default function Stats() {
  const { lang } = useLang();

  const stats = [
    {
      icon: Zap,
      value: '100%',
      label: lang === 'fr' ? 'Client-Side Processing' : 'Client-Side Processing',
      sublabel: lang === 'fr' ? 'Aucun serveur requis' : 'No server required',
      color: 'text-emerald-400',
    },
    {
      icon: DollarSign,
      value: '$0',
      label: lang === 'fr' ? 'Coût Total' : 'Total Cost',
      sublabel: lang === 'fr' ? 'Zéro budget' : 'Zero budget',
      color: 'text-green-400',
    },
    {
      icon: Clock,
      value: '48h',
      label: lang === 'fr' ? 'Temps de Développement' : 'Development Time',
      sublabel: lang === 'fr' ? 'Un week-end' : 'One weekend',
      color: 'text-cyan-400',
    },
    {
      icon: Globe,
      value: '2',
      label: lang === 'fr' ? 'Langues Supportées' : 'Languages Supported',
      sublabel: 'English + Français',
      color: 'text-purple-400',
    },
  ];

  return (
    <section className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-900/30 border-y border-gray-800/50">
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat, i) => (
            <div key={i} className="text-center group">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gray-800/50 mb-3 group-hover:scale-110 transition-transform">
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
              <p className="text-sm text-gray-300 font-medium mt-1">{stat.label}</p>
              <p className="text-xs text-gray-500">{stat.sublabel}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
