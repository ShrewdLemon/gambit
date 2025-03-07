import React, { useState, useEffect, useRef } from 'react';
import Chess from 'chess.js';
import LoadingScreen from './LoadingScreen';
import GameSettings from './GameSettings';
import BattlefieldChessBoard from './BattlefieldChessBoard';
import Timer from './Timer';
import NarrativePanel from './NarrativePanel';
import ChessEngineService from '../services/ChessEngineService';

const App = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isSettings, setIsSettings] = useState(false);
  const [gameStarted, setGameStarted] = useState(false);
  const [currentPosition, setCurrentPosition] = useState('start');
  const [currentPlayer, setCurrentPlayer] = useState('white');
  const [whiteTime, setWhiteTime] = useState(300);
  const [blackTime, setBlackTime] = useState(300);
  const [initialTime, setInitialTime] = useState(300);
  const [selectedAI, setSelectedAI] = useState(null);
  const [pieceThoughts, setPieceThoughts] = useState({});
  const [narrativeHistory, setNarrativeHistory] = useState([]);
  const [battlefieldState, setBattlefieldState] = useState({
    intensity: 0.3,
    phase: 'opening'
  });
  
  const chess = useRef(new Chess());
  const timerInterval = useRef(null);

  useEffect(() => {
    // Simulate loading time
    const timer = setTimeout(() => {
      setIsLoading(false);
      setIsSettings(true);
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (gameStarted && !isLoading) {
      clearInterval(timerInterval.current);
      if (whiteTime > 0 && blackTime > 0) {
        timerInterval.current = setInterval(() => {
          if (currentPlayer === 'white') {
            setWhiteTime((prev) => prev - 1);
          } else {
            setBlackTime((prev) => prev - 1);
          }
        }, 1000);
      }
    }
    return () => clearInterval(timerInterval.current);
  }, [currentPlayer, gameStarted, whiteTime, blackTime, isLoading]);

  // Temporary implementation that doesn't require the backend yet
  const generateMockNarrative = (move, isCapture, isCheck) => {
    const intensities = ['low', 'medium', 'high'];
    const intensity = isCapture ? 'high' : isCheck ? 'medium' : 'low';
    
    const thoughts = [
      "I must secure this position!",
      "The battlefield shifts in our favor!",
      "A strategic advancement!",
      "This move will control key territory!",
      "Let me strike while they're vulnerable!"
    ];
    
    const descriptions = isCapture 
      ? ["A decisive capture!", "Enemy piece eliminated!", "A successful attack!"]
      : ["A strategic repositioning.", "Preparing for the next phase.", "Securing defensive lines."];
    
    const impacts = isCapture
      ? ["The battlefield erupts with tension!", "A momentary advantage in the conflict!", "The balance of power shifts!"]
      : ["The battlefield terrain shifts subtly.", "A quiet moment in the ongoing campaign.", "The armies continue their strategic dance."];
    
    return {
      piece_thought: thoughts[Math.floor(Math.random() * thoughts.length)],
      action_description: descriptions[Math.floor(Math.random() * descriptions.length)],
      battlefield_impact: impacts[Math.floor(Math.random() * impacts.length)],
      intensity
    };
  };

  // Function to update battlefield state based on game progress
  const updateBattlefieldState = () => {
    // Simple logic to determine game phase and intensity
    const moveCount = chess.current.history().length;
    let phase = 'opening';
    let intensity = 0.3;
    
    if (moveCount > 10 && moveCount <= 30) {
      phase = 'middlegame';
      intensity = 0.5 + (Math.random() * 0.2); // Some randomness
    } else if (moveCount > 30) {
      phase = 'endgame';
      intensity = 0.7 + (Math.random() * 0.3);
    }
    
    // More complex indicators could go here
    setBattlefieldState({
      phase,
      intensity
    });
  };

  const makeAIMove = async () => {
    try {
      // Get a random move for now (we'll replace with real AI later)
      const moves = chess.current.moves({ verbose: true });
      if (moves.length > 0) {
        // Simple "AI" - random legal move
        const randomIndex = Math.floor(Math.random() * moves.length);
        const move = moves[randomIndex];
        
        // Make the move
        chess.current.move(move);
        setCurrentPosition(chess.current.fen());
        setCurrentPlayer(chess.current.turn() === 'w' ? 'white' : 'black');
        
        // Update battlefield state
        updateBattlefieldState();
        
        // Generate narrative
        const isCapture = move.captured !== undefined;
        const isCheck = chess.current.in_check();
        const narrative = generateMockNarrative(move, isCapture, isCheck);
        
        // Add piece thought
        setPieceThoughts(prev => ({
          ...prev,
          [move.to]: narrative.piece_thought
        }));
        
        // Add to narrative history
        setNarrativeHistory(prev => [...prev, {
          move: `${move.piece.toUpperCase()}${move.from}-${move.to}`,
          narrative
        }]);
        
        // Clear thought bubble after 5 seconds
        setTimeout(() => {
          setPieceThoughts(prev => {
            const newThoughts = { ...prev };
            delete newThoughts[move.to];
            return newThoughts;
          });
        }, 5000);
        
        // Check for game end
        if (chess.current.game_over()) {
          handleGameEnd();
        }
      }
    } catch (error) {
      console.error('Error making AI move:', error);
    }
  };

  const handleMove = async (from, to) => {
    try {
      // Check if move is legal
      const moveObj = {
        from,
        to,
        promotion: 'q' // Always promote to queen for simplicity
      };
      
      const move = chess.current.move(moveObj);
      
      if (move) {
        // Update position
        setCurrentPosition(chess.current.fen());
        setCurrentPlayer(chess.current.turn() === 'w' ? 'white' : 'black');
        
        // Update battlefield state
        updateBattlefieldState();
        
        // Generate narrative
        const isCapture = move.captured !== undefined;
        const isCheck = chess.current.in_check();
        const narrative = generateMockNarrative(move, isCapture, isCheck);
        
        // Add piece thought
        setPieceThoughts(prev => ({
          ...prev,
          [to]: narrative.piece_thought
        }));
        
        // Add to narrative history
        setNarrativeHistory(prev => [...prev, {
          move: `${move.piece.toUpperCase()}${from}-${to}`,
          narrative
        }]);
        
        // Clear thought bubble after 5 seconds
        setTimeout(() => {
          setPieceThoughts(prev => {
            const newThoughts = { ...prev };
            delete newThoughts[to];
            return newThoughts;
          });
        }, 5000);
        
        // Check for game end
        if (chess.current.game_over()) {
          handleGameEnd();
        } else if (currentPlayer === 'white' && chess.current.turn() === 'b') {
          // Make AI move after a small delay
          setTimeout(() => makeAIMove(), 500);
        }
        
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error handling move:', error);
      return false;
    }
  };
  
  const handleGameEnd = () => {
    clearInterval(timerInterval.current);
    
    let result = '';
    if (chess.current.isCheckmate()) {
      result = `${currentPlayer === 'white' ? 'Black' : 'White'} wins by checkmate!`;
    } else if (chess.current.isDraw()) {
      if (chess.current.isStalemate()) {
        result = 'Draw by stalemate!';
      } else if (chess.current.isThreefoldRepetition()) {
        result = 'Draw by repetition!';
      } else if (chess.current.isInsufficientMaterial()) {
        result = 'Draw by insufficient material!';
      } else {
        result = 'Draw!';
      }
    }
    
    alert(`Battle concluded! ${result}`);
    setGameStarted(false);
    setIsSettings(true);
  };

  if (isLoading) {
    return <LoadingScreen onLoadComplete={() => { setIsLoading(false); setIsSettings(true); }} />;
  } else if (isSettings) {
    return (
      <GameSettings
        onStartGame={(ai, time) => {
          setSelectedAI(ai);
          setInitialTime(time);
          setWhiteTime(time);
          setBlackTime(time);
          setCurrentPosition('start');
          setCurrentPlayer('white');
          setPieceThoughts({});
          setNarrativeHistory([]);
          setBattlefieldState({
            intensity: 0.3,
            phase: 'opening'
          });
          setGameStarted(true);
          setIsSettings(false);
          chess.current = new Chess();
        }}
      />
    );
  } else {
    return (
      <div className="battlefield-app">
        <Timer whiteTime={whiteTime} blackTime={blackTime} currentPlayer={currentPlayer} />
        
        <div className="main-content">
          <BattlefieldChessBoard 
            position={currentPosition} 
            onPieceDrop={handleMove} 
            currentPlayer={currentPlayer}
            pieceThoughts={pieceThoughts}
            battlefieldState={battlefieldState}
          />
          
          <NarrativePanel 
            narrativeHistory={narrativeHistory}
            battlefieldState={battlefieldState}
          />
        </div>
      </div>
    );
  }
};

export default App;