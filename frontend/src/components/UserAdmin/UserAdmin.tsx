import { useState, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, ICellRendererParams } from 'ag-grid-community';
import { apiService } from '../../services/api';
import type { UserResponse, UserCreateRequest } from '../../types';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

interface MenuOption {
  id: number;
  name: string;
}

function UserAdmin() {
  // State
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [menuOptions, setMenuOptions] = useState<MenuOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');

  // Form state
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<UserCreateRequest>({
    code: '',
    name: '',
    password: '',
    is_admin: false,
    active: true,
    email: '',
    reset_password: false,
    options: []
  });
  const [signatureFile, setSignatureFile] = useState<File | null>(null);
  const [signaturePreview, setSignaturePreview] = useState<string>('');
  const [hasExistingSignature, setHasExistingSignature] = useState<boolean>(false);

  const gridRef = useRef<AgGridReact>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-size all columns
  const autoSizeAll = (skipHeader = false) => {
    if (gridRef.current?.api) {
      const allColumnIds: string[] = [];
      gridRef.current.api.getColumns()?.forEach((column) => {
        allColumnIds.push(column.getId());
      });
      gridRef.current.api.autoSizeColumns(allColumnIds, skipHeader);
    }
  };

  // Load data on mount
  useEffect(() => {
    loadUsers();
    loadMenuOptions();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await apiService.getUsers();
      setUsers(data);
      setTimeout(() => autoSizeAll(false), 100);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load users');
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const loadMenuOptions = async () => {
    try {
      const options = await apiService.getMenuOptions();
      setMenuOptions(options);
    } catch (err: any) {
      console.error('Failed to load menu options:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.code || !formData.name || (!editingId && !formData.password)) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      let savedUser: UserResponse;

      if (editingId) {
        // Update existing user
        savedUser = await apiService.updateUser(editingId, formData);
        setSuccessMessage('User updated successfully');
      } else {
        // Create new user
        savedUser = await apiService.createUser(formData);
        setSuccessMessage('User created successfully');
      }

      // Upload signature if provided
      if (signatureFile) {
        await apiService.uploadSignature(savedUser.id, signatureFile);
      }

      // Reset form and reload users
      resetForm();
      await loadUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save user');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = async (user: UserResponse) => {
    setEditingId(user.id);
    setFormData({
      code: user.code,
      name: user.name,
      password: '', // Don't show existing password
      is_admin: user.is_admin,
      active: user.status,
      email: user.email || '',
      reset_password: false,
      options: user.options
    });

    // Load signature if exists - always try to load
    setHasExistingSignature(false);
    setSignaturePreview('');
    try {
      const blob = await apiService.getSignature(user.id);
      if (blob && blob.size > 0) {
        const url = URL.createObjectURL(blob);
        setSignaturePreview(url);
        setHasExistingSignature(true);
      }
    } catch (err) {
      // No signature or failed to load - that's okay
      console.log('No signature found for user');
    }

    // Scroll to form
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDelete = async (userId: number) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      await apiService.deleteUser(userId);
      setSuccessMessage('User deleted successfully');
      await loadUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      code: '',
      name: '',
      password: '',
      is_admin: false,
      active: true,
      email: '',
      reset_password: false,
      options: []
    });
    setEditingId(null);
    setSignatureFile(null);
    setSignaturePreview('');
    setHasExistingSignature(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleCancel = () => {
    resetForm();
    setError('');
  };

  const handleInputChange = (field: keyof UserCreateRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleOptionToggle = (optionName: string) => {
    setFormData(prev => ({
      ...prev,
      options: prev.options.includes(optionName)
        ? prev.options.filter(o => o !== optionName)
        : [...prev.options, optionName]
    }));
  };

  const handleSignatureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file (PNG, JPG, etc.)');
        return;
      }

      setSignatureFile(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setSignaturePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDeleteSignature = async () => {
    if (!editingId || !window.confirm('Are you sure you want to delete this signature?')) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      await apiService.deleteSignature(editingId);
      setSignaturePreview('');
      setHasExistingSignature(false);
      setSignatureFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setSuccessMessage('Signature deleted successfully');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete signature');
    } finally {
      setLoading(false);
    }
  };

  // Action buttons cell renderer
  const ActionButtonsRenderer = (props: ICellRendererParams<UserResponse>) => {
    return (
      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          className="btn btn-secondary"
          onClick={() => handleEdit(props.data!)}
          style={{ padding: '4px 12px', fontSize: '12px' }}
        >
          Edit
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => handleDelete(props.data!.id)}
          style={{ padding: '4px 12px', fontSize: '12px', backgroundColor: '#d32f2f', borderColor: '#d32f2f' }}
        >
          Delete
        </button>
      </div>
    );
  };

  const columnDefs: ColDef<UserResponse>[] = [
    { field: 'code', headerName: 'Code', sortable: true, filter: true, resizable: true, width: 120 },
    { field: 'name', headerName: 'Name', sortable: true, filter: true, resizable: true, width: 200 },
    { field: 'email', headerName: 'Email', sortable: true, filter: true, resizable: true, flex: 1 },
    {
      field: 'is_admin',
      headerName: 'Admin',
      sortable: true,
      filter: true,
      resizable: true,
      width: 90,
      valueFormatter: (params) => params.value ? 'Yes' : 'No'
    },
    {
      field: 'status',
      headerName: 'Active',
      sortable: true,
      filter: true,
      resizable: true,
      width: 90,
      valueFormatter: (params) => params.value ? 'Yes' : 'No'
    },
    {
      field: 'options',
      headerName: 'Permissions',
      sortable: false,
      filter: false,
      resizable: true,
      width: 300,
      valueFormatter: (params) => params.value?.join(', ') || 'None'
    },
    {
      headerName: 'Actions',
      cellRenderer: ActionButtonsRenderer,
      width: 180,
      sortable: false,
      filter: false,
      resizable: false,
      pinned: 'right'
    }
  ];

  return (
    <div>
      <div className="page-header">
        <h1>User Administration</h1>
        <p>Manage system users and their access permissions</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      {/* Form Section */}
      <div style={{
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        backgroundColor: '#f9f9f9'
      }}>
        <h2 style={{ marginBottom: '20px', fontSize: '18px' }}>
          {editingId ? 'Edit User' : 'Create New User'}
        </h2>

        <form onSubmit={handleSubmit}>
          {/* Basic Information */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px', marginBottom: '15px' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="code">Username *</label>
              <input
                id="code"
                type="text"
                value={formData.code}
                onChange={(e) => handleInputChange('code', e.target.value)}
                disabled={loading || !!editingId}
                required
                placeholder="User code/username"
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="name">Full Name *</label>
              <input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                disabled={loading}
                required
                placeholder="Full name"
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="password">Password {!editingId && '*'}</label>
              <input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                disabled={loading || (editingId && formData.reset_password)}
                required={!editingId}
                placeholder={editingId ? 'Leave blank to keep current' : 'Password'}
              />
              {editingId && formData.reset_password && (
                <small style={{ color: '#666', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                  Password field disabled - a temporary password will be generated and emailed to the user
                </small>
              )}
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                value={formData.email || ''}
                onChange={(e) => handleInputChange('email', e.target.value)}
                disabled={loading}
                placeholder="user@example.com"
              />
              {editingId && !formData.email && (
                <small style={{ color: '#e67e22', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                  Email required for password reset functionality
                </small>
              )}
            </div>
          </div>

          {/* Checkboxes */}
          <div style={{ display: 'flex', gap: '20px', marginBottom: '15px' }}>
            <div className="form-group" style={{ marginBottom: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                id="is_admin"
                type="checkbox"
                checked={formData.is_admin}
                onChange={(e) => handleInputChange('is_admin', e.target.checked)}
                disabled={loading}
                style={{ width: 'auto', margin: 0 }}
              />
              <label htmlFor="is_admin" style={{ margin: 0, cursor: 'pointer' }}>
                Administrator
              </label>
            </div>

            <div className="form-group" style={{ marginBottom: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                id="active"
                type="checkbox"
                checked={formData.active}
                onChange={(e) => handleInputChange('active', e.target.checked)}
                disabled={loading}
                style={{ width: 'auto', margin: 0 }}
              />
              <label htmlFor="active" style={{ margin: 0, cursor: 'pointer' }}>
                Active
              </label>
            </div>

            {editingId && (
              <div className="form-group" style={{ marginBottom: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  id="reset_password"
                  type="checkbox"
                  checked={formData.reset_password || false}
                  onChange={(e) => handleInputChange('reset_password', e.target.checked)}
                  disabled={loading || !formData.email}
                  style={{ width: 'auto', margin: 0 }}
                />
                <label htmlFor="reset_password" style={{ margin: 0, cursor: formData.email ? 'pointer' : 'not-allowed', color: formData.email ? 'inherit' : '#ccc' }}>
                  Reset Password (Email temporary password)
                </label>
              </div>
            )}
          </div>

          {/* Permissions */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Access Permissions:
            </label>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: '8px',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              backgroundColor: 'white'
            }}>
              {menuOptions.map((option) => (
                <div key={option.id} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <input
                    type="checkbox"
                    id={`option-${option.id}`}
                    checked={formData.options.includes(option.name)}
                    onChange={() => handleOptionToggle(option.name)}
                    disabled={loading}
                    style={{ width: 'auto', margin: 0 }}
                  />
                  <label htmlFor={`option-${option.id}`} style={{ margin: 0, cursor: 'pointer', fontSize: '14px' }}>
                    {option.name}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Signature Upload */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Signature (PNG, JPG):
            </label>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', marginBottom: '10px' }}>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleSignatureChange}
                disabled={loading}
                style={{ flex: 1 }}
              />
              {editingId && (hasExistingSignature || signaturePreview) && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleDeleteSignature}
                  disabled={loading}
                  style={{ padding: '8px 16px', backgroundColor: '#d32f2f', borderColor: '#d32f2f', whiteSpace: 'nowrap' }}
                >
                  Remove Signature
                </button>
              )}
            </div>

            {signaturePreview && (
              <div style={{
                border: '1px solid #ddd',
                borderRadius: '4px',
                padding: '10px',
                backgroundColor: 'white',
                maxWidth: '300px'
              }}>
                <p style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 'bold' }}>
                  {hasExistingSignature && !signatureFile ? 'Current Signature:' : 'Preview:'}
                </p>
                <img
                  src={signaturePreview}
                  alt="Signature preview"
                  style={{ maxWidth: '100%', height: 'auto', display: 'block' }}
                />
              </div>
            )}
          </div>

          {/* Form Buttons */}
          <div className="button-group">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Processing...' : (editingId ? 'Update User' : 'Create User')}
            </button>

            {editingId && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleCancel}
                disabled={loading}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Grid Section */}
      <div>
        <h2 style={{ marginBottom: '10px', fontSize: '18px' }}>
          Users ({users.length})
        </h2>

        <div className="ag-theme-alpine" style={{ height: '500px', width: '100%' }}>
          <AgGridReact
            ref={gridRef}
            rowData={users}
            columnDefs={columnDefs}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
            }}
            animateRows={true}
            onGridReady={() => {
              setTimeout(() => autoSizeAll(false), 100);
            }}
            onFirstDataRendered={() => {
              autoSizeAll(false);
            }}
          />
        </div>

        {users.length > 0 && (
          <div style={{ marginTop: '10px', color: '#666' }}>
            Showing {users.length} user{users.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}

export default UserAdmin;
