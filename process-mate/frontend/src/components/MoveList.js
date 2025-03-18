import React from 'react';

function MoveList({ history, currentMove, onMoveClick, variations, currentVariation, onDeleteVariation }) {
  // Group moves by pairs (white and black)
  const movesByNumber = {};
  
  history.forEach((move, index) => {
    const moveNumber = move.moveNumber;
    if (!movesByNumber[moveNumber]) {
      movesByNumber[moveNumber] = { white: null, black: null };
    }
    
    if (move.isWhite) {
      movesByNumber[moveNumber].white = { san: move.san, index };
    } else {
      movesByNumber[moveNumber].black = { san: move.san, index };
    }
  });
  
  // Render a variation's moves
  const renderVariation = (moves, startMoveIndex, variationIndex) => {
    // Group variation moves by pairs
    const varMovesByNumber = {};
    
    moves.forEach((move, idx) => {
      const moveNumber = move.moveNumber;
      if (!varMovesByNumber[moveNumber]) {
        varMovesByNumber[moveNumber] = { white: null, black: null };
      }
      
      if (move.isWhite) {
        varMovesByNumber[moveNumber].white = { san: move.san, idx };
      } else {
        varMovesByNumber[moveNumber].black = { san: move.san, idx };
      }
    });
    
    return (
      <div className="variation" key={`${startMoveIndex}-${variationIndex}`}>
        <div className="variation-header">
          <span className="variation-marker">⟦</span>
          <button 
            className="delete-variation-btn"
            onClick={(e) => {
              e.stopPropagation();
              onDeleteVariation(startMoveIndex, variationIndex);
            }}
            title="Delete variation"
          >
            ✕
          </button>
        </div>
        
        <div className="variation-moves">
          {Object.entries(varMovesByNumber).map(([number, varMoves]) => (
            <div key={`var-${startMoveIndex}-${variationIndex}-${number}`} className="move-row">
              <span className="move-number">{number}.</span>
              {varMoves.white && (
                <span 
                  className={`move ${
                    currentVariation && 
                    currentVariation.startMove === startMoveIndex && 
                    currentVariation.index === variationIndex && 
                    currentMove === startMoveIndex + varMoves.white.idx + 1 ? 'active' : ''
                  }`}
                  onClick={() => onMoveClick(startMoveIndex + varMoves.white.idx + 1, { startMove: startMoveIndex, index: variationIndex })}
                >
                  {varMoves.white.san}
                </span>
              )}
              {varMoves.black && (
                <span 
                  className={`move ${
                    currentVariation && 
                    currentVariation.startMove === startMoveIndex && 
                    currentVariation.index === variationIndex && 
                    currentMove === startMoveIndex + varMoves.black.idx + 1 ? 'active' : ''
                  }`}
                  onClick={() => onMoveClick(startMoveIndex + varMoves.black.idx + 1, { startMove: startMoveIndex, index: variationIndex })}
                >
                  {varMoves.black.san}
                </span>
              )}
            </div>
          ))}
        </div>
        <span className="variation-marker">⟧</span>
      </div>
    );
  };
  
  // Check if a move is active in the current variation
  const isMoveActiveInVariation = (moveIndex) => {
    return currentVariation && currentVariation.startMove === moveIndex;
  };
  
  return (
    <div className="move-list-container">
      <ul className="move-list">
        {Object.entries(movesByNumber).map(([number, moves]) => (
          <li key={number} className="move-row">
            <span className="move-number">{number}.</span>
            <div className="move-with-variations">
              {moves.white && (
                <span 
                  className={`move ${
                    currentMove === moves.white.index && 
                    (!currentVariation || currentVariation.startMove !== moves.white.index) ? 
                    'active' : ''
                  }`}
                  onClick={() => onMoveClick(moves.white.index)}
                >
                  {moves.white.san}
                </span>
              )}
              
              {/* Variations after white's move */}
              {variations && variations[moves.white.index] && variations[moves.white.index].map((varMoves, varIdx) => 
                renderVariation(varMoves, moves.white.index, varIdx)
              )}
            </div>
            
            <div className="move-with-variations">
              {moves.black && (
                <span 
                  className={`move ${
                    currentMove === moves.black.index && 
                    (!currentVariation || currentVariation.startMove !== moves.black.index) ? 
                    'active' : ''
                  }`}
                  onClick={() => onMoveClick(moves.black.index)}
                >
                  {moves.black.san}
                </span>
              )}
              
              {/* Variations after black's move */}
              {variations && variations[moves.black.index] && variations[moves.black.index].map((varMoves, varIdx) => 
                renderVariation(varMoves, moves.black.index, varIdx)
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default MoveList;