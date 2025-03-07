import React from 'react';
import { Chessboard } from 'react-chessboard';
import '../styles/BattlefieldChessBoard.scss';

const BattlefieldChessBoard = ({ 
  position, 
  onPieceDrop, 
  currentPlayer, 
  pieceThoughts = {},
  battlefieldState = { intensity: 0.5, phase: 'opening' } 
}) =
  // Intensity affects visual elements based on battlefield state
  const intensity = battlefieldState.intensity * 100;
ECHO is off.
  return (
    <div className="battlefield-wrapper">
      <div className={`board-wrapper ${currentPlayer}-turn phase-${battlefieldState.phase}`}
           style={{'--intensity': `${intensity}`}}>
        <Chessboard position={position} onPieceDrop={onPieceDrop} />
ECHO is off.
        {/* Piece thoughts visualized as thought bubbles */}
        <div className="piece-thoughts">
          {Object.entries(pieceThoughts).map(([square, thought]) =
            <div key={square} className="thought-bubble" data-square={square}>
              {thought}
            </div>
          ))}
        </div>
      </div>
ECHO is off.
      <div className="battlefield-status">
        <div className="battlefield-phase">
          Phase: {battlefieldState.phase.charAt(0).toUpperCase() + battlefieldState.phase.slice(1)}
        </div>
        <div className="battlefield-intensity">
          <div className="intensity-label">Battlefield Intensity:</div>
          <div className="intensity-meter">
            <div className="intensity-fill" style={{width: `${intensity}`}}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

