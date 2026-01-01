import { useState, useEffect } from 'react';
import api from '../api/client';

function GameList({ selectedUser, onPickMade }) {
  const [games, setGames] = useState([]);
  const [picks, setPicks] = useState({});
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [gamesData, picksData, usersData] = await Promise.all([
        api.getGames(),
        api.getPicks(),
        api.getUsers()
      ]);

      setGames(gamesData);
      setUsers(usersData);

      const picksMap = {};
      picksData.forEach(pick => {
        if (!picksMap[pick.game_id]) {
          picksMap[pick.game_id] = {};
        }
        picksMap[pick.game_id][pick.user_name] = pick;
      });
      setPicks(picksMap);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePick = async (gameId, userName, team) => {
    if (userName !== selectedUser) return;
    try {
      await api.submitPick(gameId, userName, team);
      await loadData();
      if (onPickMade) onPickMade();
    } catch (err) {
      alert(err.message);
    }
  };

  const formatGameTime = (dateStr) => {
    if (!dateStr) return 'TBD';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getSpreadDisplay = (spread) => {
    if (!spread) return '-';
    return spread > 0 ? `+${spread}` : spread.toString();
  };

  const truncateTeam = (name, maxLen = 8) => {
    if (!name) return '';
    if (name.length <= maxLen) return name;
    return name.substring(0, maxLen - 1) + '…';
  };

  if (loading) {
    return <div>Loading games...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (games.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <p>No games yet. Use the Admin panel to import games.</p>
      </div>
    );
  }

  const playoffGames = games.filter(g => g.is_playoff);
  const bowlGames = games.filter(g => !g.is_playoff);

  const renderSpreadsheet = (gamesList, title) => {
    if (gamesList.length === 0) return null;

    return (
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>{title}</h2>
        <div className="spreadsheet-container">
          <table className="picks-spreadsheet">
            <thead>
              <tr>
                <th className="game-col">Bowl</th>
                <th className="matchup-col">Matchup</th>
                <th className="spread-col">Line</th>
                <th className="time-col">Kickoff</th>
                {users.map(user => (
                  <th key={user.id} className={`pick-col ${user.name === selectedUser ? 'current-user' : ''}`}>
                    {user.name}
                  </th>
                ))}
                <th className="winner-col">Result</th>
              </tr>
            </thead>
            <tbody>
              {gamesList.map(game => {
                const isLocked = game.is_locked;

                return (
                  <tr key={game.id} className={isLocked ? 'locked-row' : ''}>
                    <td className="game-col">{game.bowl_name}</td>
                    <td className="matchup-col">
                      <div className="matchup-display">
                        <span className="away-team">{game.away_team}</span>
                        <span className="vs-text"> @ </span>
                        <span className="home-team">{game.home_team}</span>
                      </div>
                    </td>
                    <td className="spread-col">{getSpreadDisplay(game.spread)}</td>
                    <td className="time-col">
                      {formatGameTime(game.game_time)}
                      {isLocked && <span className="lock-icon">🔒</span>}
                    </td>
                    {users.map(user => {
                      const pick = picks[game.id]?.[user.name];
                      const isCurrentUser = user.name === selectedUser;
                      const canClick = isCurrentUser && !isLocked;

                      return (
                        <td key={user.id} className={`pick-col ${isCurrentUser ? 'current-user' : ''}`}>
                          <div className="pick-cell">
                            <button
                              className={`team-btn ${
                                pick?.picked_team === game.away_team ? 'selected' : ''
                              } ${
                                game.winner && pick?.picked_team === game.away_team
                                  ? (pick.picked_team === game.winner ? 'correct' : 'incorrect')
                                  : ''
                              } ${
                                game.winner === game.away_team ? 'winner-team' : ''
                              } ${
                                !canClick ? 'locked' : ''
                              }`}
                              onClick={() => canClick && handlePick(game.id, user.name, game.away_team)}
                              title={`${game.away_team}${canClick ? ' - Click to pick' : ''}`}
                              disabled={!canClick}
                            >
                              {truncateTeam(game.away_team)}
                            </button>
                            <button
                              className={`team-btn ${
                                pick?.picked_team === game.home_team ? 'selected' : ''
                              } ${
                                game.winner && pick?.picked_team === game.home_team
                                  ? (pick.picked_team === game.winner ? 'correct' : 'incorrect')
                                  : ''
                              } ${
                                game.winner === game.home_team ? 'winner-team' : ''
                              } ${
                                !canClick ? 'locked' : ''
                              }`}
                              onClick={() => canClick && handlePick(game.id, user.name, game.home_team)}
                              title={`${game.home_team}${canClick ? ' - Click to pick' : ''}`}
                              disabled={!canClick}
                            >
                              {truncateTeam(game.home_team)}
                            </button>
                          </div>
                        </td>
                      );
                    })}
                    <td className="winner-col">
                      {game.winner ? (
                        <span className="winner-badge">
                          {truncateTeam(game.winner, 10)}
                          {game.away_score !== null && game.home_score !== null && (
                            <span className="score">{game.away_score}-{game.home_score}</span>
                          )}
                        </span>
                      ) : (
                        <span className="pending">-</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="picks-instructions">
        <p>Click a team button in <strong>your column</strong> to make your pick. Picks lock at kickoff.</p>
        <p>Currently picking as: <strong>{selectedUser}</strong></p>
      </div>
      {renderSpreadsheet(playoffGames, 'Playoff Games')}
      {renderSpreadsheet(bowlGames, 'Bowl Games')}
    </div>
  );
}

export default GameList;
