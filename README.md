# AI CHESS GAME
## CONTROLS & FEATURES

### 1. Move Input:
- **Standard Notation:** `e2e4` (from-to squares)
- **Square Query:** `e2` shows legal moves for piece on that square
- **Piece Query:** `N` shows all legal knight moves
- **Quit Game:** Type `quit` at any turn

### 2. AI Features:
- **Three Difficulties:**
  - *Easy:* Random valid moves
  - *Medium:* Prefers captures
  - *Hard:* Uses piece values and positional bonuses
- **Auto-Promotion:** Always promotes pawns to Queens
- **Safety Checks:** Never makes moves that leave itself in check

### 3. Game Features:
- **Check Detection:** Red warning when king is threatened
- **Checkmate Detection:** Game ends immediately with red announcement
- **Pawn Promotion:** Human players choose promotion piece (`Q/R/B/N`)
- **Move Validation:** Prevents illegal moves and self-checks
- **Game Statistics:** Shown at end including duration and captures

### 4. Visual Features:
- **Color-Coded Pieces:** White (bright), Black (dark)
- **Red Alerts:** Captures, checks, promotions, and warnings
- **Suggested Moves:** Enabled/disabled at start

### 5. Win Conditions:
- **King Capture:** Immediate victory
- **Checkmate:** No legal moves while in check
- **AI Surrender:** When AI has no valid moves (non-check situations)

## HOW TO PLAY
1. Choose game mode (`1vAI` or `2 players`)
2. Select difficulty if playing against AI
3. Enter moves using chess notation
4. Use square/piece queries to see legal moves
5. Promote pawns when reaching final rank
6. Game ends when:
   - King is captured
   - Checkmate occurs
   - AI cannot move
   - Player types `quit`

## RECENT UPDATES
- Red color alerts for critical messages
- AI move validation improvements
- Detailed game statistics
- Stalemate detection for AI
- Input validation and error handling
