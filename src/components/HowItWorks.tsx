import { useLang } from '../context/LanguageContext';
import { Upload, Palette, Sparkles, Calculator, CheckCircle, AlertTriangle } from 'lucide-react';

export default function HowItWorks() {
  const { t } = useLang();

  const steps = [
    { icon: Upload, title: t.step1Title, desc: t.step1Desc, color: 'from-blue-500 to-cyan-500' },
    { icon: Palette, title: t.step2Title, desc: t.step2Desc, color: 'from-emerald-500 to-green-500' },
    { icon: Sparkles, title: t.step3Title, desc: t.step3Desc, color: 'from-purple-500 to-pink-500' },
    { icon: Calculator, title: t.step4Title, desc: t.step4Desc, color: 'from-amber-500 to-orange-500' },
    { icon: CheckCircle, title: t.step5Title, desc: t.step5Desc, color: 'from-emerald-400 to-teal-500' },
  ];

  const limitations = [t.lim1, t.lim2, t.lim3, t.lim4, t.lim5];

  return (
    <section id="how-it-works" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900/50">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">{t.howTitle}</h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">{t.howSubtitle}</p>
        </div>

        {/* Steps */}
        <div className="space-y-8 mb-20">
          {steps.map((step, i) => (
            <div key={i} className="flex gap-6 items-start group">
              {/* Step number + icon */}
              <div className="flex-shrink-0">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                  <step.icon className="w-7 h-7 text-white" />
                </div>
              </div>
              {/* Content */}
              <div className="pt-1">
                <h3 className="text-xl font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-gray-400 leading-relaxed">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Visual: Pipeline diagram */}
        <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 mb-16">
          <h3 className="text-lg font-semibold text-white mb-6 text-center">Pipeline Overview</h3>
          <div className="flex flex-wrap items-center justify-center gap-3 text-sm">
            <PipelineStep label="RGB Image" color="bg-blue-500/20 text-blue-300 border-blue-500/30" />
            <Arrow />
            <PipelineStep label="HSV Convert" color="bg-purple-500/20 text-purple-300 border-purple-500/30" />
            <Arrow />
            <PipelineStep label="Green Threshold" color="bg-emerald-500/20 text-emerald-300 border-emerald-500/30" />
            <Arrow />
            <PipelineStep label="Morphology" color="bg-pink-500/20 text-pink-300 border-pink-500/30" />
            <Arrow />
            <PipelineStep label="Count Pixels" color="bg-amber-500/20 text-amber-300 border-amber-500/30" />
            <Arrow />
            <PipelineStep label="Carbon Estimate" color="bg-green-500/20 text-green-300 border-green-500/30" />
          </div>
        </div>

        {/* Limitations */}
        <div className="bg-amber-500/5 rounded-2xl p-8 border border-amber-500/20">
          <div className="flex items-center gap-3 mb-6">
            <AlertTriangle className="w-6 h-6 text-amber-400" />
            <h3 className="text-xl font-semibold text-white">{t.limitationsTitle}</h3>
          </div>
          <ul className="space-y-3">
            {limitations.map((lim, i) => (
              <li key={i} className="flex items-start gap-3 text-gray-300">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2 flex-shrink-0" />
                <span className="text-sm leading-relaxed">{lim}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

function PipelineStep({ label, color }: { label: string; color: string }) {
  return (
    <span className={`px-4 py-2 rounded-lg border ${color} font-medium`}>
      {label}
    </span>
  );
}

function Arrow() {
  return <span className="text-gray-600 text-xl">→</span>;
}
