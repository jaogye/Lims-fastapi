import { Link, useLocation } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';

interface MenuItem {
  path: string;
  label: string;
  requiredOption: string;
}

const menuItems: MenuItem[] = [
  { path: '/master-tables', label: 'Master Tables', requiredOption: 'Master Tables' },
  { path: '/input-data', label: 'Input Data', requiredOption: 'Input Data' },
  { path: '/manual-sample', label: 'Manual Sample', requiredOption: 'Manual Sample' },
  { path: '/report-generation', label: 'Report Gen', requiredOption: 'Report Gen' },
  { path: '/view-jobs', label: 'View Jobs', requiredOption: 'View Jobs' },
  { path: '/user-admin', label: 'User Admin', requiredOption: 'User Admin' },
];

function Sidebar() {
  const location = useLocation();
  const { user } = useUser();

  // Filter menu items based on user permissions
  // Admins see all options, regular users only see options they have access to
  const visibleMenuItems = menuItems.filter((item) => {
    if (!user) return false;
    if (user.is_admin) return true;
    return user.options.some(option => option.trim() === item.requiredOption);
  });

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
        {visibleMenuItems.map((item) => (
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
