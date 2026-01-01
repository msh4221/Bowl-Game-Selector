const API_BASE = 'http://localhost:8000';

class APIClient {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.clearToken();
      window.location.reload();
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Auth
  async login(password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async verifyToken() {
    if (!this.token) return false;
    try {
      await this.request('/auth/verify');
      return true;
    } catch {
      return false;
    }
  }

  logout() {
    this.clearToken();
  }

  // Games
  async getGames() {
    return this.request('/games/');
  }

  async createGame(game) {
    return this.request('/games/', {
      method: 'POST',
      body: JSON.stringify(game),
    });
  }

  async updateGame(gameId, updates) {
    return this.request(`/games/${gameId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteGame(gameId) {
    return this.request(`/games/${gameId}`, {
      method: 'DELETE',
    });
  }

  // Picks
  async getUsers() {
    return this.request('/picks/users');
  }

  async getPicks() {
    return this.request('/picks/');
  }

  async submitPick(gameId, userName, pickedTeam) {
    return this.request('/picks/', {
      method: 'POST',
      body: JSON.stringify({
        game_id: gameId,
        user_name: userName,
        picked_team: pickedTeam,
      }),
    });
  }

  async getLeaderboard() {
    return this.request('/picks/leaderboard');
  }

  // Archive
  async getArchivedSeasons() {
    return this.request('/archive/');
  }

  async getArchivedSeason(year) {
    return this.request(`/archive/${year}`);
  }

  async archiveCurrentSeason() {
    return this.request('/archive/create', {
      method: 'POST',
    });
  }

  // Admin
  async importGames() {
    return this.request('/admin/import-games', {
      method: 'POST',
    });
  }

  async refreshOdds() {
    return this.request('/admin/refresh-odds', {
      method: 'POST',
    });
  }

  async getApiStatus() {
    return this.request('/admin/api-status');
  }
}

export const api = new APIClient();
export default api;
