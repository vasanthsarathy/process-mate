import React, { useState, useEffect } from 'react';
import { Chessboard } from 'react-chessboard';
import { Chess } from 'chess.js';

function ChessboardComponent({ fen, onPieceDrop, currentGame }) {
  const [isDraggable, setIsDraggable] = useState(true);
  const [showValidMoves, setShowValidMoves] = useState(true);
  const [showLastMove, setShowLastMove] = useState(true);
  const [boardOrientation, setBoardOrientation] = useState('white');
  const [validMoves, setValidMoves] = useState({});
  
  // When FEN changes, reset the valid moves highlight
  useEffect(() => {
    if (showValidMoves && currentGame) {
      // Leave validMoves empty to clear any previous highlights
      setValidMoves({});
    }
  }, [fen, currentGame, showValidMoves]);
  
  // Get last move from fen for highlighting
  const getLastMove = () => {
    try {
      const game = new Chess(fen);
      const history = game.history({ verbose: true });
      if (history.length > 0) {
        const lastMove = history[history.length - 1];
        return [lastMove.from, lastMove.to];
      }
    } catch (err) {
      console.error("Error getting last move:", err);
    }
    return null;
  };

  // Flip the board orientation
  const flipBoard = () => {
    setBoardOrientation(boardOrientation === 'white' ? 'black' : 'white');
  };
  
  // Show valid moves when hovering a piece
  const onPieceHover = (piece, sourceSquare) => {
    if (!showValidMoves || !currentGame) return;
    
    try {
      // Create a temporary game to check moves
      const tempGame = new Chess(fen);
      
      // Get all possible moves for the piece
      const moves = tempGame.moves({ 
        square: sourceSquare, 
        verbose: true 
      });
      
      // Create styles for valid destination squares
      const newSquareStyles = {};
      moves.forEach(move => {
        newSquareStyles[move.to] = {
          background: 'radial-gradient(circle, rgba(0,0,0,.1) 25%, transparent 25%)',
          borderRadius: '50%'
        };
      });
      
      setValidMoves(newSquareStyles);
    } catch (err) {
      console.error('Error calculating valid moves:', err);
      setValidMoves({});
    }
  };
  
  // Handle piece drop and validate the move
  const handlePieceDrop = (sourceSquare, targetSquare, piece) => {
    // Clear highlight when dropping
    setValidMoves({});
    
    // Call the provided onPieceDrop function
    return onPieceDrop(sourceSquare, targetSquare, piece);
  };

  // Configuration for the chessboard
  const boardConfig = {
    position: fen,
    onPieceDrop: handlePieceDrop,
    onPieceClick: (piece, sourceSquare) => onPieceHover(piece, sourceSquare),
    boardWidth: 500,
    isDraggablePiece: () => isDraggable,
    customBoardStyle: {
      borderRadius: '4px',
      boxShadow: '0 5px 15px rgba(0, 0, 0, 0.5)'
    },
    customDarkSquareStyle: { backgroundColor: '#769656' },
    customLightSquareStyle: { backgroundColor: '#eeeed2' },
    showBoardNotation: true,
    arePiecesDraggable: isDraggable,
    areArrowsAllowed: true,
    animationDuration: 300,
    arePremovesAllowed: false, // Disable premoves
    showLastMove: showLastMove,
    lastMove: getLastMove() || [],
    customArrows: [],
    customSquareStyles: validMoves,
    boardOrientation: boardOrientation
  };
  
  return (
    <div>
      <Chessboard {...boardConfig} />
      <div className="board-options" style={{ marginTop: '10px' }}>
        <label>
          <input 
            type="checkbox" 
            checked={showValidMoves} 
            onChange={() => {
              setShowValidMoves(!showValidMoves);
              setValidMoves({}); // Clear highlights when toggling
            }}
          /> 
          Show Valid Moves
        </label>
        <label style={{ marginLeft: '10px' }}>
          <input 
            type="checkbox" 
            checked={showLastMove} 
            onChange={() => setShowLastMove(!showLastMove)}
          /> 
          Highlight Last Move
        </label>
        <button 
          style={{ 
            marginLeft: '10px', 
            padding: '5px 10px', 
            backgroundColor: '#4a6da7', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }} 
          onClick={flipBoard}
        >
          Flip Board
        </button>
      </div>
    </div>
  );
}

export default ChessboardComponent;