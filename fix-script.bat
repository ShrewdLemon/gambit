@echo off
echo Fixing UI component files...

:: Set working directory to script location
cd %~dp0

echo Creating a fresh React app
npx create-react-app chess-ui
cd chess-ui

echo Installing dependencies
npm install react-chessboard chess.js sass

echo Creating directory structure
mkdir src\components
mkdir src\services
mkdir src\styles

:: Create index.scss with proper content
echo Creating styles...
(
echo * {
echo   margin: 0;
echo   padding: 0;
echo   box-sizing: border-box;
echo }
echo.
echo body {
echo   font-family: Arial, sans-serif;
echo   background: #080810;
echo   color: #fff;
echo   background-image: 
echo     radial-gradient^(circle at 10%% 20%%, rgba^(100, 43, 115, 0.1^) 0%%, rgba^(4, 0, 4, 0^) 50%%^),
echo     radial-gradient^(circle at 90%% 80%%, rgba^(100, 43, 115, 0.1^) 0%%, rgba^(4, 0, 4, 0^) 50%%^);
echo }
echo.
echo .battlefield-app {
echo   max-width: 1000px;
echo   margin: 20px auto;
echo   padding: 20px;
echo }
echo.
echo .main-content {
echo   display: flex;
echo   gap: 20px;
echo   justify-content: center;
echo   margin-top: 20px;
echo }
echo.
echo @media ^(max-width: 950px^) {
echo   .main-content {
echo     flex-direction: column;
echo     align-items: center;
echo   }
echo }
) > src\styles\index.scss

