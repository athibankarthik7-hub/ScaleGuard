import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './components/MainLayout';
import DashboardPage from './pages/DashboardPage';
import ArchitecturePage from './pages/ArchitecturePage';
import IncidentDebugger from './pages/IncidentDebugger';
import LandingPage from './pages/LandingPage';
import Simulation from './pages/Simulation';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<MainLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="architecture" element={<ArchitecturePage />} />
          <Route path="simulation" element={<Simulation />} />
          <Route path="incidents" element={<IncidentDebugger />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
