import { useState } from 'react';

function Login({ onLogin }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await onLogin(password);
    } catch (err) {
      setError(err.message || 'Incorrect password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>Bowl Picks</h1>
        <p>Enter the family password to continue</p>

        <form onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />

          <button type="submit" disabled={loading || !password}>
            {loading ? 'Logging in...' : 'Enter'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
