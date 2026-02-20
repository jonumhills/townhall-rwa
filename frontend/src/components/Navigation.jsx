import { Link } from 'react-router-dom';

function Navigation() {
  return (
    <nav className="bg-black/80 backdrop-blur-xl sticky top-0 z-50 border-b border-red-500/20">
      <div className="container mx-auto px-8 py-5">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-4">
            <div className="w-11 h-11 bg-red-500/20 rounded-xl flex items-center justify-center border border-red-500/30">
              <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <span className="text-white font-black text-2xl tracking-wider">TOWNHALL</span>
              <span className="block text-gray-500 text-sm">Intelligence Platform</span>
            </div>
          </Link>

          <div className="hidden md:flex items-center gap-10">
            <a href="#features" className="text-gray-400 hover:text-white transition-colors text-base font-medium">
              Features
            </a>
            <a href="#stats" className="text-gray-400 hover:text-white transition-colors text-base font-medium">
              Statistics
            </a>
            <Link
              to="/map"
              className="px-7 py-3 bg-red-600 hover:bg-red-500 text-white font-bold text-base rounded-xl transition-colors border border-red-500/30"
            >
              View Map
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
