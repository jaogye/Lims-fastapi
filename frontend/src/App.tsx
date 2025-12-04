import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { apiService } from './services/api';
import Layout from './components/Layout/Layout';
import Login from './components/Login/Login';
import MasterTable from './components/MasterTable/MasterTable';
import InputData from './components/InputData/InputData';
import ManualSample from './components/ManualSample/ManualSample';
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
          <Route path="/" element={<div className="page-header"><h1>Welcome to LIMS @ INC </h1><p>Select an option from the menu to get started.</p></div>} />
          <Route path="/master-tables" element={<MasterTable />} />
          <Route path="/input-data" element={<InputData />} />
          <Route path="/manual-sample" element={<ManualSample />} />
          <Route path="/user-admin" element={<div className="page-header"><h1>User Administration</h1><p>Component not yet implemented. See FRONTEND_IMPLEMENTATION_GUIDE.md</p></div>} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
