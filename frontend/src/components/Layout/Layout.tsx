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
