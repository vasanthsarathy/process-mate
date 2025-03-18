import React from 'react';

function MoveList({ history, currentMove, onMoveClick }) {
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
  
  return (
    <div className="move-list-container">
      <ul className="move-list">
        {Object.entries(movesByNumber).map(([number, moves]) => (
          <li key={number} className="move-row">
            <span className="move-number">{number}.</span>
            {moves.white && (
              <span 
                className={`move ${currentMove === moves.white.index ? 'active' : ''}`}
                onClick={() => onMoveClick(moves.white.index)}
              >
                {moves.white.san}
              </span>
            )}
            {moves.black && (
              <span 
                className={`move ${currentMove === moves.black.index ? 'active' : ''}`}
                onClick={() => onMoveClick(moves.black.index)}
              >
                {moves.black.san}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default MoveList;