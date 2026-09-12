import { useLang } from '../context/LanguageContext';
import { Shield, Wifi, Monitor } from 'lucide-react';

export default function Hero() {
  const { t } = useLang();

  const scrollToAnalyzer = () => {
    document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-gray-950 via-emerald-950/20 to-gray-950" />
      <div className="absolute inset-0 opacity-20" style={{
        backgroundImage: 'url(https://image.qwenlm.ai/generated-images/7968361f-d14f-4331-a9d7-0b9d3fa83141/_result.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        filter: 'blur(2px) saturate(0.5)',
      }} />
      <div className="absolute inset-0 bg-gray-950/60" />
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-green-500/15 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl animate-pulse delay-500" />
      </div>

      {/* Grid pattern */}
      <div className="absolute inset-0 opacity-5" style={{
        backgroundImage: 'linear-gradient(rgba(16, 185, 129, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(16, 185, 129, 0.3) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }} />

      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm mb-8">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Flora Carbon AI Hackathon — Kolkata 2026
        </div>

        {/* Title */}
        <h1 className="text-4xl sm:text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          {t.heroTitle.split(' ').map((word, i) => (
            <span key={i} className={i >= t.heroTitle.split(' ').length - 2 ? 'text-emerald-400' : ''}>
              {word}{' '}
            </span>
          ))}
        </h1>

        {/* Subtitle */}
        <p className="text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto mb-10 leading-relaxed">
          {t.heroSubtitle}
        </p>

        {/* CTA */}
        <button
          onClick={scrollToAnalyzer}
          className="group inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 text-white font-semibold text-lg shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:scale-105 transition-all duration-300"
        >
          {t.heroCta}
          <span className="group-hover:translate-x-1 transition-transform">→</span>
        </button>

        {/* Trust badges */}
        <div className="flex flex-wrap items-center justify-center gap-6 mt-12">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Shield className="w-4 h-4 text-emerald-500" />
            {t.heroOpenSource}
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Wifi className="w-4 h-4 text-emerald-500" />
            {t.heroNoApi}
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Monitor className="w-4 h-4 text-emerald-500" />
            {t.heroBrowser}
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 rounded-full border-2 border-gray-600 flex items-start justify-center p-1.5">
          <div className="w-1.5 h-3 rounded-full bg-emerald-400 animate-pulse" />
        </div>
      </div>
    </section>
  );
}
