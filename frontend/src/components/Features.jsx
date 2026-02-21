import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const features = [
  {
    title: 'Blockchain Deed NFTs',
    description: 'Property deeds tokenized as NFTs on Hedera and ADI Chain with verified ownership',
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    highlight: true,
    gradientFrom: 'rgba(255,68,0,0.12)',
    borderColor: 'rgba(255,68,0,0.25)',
    iconBg: 'rgba(255,68,0,0.15)',
    iconColor: '#ff6030',
  },
  {
    title: 'Fractional Ownership',
    description: 'Own 1/1000th of real estate parcels with ERC-20 share tokens tradeable on-chain',
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    highlight: true,
    gradientFrom: 'rgba(255,120,0,0.12)',
    borderColor: 'rgba(255,120,0,0.25)',
    iconBg: 'rgba(255,120,0,0.15)',
    iconColor: '#ff8800',
  },
  {
    title: 'Multi-Chain Marketplace',
    description: 'Trade property shares on Hedera (HBAR) and ADI Chain with instant settlement',
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    highlight: true,
    gradientFrom: 'rgba(255,68,0,0.08)',
    borderColor: 'rgba(255,68,0,0.15)',
    iconBg: 'rgba(255,68,0,0.1)',
    iconColor: '#ff4400',
  },
  {
    title: 'Rezoning Intelligence',
    description: 'AI-powered tracking of government rezoning decisions with geospatial analysis',
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
    ),
    highlight: false,
    gradientFrom: 'rgba(220,38,38,0.08)',
    borderColor: 'rgba(220,38,38,0.15)',
    iconBg: 'rgba(220,38,38,0.1)',
    iconColor: '#f87171',
  },
  {
    title: 'County Admin Dashboard',
    description: 'Verify deeds, approve claims, and mint NFTs with county-controlled wallets',
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    highlight: false,
    gradientFrom: 'rgba(255,150,0,0.08)',
    borderColor: 'rgba(255,150,0,0.15)',
    iconBg: 'rgba(255,150,0,0.1)',
    iconColor: '#fbbf24',
  },
  {
    title: 'Interactive GIS Maps',
    description: 'Mapbox visualization showing tokenized parcels in gold with real-time data',
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
    ),
    highlight: false,
    gradientFrom: 'rgba(255,80,0,0.08)',
    borderColor: 'rgba(255,80,0,0.15)',
    iconBg: 'rgba(255,80,0,0.1)',
    iconColor: '#fb923c',
  },
];

function Features() {
  const navigate = useNavigate();

  return (
    <section id="features" className="py-28 bg-black relative overflow-hidden">
      <div className="absolute bottom-0 left-1/4 w-[600px] h-[400px] bg-red-600/5 rounded-full blur-3xl pointer-events-none" />

      <div className="container mx-auto px-6 max-w-7xl relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-full mb-6">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-red-400 text-sm font-medium tracking-widest uppercase">Platform Capabilities</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            Tokenization{' '}
            <span className="bg-gradient-to-r from-red-500 to-orange-400 bg-clip-text text-transparent">Platform</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-3xl mx-auto">
            Multi-chain real estate tokenization with blockchain-verified deeds and fractional ownership
          </p>
        </motion.div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.08 }}
              viewport={{ once: true }}
              className="relative rounded-3xl p-7 overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:-translate-y-1 group"
              style={{
                background: `linear-gradient(135deg, ${feature.gradientFrom} 0%, rgba(0,0,0,0.8) 100%)`,
                border: `1px solid ${feature.borderColor}`,
                boxShadow: '0 4px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04)',
              }}
            >
              {/* AI badge */}
              {feature.highlight && (
                <div className="absolute top-5 right-5">
                  <span
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black uppercase tracking-wider"
                    style={{ background: 'rgba(255,68,0,0.2)', color: '#ff6030', border: '1px solid rgba(255,68,0,0.3)' }}
                  >
                    <span className="w-1.5 h-1.5 bg-red-400 rounded-full animate-pulse" />
                    AI
                  </span>
                </div>
              )}

              {/* Icon */}
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center mb-5"
                style={{ background: feature.iconBg, color: feature.iconColor }}
              >
                {feature.icon}
              </div>

              {/* Title */}
              <h3 className="text-lg font-black text-white mb-3 tracking-wide">
                {feature.title}
              </h3>

              {/* Description */}
              <p className="text-sm text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* CTA Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-5 rounded-3xl overflow-hidden p-12 text-center relative"
          style={{
            background: 'linear-gradient(135deg, rgba(255,68,0,0.12) 0%, rgba(0,0,0,0.9) 50%, rgba(255,100,0,0.08) 100%)',
            border: '1px solid rgba(255,68,0,0.2)',
            boxShadow: '0 4px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04)',
          }}
        >
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,68,0,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,68,0,0.02)_1px,transparent_1px)] bg-[size:40px_40px]" />
          <div className="relative z-10">
            <h3 className="text-3xl md:text-4xl font-black text-white mb-4">
              Ready To Tokenize Real Estate?
            </h3>
            <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
              Discover tokenized parcels, trade fractional shares, and invest in real estate on the blockchain
            </p>
            <button
              onClick={() => navigate('/map')}
              className="inline-flex items-center gap-3 px-8 py-4 text-white font-black text-base rounded-2xl transition-all hover:scale-105"
              style={{
                background: 'linear-gradient(135deg, #ff4400, #ff8800)',
                boxShadow: '0 8px 30px rgba(255,68,0,0.4)',
              }}
            >
              EXPLORE PLATFORM
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

export default Features;
