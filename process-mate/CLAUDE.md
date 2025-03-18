# Process-Mate Development Guidelines

## Commands
- **Backend Start**: `cd backend && python app.py`
- **Frontend Start**: `cd frontend && npm start`
- **Frontend Build**: `cd frontend && npm run build`
- **Frontend Test**: `cd frontend && npm test`
- **Single Test**: `cd frontend && npm test -- -t "test_name"`
- **Python Tests**: `cd backend && python -m unittest discover`

## Code Style

### Python
- Use docstrings for classes and functions (triple quotes)
- Type hints for function parameters and return values
- Exception handling with specific exception types
- PEP 8 style guidelines (4-space indentation)
- Class names: PascalCase, function/variable names: snake_case
- Import order: standard library, third-party, local

### JavaScript/React
- React functional components with hooks
- JSDoc comments for functions and components
- Error handling with try/catch blocks
- Destructure props in component parameters
- Use const/let appropriately, avoid var
- Prefer async/await over Promise chains
- Export named functions rather than anonymous ones

## Project Structure
Backend (Flask) and frontend (React) communicate via REST API.
Always use absolute paths for imports and maintain separation of concerns.