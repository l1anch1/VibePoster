/**
 * Landing Page 组件
 *
 * iOS 液态玻璃风格（与 Editor 统一）
 */

import React from 'react';

interface LandingPageProps {
  onEnter: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onEnter }) => {
  return (
    <div
      className="min-h-screen overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #e0e7ff 0%, #fae8ff 50%, #fef3c7 100%)' }}
    >
      {/* 动态背景光晕 */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-gradient-to-br from-blue-300/40 to-purple-300/40 blur-3xl animate-pulse" />
        <div
          className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-pink-300/40 to-orange-200/40 blur-3xl animate-pulse"
          style={{ animationDelay: '1s' }}
        />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full bg-gradient-to-br from-cyan-200/30 to-blue-200/30 blur-3xl" />
      </div>

      {/* Header */}
      <nav
        className="relative z-50 flex items-center justify-between px-6 py-4 lg:px-12 mx-4 mt-4 rounded-2xl"
        style={{
          background: 'rgba(255,255,255,0.6)',
          backdropFilter: 'blur(20px) saturate(180%)',
          boxShadow: '0 4px 24px rgba(0,0,0,0.06), inset 0 0 0 1px rgba(255,255,255,0.5)',
        }}
      >
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-violet-500/30">
            <span className="text-white text-sm font-bold">V</span>
          </div>
          <span className="font-bold text-lg text-gray-800">VibePoster</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-700">
          <a href="#features" className="hover:text-violet-600 transition-colors">
            Features
          </a>
          <a href="#how-it-works" className="hover:text-violet-600 transition-colors">
            How it Works
          </a>
          <a href="#pricing" className="hover:text-violet-600 transition-colors">
            Pricing
          </a>
        </div>
        <button
          onClick={onEnter}
          className="px-5 py-2.5 text-sm font-semibold bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white rounded-xl hover:opacity-90 transition-all shadow-lg shadow-violet-500/30"
        >
          Launch App →
        </button>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center px-6 pt-20 pb-32 text-center">
        <div
          className="inline-flex items-center gap-2 px-4 py-2 mb-8 text-xs font-medium text-gray-700 rounded-full"
          style={{
            background: 'rgba(255,255,255,0.7)',
            backdropFilter: 'blur(10px)',
            boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.5)',
          }}
        >
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          Powered by AI • Now in Beta
        </div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-[1.1]">
          <span className="bg-gradient-to-r from-gray-900 via-violet-800 to-violet-600 bg-clip-text text-transparent">
            Create Stunning
          </span>
          <br />
          <span className="bg-gradient-to-r from-violet-600 via-fuchsia-500 to-orange-400 bg-clip-text text-transparent">
            Posters in Seconds
          </span>
        </h1>

        <p className="max-w-xl text-lg text-gray-700 mb-10 leading-relaxed">
          Transform your ideas into professional designs with AI. No design skills needed. Just
          describe what you want.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4">
          <button
            onClick={onEnter}
            className="group flex items-center gap-2 px-8 py-4 text-base font-semibold bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white rounded-2xl hover:opacity-90 transition-all shadow-xl shadow-violet-500/30"
          >
            <span>Start Creating Free</span>
            <svg
              className="w-5 h-5 group-hover:translate-x-1 transition-transform"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 8l4 4m0 0l-4 4m4-4H3"
              />
            </svg>
          </button>
          <button
            className="flex items-center gap-2 px-6 py-4 text-base font-medium text-gray-800 rounded-2xl transition-all hover:bg-white/80"
            style={{
              background: 'rgba(255,255,255,0.7)',
              backdropFilter: 'blur(10px)',
              boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.5)',
            }}
          >
            <svg className="w-5 h-5 text-violet-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
            <span>Watch Demo</span>
          </button>
        </div>

        {/* Preview */}
        <div className="relative mt-20 w-full max-w-4xl">
          <div
            className="relative rounded-[32px] overflow-hidden"
            style={{
              background: 'rgba(255,255,255,0.7)',
              backdropFilter: 'blur(20px) saturate(180%)',
              boxShadow:
                '0 25px 80px rgba(0,0,0,0.1), 0 8px 32px rgba(139,92,246,0.15), inset 0 0 0 1px rgba(255,255,255,0.5)',
            }}
          >
            <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-200/50">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-yellow-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
              </div>
              <span className="text-xs text-gray-600 ml-2 font-semibold">VibePoster Editor</span>
            </div>
            <div className="aspect-video bg-gradient-to-br from-violet-50 via-white to-fuchsia-50 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-xl shadow-violet-500/30">
                  <span className="text-4xl">✨</span>
                </div>
                <p className="text-sm font-medium text-gray-600">Your creative canvas awaits</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Features Section */}
      <section id="features" className="relative z-10 px-6 py-24">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-900">
            Everything you need to create
          </h2>
          <p className="text-base text-gray-600 text-center mb-16 max-w-2xl mx-auto">
            Powerful features that make poster design effortless
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: '🎯',
                title: 'AI-Powered Design',
                desc: 'Just describe your vision and watch AI bring it to life',
              },
              {
                icon: '🎨',
                title: 'Smart Templates',
                desc: 'Industry-specific templates optimized for every use case',
              },
              {
                icon: '✏️',
                title: 'Easy Editing',
                desc: 'Intuitive drag-and-drop editor with real-time preview',
              },
              {
                icon: '📱',
                title: 'Multiple Formats',
                desc: 'Export in any size - social media, print, web, and more',
              },
              {
                icon: '🎭',
                title: 'Brand Kit',
                desc: 'Upload your brand guidelines for consistent designs',
              },
              {
                icon: '⚡',
                title: 'Lightning Fast',
                desc: 'Generate professional posters in under 30 seconds',
              },
            ].map((feature, i) => (
              <div
                key={i}
                className="p-6 rounded-3xl transition-all hover:scale-[1.02]"
                style={{
                  background: 'rgba(255,255,255,0.6)',
                  backdropFilter: 'blur(20px) saturate(180%)',
                  boxShadow: '0 4px 24px rgba(0,0,0,0.06), inset 0 0 0 1px rgba(255,255,255,0.5)',
                }}
              >
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-100 to-fuchsia-100 flex items-center justify-center mb-4 text-2xl">
                  {feature.icon}
                </div>
                <h3 className="text-base font-semibold mb-2 text-gray-900">{feature.title}</h3>
                <p className="text-sm text-gray-600 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="relative z-10 px-6 py-24">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-900">
            How it Works
          </h2>
          <p className="text-base text-gray-600 text-center mb-16">Three simple steps to stunning designs</p>

          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            {[
              { step: '01', title: 'Describe', desc: 'Tell AI what you want to create' },
              { step: '02', title: 'Generate', desc: 'AI creates multiple design options' },
              { step: '03', title: 'Customize', desc: 'Fine-tune and export your poster' },
            ].map((item, i) => (
              <div key={i} className="flex-1 text-center">
                <div
                  className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4"
                  style={{
                    background: 'rgba(255,255,255,0.7)',
                    backdropFilter: 'blur(10px)',
                    boxShadow:
                      '0 4px 24px rgba(139,92,246,0.15), inset 0 0 0 1px rgba(255,255,255,0.5)',
                  }}
                >
                  <span className="text-sm font-bold bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">
                    {item.step}
                  </span>
                </div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900">{item.title}</h3>
                <p className="text-sm text-gray-600 leading-relaxed">{item.desc}</p>
                {i < 2 && (
                  <div className="hidden md:block text-3xl text-violet-300 mt-4 font-light">→</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 px-6 py-24 text-center">
        <div
          className="max-w-2xl mx-auto p-12 rounded-[40px]"
          style={{
            background: 'rgba(255,255,255,0.6)',
            backdropFilter: 'blur(20px) saturate(180%)',
            boxShadow: '0 8px 40px rgba(139,92,246,0.15), inset 0 0 0 1px rgba(255,255,255,0.5)',
          }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
            Ready to create something amazing?
          </h2>
          <p className="text-base text-gray-600 mb-8">Join thousands of creators using VibePoster</p>
          <button
            onClick={onEnter}
            className="px-8 py-4 text-base font-semibold bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white rounded-2xl hover:opacity-90 transition-all shadow-xl shadow-violet-500/30"
          >
            Get Started — It's Free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-8 border-t border-white/30">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-gray-700 text-sm">
            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
              <span className="text-white text-xs font-bold">V</span>
            </div>
            <span className="font-semibold">VibePoster</span>
            <span className="text-gray-500">© 2025</span>
          </div>
          <div className="flex items-center gap-6 text-sm font-medium text-gray-600">
            <a href="#" className="hover:text-violet-600 transition-colors">
              Privacy
            </a>
            <a href="#" className="hover:text-violet-600 transition-colors">
              Terms
            </a>
            <a href="#" className="hover:text-violet-600 transition-colors">
              Contact
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};
