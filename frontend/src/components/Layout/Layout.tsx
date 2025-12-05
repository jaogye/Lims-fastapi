import Sidebar from './Sidebar';
import { useUser } from '../../contexts/UserContext';

interface LayoutProps {
  children: React.ReactNode;
  onLogout: () => void;
}

function Layout({ children, onLogout }: LayoutProps) {
  const { user } = useUser();

  return (
    <div className="app">
      <Sidebar />
      <div className="main-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#2c3e50' }}>
            {user && `User: ${user.code}`}
          </div>
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
