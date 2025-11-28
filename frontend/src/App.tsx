import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { apiService } from './services/api';
import Layout from './components/Layout/Layout';
import Login from './components/Login/Login';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(apiService.isAuthenticated());

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    await apiService.logout();
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <BrowserRouter>
      <Layout onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<div className="page-header"><h1>Welcome to LIMS @ PVS</h1><p>Select an option from the menu to get started.</p></div>} />
          <Route path="/master-tables" element={<div className="page-header"><h1>Master Tables</h1><p>Component not yet implemented. See FRONTEND_IMPLEMENTATION_GUIDE.md</p></div>} />
          <Route path="/input-data" element={<div className="page-header"><h1>Input Data</h1><p>Component not yet implemented. See FRONTEND_IMPLEMENTATION_GUIDE.md</p></div>} />
          <Route path="/manual-sample" element={<div className="page-header"><h1>Manual Sample</h1><p>Component not yet implemented. See FRONTEND_IMPLEMENTATION_GUIDE.md</p></div>} />
          <Route path="/user-admin" element={<div className="page-header"><h1>User Administration</h1><p>Component not yet implemented. See FRONTEND_IMPLEMENTATION_GUIDE.md</p></div>} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
