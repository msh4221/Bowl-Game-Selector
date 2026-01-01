import { useState, useEffect } from 'react';
import api from './api/client';
import Login from './components/Login';
import GameList from './components/GameList';
import Leaderboard from './components/Leaderboard';
import ArchiveViewer from './components/ArchiveViewer';
import AdminPanel from './components/AdminPanel';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('games');
  const [selectedUser, setSelectedUser] = useState('');
  const [users, setUsers] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadUsers();
    }
  }, [isAuthenticated]);

  const checkAuth = async () => {
    const isValid = await api.verifyToken();
    setIsAuthenticated(isValid);
    setLoading(false);
  };

  const loadUsers = async () => {
    try {
      const userData = await api.getUsers();
      setUsers(userData);
      if (userData.length > 0 && !selectedUser) {
        setSelectedUser(userData[0].name);
      }
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const handleLogin = async (password) => {
    await api.login(password);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
  };

  const refreshData = () => {
    setRefreshKey(prev => prev + 1);
  };

  if (loading) {
    return (
      <div className="login-container">
        <div className="login-box">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="container">
      <header className="header">
        <h1>Annual Bowl Picks</h1>
        <div className="header-actions">
          <button className="btn-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <div className="user-selector">
        <label>Picking as:</label>
        <select
          value={selectedUser}
          onChange={(e) => setSelectedUser(e.target.value)}
        >
          {users.map(user => (
            <option key={user.id} value={user.name}>
              {user.name}
            </option>
          ))}
        </select>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'games' ? 'active' : ''}`}
          onClick={() => setActiveTab('games')}
        >
          Games
        </button>
        <button
          className={`tab ${activeTab === 'leaderboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('leaderboard')}
        >
          Leaderboard
        </button>
        <button
          className={`tab ${activeTab === 'archive' ? 'active' : ''}`}
          onClick={() => setActiveTab('archive')}
        >
          Archives
        </button>
        <button
          className={`tab ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => setActiveTab('admin')}
        >
          Admin
        </button>
      </div>

      {activeTab === 'games' && (
        <GameList
          key={refreshKey}
          selectedUser={selectedUser}
          onPickMade={refreshData}
        />
      )}
      {activeTab === 'leaderboard' && (
        <Leaderboard key={refreshKey} />
      )}
      {activeTab === 'archive' && (
        <ArchiveViewer />
      )}
      {activeTab === 'admin' && (
        <AdminPanel onDataChange={refreshData} />
      )}
    </div>
  );
}

export default App;
