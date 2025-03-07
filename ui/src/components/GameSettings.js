import React, { useState } from 'react';
import '../styles/GameSettings.scss';

const aiPersonalities = [
  {
    id: 'dutiful_pawn',
    name: 'Dutiful Pawn',
    description: 'Defensive and methodical',
  },
  {
    id: 'aggressive_pawn',
    name: 'Aggressive Pawn',
    description: 'Always pushing forward',
  },
  {
    id: 'unpredictable_knight',
    name: 'Unpredictable Knight',
    description: 'Makes surprising tactical moves',
    skillLevel: 10
  },
  {
    id: 'strategic_bishop',
    name: 'Strategic Bishop',
    description: 'Plans several moves ahead',
    skillLevel: 12
  },
  {
    id: 'powerful_rook',
    name: 'Powerful Rook',
    description: 'Dominates open files with force',
    skillLevel: 15
  },
  {
    id: 'dominant_queen',
    name: 'Dominant Queen',
    description: 'Aggressive and tactical',
    skillLevel: 18
  },
  {
    id: 'cautious_king',
    name: 'Cautious King',
    description: 'Defensive mastermind',
    skillLevel: 20
  }
];

const timeOptions = [
  { value: 60, label: '1 Minute' },
  { value: 180, label: '3 Minutes' },
  { value: 300, label: '5 Minutes' },
  { value: 600, label: '10 Minutes' },
  { value: 900, label: '15 Minutes' },
];

const GameSettings = ({ onStartGame }) =
  const [selectedAI, setSelectedAI] = useState(null);
  const [selectedTime, setSelectedTime] = useState(300);

  return (
    <div className="game-settings">
      <h1 className="settings-title">Self-Aware Chess Battlefield</h1>

      <div className="ai-section">
        <h2 className="section-title">Choose Your Opponent</h2>
        <div className="ai-list">
          {aiPersonalities.map(ai =
            <div 
              key={ai.id} 
              className={`ai-card ${selectedAI === ai ? 'selected' : ''}`}
              onClick={() =
            >
              <div className="ai-icon">{ai.name[0]}</div>
              <div className="ai-name">{ai.name}</div>
              <div className="ai-skill">{ai.description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="time-section">
        <h2 className="section-title">Choose Time Control</h2>
        <div className="time-options">
          {timeOptions.map(time =
            <div
              key={time.value}
              className={`time-option ${selectedTime === time.value ? 'selected' : ''}`}
              onClick={() =
            >
              {time.label}
            </div>
          ))}
        </div>
      </div>

      <button 
        className="start-button"
        disabled={!selectedAI}
        onClick={() =, selectedTime)}
      >
        Start Battle
      </button>
    </div>
  );
};

