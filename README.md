# Chess Thought Process Analyzer

A focused application designed for adult chess improvers to analyze chess games move-by-move according to a structured thought process.

## Overview

Chess Thought Process Analyzer helps you systematically analyze each move in your chess games using a well-defined thought process. By following this structured approach, you can develop better habits when analyzing positions during actual games.

The application follows a specific thought process flowchart:

1. **Check for opponent threats** (max 3-ply tactic)
2. **If threats exist**: List all options for responses (capture attacker, block, escape, counterattack)
3. **If no threats**: Perform checks, captures, and threats (CCT) analysis and look for tactical signals
4. **Generate candidate moves and quickly eliminate clearly bad ones**
5. **Calculate variations until position is quiet** (no forcing moves or immediate threats)
6. **Evaluate the position** (positive, equal, or negative)
7. **Choose a move** and blunder-check before playing

## Features

- **PGN Import**: Load your chess games from PGN files
- **Interactive Board**: Visualize and navigate through the game
- **Thought Process Analysis**: Get step-by-step analysis of each position
- **CCT Analysis**: Systematic checks, captures, and threats identification
- **Candidate Move Evaluation**: Quick elimination of clearly inferior moves
- **Deep Calculation**: Analysis of variations until the position is quiet
- **Engine Integration**: Get objective evaluation from Stockfish
- **Save Analysis**: Export the analysis for future reference

## Installation

### Requirements

- Python 3.6 or later
- Required packages:
  - python-chess
  - cairosvg
  - pillow
- Stockfish chess engine (recommended)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/chess-thought-analyzer.git
   cd chess-thought-analyzer
   ```

2. Install dependencies:
   ```
   pip install python-chess cairosvg pillow
   ```

3. Download Stockfish from [stockfishchess.org](https://stockfishchess.org/download/) and place it in the `stockfish` directory or a location of your choice.

4. Run the launcher:
   ```
   python launcher.py
   ```

## Usage

1. **Load a PGN file**: Click File > Open PGN and select your chess game file
2. **Navigate through the game**: Use the navigation buttons to move through the game
3. **Select a move**: Click on a move in the move list to jump to that position
4. **Analyze the position**: The right panel will show the thought process analysis for the current position
5. **Save analysis**: Use File > Save Analysis to export the analysis for the current position

## Thought Process Guide

The analysis for each position follows this structure:

1. **Opponent Threats?**
   - Check if your king is in check
   - Check if any pieces are under attack
   - Look for tactical threats (forks, pins, etc.)

2. **Response Options** (if threats exist)
   - Capture the attacker
   - Block the threat
   - Move the attacked piece
   - Create a counterattack

3. **CCT Analysis & Tactical Signals** (if no threats)
   - Systematically check all possible:
     - Checks: Moves that give check to the opponent
     - Captures: All possible piece captures
     - Threats: Moves that create immediate threats
   - Look for tactical patterns (pins, forks, discovered attacks)
   - Identify undefended or poorly defended pieces

4. **Candidate Move Selection**
   - Generate candidate moves from CCT analysis
   - Quickly eliminate clearly inferior moves
   - Focus detailed analysis on remaining candidates

5. **Position Calculation**
   - Calculate variations until reaching a quiet position
   - A position is quiet when there are no:
     - Checks
     - Captures
     - Immediate threats
   - Assess the resulting positions

6. **Position Evaluation**
   - Determine if position is favorable (+), equal (=), or unfavorable (-)
   - Consider material, piece activity, pawn structure, king safety

7. **Move Selection & Blunder Check**
   - Choose the best move based on the analysis
   - Verify it doesn't blunder material
   - Ensure it aligns with strategic goals

## Customization

You can modify the thought process analysis by editing the analysis functions in the source code.

## License

[MIT License](LICENSE)

## Acknowledgments

- [python-chess](https://python-chess.readthedocs.io/): Chess library for Python
- [Stockfish](https://stockfishchess.org/): Open-source chess engine
- [cairosvg](https://cairosvg.org/): SVG to PNG converter

---

*Developed specifically for adult chess improvers looking to enhance their thought process during games.*# Chess Thought Process Analyzer

A focused application designed for adult chess improvers to analyze chess games move-by-move according to a structured thought process.

## Overview

Chess Thought Process Analyzer helps you systematically analyze each move in your chess games using a well-defined thought process. By following this structured approach, you can develop better habits when analyzing positions during actual games.

The application follows a specific thought process flowchart:

1. **Check for opponent threats** (max 3-ply tactic)
2. **If threats exist**: List all options for responses (capture attacker, block, escape, counterattack)
3. **If no threats**: Determine game phase and check for tactical signals or strategic elements
4. **Calculate and evaluate** the position
5. **Choose a move** and blunder-check before playing

## Features

- **PGN Import**: Load your chess games from PGN files
- **Interactive Board**: Visualize and navigate through the game
- **Thought Process Analysis**: Get step-by-step analysis of each position
- **Engine Integration**: Get objective evaluation from Stockfish
- **Custom Flowchart**: Analysis follows your specific thought process
- **Save Analysis**: Export the analysis for future reference

## Installation

### Requirements

- Python 3.6 or later
- Required packages:
  - python-chess
  - cairosvg
  - pillow
- Stockfish chess engine (recommended)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/chess-thought-analyzer.git
   cd chess-thought-analyzer
   ```

2. Install dependencies:
   ```
   pip install python-chess cairosvg pillow
   ```

3. Download Stockfish from [stockfishchess.org](https://stockfishchess.org/download/) and place it in the `stockfish` directory or a location of your choice.

4. Run the launcher:
   ```
   python launcher.py
   ```

## Usage

1. **Load a PGN file**: Click File > Open PGN and select your chess game file
2. **Navigate through the game**: Use the navigation buttons to move through the game
3. **Select a move**: Click on a move in the move list to jump to that position
4. **Analyze the position**: The right panel will show the thought process analysis for the current position
5. **Save analysis**: Use File > Save Analysis to export the analysis for the current position

## Thought Process Guide

The analysis for each position follows this structure:

1. **Opponent Threats?**
   - Check if your king is in check
   - Check if any pieces are under attack
   - Look for tactical threats (forks, pins, etc.)

2. **Response Options** (if threats exist)
   - Capture the attacker
   - Block the threat
   - Move the attacked piece
   - Create a counterattack

3. **Game Phase & Tactical Signals** (if no threats)
   - Determine the game phase (opening, middlegame, endgame)
   - Look for tactical signals (undefended pieces, pins, etc.)

4. **Position Evaluation**
   - Engine evaluation
   - Subjective assessment (+, =, -)

5. **Move Selection & Blunder Check**
   - Choose a move based on the analysis
   - Verify it doesn't blunder material

## Customization

You can modify the thought process analysis by editing the analysis functions in the source code.

## License

[MIT License](LICENSE)

## Acknowledgments

- [python-chess](https://python-chess.readthedocs.io/): Chess library for Python
- [Stockfish](https://stockfishchess.org/): Open-source chess engine
- [cairosvg](https://cairosvg.org/): SVG to PNG converter

---

*Developed specifically for adult chess improvers looking to enhance their thought process during games.*
