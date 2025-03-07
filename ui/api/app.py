# Basic Flask API for Chess Battlefield
from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import random

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Simulate battlefield engine responses
def generate_narrative(piece_type, is_capture, gives_check):
    """Generate narrative based on move characteristics."""
    piece_personalities = {
        'p': {"type": "pawn", "personality": "dutiful", "motivation": "promotion"},
        'n': {"type": "knight", "personality": "unpredictable", "motivation": "tactical advantage"},
        'b': {"type": "bishop", "personality": "strategic", "motivation": "long-term control"},
        'r': {"type": "rook", "personality": "straightforward", "motivation": "dominance"},
        'q': {"type": "queen", "personality": "powerful", "motivation": "checkmate"},
        'k': {"type": "king", "personality": "cautious", "motivation": "survival"}
    }
    
    piece_thoughts = [
        "I must secure this position!",
        "The battlefield shifts in our favor!",
        "A strategic advancement!",
        "This move will control key territory!",
        "Let me strike while they're vulnerable!"
    ]
    
    if gives_check:
        piece_thoughts = [
            "The enemy king is exposed!",
            "Check! We've got them on the defensive!",
            "Their king cannot hide forever!",
            "A direct threat to their commander!",
            "The endgame approaches!"
        ]
    
    if is_capture:
        action_descriptions = [
            f"The {piece_personalities.get(piece_type.lower(), {}).get('personality', 'determined')} {chess.piece_name(chess.PIECE_SYMBOLS.index(piece_type.lower()) if piece_type.lower() in chess.PIECE_SYMBOLS else 1)} eliminates an enemy!",
            f"A decisive capture by the {piece_personalities.get(piece_type.lower(), {}).get('personality', 'determined')} {chess.piece_name(chess.PIECE_SYMBOLS.index(piece_type.lower()) if piece_type.lower() in chess.PIECE_SYMBOLS else 1)}!",
            f"The {chess.piece_name(chess.PIECE_SYMBOLS.index(piece_type.lower()) if piece_type.lower() in chess.PIECE_SYMBOLS else 1)} claims a victim on the battlefield!"
        ]
        battlefield_impacts = [
            "The battlefield erupts with tension!",
            "A momentary advantage in the ongoing conflict!",
            "The balance of power shifts!"
        ]
        intensity = "high"
    else:
        action_descriptions = [
            f"The {piece_personalities.get(piece_type.lower(), {}).get('personality', 'determined')} {chess.piece_name(chess.PIECE_SYMBOLS.index(piece_type.lower()) if piece_type.lower() in chess.PIECE_SYMBOLS else 1)} advances to a strategic position.",
            f"A careful maneuver by the {chess.piece_name(chess.PIECE_SYMBOLS.index(piece_type.lower()) if piece_type.lower() in chess.PIECE_SYMBOLS else 1)}.",
            f"The {piece_personalities.get(piece_type.lower(), {}).get('personality', 'determined')} {chess.piece_name(chess.PIECE_SYMBOLS.index(piece_type.lower()) if piece_type.lower() in chess.PIECE_SYMBOLS else 1)} repositions for better control."
        ]
        battlefield_impacts = [
            "The battlefield terrain shifts subtly.",
            "A quiet moment in the ongoing campaign.",
            "The armies continue their strategic dance."
        ]
        intensity = "medium" if gives_check else "low"
    
    return {
        "piece_thought": random.choice(piece_thoughts),
        "action_description": random.choice(action_descriptions),
        "battlefield_impact": random.choice(battlefield_impacts),
        "intensity": intensity
    }

@app.route('/api/move', methods=['POST'])
def make_move():
    """Process a move and return narrative."""
    data = request.json
    fen = data.get('fen')
    move_uci = data.get('move')
    
    if not fen or not move_uci:
        return jsonify({"success": False, "error": "Missing FEN or move"}), 400
    
    try:
        board = chess.Board(fen)
        move = chess.Move.from_uci(move_uci)
        
        piece = board.piece_at(move.from_square)
        is_capture = board.is_capture(move)
        
        board.push(move)
        gives_check = board.is_check()
        
        # Calculate battlefield intensity based on material tension and checks
        total_pieces = sum(1 for _ in board.piece_map().values())
        max_pieces = 32  # Starting position
        progress = 1 - (total_pieces / max_pieces)
        
        # Determine game phase
        if len(board.move_stack) < 10:
            phase = "opening"
        elif progress > 0.6 or total_pieces < 10:
            phase = "endgame"
        else:
            phase = "middlegame"
        
        # Generate narrative
        narrative = generate_narrative(
            piece.symbol() if piece else 'p',
            is_capture,
            gives_check
        )
        
        return jsonify({
            "success": True,
            "fen": board.fen(),
            "narrative": narrative,
            "battlefield_state": {
                "intensity": min(0.3 + progress * 0.7, 1.0),
                "phase": phase
            }
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/analyze', methods=['POST'])
def analyze_position():
    """Analyze a position and return strategic features."""
    data = request.json
    fen = data.get('fen')
    
    if not fen:
        return jsonify({"success": False, "error": "Missing FEN"}), 400
    
    try:
        # This would be replaced with your GNN analysis
        return jsonify({
            "success": True,
            "evaluation": 0.1,  # Slightly favoring white
            "features": {
                "material_balance": 0,
                "king_safety": {
                    "white": 0.8,
                    "black": 0.7
                },
                "center_control": {
                    "white": 0.6,
                    "black": 0.5
                }
            }
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/best-move', methods=['POST'])
def get_best_move():
    """Get the best move for a position."""
    data = request.json
    fen = data.get('fen')
    skill_level = data.get('skill_level', 20)
    
    if not fen:
        return jsonify({"success": False, "error": "Missing FEN"}), 400
    
    try:
        board = chess.Board(fen)
        legal_moves = list(board.legal_moves)
        
        if not legal_moves:
            return jsonify({"success": False, "error": "No legal moves"}), 400
        
        # This would be replaced with your Stockfish analysis
        # For now, just return a random legal move
        best_move = random.choice(legal_moves)
        
        return jsonify({
            "success": True,
            "bestMove": best_move.uci(),
            "evaluation": 0.1  # Placeholder evaluation
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)