:: Create LoadingScreen.scss
(
echo .loading-screen {
echo   background: black;
echo   width: 100vw;
echo   height: 100vh;
echo   display: flex;
echo   justify-content: center;
echo   align-items: center;
echo   position: relative;
echo   overflow: hidden;
echo }
echo.
echo .knight {
echo   width: 200px;
echo   height: 200px;
echo   animation: rotate 2s infinite linear;
echo   filter: drop-shadow^(0 0 10px #ff00de^);
echo }
echo.
echo .loading-title {
echo   position: absolute;
echo   top: 20%%;
echo   font-size: 2.5rem;
echo   font-weight: bold;
echo   background: linear-gradient^(90deg, #00c8ff, #ff00de^);
echo   -webkit-background-clip: text;
echo   -webkit-text-fill-color: transparent;
echo   text-shadow: 0 0 10px rgba^(255, 0, 222, 0.5^);
echo }
echo.
echo @keyframes rotate {
echo   from { transform: rotate^(0deg^); }
echo   to { transform: rotate^(360deg^); }
echo }
echo.
echo .digit {
echo   position: absolute;
echo   font-size: 20px;
echo   color: #fff;
echo   text-shadow: 0 0 5px #fff, 0 0 10px #ff00de;
echo }
) > src\styles\LoadingScreen.scss

:: Create components (just a few essential ones for brevity)
echo Creating essential components...

(
echo import React, { useEffect } from 'react';
echo import '../styles/LoadingScreen.scss';
echo.
echo const LoadingScreen = ({ onLoadComplete }) =^> {
echo   useEffect(() =^> {
echo     const timer = setTimeout(onLoadComplete, 3000);
echo     return () =^> clearTimeout(timer);
echo   }, [onLoadComplete]);
echo.
echo   useEffect(() =^> {
echo     const interval = setInterval(() =^> {
echo       const digit = Math.floor(Math.random() * 2);
echo       const digitDiv = document.createElement('div');
echo       digitDiv.classList.add('digit');
echo       digitDiv.innerHTML = digit;
echo       digitDiv.style.left = `${Math.random() * window.innerWidth}px`;
echo       digitDiv.style.top = '-20px';
echo       document.body.appendChild(digitDiv);
echo       digitDiv.animate(
echo         [{ transform: 'translateY(0)' }, { transform: 'translateY(100vh)' }],
echo         { duration: 2000, easing: 'linear' }
echo       );
echo       setTimeout(() =^> digitDiv.remove(), 2000);
echo     }, 100);
echo     return () =^> clearInterval(interval);
echo   }, []);
echo.
echo   return (
echo     ^<div className="loading-screen"^>
echo       ^<div className="loading-title"^>Self-Aware Chess Battlefield^</div^>
echo       ^<img src="/knight.svg" alt="Knight" className="knight" /^>
echo     ^</div^>
echo   );
echo };
echo.
echo export default LoadingScreen;
) > src\components\LoadingScreen.js

:: Create a simple App.js to start with
(
echo import React, { useState, useEffect } from 'react';
echo import './App.css';
echo import { Chess } from 'chess.js';
echo import { Chessboard } from 'react-chessboard';
echo import './styles/index.scss';
echo import LoadingScreen from './components/LoadingScreen';
echo.
echo function App() {
echo   const [isLoading, setIsLoading] = useState(true);
echo   const [game, setGame] = useState(new Chess());
echo.
echo   useEffect(() =^> {
echo     // This simulates the loading screen for demonstration
echo     const timer = setTimeout(() =^> {
echo       setIsLoading(false);
echo     }, 3000);
echo     
echo     return () =^> clearTimeout(timer);
echo   }, []);
echo.
echo   function makeAMove(move) {
echo     const gameCopy = new Chess(game.fen());
echo     const result = gameCopy.move(move);
echo     setGame(gameCopy);
echo     return result; // null if the move was illegal, the move object if the move was legal
echo   }
echo.
echo   function onDrop(sourceSquare, targetSquare) {
echo     const move = makeAMove({
echo       from: sourceSquare,
echo       to: targetSquare,
echo       promotion: 'q' // always promote to a queen for example simplicity
echo     });
echo.
echo     // illegal move
echo     if (move === null) return false;
echo     return true;
echo   }
echo.
echo   if (isLoading) {
echo     return ^<LoadingScreen onLoadComplete={() =^> setIsLoading(false)} /^>;
echo   }
echo.
echo   return (
echo     ^<div className="App"^>
echo       ^<header className="App-header"^>
echo         ^<h1^>Self-Aware Chess Battlefield^</h1^>
echo       ^</header^>
echo       ^<div style={{ width: '500px', margin: '0 auto' }}^>
echo         ^<Chessboard position={game.fen()} onPieceDrop={onDrop} />
echo       ^</div^>
echo     ^</div^>
echo   );
echo }
echo.
echo export default App;
) > src\App.js

:: Create placeholder SVG
echo Creating placeholder knight.svg...
if not exist public\knight.svg (
  (
    echo ^<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45"^>
    echo   ^<g fill="none" fill-rule="evenodd" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"^>
    echo     ^<path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21" fill="#fff"/^>
    echo     ^<path d="M24 18c.38 2.91-5.55 7.37-8 9-3 2-2.82 4.34-5 4-1.042-.94 1.41-3.04 0-3-1 0 .19 1.23-1 2-1 0-4.003 1-4-4 0-2 6-12 6-12s1.89-1.9 2-3.5c-.73-.994-.5-2-.5-3 1-1 3 2.5 3 2.5h2s.78-1.992 2.5-3c1 0 1 3 1 3" fill="#fff"/^>
    echo     ^<path d="M9.5 25.5a.5.5 0 1 1-1 0 .5.5 0 1 1 1 0zm5.433-9.75a.5 1.5 30 1 1-.866-.5.5 1.5 30 1 1 .866.5z" fill="#000"/^>
    echo   ^</g^>
    echo ^</svg^>
  ) > public\knight.svg
)

:: Create startup script to run both UI and Flask API
echo Creating startup script...
(
echo @echo off
echo Starting Chess Battlefield...
echo.
echo Starting API server...
echo start cmd /k "cd %~dp0..\api && python app.py"
echo.
echo Starting React app...
echo start cmd /k "cd %~dp0 && npm start"
) > start-game.bat

echo All files have been created successfully!
echo.
echo To start the game:
echo 1. Run 'start-game.bat' to start both the API and UI
echo.
echo Or start components individually:
echo 1. Make sure your Python API is running: cd ..\api && python app.py
echo 2. Start the UI: npm start
echo.
pause
