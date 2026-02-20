import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Navigation from '../components/Navigation';
import Hero from '../components/Hero';
import Statistics from '../components/Statistics';
import Features from '../components/Features';
import Footer from '../components/Footer';
import CustomCursor from '../components/CustomCursor';
import api from '../services/api';

function Landing() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await api.getStats();
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-black overflow-x-hidden">
      <CustomCursor />

      {/* Animated background gradient */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-red-950/20 via-black to-orange-950/20" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-red-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-orange-600/10 rounded-full blur-3xl animate-pulse delay-700" />
      </div>

      <div className="relative z-10">
        <Navigation />
        <Hero onViewMap={() => navigate('/map')} />
        {!loading && stats && <Statistics stats={stats} />}
        <Features />
        <Footer />
      </div>
    </div>
  );
}

export default Landing;
