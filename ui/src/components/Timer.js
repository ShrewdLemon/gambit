import React from 'react';
import '../styles/Timer.scss';

const formatTime = (seconds) =
  const minutes = Math.floor(seconds / 60);
  const secs = seconds  60;
};

const Timer = ({ whiteTime, blackTime, currentPlayer }) =
  return (
    <div className="timer">
      <div className={`timer-white ${currentPlayer === 'white' ? 'active' : ''}`}>
        White: {formatTime(whiteTime)}
      </div>
      <div className={`timer-black ${currentPlayer === 'black' ? 'active' : ''}`}>
        Black: {formatTime(blackTime)}
      </div>
    </div>
  );
};

