import React, { useState, useEffect } from 'react';
import { Chess } from 'chess.js';
import ChessboardComponent from './components/ChessboardComponent';
import MoveList from './components/MoveList';
import AnalysisPanel from './components/AnalysisPanel';
import PGNLoader from './components/PGNLoader';
import { fetchAnalysis, fetchEngineAnalysis } from './services/api';

function App() {
  const [game, setGame] = useState(new Chess());
  const [fen, setFen] = useState(game.fen());
  const [history, setHistory] = useState([]);
  const [currentMove, setCurrentMove] = useState(-1); // -1 means starting position
  const [analysis, setAnalysis] = useState(null);
  const [engineAnalysis, setEngineAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  // Initialize history when the game changes
  useEffect(() => {
    const moves = [];
    const gameCopy = new Chess();
    
    for (let i = 0; i < game.history().length; i++) {
      const move = game.history()[i];
      gameCopy.move(move);
      moves.push({
        san: move,
        fen: gameCopy.fen(),
        moveNumber: Math.floor(i / 2) + 1,
        isWhite: i % 2 === 0
      });
    }
    
    setHistory(moves);
  }, [game]);

  // Update the board when the current move changes
  useEffect(() => {
    if (currentMove === -1) {
      // Starting position
      setFen(new Chess().fen());
    } else if (currentMove >= 0 && currentMove < history.length) {
      setFen(history[currentMove].fen);
    }
  }, [currentMove, history]);
  
  // Update the current move and history when a game is loaded
  useEffect(() => {
    // Reset the FEN display when a game is loaded
    if (game) {
      if (currentMove === -1) {
        setFen(new Chess().fen());
      } else if (history.length > 0 && currentMove >= 0 && currentMove < history.length) {
        setFen(history[currentMove].fen);
      }
    }
  }, [game, history, currentMove]);

  // Get analysis when a move is made or selected
  useEffect(() => {
    if (currentMove >= 0 && !loading) {
      getAnalysis();
    }
  }, [currentMove]);

  const makeMove = (move) => {
    // Create a new game object to avoid mutation
    const gameCopy = new Chess(game.fen());
    
    try {
      gameCopy.move(move);
      setGame(gameCopy);
      setCurrentMove(gameCopy.history().length - 1);
    } catch (error) {
      console.error('Invalid move:', move);
    }
  };
  
  const handleGameLoad = (loadedGame) => {
    try {
      // Store the original PGN for future resets
      const pgn = loadedGame.pgn();
      setOriginalPgn(pgn);
      
      setGame(loadedGame);
      // Go to the end of the game when loading
      // This will trigger the history update via useEffect
      setTimeout(() => {
        // Use setTimeout to ensure the history is updated first
        const moveCount = loadedGame.history().length - 1;
        setCurrentMove(moveCount >= 0 ? moveCount : -1);
      }, 100);
      setAnalysis(null);
      setEngineAnalysis(null);
    } catch (error) {
      console.error("Error handling game load:", error);
    }
  };
  
  // Store the original PGN when a game is loaded
  const [originalPgn, setOriginalPgn] = useState('');
  
  const resetGame = () => {
    if (originalPgn) {
      // If we have a stored PGN, reload it
      try {
        const loadedGame = new Chess();
        loadedGame.loadPgn(originalPgn);
        setGame(loadedGame);
        setTimeout(() => {
          const moveCount = loadedGame.history().length - 1;
          setCurrentMove(moveCount >= 0 ? moveCount : -1);
        }, 100);
      } catch (error) {
        console.error("Error reloading original PGN:", error);
        // Fall back to new game if reload fails
        setGame(new Chess());
        setCurrentMove(-1);
      }
    } else {
      // No original PGN stored, just reset to a new game
      setGame(new Chess());
      setCurrentMove(-1);
    }
    setAnalysis(null);
    setEngineAnalysis(null);
  };

  const getAnalysis = async () => {
    if (currentMove < 0 || currentMove >= history.length) return;
    
    setLoading(true);
    try {
      // PLACEHOLDER: These functions will call your API endpoints
      const moveAnalysis = await fetchAnalysis(fen, history[currentMove].san);
      const engineData = await fetchEngineAnalysis(fen);
      
      setAnalysis(moveAnalysis);
      setEngineAnalysis(engineData);
    } catch (error) {
      console.error('Error fetching analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const onPieceDrop = (sourceSquare, targetSquare) => {
    const move = {
      from: sourceSquare,
      to: targetSquare,
      promotion: 'q' // Default promotion to queen
    };
    
    makeMove(move);
    return true;
  };

  const handleMoveClick = (index) => {
    setCurrentMove(index);
  };

  const navigateMoves = (direction) => {
    if (direction === 'first') {
      setCurrentMove(-1);
    } else if (direction === 'prev' && currentMove > -1) {
      setCurrentMove(currentMove - 1);
    } else if (direction === 'next' && currentMove < history.length - 1) {
      setCurrentMove(currentMove + 1);
    } else if (direction === 'last') {
      setCurrentMove(history.length - 1);
    }
  };

  return (
    <div className="app-container">
      <header className="bg-white p-4 border-b border-gray-200 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-800">Process<span className="text-blue-500">Mate</span></h1>
      </header>
      
      <div className="main-content">
        <div className="left-panel">
          <div className="board-container">
            <ChessboardComponent 
              fen={fen} 
              onPieceDrop={onPieceDrop} 
            />
            
            <div className="board-controls">
              <button 
                className="nav-button" 
                onClick={() => navigateMoves('first')} 
                disabled={currentMove === -1}
              >
                ⟪
              </button>
              <button 
                className="nav-button" 
                onClick={() => navigateMoves('prev')} 
                disabled={currentMove === -1}
              >
                ◀
              </button>
              <button 
                className="nav-button" 
                onClick={() => navigateMoves('next')} 
                disabled={currentMove >= history.length - 1}
              >
                ▶
              </button>
              <button 
                className="nav-button" 
                onClick={() => navigateMoves('last')} 
                disabled={currentMove >= history.length - 1}
              >
                ⟫
              </button>
              <button 
                className="reset-button" 
                onClick={resetGame} 
              >
                Reset
              </button>
            </div>
          </div>
          
          <div className="pgn-container">
            <PGNLoader onGameLoad={handleGameLoad} />
          </div>
        </div>

        <div className="right-panel">
          <div className="moves-container">
            <h2 className="section-title">Move List</h2>
            <MoveList 
              history={history} 
              currentMove={currentMove} 
              onMoveClick={handleMoveClick} 
            />
          </div>
          
          <div className="analysis-container">
            <h2 className="section-title">Analysis</h2>
            <AnalysisPanel 
              analysis={analysis} 
              engineAnalysis={engineAnalysis} 
              loading={loading} 
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;