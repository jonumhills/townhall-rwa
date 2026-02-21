import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import MapView from './pages/MapView';
import AdminDashboard from './pages/AdminDashboard';
import MapsDurham from './pages/MapsDurham';
import AdminDurham from './pages/AdminDurham';
import './index.css';

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/map" element={<MapView />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/mapsdurham" element={<MapsDurham />} />
        <Route path="/admindurham" element={<AdminDurham />} />
      </Routes>
    </Router>
  );
}

export default App;
