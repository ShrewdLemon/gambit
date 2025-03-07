class ChessEngineService {
  constructor() {
    this.apiBaseUrl = 'http://localhost:5000/api'; // Adjust to your Python API endpoint
  }
ECHO is off.
  async getMoveWithNarrative(boardFen, move) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/move`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fen: boardFen,
          move: move
        }),
      });
ECHO is off.
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
ECHO is off.
      return await response.json();
    } catch (error) {
      console.error('Error making move:', error);
      // Fallback to local move if API fails
      return {
        success: true,
        fen: null, // The frontend will need to calculate this
        narrative: {
          piece_thought: "Connection to battlefield command lost!",
          action_description: "The piece moves forward uncertainly.",
          battlefield_impact: "The battlefield continues without strategic guidance.",
          intensity: "low"
        },
        battlefield_state: {
          intensity: 0.3,
          phase: "unknown"
        }
      };
    }
  }
ECHO is off.
  async getPositionAnalysis(boardFen) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fen: boardFen
        }),
      });
ECHO is off.
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
ECHO is off.
      return await response.json();
    } catch (error) {
      console.error('Error analyzing position:', error);
      return {
        evaluation: 0,
        features: {}
      };
    }
  }
ECHO is off.
  async getBestMove(boardFen, skillLevel = 15) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/best-move`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fen: boardFen,
          skill_level: skillLevel
        }),
      });
ECHO is off.
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
ECHO is off.
      return await response.json();
    } catch (error) {
      console.error('Error getting best move:', error);
      // Fallback to null and let the caller handle
      return null;
    }
  }
}

