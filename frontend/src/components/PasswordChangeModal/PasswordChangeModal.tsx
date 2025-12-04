import { useState } from 'react';
import { apiService } from '../../services/api';
import './PasswordChangeModal.css';

interface PasswordChangeModalProps {
  isOpen: boolean;
  onPasswordChanged: () => void;
}

function PasswordChangeModal({ isOpen, onPasswordChanged }: PasswordChangeModalProps) {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!oldPassword || !newPassword || !confirmPassword) {
      setError('All fields are required');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters long');
      return;
    }

    if (newPassword === oldPassword) {
      setError('New password must be different from the current password');
      return;
    }

    setLoading(true);

    try {
      await apiService.changePassword({
        old_password: oldPassword,
        new_password: newPassword
      });

      // Success - notify parent component
      onPasswordChanged();

      // Reset form
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to change password. Please check your current password and try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="password-modal-overlay">
      <div className="password-modal">
        <div className="password-modal-header">
          <h2>Change Password Required</h2>
          <p className="password-modal-subtitle">
            Your password has been reset by an administrator. For security reasons, you must change your password before continuing.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="password-modal-form">
          {error && (
            <div className="password-modal-error">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="oldPassword">Current (Temporary) Password *</label>
            <input
              id="oldPassword"
              type="password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              disabled={loading}
              required
              autoComplete="current-password"
              placeholder="Enter your temporary password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="newPassword">New Password *</label>
            <input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              disabled={loading}
              required
              autoComplete="new-password"
              placeholder="Enter new password (min. 6 characters)"
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password *</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
              required
              autoComplete="new-password"
              placeholder="Re-enter new password"
              minLength={6}
            />
          </div>

          <div className="password-modal-footer">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Changing Password...' : 'Change Password'}
            </button>
          </div>

          <div className="password-modal-info">
            <strong>Password Requirements:</strong>
            <ul>
              <li>Must be at least 6 characters long</li>
              <li>Must be different from your current password</li>
              <li>Should be unique and not used elsewhere</li>
            </ul>
          </div>
        </form>
      </div>
    </div>
  );
}

export default PasswordChangeModal;
