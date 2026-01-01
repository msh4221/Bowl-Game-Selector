import { useState, useEffect } from 'react';
import api from '../api/client';

function GameList({ selectedUser, onPickMade }) {
  const [games, setGames] = useState([]);
  const [picks, setPicks] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [gamesData, picksData] = await Promise.all([
        api.getGames(),
        api.getPicks()
      ]);

      setGames(gamesData);

      // Organize picks by game_id and user
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

  const handlePick = async (gameId, team) => {
    try {
      await api.submitPick(gameId, selectedUser, team);
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

  const getSpreadDisplay = (game, team) => {
    if (!game.spread) return '';

    if (team === game.home_team) {
      return game.spread > 0 ? `+${game.spread}` : game.spread.toString();
    } else {
      const awaySpread = -game.spread;
      return awaySpread > 0 ? `+${awaySpread}` : awaySpread.toString();
    }
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

  // Group games by playoff status
  const playoffGames = games.filter(g => g.is_playoff);
  const bowlGames = games.filter(g => !g.is_playoff);

  const renderGameCard = (game) => {
    const userPick = picks[game.id]?.[selectedUser];
    const isLocked = game.is_locked;

    return (
      <div key={game.id} className="game-card">
        <div className="game-header">
          <span className="bowl-name">{game.bowl_name}</span>
          <span className="game-time">
            {formatGameTime(game.game_time)}
            {isLocked && <span className="lock-indicator"> (Locked)</span>}
          </span>
        </div>

        <div className="game-teams">
          <div
            className={`team ${
              userPick?.picked_team === game.away_team ? 'selected' : ''
            } ${
              game.winner === game.away_team ? 'winner' : ''
            } ${
              game.winner && game.winner !== game.away_team ? 'loser' : ''
            } ${
              isLocked ? 'locked' : ''
            }`}
            onClick={() => !isLocked && handlePick(game.id, game.away_team)}
          >
            <div className="team-name">{game.away_team}</div>
            <div className="team-spread">{getSpreadDisplay(game, game.away_team)}</div>
            {userPick?.picked_team === game.away_team && (
              <div className={`score-badge ${
                userPick.is_correct === true ? 'correct' :
                userPick.is_correct === false ? 'incorrect' : 'pending'
              }`}>
                {userPick.is_correct === true ? 'Correct' :
                 userPick.is_correct === false ? 'Wrong' : 'Your Pick'}
              </div>
            )}
          </div>

          <span className="vs-divider">VS</span>

          <div
            className={`team ${
              userPick?.picked_team === game.home_team ? 'selected' : ''
            } ${
              game.winner === game.home_team ? 'winner' : ''
            } ${
              game.winner && game.winner !== game.home_team ? 'loser' : ''
            } ${
              isLocked ? 'locked' : ''
            }`}
            onClick={() => !isLocked && handlePick(game.id, game.home_team)}
          >
            <div className="team-name">{game.home_team}</div>
            <div className="team-spread">{getSpreadDisplay(game, game.home_team)}</div>
            {userPick?.picked_team === game.home_team && (
              <div className={`score-badge ${
                userPick.is_correct === true ? 'correct' :
                userPick.is_correct === false ? 'incorrect' : 'pending'
              }`}>
                {userPick.is_correct === true ? 'Correct' :
                 userPick.is_correct === false ? 'Wrong' : 'Your Pick'}
              </div>
            )}
          </div>
        </div>

        {game.winner && (
          <div style={{ textAlign: 'center', marginTop: '1rem', color: '#10b981' }}>
            Winner: {game.winner}
            {game.home_score !== null && game.away_score !== null && (
              <span> ({game.away_score} - {game.home_score})</span>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      {playoffGames.length > 0 && (
        <>
          <h2>Playoff Games</h2>
          {playoffGames.map(renderGameCard)}
        </>
      )}

      {bowlGames.length > 0 && (
        <>
          <h2 style={{ marginTop: playoffGames.length > 0 ? '2rem' : 0 }}>Bowl Games</h2>
          {bowlGames.map(renderGameCard)}
        </>
      )}
    </div>
  );
}

export default GameList;
