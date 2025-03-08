import os
import subprocess
import chess
import chess.engine
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Find Stockfish using a relative path within the project
def find_stockfish():
    # Base directory is where this script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for Stockfish in common locations relative to this script
    possible_paths = [
        os.path.join(base_dir, "stockfish", "stockfish-windows-x86-64-avx2.exe"),  # Windows
        os.path.join(base_dir, "..", "src", "engine", "stockfish", "stockfish-windows-x86-64-avx2.exe"),  # Windows relative to project root
        os.path.join(base_dir, "stockfish", "stockfish"),  # Linux/Mac
        os.path.join(base_dir, "..", "src", "engine", "stockfish", "stockfish")  # Linux/Mac relative to project root
    ]
    
    # Add more platform-specific paths as needed
    if os.name == 'nt':  # Windows
        possible_paths.append(os.path.join(base_dir, "stockfish.exe"))
    else:  # Unix-like
        possible_paths.append(os.path.join(base_dir, "stockfish"))
    
    # Check which path exists
    for path in possible_paths:
        if os.path.isfile(path):
            print(f"Found Stockfish at: {path}")
            return path
    
    # If not found, raise an error
    raise FileNotFoundError("Stockfish engine not found. Please place it in the 'stockfish' directory.")

# Try to find Stockfish
STOCKFISH_PATH = find_stockfish()

@app.route('/api/best-move', methods=['POST'])
def get_best_move():
    """Get the best move from Stockfish for a position."""
    data = request.json
    fen = data.get('fen')
    skill_level = data.get('skill_level', 20)
    move_time = data.get('move_time', 1000)  # milliseconds
    
    if not fen:
        return jsonify({"success": False, "error": "Missing FEN"}), 400
    
    try:
        # Create a chess board from the FEN
        board = chess.Board(fen)
        
        # Initialize the Stockfish engine
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        
        # Set skill level
        engine.configure({"Skill Level": skill_level})
        
        # Get the best move
        result = engine.play(
            board, 
            chess.engine.Limit(time=move_time/1000)  # Convert to seconds
        )
        
        # Close the engine
        engine.quit()
        
        # Return the best move
        return jsonify({
            "success": True,
            "bestMove": result.move.uci(),
            "ponder": result.ponder.uci() if result.ponder else None,
            "evaluation": None  # Could calculate eval if needed
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# Your existing routes...

if __name__ == '__main__':
    app.run(debug=True, port=5000)