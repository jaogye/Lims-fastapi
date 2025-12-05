import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { apiService } from './services/api';
import { UserProvider } from './contexts/UserContext';
import Layout from './components/Layout/Layout';
import Login from './components/Login/Login';
import MasterTable from './components/MasterTable/MasterTable';
import InputData from './components/InputData/InputData';
import ManualSample from './components/ManualSample/ManualSample';
import ReportGeneration from './components/ReportGeneration/ReportGeneration';
import ViewJobs from './components/ViewJobs/ViewJobs';
import UserAdmin from './components/UserAdmin/UserAdmin';
import PasswordChangeModal from './components/PasswordChangeModal/PasswordChangeModal';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(apiService.isAuthenticated());
  const [needsPasswordChange, setNeedsPasswordChange] = useState(false);
  const [checkingPassword, setCheckingPassword] = useState(false);

  // Check if user needs to change password after authentication
  useEffect(() => {
    const checkPasswordStatus = async () => {
      if (isAuthenticated && !checkingPassword) {
        setCheckingPassword(true);
        try {
          const user = await apiService.getCurrentUser();
          if (user.temp_password) {
            setNeedsPasswordChange(true);
          }
        } catch (error) {
          console.error('Failed to check password status:', error);
        } finally {
          setCheckingPassword(false);
        }
      }
    };

    checkPasswordStatus();
  }, [isAuthenticated]);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    await apiService.logout();
    setIsAuthenticated(false);
    setNeedsPasswordChange(false);
  };

  const handlePasswordChanged = async () => {
    setNeedsPasswordChange(false);
    // Optionally refresh user data
    try {
      await apiService.getCurrentUser();
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <UserProvider>
      <PasswordChangeModal
        isOpen={needsPasswordChange}
        onPasswordChanged={handlePasswordChanged}
      />
      <BrowserRouter>
        <Layout onLogout={handleLogout}>
          <Routes>
            <Route path="/" element={<div className="page-header"><h1>Welcome to LIMS @ INC </h1><p>Select an option from the menu to get started.</p></div>} />
            <Route path="/master-tables" element={<MasterTable />} />
            <Route path="/input-data" element={<InputData />} />
            <Route path="/manual-sample" element={<ManualSample />} />
            <Route path="/report-generation" element={<ReportGeneration />} />
            <Route path="/view-jobs" element={<ViewJobs />} />
            <Route path="/user-admin" element={<UserAdmin />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </UserProvider>
  );
}

export default App;
