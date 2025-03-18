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
  const [variations, setVariations] = useState({}); // Map of move index to array of variations
  const [currentVariation, setCurrentVariation] = useState(null); // Currently active variation path
  const [currentPosition, setCurrentPosition] = useState(new Chess()); // Chess position at current move

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
    setVariations({});
    setCurrentVariation(null);
  }, [game]);

  // Update the board when the current move changes
  useEffect(() => {
    const chess = new Chess();
    
    if (currentMove === -1) {
      // Starting position
      setFen(chess.fen());
      setCurrentPosition(chess);
    } else if (currentMove >= 0 && currentMove < history.length) {
      // If we're in a variation, replay moves from the main line up to the variation point
      // then replay the variation moves
      if (currentVariation && currentVariation.startMove <= currentMove) {
        // Replay main line up to variation start point
        for (let i = 0; i <= currentVariation.startMove; i++) {
          if (i < history.length) {
            chess.move(history[i].san);
          }
        }
        
        // Then play variation moves
        const variationPath = variations[currentVariation.startMove]?.[currentVariation.index] || [];
        const variationMoveIndex = currentMove - currentVariation.startMove - 1;
        
        if (variationMoveIndex >= 0 && variationMoveIndex < variationPath.length) {
          for (let i = 0; i <= variationMoveIndex; i++) {
            chess.move(variationPath[i].san);
          }
        }
        
        setFen(chess.fen());
        setCurrentPosition(chess);
      } else {
        // Standard main line replay
        for (let i = 0; i <= currentMove; i++) {
          if (i < history.length) {
            chess.move(history[i].san);
          }
        }
        setFen(chess.fen());
        setCurrentPosition(chess);
      }
    }
  }, [currentMove, history, variations, currentVariation]);

  // Get analysis when a move is made or selected
  useEffect(() => {
    if (currentMove >= 0 && !loading) {
      getAnalysis();
    }
  }, [currentMove, currentVariation]);

  const makeMove = (move) => {
    try {
      // Check if we're on a mainline move or creating a variation
      if (currentMove < history.length - 1 && currentMove >= -1 && !currentVariation) {
        // We're not at the end of main line - create variation
        const startMoveIndex = currentMove;
        const currentChess = new Chess(currentPosition.fen());
        
        // Try to make the move
        const result = currentChess.move(move);
        
        if (!result) {
          console.error('Invalid move:', move);
          return false;
        }
        
        // Create or update a variation
        const newVariation = {
          san: result.san,
          fen: currentChess.fen(),
          moveNumber: currentMove >= 0 ? history[currentMove].moveNumber : 1,
          isWhite: currentMove >= 0 ? !history[currentMove].isWhite : true
        };
        
        // Add to variations
        const moveVariations = variations[startMoveIndex] || [];
        
        // Check if this same variation already exists
        const existingVarIndex = moveVariations.findIndex(
          varMoves => varMoves.length > 0 && varMoves[0].san === newVariation.san
        );
        
        if (existingVarIndex !== -1) {
          // Use existing variation
          setCurrentVariation({
            startMove: startMoveIndex,
            index: existingVarIndex
          });
        } else {
          // Create a new variation
          const newVariations = { ...variations };
          newVariations[startMoveIndex] = [...moveVariations, [newVariation]];
          setVariations(newVariations);
          
          // Set current variation to the newly created one
          setCurrentVariation({
            startMove: startMoveIndex,
            index: newVariations[startMoveIndex].length - 1
          });
        }
        
        // Move to the first move of the variation
        setCurrentMove(startMoveIndex + 1);
        return true;
      } else if (currentVariation) {
        // Either adding to an existing variation or creating a sub-variation from a variation
        const varMoves = variations[currentVariation.startMove][currentVariation.index];
        const varMoveIndex = currentMove - currentVariation.startMove - 1;
        
        // If we're not at the end of the variation, create a subvariation
        if (varMoveIndex < varMoves.length - 1) {
          // Sub-variations are not implemented in this version
          console.log("Sub-variations are not supported yet");
          return false;
        }
        
        // We're at the end of a variation - add to it
        const currentChess = new Chess(currentPosition.fen());
        const result = currentChess.move(move);
        
        if (!result) {
          console.error('Invalid move:', move);
          return false;
        }
        
        // Create the new variation move
        const newMove = {
          san: result.san,
          fen: currentChess.fen(),
          moveNumber: Math.floor((varMoves.length + currentVariation.startMove + 1) / 2) + 1,
          isWhite: (varMoves.length + currentVariation.startMove + 1) % 2 === 0
        };
        
        // Update variations
        const newVariations = { ...variations };
        newVariations[currentVariation.startMove][currentVariation.index] = [...varMoves, newMove];
        setVariations(newVariations);
        
        // Move to the newly added move
        setCurrentMove(currentMove + 1);
        return true;
      } else {
        // Adding to main line
        // Create a new game object to avoid mutation
        const gameCopy = new Chess(currentPosition.fen());
        const result = gameCopy.move(move);
        
        if (!result) {
          console.error('Invalid move:', move);
          return false;
        }
        
        // Update the game with all moves up to the current position plus the new move
        const newGame = new Chess();
        
        if (currentMove >= 0) {
          // Replay all moves up to current
          for (let i = 0; i <= currentMove; i++) {
            newGame.move(history[i].san);
          }
        }
        
        // Add the new move
        newGame.move(result.san);
        
        // Update game state
        setGame(newGame);
        setCurrentVariation(null);
        
        // This will be updated after history is recalculated
        setTimeout(() => {
          setCurrentMove(currentMove + 1);
        }, 50);
        
        return true;
      }
    } catch (error) {
      console.error('Error making move:', error);
      return false;
    }
  };
  
  const handleGameLoad = (loadedGame) => {
    try {
      // Store the original PGN for future resets
      const pgn = loadedGame.pgn();
      setOriginalPgn(pgn);
      
      setGame(loadedGame);
      setVariations({});
      setCurrentVariation(null);
      
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
        setVariations({});
        setCurrentVariation(null);
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
      setVariations({});
      setCurrentVariation(null);
      setCurrentMove(-1);
    }
    setAnalysis(null);
    setEngineAnalysis(null);
  };

  const getAnalysis = async () => {
    if (currentMove < 0) return;
    
    // Determine the right move to analyze based on whether we're in a variation
    let moveToAnalyze;
    let positionFen;
    
    if (currentVariation && currentMove > currentVariation.startMove) {
      const varMoveIndex = currentMove - currentVariation.startMove - 1;
      if (varMoveIndex >= 0 && 
          variations[currentVariation.startMove] && 
          variations[currentVariation.startMove][currentVariation.index] && 
          varMoveIndex < variations[currentVariation.startMove][currentVariation.index].length) {
        const varMove = variations[currentVariation.startMove][currentVariation.index][varMoveIndex];
        moveToAnalyze = varMove.san;
        positionFen = varMove.fen;
      } else {
        return;
      }
    } else if (currentMove < history.length) {
      moveToAnalyze = history[currentMove].san;
      positionFen = history[currentMove].fen;
    } else {
      return;
    }
    
    setLoading(true);
    try {
      // PLACEHOLDER: These functions will call your API endpoints
      const moveAnalysis = await fetchAnalysis(positionFen, moveToAnalyze);
      const engineData = await fetchEngineAnalysis(positionFen);
      
      setAnalysis(moveAnalysis);
      setEngineAnalysis(engineData);
    } catch (error) {
      console.error('Error fetching analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const onPieceDrop = (sourceSquare, targetSquare, piece) => {
    const move = {
      from: sourceSquare,
      to: targetSquare,
      promotion: 'q' // Default promotion to queen
    };
    
    // Try to make the move
    return makeMove(move);
  };

  const handleMoveClick = (index, variation = null) => {
    setCurrentVariation(variation);
    setCurrentMove(index);
  };

  const navigateMoves = (direction) => {
    if (direction === 'first') {
      setCurrentVariation(null);
      setCurrentMove(-1);
    } else if (direction === 'prev' && currentMove > -1) {
      // If in variation and going back to main line
      if (currentVariation && currentMove === currentVariation.startMove + 1) {
        setCurrentVariation(null);
      }
      setCurrentMove(currentMove - 1);
    } else if (direction === 'next') {
      if (currentVariation) {
        const varMoves = variations[currentVariation.startMove][currentVariation.index];
        const varMoveIndex = currentMove - currentVariation.startMove - 1;
        
        if (varMoveIndex < varMoves.length - 1) {
          setCurrentMove(currentMove + 1);
        }
      } else if (currentMove < history.length - 1) {
        setCurrentMove(currentMove + 1);
      }
    } else if (direction === 'last') {
      if (currentVariation) {
        const varMoves = variations[currentVariation.startMove][currentVariation.index];
        setCurrentMove(currentVariation.startMove + varMoves.length);
      } else {
        setCurrentMove(history.length - 1);
      }
    }
  };

  const deleteVariation = (startMoveIndex, variationIndex) => {
    if (variations[startMoveIndex] && variations[startMoveIndex][variationIndex]) {
      // If the variation we're deleting is active, go back to main line
      if (currentVariation && 
          currentVariation.startMove === startMoveIndex && 
          currentVariation.index === variationIndex) {
        setCurrentVariation(null);
        setCurrentMove(startMoveIndex);
      }
      
      // Remove the variation
      const newVariations = { ...variations };
      newVariations[startMoveIndex] = newVariations[startMoveIndex].filter((_, i) => i !== variationIndex);
      
      // If no variations left at this move, remove the entry
      if (newVariations[startMoveIndex].length === 0) {
        delete newVariations[startMoveIndex];
      }
      
      setVariations(newVariations);
    }
  };

  return (
    <div className="app-container">
      <header className="bg-white p-4 border-b border-gray-200 shadow-sm">
        <div className="max-w-[500px] mx-auto">
          <h1 className="text-2xl font-bold text-gray-800">Process<span className="text-blue-500">Mate</span></h1>
        </div>
      </header>
      
      <div className="main-content">
        <div className="left-panel">
          <div className="board-container">
            <ChessboardComponent 
              fen={fen} 
              onPieceDrop={onPieceDrop} 
              currentGame={currentPosition}
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
                disabled={
                  (currentVariation 
                    ? currentMove >= currentVariation.startMove + variations[currentVariation.startMove][currentVariation.index].length 
                    : currentMove >= history.length - 1)
                }
              >
                ▶
              </button>
              <button 
                className="nav-button" 
                onClick={() => navigateMoves('last')} 
                disabled={
                  (currentVariation 
                    ? currentMove >= currentVariation.startMove + variations[currentVariation.startMove][currentVariation.index].length 
                    : currentMove >= history.length - 1)
                }
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
              variations={variations}
              currentVariation={currentVariation}
              onDeleteVariation={deleteVariation}
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