import React, { useEffect } from 'react';
import '../styles/LoadingScreen.scss';

const LoadingScreen = ({ onLoadComplete }) =
  useEffect(() =
    const timer = setTimeout(onLoadComplete, 3000);
    return () =
  }, [onLoadComplete]);

  useEffect(() =
    const interval = setInterval(() =
      const digit = Math.floor(Math.random() * 2);
      const digitDiv = document.createElement('div');
      digitDiv.classList.add('digit');
      digitDiv.innerHTML = digit;
      digitDiv.style.left = `${Math.random() * window.innerWidth}px`;
      digitDiv.style.top = '-20px';
      document.body.appendChild(digitDiv);
      digitDiv.animate(
        [{ transform: 'translateY(0)' }, { transform: 'translateY(100vh)' }],
        { duration: 2000, easing: 'linear' }
      );
      setTimeout(() =, 2000);
    }, 100);
    return () =
  }, []);

  return (
    <div className="loading-screen">
      <div className="loading-title">Self-Aware Chess Battlefield</div>
      <img src="/knight.svg" alt="Knight" className="knight" />
    </div>
  );
};

