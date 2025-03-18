# Process-Mate Web App

A web application for analyzing processes and understanding the thought patterns behind decisions. This project provides a skeleton structure with placeholder functions where you can implement your own custom logic.

## Project Structure

The application is divided into two main parts:

### Backend (Python/Flask)

- `app.py`: Main Flask application with API endpoints
- `api/analyzer.py`: Core logic for chess position analysis (placeholders)

### Frontend (React)

- React components for a Lichess-like UI
- Interactive chess board using react-chessboard
- Move list with history navigation
- Analysis panel for thought process breakdown

## Features

- Interactive chess board that allows piece movement
- Move history panel with clickable moves
- Board navigation (first, previous, next, last move)
- Thought process analysis broken down by:
  - Tactics
  - Strategy
  - Calculation
  - Position evaluation
  - Plans
- Engine analysis with evaluation bar and top moves

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd process-mate/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask application:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd process-mate/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Customization

The application is designed with placeholder functions that you can replace with your own implementation:

### Backend

- `analyze_position()`: Implement your custom position analysis logic
- `get_engine_analysis()`: Implement your custom engine integration
- `parse_pgn()`: Customize PGN parsing as needed

### Frontend

- Modify the UI components to fit your needs
- Customize the board appearance
- Add additional features to the analysis panel

## Requirements

- Python 3.8+
- Node.js 14+
- python-chess
- React