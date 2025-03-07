"""Chess engine core with battlefield extensions.""" 
"""Chess engine core with battlefield extensions."""
import chess
import chess.engine
import os
import platform
import logging
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChessEngine:
    """Core chess engine using Stockfish and python-chess."""
    
    def __init__(self, stockfish_path: Optional[str] = None, skill_level: int = 20):
        """Initialize the chess engine.
        
        Args:
            stockfish_path: Path to Stockfish executable. If None, attempt to find it.
            skill_level: Stockfish skill level (0-20, with 20 being strongest)
        """
        self.board = chess.Board()
        self.stockfish_path = stockfish_path or self._find_stockfish()
        self.skill_level = skill_level
        self.engine = None
        self.is_engine_running = False
        
        # Game state tracking
        self.move_history = []
        self.position_scores = []
        self.current_player = chess.WHITE  # White starts
        
        # Initialize engine
        self._start_engine()
    
    def _find_stockfish(self) -> str:
        """Find Stockfish executable based on operating system."""
        system = platform.system().lower()
        
        # Default paths to check based on OS
        if system == "windows":
            paths = [
                os.path.join("engines", "stockfish", "stockfish-windows-x86-64.exe"),
                "stockfish.exe",
            ]
        elif system == "linux":
            paths = [
                os.path.join("engines", "stockfish", "stockfish-ubuntu-x86-64"),
                "/usr/local/bin/stockfish",
                "/usr/bin/stockfish",
            ]
        elif system == "darwin":  # macOS
            paths = [
                os.path.join("engines", "stockfish", "stockfish-macos-x86-64"),
                "/usr/local/bin/stockfish",
            ]
        else:
            logger.error(f"Unsupported platform: {system}")
            raise ValueError(f"Unsupported platform: {system}")
        
        # Check if any of the paths exist
        for path in paths:
            if os.path.isfile(path):
                logger.info(f"Found Stockfish at: {path}")
                return path
        
        logger.warning("Stockfish not found in default locations. Please specify path manually.")
        raise FileNotFoundError("Stockfish executable not found")
    
    def _start_engine(self):
        """Start the Stockfish engine process."""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            self.engine.configure({"Skill Level": self.skill_level})
            self.is_engine_running = True
            logger.info(f"Engine started with skill level {self.skill_level}")
        except Exception as e:
            logger.error(f"Failed to start engine: {e}")
            raise
    
    def close(self):
        """Close the engine process."""
        if self.engine and self.is_engine_running:
            self.engine.quit()
            self.is_engine_running = False
            logger.info("Engine stopped")
    
    def reset_board(self):
        """Reset the board to the starting position."""
        self.board = chess.Board()
        self.move_history = []
        self.position_scores = []
        self.current_player = chess.WHITE
        logger.info("Board reset to starting position")
    
    def set_skill_level(self, level: int):
        """Set Stockfish skill level (0-20).
        
        Args:
            level: Skill level between 0 (weakest) and 20 (strongest)
        """
        if not 0 <= level <= 20:
            raise ValueError("Skill level must be between 0 and 20")
        
        self.skill_level = level
        if self.engine and self.is_engine_running:
            self.engine.configure({"Skill Level": level})
            logger.info(f"Skill level set to {level}")
    
    def make_move(self, move_uci: str) -> bool:
        """Make a move on the board.
        
        Args:
            move_uci: Move in UCI format (e.g., "e2e4")
            
        Returns:
            True if move was made successfully, False otherwise
        """
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move_uci)
                self.current_player = not self.current_player
                logger.info(f"Move made: {move_uci}")
                
                # Evaluate position after move
                score = self.evaluate_position()
                self.position_scores.append(score)
                
                return True
            else:
                logger.warning(f"Illegal move: {move_uci}")
                return False
        except Exception as e:
            logger.error(f"Error making move: {e}")
            return False
    
    def get_best_move(self, time_limit: float = 0.1) -> Tuple[str, float]:
        """Get the best move from Stockfish for the current position.
        
        Args:
            time_limit: Time in seconds to think
            
        Returns:
            Tuple of (best_move_uci, score_in_centipawns)
        """
        if not self.is_engine_running:
            logger.error("Engine not running")
            raise RuntimeError("Engine not running")
        
        result = self.engine.play(
            self.board,
            chess.engine.Limit(time=time_limit)
        )
        
        best_move = result.move
        info = self.engine.analyse(self.board, chess.engine.Limit(time=time_limit))
        score = info["score"].white().score(mate_score=10000)
        
        logger.info(f"Best move: {best_move.uci()}, Score: {score}")
        return best_move.uci(), score
    
    def evaluate_position(self) -> float:
        """Evaluate the current position.
        
        Returns:
            Score in centipawns (positive is good for white)
        """
        if not self.is_engine_running:
            logger.error("Engine not running")
            raise RuntimeError("Engine not running")
        
        info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
        score = info["score"].white().score(mate_score=10000)
        
        return score
    
    def get_legal_moves(self) -> List[str]:
        """Get all legal moves for the current position.
        
        Returns:
            List of moves in UCI format
        """
        return [move.uci() for move in self.board.legal_moves]
    
    def is_game_over(self) -> bool:
        """Check if the game is over.
        
        Returns:
            True if game is over, False otherwise
        """
        return self.board.is_game_over()
    
    def get_game_result(self) -> Optional[str]:
        """Get the result of the game if it's over.
        
        Returns:
            "1-0" (white wins), "0-1" (black wins), "1/2-1/2" (draw), or None if game not over
        """
        if not self.is_game_over():
            return None
        
        return self.board.result()
    
    def get_position_features(self) -> Dict[str, Any]:
        """Extract strategic features from the current position.
        
        This will be enhanced with GNN-based analysis in future versions.
        
        Returns:
            Dictionary of position features
        """
        features = {
            "material_balance": self._calculate_material_balance(),
            "king_safety": self._evaluate_king_safety(),
            "center_control": self._evaluate_center_control(),
            "development": self._evaluate_development(),
            "pawn_structure": self._evaluate_pawn_structure(),
        }
        
        return features
    
    def _calculate_material_balance(self) -> int:
        """Calculate material balance (positive favors white).
        
        Returns:
            Material balance in centipawns
        """
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
        }
        
        balance = 0
        for piece_type in piece_values:
            balance += len(self.board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
            balance -= len(self.board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
        
        return balance
    
    def _evaluate_king_safety(self) -> Dict[str, float]:
        """Evaluate king safety for both sides.
        
        Returns:
            Dictionary with safety scores
        """
        # This is a simple placeholder implementation
        # Will be enhanced with more sophisticated metrics
        white_king_sq = self.board.king(chess.WHITE)
        black_king_sq = self.board.king(chess.BLACK)
        
        white_attackers = len(self.board.attackers(chess.BLACK, white_king_sq)) if white_king_sq else 0
        black_attackers = len(self.board.attackers(chess.WHITE, black_king_sq)) if black_king_sq else 0
        
        return {
            "white_king_attackers": white_attackers,
            "black_king_attackers": black_attackers,
            "white_king_safety": max(0, 100 - (white_attackers * 20)),
            "black_king_safety": max(0, 100 - (black_attackers * 20)),
        }
    
    def _evaluate_center_control(self) -> Dict[str, int]:
        """Evaluate center control.
        
        Returns:
            Dictionary with center control metrics
        """
        center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        white_control = 0
        black_control = 0
        
        for sq in center_squares:
            white_control += len(self.board.attackers(chess.WHITE, sq))
            black_control += len(self.board.attackers(chess.BLACK, sq))
        
        return {
            "white_center_control": white_control,
            "black_center_control": black_control,
        }
    
    def _evaluate_development(self) -> Dict[str, int]:
        """Evaluate piece development.
        
        Returns:
            Dictionary with development metrics
        """
        # Count developed pieces (non-pawns that have moved from starting position)
        white_developed = 0
        black_developed = 0
        
        # Knights developed
        if not self.board.pieces(chess.KNIGHT, chess.WHITE) & chess.BB_B1:
            white_developed += 1
        if not self.board.pieces(chess.KNIGHT, chess.WHITE) & chess.BB_G1:
            white_developed += 1
        if not self.board.pieces(chess.KNIGHT, chess.BLACK) & chess.BB_B8:
            black_developed += 1
        if not self.board.pieces(chess.KNIGHT, chess.BLACK) & chess.BB_G8:
            black_developed += 1
        
        # Bishops developed
        if not self.board.pieces(chess.BISHOP, chess.WHITE) & chess.BB_C1:
            white_developed += 1
        if not self.board.pieces(chess.BISHOP, chess.WHITE) & chess.BB_F1:
            white_developed += 1
        if not self.board.pieces(chess.BISHOP, chess.BLACK) & chess.BB_C8:
            black_developed += 1
        if not self.board.pieces(chess.BISHOP, chess.BLACK) & chess.BB_F8:
            black_developed += 1
        
        return {
            "white_development": white_developed,
            "black_development": black_developed,
        }
    
    def _evaluate_pawn_structure(self) -> Dict[str, int]:
        """Evaluate pawn structure.
        
        Returns:
            Dictionary with pawn structure metrics
        """
        white_pawns = self.board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = self.board.pieces(chess.PAWN, chess.BLACK)
        
        # Count isolated pawns
        white_isolated = 0
        black_isolated = 0
        
        # Count doubled pawns
        white_doubled_files = 0
        black_doubled_files = 0
        
        # Check each file
        for file in range(8):
            file_mask = chess.BB_FILES[file]
            white_file_pawns = bin(white_pawns & file_mask).count('1')
            black_file_pawns = bin(black_pawns & file_mask).count('1')
            
            # Check for doubled pawns
            if white_file_pawns > 1:
                white_doubled_files += 1
            if black_file_pawns > 1:
                black_doubled_files += 1
            
            # Check for isolated pawns
            adjacent_files_mask = 0
            if file > 0:
                adjacent_files_mask |= chess.BB_FILES[file - 1]
            if file < 7:
                adjacent_files_mask |= chess.BB_FILES[file + 1]
            
            if white_file_pawns > 0 and not (white_pawns & adjacent_files_mask):
                white_isolated += white_file_pawns
            if black_file_pawns > 0 and not (black_pawns & adjacent_files_mask):
                black_isolated += black_file_pawns
        
        return {
            "white_isolated_pawns": white_isolated,
            "black_isolated_pawns": black_isolated,
            "white_doubled_files": white_doubled_files,
            "black_doubled_files": black_doubled_files,
        }


class BattlefieldChessEngine(ChessEngine):
    """Extended chess engine with battlefield narrative capabilities."""
    
    def __init__(self, stockfish_path: Optional[str] = None, skill_level: int = 20):
        """Initialize the battlefield chess engine.
        
        Args:
            stockfish_path: Path to Stockfish executable. If None, attempt to find it.
            skill_level: Stockfish skill level (0-20, with 20 being strongest)
        """
        super().__init__(stockfish_path, skill_level)
        
        # Battlefield state tracking
        self.battlefield_intensity = 0.0  # 0.0 to 1.0
        self.piece_personalities = self._initialize_piece_personalities()
        self.narrative_context = {
            "phase": "opening",  # opening, middlegame, endgame
            "key_moments": [],
            "recurring_themes": [],
        }
    
    def _initialize_piece_personalities(self) -> Dict[str, Dict]:
        """Initialize personality profiles for different piece types."""
        return {
            "P": {  # White pawns
                "personality": "dutiful",
                "motivation": "promotion",
                "risk_tolerance": 0.3,
            },
            "N": {  # White knights
                "personality": "unpredictable",
                "motivation": "tactical advantage",
                "risk_tolerance": 0.7,
            },
            "B": {  # White bishops
                "personality": "strategic",
                "motivation": "long-term control",
                "risk_tolerance": 0.5,
            },
            "R": {  # White rooks
                "personality": "straightforward",
                "motivation": "dominance",
                "risk_tolerance": 0.4,
            },
            "Q": {  # White queen
                "personality": "powerful",
                "motivation": "checkmate",
                "risk_tolerance": 0.6,
            },
            "K": {  # White king
                "personality": "cautious",
                "motivation": "survival",
                "risk_tolerance": 0.1,
            },
            "p": {  # Black pawns
                "personality": "sacrificial",
                "motivation": "promotion",
                "risk_tolerance": 0.3,
            },
            "n": {  # Black knights
                "personality": "agile",
                "motivation": "disruption",
                "risk_tolerance": 0.7,
            },
            "b": {  # Black bishops
                "personality": "far-sighted",
                "motivation": "diagonal control",
                "risk_tolerance": 0.5,
            },
            "r": {  # Black rooks
                "personality": "powerful",
                "motivation": "file control",
                "risk_tolerance": 0.4,
            },
            "q": {  # Black queen
                "personality": "dominant",
                "motivation": "attack",
                "risk_tolerance": 0.6,
            },
            "k": {  # Black king
                "personality": "defensive",
                "motivation": "survival",
                "risk_tolerance": 0.1,
            },
        }
    
    def make_move(self, move_uci: str) -> Dict[str, Any]:
        """Make a move and generate narrative context.
        
        Args:
            move_uci: Move in UCI format (e.g., "e2e4")
            
        Returns:
            Dictionary with move result and narrative information
        """
        # Make the actual move using parent class
        move_success = super().make_move(move_uci)
        
        if not move_success:
            return {"success": False}
        
        # Update battlefield state
        self._update_battlefield_state()
        
        # Generate narrative for the move
        narrative = self._generate_move_narrative(move_uci)
        
        return {
            "success": True,
            "narrative": narrative,
            "battlefield_state": {
                "intensity": self.battlefield_intensity,
                "phase": self.narrative_context["phase"],
            }
        }
    
    def _update_battlefield_state(self):
        """Update the battlefield state based on current position."""
        # Determine game phase
        if len(self.move_history) < 10:
            self.narrative_context["phase"] = "opening"
        elif self._calculate_material_balance() < 1500 or len(self.get_legal_moves()) < 30:
            self.narrative_context["phase"] = "endgame"
        else:
            self.narrative_context["phase"] = "middlegame"
        
        # Calculate battlefield intensity based on:
        # 1. Material tension (pieces that can capture each other)
        # 2. King safety
        # 3. Tactical opportunities
        # 4. Position evaluation volatility
        
        # Material tension: count attacked pieces
        tension = 0
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                attackers = self.board.attackers(not piece.color, square)
                if attackers:
                    tension += 1
        
        # Normalize tension to 0-1 range
        tension = min(tension / 6.0, 1.0)
        
        # King safety factor
        king_safety = self._evaluate_king_safety()
        safety_factor = min(
            (100 - king_safety["white_king_safety"]) / 100.0,
            (100 - king_safety["black_king_safety"]) / 100.0
        )
        
        # Position volatility: based on recent evaluation changes
        volatility = 0.0
        if len(self.position_scores) >= 3:
            recent_scores = self.position_scores[-3:]
            diffs = [abs(recent_scores[i] - recent_scores[i-1]) for i in range(1, len(recent_scores))]
            avg_diff = sum(diffs) / len(diffs)
            volatility = min(avg_diff / 200.0, 1.0)  # Normalize to 0-1
        
        # Combined intensity
        self.battlefield_intensity = (tension * 0.4) + (safety_factor * 0.3) + (volatility * 0.3)
    
    def _generate_move_narrative(self, move_uci: str) -> Dict[str, str]:
        """Generate narrative for a move.
        
        Args:
            move_uci: Move in UCI notation
            
        Returns:
            Dictionary with narrative elements
        """
        # This is a placeholder implementation - will be replaced with
        # template-based generation and eventually ML-based generation
        
        # Parse the move
        from_square = chess.parse_square(move_uci[:2])
        to_square = chess.parse_square(move_uci[2:4])
        piece = self.board.piece_at(to_square)
        
        if not piece:
            # Move was already made, so the piece is at the destination
            # This can happen with en passant or castling
            piece_symbol = '?'
        else:
            piece_symbol = piece.symbol()
        
        # Check if it was a capture
        was_capture = self.board.is_capture(chess.Move.from_uci(move_uci))
        
        # Check if it gives check
        gives_check = self.board.is_check()
        
        # Basic narrative pieces
        if was_capture:
            action = "captures"
            intensity = "high"
        else:
            action = "moves to"
            intensity = "medium" if gives_check else "low"
        
        # Get piece personality
        personality = self.piece_personalities.get(piece_symbol, {"personality": "unknown"})
        
        # Generate basic narrative
        narrative = {
            "piece_thought": f"I must secure {chess.square_name(to_square)}!",
            "action_description": f"The {personality['personality']} {chess.piece_name(piece.piece_type)} {action} {chess.square_name(to_square)}",
            "battlefield_impact": f"The battlefield {'erupts with tension' if was_capture else 'shifts slightly'}",
            "intensity": intensity,
        }
        
        if gives_check:
            narrative["action_description"] += ", threatening the enemy king"
            narrative["piece_thought"] = "The enemy king is vulnerable!"
        
        return narrative


# Test code
if __name__ == "__main__":
    try:
        import os
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define path relative to the script location
        stockfish_exe_path = os.path.join(script_dir, "stockfish", "stockfish-windows-x86-64-avx2.exe")
        
        print(f"Looking for Stockfish at: {stockfish_exe_path}")
        
        # Create a basic chess engine with the relative path
        engine = ChessEngine(stockfish_path=stockfish_exe_path)
        
        # Test some basic functionality
        print(f"Legal moves: {engine.get_legal_moves()}")
        
        # Make a move
        engine.make_move("e2e4")
        print(f"Position after e2e4: {engine.board}")
        
        # Get best response
        best_move, score = engine.get_best_move(0.5)
        print(f"Best response: {best_move}, Score: {score}")
        
        # Get position features
        features = engine.get_position_features()
        print(f"Position features: {features}")
        
        # Test battlefield extension
        battlefield = BattlefieldChessEngine(stockfish_path=stockfish_exe_path)
        result = battlefield.make_move("e2e4")
        print(f"Battlefield narrative: {result['narrative']}")
        
        # Clean up
        engine.close()
        battlefield.close()
        
    except Exception as e:
        print(f"Error in test: {e}")