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
