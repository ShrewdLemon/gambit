import React, { useState, useEffect, useRef } from 'react';
import { Chessboard } from 'react-chessboard';
import { Chess } from 'chess.js';
import './App.css';

function App() {
  const [game, setGame] = useState(new Chess());
  const [stockfishLevel, setStockfishLevel] = useState(10); // 0-20 skill level
  const [currentPlayer, setCurrentPlayer] = useState('w');
  const [whiteTime, setWhiteTime] = useState(300); // 5 minutes in seconds
  const [blackTime, setBlackTime] = useState(300);
  const [isTimeRunning, setIsTimeRunning] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  
  const timerRef = useRef(null);

  // Timer effect
  useEffect(() => {
    if (isTimeRunning) {
      timerRef.current = setInterval(() => {
        if (currentPlayer === 'w') {
          setWhiteTime(prev => {
            if (prev <= 0) {
              clearInterval(timerRef.current);
              alert("Black wins on time!");
              return 0;
            }
            return prev - 1;
          });
        } else {
          setBlackTime(prev => {
            if (prev <= 0) {
              clearInterval(timerRef.current);
              alert("White wins on time!");
              return 0;
            }
            return prev - 1;
          });
        }
      }, 1000);
    }
    
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [currentPlayer, isTimeRunning]);

  async function getAIMove(fen) {
    try {
      setIsThinking(true);
      const response = await fetch('http://localhost:5000/api/best-move', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fen: fen,
          skill_level: stockfishLevel,
          move_time: 1000 // 1 second
        }),
      });
      
      const data = await response.json();
      setIsThinking(false);
      
      if (data.success && data.bestMove) {
        const from = data.bestMove.substring(0, 2);
        const to = data.bestMove.substring(2, 4);
        makeMove(from, to);
      } else {
        console.error('Error getting AI move:', data.error);
      }
    } catch (error) {
      setIsThinking(false);
      console.error('Error communicating with API:', error);
    }
  }

  function makeMove(from, to) {
    try {
      const gameCopy = new Chess(game.fen());
      const move = gameCopy.move({
        from,
        to,
        promotion: 'q' // Always promote to queen for simplicity
      });
      
      if (move) {
        setGame(gameCopy);
        // Start the timer if it's not running
        if (!isTimeRunning) {
          setIsTimeRunning(true);
        }
        
        // Update current player
        setCurrentPlayer(gameCopy.turn());
        
        // If game over, alert the result
        if (gameCopy.isGameOver()) {
          if (gameCopy.isCheckmate()) {
            alert(`Checkmate! ${gameCopy.turn() === 'w' ? 'Black' : 'White'} wins!`);
          } else if (gameCopy.isDraw()) {
            alert("Game is a draw!");
          }
          setIsTimeRunning(false);
        } else if (gameCopy.turn() === 'b' && currentPlayer === 'w') {
          // If it's AI's turn, get best move
          getAIMove(gameCopy.fen());
        }
        
        return true;
      }
      return false;
    } catch (error) {
      console.error("Invalid move:", error);
      return false;
    }
  }

  function onDrop(sourceSquare, targetSquare) {
    // Only allow moves for the player's turn
    if ((currentPlayer === 'w' && game.turn() === 'b') || 
        (currentPlayer === 'b' && game.turn() === 'w')) {
      return false;
    }
    
    // Don't allow moves while AI is thinking
    if (isThinking) {
      return false;
    }
    
    return makeMove(sourceSquare, targetSquare);
  }

  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  }
  
  function resetGame() {
    setGame(new Chess());
    setCurrentPlayer('w');
    setWhiteTime(300);
    setBlackTime(300);
    setIsTimeRunning(false);
    setIsThinking(false);
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  }

  return (
    <div className="App">
      <header className="App-header" style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#282c34', color: 'white' }}>
        <h1>Self-Aware Chess Battlefield</h1>
      </header>
      
      {/* Timer display */}
      <div style={{ display: 'flex', justifyContent: 'space-around', width: '500px', margin: '0 auto 20px auto' }}>
        <div style={{ 
          padding: '10px', 
          backgroundColor: currentPlayer === 'w' ? '#4d8ecc' : '#333', 
          borderRadius: '4px',
          color: 'white'
        }}>
          White: {formatTime(whiteTime)}
        </div>
        <div style={{ 
          padding: '10px', 
          backgroundColor: currentPlayer === 'b' ? '#4d8ecc' : '#333', 
          borderRadius: '4px',
          color: 'white'
        }}>
          Black: {formatTime(blackTime)}
        </div>
      </div>
      
      {/* AI thinking indicator */}
      {isThinking && (
        <div style={{ textAlign: 'center', margin: '10px 0' }}>
          AI is thinking...
        </div>
      )}
      
      {/* Chess board */}
      <div style={{ width: '500px', margin: '0 auto' }}>
        <Chessboard 
          position={game.fen()} 
          onPieceDrop={onDrop} 
          boardOrientation="white"
        />
      </div>
      
      {/* Controls */}
      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <button 
          onClick={resetGame} 
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#4d8ecc', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Reset Game
        </button>
        
        <div style={{ marginTop: '10px' }}>
          <label htmlFor="skill-level">AI Skill Level: </label>
          <input 
            type="range" 
            id="skill-level" 
            min="0" 
            max="20" 
            value={stockfishLevel}
            onChange={(e) => setStockfishLevel(parseInt(e.target.value))}
          />
          <span style={{ marginLeft: '10px' }}>{stockfishLevel}</span>
        </div>
      </div>
    </div>
  );
}

export default App;