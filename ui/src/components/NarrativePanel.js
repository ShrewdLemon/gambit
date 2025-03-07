import React from 'react';
import '../styles/NarrativePanel.scss';

const NarrativePanel = ({ narrativeHistory, battlefieldState }) =
  const getIntensityClass = (intensity) =
    switch (intensity) {
      case 'high': return 'high-intensity';
      case 'medium': return 'medium-intensity';
      case 'low': return 'low-intensity';
      default: return '';
    }
  };
ECHO is off.
  return (
    <div className="narrative-panel">
      <div className="panel-header">
        <h3>Battlefield Commentary</h3>
        <div className="battlefield-phase-indicator">
          {battlefieldState.phase.toUpperCase()}
        </div>
      </div>
ECHO is off.
      <div className="narrative-content">
        {narrativeHistory.length === 0 ? (
          <div className="empty-narrative">
            <p>The battlefield awaits your command...</p>
          </div>
        ) : (
          <div className="narrative-entries">
            {narrativeHistory.slice().reverse().map((entry, index) =
              <div 
                key={`${entry.move}-${index}`} 
                className={`narrative-entry ${getIntensityClass(entry.narrative.intensity)}`}
              >
                <div className="move-notation">{entry.move}</div>
                <div className="action-description">{entry.narrative.action_description}</div>
                <div className="battlefield-impact">{entry.narrative.battlefield_impact}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

