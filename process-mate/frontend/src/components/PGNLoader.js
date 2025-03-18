import React, { useState } from 'react';
import { Chess } from 'chess.js';

function PGNLoader({ onGameLoad }) {
  const [pgnText, setPgnText] = useState('');
  const [error, setError] = useState('');

  const handlePgnChange = (e) => {
    setPgnText(e.target.value);
    setError('');
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Check file extension
    if (!file.name.toLowerCase().endsWith('.pgn')) {
      setError('Please upload a .pgn file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target.result;
      // Basic validation - check for common PGN headers
      if (content.includes('[Event') && content.includes('[White') && content.includes('[Black')) {
        setPgnText(content);
        setError('');
      } else {
        setPgnText(content); // Still set the content but warn the user
        setError('Warning: The file may not be in standard PGN format, but we\'ll try to load it anyway.');
      }
    };
    reader.onerror = () => {
      setError('Error reading file. Please try again.');
    };
    reader.readAsText(file);
  };

  const loadGame = () => {
    if (!pgnText.trim()) {
      setError('Please enter PGN text or upload a file');
      return;
    }

    try {
      const game = new Chess();
      // In newer versions of chess.js, loadPgn doesn't return success/failure
      // It throws an exception on failure instead
      game.loadPgn(pgnText);
      
      // If we reached here, PGN loaded successfully
      onGameLoad(game);
      setError('');
      // Keep the PGN text in the textarea
      // setPgnText('');  // Removed this line
    } catch (err) {
      console.error('PGN loading error:', err);
      setError(`Failed to load PGN. Please check the format.`);
    }
  };

  return (
    <div className="pgn-loader">
      <h2 className="section-title">Load PGN</h2>
      
      <div className="mb-2">
        <textarea
          className="pgn-textarea"
          placeholder="Paste PGN text here..."
          value={pgnText}
          onChange={handlePgnChange}
          rows={3}
        />
      </div>
      
      <div className="pgn-controls">
        <label className="file-upload-label">
          <input 
            type="file" 
            accept=".pgn" 
            onChange={handleFileUpload}
            className="file-input"
          />
          <span className="file-button">Upload PGN</span>
        </label>
      
        <button 
          className="load-button" 
          onClick={loadGame}
        >
          Load
        </button>
      </div>
      
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default PGNLoader;