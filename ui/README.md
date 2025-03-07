# Self-Aware Chess Battlefield UI

This is the UI component for the Self-Aware Chess Battlefield project, which transforms traditional chess into a narrative-driven experience with self-aware pieces.

## Setup Instructions

### 1. Set up the UI

```bash
# Install dependencies
cd ui
npm install

# Start the UI development server
npm start
```

### 2. Set up the temporary API (until full Python integration)

```bash
# Install API dependencies
cd api
pip install -r requirements.txt

# Start the API server
python app.py
```

### 3. Integration with your Python engine

The UI is designed to work with your Python-based chess engine and GNN position understanding system. Once your backend components are ready, you can:

1. Replace the temporary API with your actual BattlefieldChessEngine
2. Connect the GNN position analysis system to the API endpoints
3. Enhance the narrative generation with your personality system

## Features

- Interactive chessboard with move validation
- Battlefield narrative generation
- Visual representation of battlefield intensity and phase
- Piece "thoughts" displayed as speech bubbles
- Tiered AI opponents with personalities
- Game timer and move history

## Project Structure

```
ui/                      # React UI components
├── public/              # Static assets
├── src/                 # Source code
│   ├── components/      # React components
│   ├── services/        # API services
│   └── styles/          # SCSS styles
└── package.json         # Dependencies

api/                     # Temporary API (to be replaced)
├── app.py               # Flask server
└── requirements.txt     # Python dependencies
```
