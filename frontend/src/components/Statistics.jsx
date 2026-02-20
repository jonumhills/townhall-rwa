import { motion } from 'framer-motion';

const statItems = [
  {
    label: 'Petitions Tracked',
    suffix: '+',
    key: 'total_petitions',
    description: 'Automated monitoring',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    gradientFrom: 'rgba(255,68,0,0.15)',
    gradientTo: 'rgba(255,100,0,0.05)',
    borderColor: 'rgba(255,68,0,0.2)',
    iconBg: 'rgba(255,68,0,0.15)',
    iconColor: '#ff6030',
  },
  {
    label: 'Parcel Locations',
    suffix: '+',
    key: 'total_pins',
    description: 'GIS mapped properties',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    gradientFrom: 'rgba(255,120,0,0.15)',
    gradientTo: 'rgba(255,68,0,0.05)',
    borderColor: 'rgba(255,120,0,0.2)',
    iconBg: 'rgba(255,120,0,0.15)',
    iconColor: '#ff8800',
  },
  {
    label: 'Meetings Analyzed',
    suffix: '',
    key: 'total_meetings',
    description: 'Government sessions',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    ),
    gradientFrom: 'rgba(220,38,38,0.15)',
    gradientTo: 'rgba(255,68,0,0.05)',
    borderColor: 'rgba(220,38,38,0.2)',
    iconBg: 'rgba(220,38,38,0.15)',
    iconColor: '#f87171',
  },
  {
    label: 'Counties Covered',
    suffix: '',
    key: 'total_counties',
    description: 'Active regions',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
    ),
    gradientFrom: 'rgba(255,150,0,0.15)',
    gradientTo: 'rgba(255,80,0,0.05)',
    borderColor: 'rgba(255,150,0,0.2)',
    iconBg: 'rgba(255,150,0,0.15)',
    iconColor: '#fbbf24',
  },
];

const metrics = [
  { value: '24/7', label: 'Continuous Monitoring' },
  { value: '95%', label: 'AI Accuracy Rate' },
  { value: '<5min', label: 'Alert Response Time' },
];

function Statistics({ stats }) {
  return (
    <section id="stats" className="py-28 bg-black relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[500px] bg-red-600/5 rounded-full blur-3xl pointer-events-none" />

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
            <span className="text-red-400 text-sm font-medium tracking-widest uppercase">Platform Impact</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            By The{' '}
            <span className="bg-gradient-to-r from-red-500 to-orange-400 bg-clip-text text-transparent">Numbers</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Real-time data powered by Elasticsearch Agent Builder
          </p>
        </motion.div>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {statItems.map((item, index) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="relative rounded-3xl p-7 overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:-translate-y-1"
              style={{
                background: `linear-gradient(135deg, ${item.gradientFrom} 0%, rgba(0,0,0,0.7) 100%)`,
                border: `1px solid ${item.borderColor}`,
                boxShadow: '0 4px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04)',
              }}
            >
              <div className="relative z-10">
                {/* Icon */}
                <div
                  className="w-12 h-12 rounded-2xl flex items-center justify-center mb-5"
                  style={{ background: item.iconBg, color: item.iconColor }}
                >
                  {item.icon}
                </div>

                {/* Value */}
                <div className="text-5xl font-black text-white mb-1 tracking-tight">
                  {stats[item.key]?.toLocaleString()}{item.suffix}
                </div>

                {/* Label */}
                <div className="text-base font-semibold text-white/90 mb-1">{item.label}</div>

                {/* Description */}
                <div className="text-sm text-gray-500">{item.description}</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Metrics Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-5 rounded-3xl overflow-hidden"
          style={{
            background: 'linear-gradient(135deg, rgba(255,68,0,0.08) 0%, rgba(0,0,0,0.9) 50%, rgba(255,100,0,0.06) 100%)',
            border: '1px solid rgba(255,68,0,0.15)',
            boxShadow: '0 4px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04)',
          }}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-red-500/10">
            {metrics.map((m, i) => (
              <div key={i} className="flex flex-col items-center justify-center py-10 px-6 text-center gap-2">
                <div className="text-5xl font-black bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                  {m.value}
                </div>
                <div className="text-sm font-bold text-gray-400 uppercase tracking-widest">{m.label}</div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

export default Statistics;
