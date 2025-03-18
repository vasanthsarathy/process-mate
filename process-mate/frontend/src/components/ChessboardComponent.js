import React, { useState } from 'react';
import { Chessboard } from 'react-chessboard';
import { Chess } from 'chess.js';

function ChessboardComponent({ fen, onPieceDrop }) {
  const [isDraggable, setIsDraggable] = useState(true);
  const [showValidMoves, setShowValidMoves] = useState(true);
  const [showLastMove, setShowLastMove] = useState(true);
  const [boardOrientation, setBoardOrientation] = useState('white');
  
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

  // Configuration for the chessboard
  const boardConfig = {
    position: fen,
    onPieceDrop: onPieceDrop,
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
    arePremovesAllowed: true,
    showLastMove: showLastMove,
    lastMove: getLastMove() || [],
    customArrows: [],
    customSquareStyles: showValidMoves ? {} : {},
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
            onChange={() => setShowValidMoves(!showValidMoves)}
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