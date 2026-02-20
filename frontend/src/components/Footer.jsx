function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <h3 className="text-xl font-bold mb-4">Townhall</h3>
            <p className="text-gray-400">
              Tracking government rezoning decisions with AI-powered data extraction and GIS mapping.
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#features" className="hover:text-white transition">Features</a></li>
              <li><a href="#stats" className="hover:text-white transition">Statistics</a></li>
              <li><a href="/map" className="hover:text-white transition">View Map</a></li>
              <li><a href="http://localhost:8000/docs" target="_blank" className="hover:text-white transition">API Docs</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Technology</h4>
            <ul className="space-y-2 text-gray-400">
              <li>React + Vite + Tailwind</li>
              <li>FastAPI + Python</li>
              <li>Mapbox GL JS</li>
              <li>Mecklenburg County GIS</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
          <p>&copy; {currentYear} Townhall Rezoning Tracker. Built for the Elasticsearch Hackathon.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
