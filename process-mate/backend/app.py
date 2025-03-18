#!/usr/bin/env python3
"""
Process-Mate Web App Backend
Flask API that serves as the backend for the process analysis web application
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import chess.engine
from api.analyzer import ProcessAnalyzer

app = Flask(__name__)
CORS(app)

# Initialize the process analyzer
analyzer = ProcessAnalyzer()

@app.route('/api/analyze', methods=['POST'])
def analyze_position():
    """
    Analyze a chess position and return insights on the thought process
    """
    data = request.json
    fen = data.get('fen', chess.STARTING_FEN)
    move = data.get('move')
    
    # PLACEHOLDER: This function will be implemented by the user
    # It should analyze the position and the thought process behind a move
    result = analyzer.analyze_position(fen, move)
    
    return jsonify(result)

@app.route('/api/engine-analysis', methods=['POST'])
def get_engine_analysis():
    """
    Get engine analysis for a given position
    """
    data = request.json
    fen = data.get('fen', chess.STARTING_FEN)
    depth = data.get('depth', 20)
    
    # PLACEHOLDER: This function will be implemented by the user
    # It should return Stockfish analysis for the position
    result = analyzer.get_engine_analysis(fen, depth)
    
    return jsonify(result)

@app.route('/api/validate-pgn', methods=['POST'])
def validate_pgn():
    """
    Validate and parse a PGN game
    """
    data = request.json
    pgn_text = data.get('pgn', '')
    
    # PLACEHOLDER: This function will be implemented by the user
    # It should validate the PGN and return the game data
    result = analyzer.parse_pgn(pgn_text)
    
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    """
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))