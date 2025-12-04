# LIMS Frontend Implementation Guide

## Overview
This guide provides complete instructions for implementing the React + TypeScript frontend for the LIMS application using AG-Grid and Vite.

## What Has Been Created

### Backend (Complete)
- ✅ Manual samples CRUD endpoints (`/api/samples/manual-samples`)
- ✅ User administration endpoints (`/api/users`)
- ✅ Master data list endpoints (products, qualities, sample_points, variables)
- ✅ Service layer methods for all new features
- ✅ Routers registered in main.py

### Frontend Structure (Partial)
- ✅ Project setup (package.json, vite.config.ts, tsconfig.json)
- ✅ TypeScript types (src/types/index.ts)
- ✅ API service layer (src/services/api.ts)
- ✅ Entry point (src/main.tsx)

## Installation Steps

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Create Remaining Files** (Follow sections below)

3. **Run Development Server**
   ```bash
   npm run dev
   ```

4. **Build for Production**
   ```bash
   npm run build
   ```

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── Login/
│   │   │   └── Login.tsx
│   │   ├── MasterTable/
│   │   │   └── MasterTable.tsx
│   │   ├── InputData/
│   │   │   └── InputData.tsx
│   │   ├── ManualSample/
│   │   │   └── ManualSample.tsx
│   │   └── UserAdmin/
│   │       └── UserAdmin.tsx
│   ├── services/
│   │   └── api.ts (✅ Created)
│   ├── types/
│   │   └── index.ts (✅ Created)
│   ├── App.tsx
│   ├── App.css
│   ├── index.css
│   └── main.tsx (✅ Created)
├── index.html (✅ Created)
├── package.json (✅ Created)
├── tsconfig.json (✅ Created)
├── tsconfig.node.json (✅ Created)
└── vite.config.ts (✅ Created)
```

## Component Implementation

### 1. src/index.css
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
}

#root {
  min-height: 100vh;
}

/* AG-Grid Theme Imports */
@import "ag-grid-community/styles/ag-grid.css";
@import "ag-grid-community/styles/ag-theme-alpine.css";
```

### 2. src/App.css
```css
.app {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ddd;
}

.page-header h1 {
  font-size: 24px;
  color: #333;
}

/* Login Page */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f0f0;
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 400px;
}

.login-box h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4CAF50;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #666;
  color: white;
}

.btn-secondary:hover {
  background-color: #555;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover {
  background-color: #da190b;
}

.btn-full {
  width: 100%;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

/* Error Messages */
.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  border-left: 4px solid #c62828;
}

.success-message {
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  border-left: 4px solid #2e7d32;
}

/* AG-Grid Container */
.ag-theme-alpine {
  --ag-border-color: #ddd;
}

.grid-container {
  height: 600px;
  width: 100%;
  margin-bottom: 20px;
}

/* Sample List Colors */
.sample-complete {
  background-color: #4CAF50 !important;
  color: white;
}

.sample-incomplete {
  background-color: #FF9800 !important;
  color: white;
}
```

### 3. src/App.tsx
```typescript
import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { apiService } from './services/api';
import Layout from './components/Layout/Layout';
import Login from './components/Login/Login';
import MasterTable from './components/MasterTable/MasterTable';
import InputData from './components/InputData/InputData';
import ManualSample from './components/ManualSample/ManualSample';
import UserAdmin from './components/UserAdmin/UserAdmin';
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
          <Route path="/" element={<Navigate to="/input-data" />} />
          <Route path="/master-tables" element={<MasterTable />} />
          <Route path="/input-data" element={<InputData />} />
          <Route path="/manual-sample" element={<ManualSample />} />
          <Route path="/user-admin" element={<UserAdmin />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
```

### 4. src/components/Layout/Sidebar.tsx
```typescript
import { Link, useLocation } from 'react-router-dom';

interface MenuItem {
  path: string;
  label: string;
}

const menuItems: MenuItem[] = [
  { path: '/master-tables', label: 'Master Tables' },
  { path: '/input-data', label: 'Input Data' },
  { path: '/manual-sample', label: 'Manual Sample' },
  { path: '/user-admin', label: 'User Admin' },
];

function Sidebar() {
  const location = useLocation();

  return (
    <div style={{
      width: '200px',
      backgroundColor: '#2c3e50',
      color: 'white',
      padding: '20px 0',
      minHeight: '100vh'
    }}>
      <div style={{ padding: '0 20px', marginBottom: '30px' }}>
        <h2 style={{ fontSize: '20px', margin: 0 }}>LIMS @ INC </h2>
      </div>
      <nav>
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            style={{
              display: 'block',
              padding: '15px 20px',
              color: 'white',
              textDecoration: 'none',
              backgroundColor: location.pathname === item.path ? '#34495e' : 'transparent',
              transition: 'background-color 0.3s'
            }}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  );
}

export default Sidebar;
```

