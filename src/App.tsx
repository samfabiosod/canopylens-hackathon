import { LanguageProvider } from './context/LanguageContext';
import Header from './components/Header';
import Hero from './components/Hero';
import Stats from './components/Stats';
import Analyzer from './components/Analyzer';
import HowItWorks from './components/HowItWorks';
import Documentation from './components/Documentation';
import Footer from './components/Footer';

function App() {
  return (
    <LanguageProvider>
      <div className="min-h-screen bg-gray-950 text-white">
        <Header />
        <main>
          <Hero />
          <Stats />
          <Analyzer />
          <HowItWorks />
          <Documentation />
        </main>
        <Footer />
      </div>
    </LanguageProvider>
  );
}

export default App;