### 5. src/components/Layout/Layout.tsx
```typescript
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  onLogout: () => void;
}

function Layout({ children, onLogout }: LayoutProps) {
  return (
    <div className="app">
      <Sidebar />
      <div className="main-content">
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '20px' }}>
          <button className="btn btn-secondary" onClick={onLogout}>
            Sign Out
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export default Layout;
```

### 6. src/components/Login/Login.tsx
```typescript
import { useState } from 'react';
import { apiService } from '../../services/api';

interface LoginProps {
  onLogin: () => void;
}

function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [retypePassword, setRetypePassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await apiService.login(username, password);
      onLogin();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  const handleSavePassword = () => {
    if (newPassword !== retypePassword) {
      setError('Passwords do not match');
      return;
    }
    // TODO: Implement password change
    setShowNewPassword(false);
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>LIMS @ INC </h1>
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>User Name</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary btn-full">
            Sign In
          </button>
        </form>

        {showNewPassword && (
          <>
            <div className="form-group" style={{ marginTop: '20px' }}>
              <label>New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Retype Password</label>
              <input
                type="password"
                value={retypePassword}
                onChange={(e) => setRetypePassword(e.target.value)}
              />
            </div>

            <button
              className="btn btn-primary btn-full"
              onClick={handleSavePassword}
            >
              Save Password
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default Login;
```

## Continued in Part 2...

### 7. Master Table Component (src/components/MasterTable/MasterTable.tsx)

This component should:
- Display a dropdown to select table type
- Show AG-Grid with downloaded data
- Provide Download button to export to Excel
- Provide Upload button to import from Excel

Key implementation:
- Use AG-Grid's `autoSizeColumns` for dynamic column sizing
- Handle file download using `apiService.downloadMasterData()`
- Handle file upload using `apiService.uploadMasterData()`
- Display validation errors from upload endpoint

### 8. Input Data Component (src/components/InputData/InputData.tsx)

This component should:
- Display date picker
- Show two panels: Sample List (left) and Sample Details (right)
- Color-code sample numbers (green=complete, orange=incomplete)
- Show measurement grid with quality info
- Provide buttons: GetData, Update, COA, COC, C of Day

Key features:
- When user clicks GetData, call `/api/samples/create-sample` then `/api/samples/get_samples`
- Maintain selected sample state
- Enable/disable certificate buttons based on sample.coa, sample.coc, sample.day_coa flags
- Use AG-Grid for both sample list and measurement grid
- Validate measurements are within min/max range before update

### 9. Manual Sample Component (src/components/ManualSample/ManualSample.tsx)

This component should:
- Display date picker
- Show AG-Grid with manual samples for selected date
- Provide form to create/edit manual samples
- Include dropdowns for Sample Point, Product, Quality
- Buttons: Select, New, Save, Delete

Key implementation:
- Load dropdowns from `/api/master-data/sample-points`, `/products`, `/qualities`
- On Select, populate form with selected sample data
- On New, clear form and set create mode
- On Save, call create or update endpoint based on mode
- On Delete, call delete endpoint

### 10. User Administration Component (src/components/UserAdmin/UserAdmin.tsx)

This component should:
- Show grid of users
- Form to create/edit users
- Checkboxes for Active and Administrator
- File upload for signature
- Grid showing access permissions
- Buttons: New, Save, Reset Password, Load Image

Key features:
- Load users from `/api/users/`
- Load access permissions from `/api/users/{id}/access`
- Handle signature upload to `/api/users/{id}/signature`
- Show access grid with checkboxes for each permission

## FastAPI Static File Serving

Add to `main.py`:

```python
from fastapi.staticfiles import StaticFiles

# After all router registrations
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

## Running the Application

1. **Development**:
   - Frontend: `cd frontend && npm run dev` (runs on http://localhost:5173)
   - Backend: `python main.py` (runs on http://localhost:8000)

2. **Production**:
   - Build frontend: `cd frontend && npm run build`
   - Run backend: `python main.py`
   - Access app at http://localhost:8000

## Next Steps

1. Install frontend dependencies
2. Create the remaining component files
3. Test each component individually
4. Integrate with backend
5. Build and deploy

## Additional Resources

- AG-Grid React Documentation: https://www.ag-grid.com/react-data-grid/
- React Router Documentation: https://reactrouter.com/
- Axios Documentation: https://axios-http.com/
