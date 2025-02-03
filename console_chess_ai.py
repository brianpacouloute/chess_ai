import random
import time
import datetime
import glob

# ANSI escape codes for color
WHITE_PIECE_COLOR = "\033[97m" 
BLACK_PIECE_COLOR = "\033[30m" 
RED_COLOR = "\033[31m"
COLUMN_COLOR = "\033[34m" 
ROW_COLOR = "\033[32m"  
RESET_COLOR = "\033[0m" 
RED_ALERT = "\033[31m[LEARNING]\033[0m "

# Representing the chess board
def initialize_board():
    board = [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]
    return board

def board_to_fen(board, current_turn):
    fen_rows = []
    for row in board:
        fen_row = []
        empty = 0
        for cell in row:
            if cell == '.':
                empty += 1
            else:
                if empty > 0:
                    fen_row.append(str(empty))
                    empty = 0
                fen_row.append(cell)
        if empty > 0:
            fen_row.append(str(empty))
        fen_rows.append(''.join(fen_row))
    fen = '/'.join(fen_rows)
    fen += f' {current_turn[0]}'  # Add active color
    return fen

def parse_fen(fen_str):
    fen_parts = fen_str.rsplit(' ', 1)
    fen_board = fen_parts[0]
    board = []
    for row in fen_board.split('/'):
        new_row = []
        for c in row:
            if c.isdigit():
                new_row.extend(['.'] * int(c))
            else:
                new_row.append(c)
        board.append(new_row)
    return board

class GameMemory:
    def __init__(self):
        self.memory = {}
        self.load_all_games()
    
    def load_all_games(self):
        game_files = glob.glob("chess_games/*.txt")
        for game_file in game_files:
            self.process_game_file(game_file)
    
    def process_game_file(self, filename):
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            result = None
            moves = []
            for line in lines:
                if line.startswith("Result:"):
                    result = line.split(":", 1)[1].strip()
                elif line.startswith("Move:"):
                    moves.append(line.strip().split(":", 2)[1:])
            
            if not result or not moves:
                return
            
            white_outcome = None
            if "White wins" in result:
                white_outcome = 'win'
            elif "Black wins" in result:
                white_outcome = 'loss'
            else:
                white_outcome = 'draw'
            
            board = initialize_board()
            current_turn = 'white'
            for move in moves:
                fen_before, move_uci = move
                board_state = parse_fen(fen_before)
                outcome = white_outcome if current_turn == 'white' else 'loss' if white_outcome == 'win' else 'win' if white_outcome == 'loss' else 'draw'
                
                if fen_before not in self.memory:
                    self.memory[fen_before] = {}
                
                if move_uci not in self.memory[fen_before]:
                    self.memory[fen_before][move_uci] = {'wins': 0, 'losses': 0, 'draws': 0}
                
                if outcome == 'win':
                    self.memory[fen_before][move_uci]['wins'] += 1
                elif outcome == 'loss':
                    self.memory[fen_before][move_uci]['losses'] += 1
                else:
                    self.memory[fen_before][move_uci]['draws'] += 1
                
                # Update board state silently
                start, end = notation_to_coordinates(move_uci)
                move_piece(board_state, start, end, silent=True)  # Added silent=True here
                current_turn = 'black' if current_turn == 'white' else 'white'
        except Exception as e:
            print(f"Error processing {filename}: {e}")

def get_rating():
    try:
        with open("chess_rating.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return 1000  

def update_rating(result, difficulty):
    rating = get_rating()
    k_values = {'easy': 10, 'medium': 20, 'hard': 30}
    k = k_values.get(difficulty, 10)
    
    if result == 'win':
        rating += k
    elif result == 'loss':
        rating -= k
    
    rating = max(rating, 0)
    with open("chess_rating.txt", "w") as f:
        f.write(str(rating))
    return rating

def check_for_win(board):
    white_king = False
    black_king = False
    
    # Scan entire board for kings
    for row in board:
        for piece in row:
            if piece == 'K':
                white_king = True
            elif piece == 'k':
                black_king = True
    
    if not white_king and not black_king:
        return "Draw - Both kings captured!"
    if not white_king:
        return "Black wins by capturing the king!"
    if not black_king:
        return "White wins by capturing the king!"
    return None


# Display the board with colors
def print_board(board):
    print(f"    {COLUMN_COLOR}a b c d e f g h{RESET_COLOR}")
    print("  +----------------+")
    for row_index, row in enumerate(board):
        # Corrected row numbering (8-row_index since row 0 is rank 8)
        print(f"{ROW_COLOR}{8 - row_index}{RESET_COLOR} |", end=' ')
        for piece in row:
            print(get_piece_color(piece) + piece + RESET_COLOR, end=' ')
        print("|")
    print("  +----------------+")

# Check if the move is within board bounds
def is_in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8


def generate_medium_move(board, color):
    """Better than random but still simple - prefers captures"""
    moves = []
    capture_moves = []
    
    for i in range(8):
        for j in range(8):
            if (color == 'white' and board[i][j].isupper()) or (color == 'black' and board[i][j].islower()):
                legal_moves = show_legal_moves(board, (i, j))
                for end in legal_moves:
                    target = board[end[0]][end[1]]
                    if target != '.':
                        capture_moves.append(((i, j), end))
                    else:
                        moves.append(((i, j), end))
    
    # Prefer capture moves if available
    if capture_moves:
        return random.choice(capture_moves)
    return random.choice(moves) if moves else None

def generate_hard_move(board, color, memory):
    current_fen = board_to_fen(board, color)
    if current_fen in memory.memory:
        moves = memory.memory[current_fen]
        best_move = None
        best_score = -float('inf')
        
        for move, stats in moves.items():
            total = stats['wins'] + stats['losses'] + stats['draws']
            if total == 0:
                continue
            score = (stats['wins'] - stats['losses']) / total
            if score > best_score:
                best_score = score
                best_move = move
            elif score == best_score:
                if random.random() < 0.5:
                    best_move = move
        
        if best_move:
            print(f"{RED_ALERT}Using learned move: {best_move}")
            return notation_to_coordinates(best_move)
    
    # Fallback to original hard move logic
    piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
                    'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
    best_move = None
    best_value = -999
    
    for i in range(8):
        for j in range(8):
            if (color == 'white' and board[i][j].isupper()) or (color == 'black' and board[i][j].islower()):
                legal_moves = show_legal_moves(board, (i, j))
                for end in legal_moves:
                    current_value = 0
                    target = board[end[0]][end[1]]
                    if target != '.':
                        current_value += piece_values.get(target, 0)
                    
                    if color == 'white':
                        current_value += (7 - end[0]) * 0.1
                    else:
                        current_value += end[0] * 0.1
                        
                    if current_value > best_value:
                        best_value = current_value
                        best_move = ((i, j), end)
    
    return best_move if best_move else generate_medium_move(board, color)



# Convert move from notation like a1a2 to (start, end) coordinates
def notation_to_coordinates(move):
    move = move.lower().replace("-", "").replace(" ", "")
    if len(move) != 4:
        raise ValueError("Invalid move notation. Use format like 'a2a4'")
    start_col = ord(move[0]) - 97
    start_row = 8 - int(move[1])
    end_col = ord(move[2]) - 97
    end_row = 8 - int(move[3])
    return (start_row, start_col), (end_row, end_col)

# Get the piece color for printing
def get_piece_color(piece):
    if piece.isupper():
        return WHITE_PIECE_COLOR
    elif piece.islower():
        return BLACK_PIECE_COLOR
    return RESET_COLOR

# Move piece and handle captured pieces
def move_piece(board, start, end, silent=False):
    start_row, start_col = start
    end_row, end_col = end
    
    piece = board[start_row][start_col]
    target = board[end_row][end_col]
    
    if target != '.' and not silent:  # Added silent check
        print(f"{get_piece_color(piece)}{piece}{RESET_COLOR} captured {get_piece_color(target)}{target}{RESET_COLOR}!")
    
    # Handle pawn promotion
    if piece in ['P', 'p']:
        promotion_row = 0 if piece == 'P' else 7
        if end_row == promotion_row:
            piece = 'Q' if piece.isupper() else 'q'
    
    board[end_row][end_col] = piece
    board[start_row][start_col] = '.'

# Generate random moves (easy AI)
def generate_random_move(board, color):
    valid_moves = []
    in_check = is_in_check(board, color)
    
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if (color == 'white' and piece.isupper()) or (color == 'black' and piece.islower()):
                moves = show_legal_moves(board, (i, j))
                for move in moves:
                    temp_board = simulate_move(board, (i, j), move)
                    # Only consider moves that resolve check if in check
                    if not in_check or not is_in_check(temp_board, color):
                        valid_moves.append(((i, j), move))
    
    return random.choice(valid_moves) if valid_moves else None


def is_in_check(board, color):
    king_pos = find_king_position(board, color)
    if king_pos is None:
        return False
    
    opponent_color = 'black' if color == 'white' else 'white'
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != '.' and ((opponent_color == 'white' and piece.isupper()) or \
                                 (opponent_color == 'black' and piece.islower())):
                moves = show_legal_moves(board, (row, col))
                if king_pos in moves:
                    return True
    return False

def simulate_move(board, start, end):
    temp_board = [row.copy() for row in board]
    start_row, start_col = start
    end_row, end_col = end
    piece = temp_board[start_row][start_col]
    
    # Handle pawn promotion in simulation
    if piece in ['P', 'p']:
        if (piece == 'P' and end_row == 0) or (piece == 'p' and end_row == 7):
            piece = 'Q' if piece == 'P' else 'q'
    
    temp_board[end_row][end_col] = piece
    temp_board[start_row][start_col] = '.'
    return temp_board

def find_king_position(board, color):
    king = 'K' if color == 'white' else 'k'
    for row in range(8):
        for col in range(8):
            if board[row][col] == king:
                return (row, col)
    return None

def is_checkmate(board, color):
    if not is_in_check(board, color):
        return False
    
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if (color == 'white' and piece.isupper()) or (color == 'black' and piece.islower()):
                moves = show_legal_moves(board, (i, j))
                for move in moves:
                    temp_board = simulate_move(board, (i, j), move)
                    if not is_in_check(temp_board, color):
                        return False
    return True

# Show legal moves for a piece
def show_legal_moves(board, start):
    legal_moves = []
    x, y = start
    piece = board[x][y]
    
    # Pawn movement (Fixed pawn movement added conversion when reaches the otehr side)
    if piece == 'P' or piece == 'p':
        if piece == 'P':  # White pawn
            # Normal moves
            if is_in_bounds(x-1, y) and board[x-1][y] == '.':
                legal_moves.append((x-1, y))
                # Initial two-square move
                if x == 6 and board[x-2][y] == '.':
                    legal_moves.append((x-2, y))
            # Captures
            for dy in [-1, 1]:
                if is_in_bounds(x-1, y+dy) and board[x-1][y+dy] != '.' and board[x-1][y+dy].islower():
                    legal_moves.append((x-1, y+dy))
        else:  # Black pawn
            # Normal moves
            if is_in_bounds(x+1, y) and board[x+1][y] == '.':
                legal_moves.append((x+1, y))
                # Initial two-square move
                if x == 1 and board[x+2][y] == '.':
                    legal_moves.append((x+2, y))
            # Captures
            for dy in [-1, 1]:
                if is_in_bounds(x+1, y+dy) and board[x+1][y+dy] != '.' and board[x+1][y+dy].isupper():
                    legal_moves.append((x+1, y+dy))

    # Rook movement
    elif piece == 'r' or piece == 'R':
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            x_new, y_new = x, y
            while is_in_bounds(x_new + dx, y_new + dy):
                x_new += dx
                y_new += dy
                if board[x_new][y_new] == '.':
                    legal_moves.append((x_new, y_new))
                elif (piece.isupper() and board[x_new][y_new].isupper()) or \
                     (piece.islower() and board[x_new][y_new].islower()):
                    break
                else:
                    legal_moves.append((x_new, y_new))
                    break

    # Knight movement
    elif piece == 'n' or piece == 'N':
        knight_moves = [(-2, -1), (-2, 1), (2, -1), (2, 1),
                        (-1, -2), (1, -2), (-1, 2), (1, 2)]
        for dx, dy in knight_moves:
            x_new = x + dx
            y_new = y + dy
            if is_in_bounds(x_new, y_new):
                target = board[x_new][y_new]
                if target == '.' or (piece.isupper() != target.isupper()):
                    legal_moves.append((x_new, y_new))

    # Bishop movement
    elif piece == 'b' or piece == 'B':
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            x_new, y_new = x, y
            while is_in_bounds(x_new + dx, y_new + dy):
                x_new += dx
                y_new += dy
                if board[x_new][y_new] == '.':
                    legal_moves.append((x_new, y_new))
                elif (piece.isupper() and board[x_new][y_new].isupper()) or \
                     (piece.islower() and board[x_new][y_new].islower()):
                    break
                else:
                    legal_moves.append((x_new, y_new))
                    break

    # Queen movement
    elif piece == 'q' or piece == 'Q':
        # Combine rook and bishop directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            x_new, y_new = x, y
            while is_in_bounds(x_new + dx, y_new + dy):
                x_new += dx
                y_new += dy
                if board[x_new][y_new] == '.':
                    legal_moves.append((x_new, y_new))
                elif (piece.isupper() and board[x_new][y_new].isupper()) or \
                     (piece.islower() and board[x_new][y_new].islower()):
                    break
                else:
                    legal_moves.append((x_new, y_new))
                    break

    # King movement
    elif piece == 'k' or piece == 'K':
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            x_new = x + dx
            y_new = y + dy
            if is_in_bounds(x_new, y_new):
                target = board[x_new][y_new]
                if target == '.' or (piece.isupper() != target.isupper()):
                    legal_moves.append((x_new, y_new))

    return legal_moves


# Convert coordinates to chess notation
def coordinates_to_notation(x, y):
    return f"{chr(y + 97)}{8 - x}"

# Difficulty explanation
def explain_difficulty():
    print("Difficulty levels:")
    print("  Easy: The AI makes random moves.")
    print("  Medium: The AI makes better moves but is still somewhat random.")
    print("  Hard: The AI tries to make the best move based on piece evaluation.")

# Validate the difficulty input
def set_difficulty():
    while True:
        difficulty = input("Choose difficulty (easy, medium, hard): ").lower()
        if difficulty in ['easy', 'medium', 'hard']:
            print(f"You chose {difficulty.capitalize()} difficulty.")
            return difficulty
        else:
            print("Invalid input. Please enter 'easy', 'medium', or 'hard'.")

def ai_move(board):
    # Just a placeholder for Black's move: Choose random piece and move it (will need improvement)
    # For simplicity, we'll move the first available black piece
    for row in range(7, 0, -1):  # Black pieces are on rows 7 and 8
        for col in range(8):
            if board[row][col].islower():
                # Here we just attempt to move one step forward for simplicity
                if row < 7 and board[row + 1][col] == '.':
                    move_piece(board, (row, col), (row + 1, col))
                    return
                if row > 0 and board[row - 1][col] == '.':
                    move_piece(board, (row, col), (row - 1, col))
                    return

def game_loop():
    board = initialize_board()
    print("Welcome to Chess!")
    
    # Game statistics
    game_stats = {
        'moves': 0,
        'captures': {'white': 0, 'black': 0},
        'promotions': 0,
        'checks': 0,
        'start_time': time.time()
    }

    # Validate game mode
    while True:
        mode = input("Choose game mode (1 - Player vs AI, 2 - Two Player): ").strip()
        if mode in ['1', '2']:
            break
        print("Invalid input. Enter 1 or 2")

    # Validate and echo suggested moves choice
    show_suggested = ''
    while show_suggested not in ['y', 'n']:
        show_suggested = input("Enable suggested moves? (y/n): ").lower().strip()
        if show_suggested not in ['y', 'n']:
            print("Please enter 'y' or 'n'")
    show_suggested_moves = show_suggested == 'y'
    print(f"Suggested moves {'enabled' if show_suggested_moves else 'disabled'}")

    # AI setup
    ai_difficulty = None
    player_color = None
    memory = None
    if mode == '1':
        ai_difficulty = set_difficulty()
        # Initialize AI memory for hard mode
        if ai_difficulty == 'hard':
            memory = GameMemory()
        # Validate and echo color choice
        while True:
            color_choice = input("Choose your color (w/b): ").strip().lower()
            if color_choice in ['w', 'b']:
                player_color = 'white' if color_choice == 'w' else 'black'
                print(f"You are playing as {player_color}")
                break
            print("Invalid input. Enter 'w' or 'b'")

    current_turn = 'white'
    game_over = False
    
    # Create game directory if not exists
    import os
    if not os.path.exists('chess_games'):
        os.makedirs('chess_games')

    # Initialize game logging
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    game_filename = f"chess_games/game_{timestamp}.txt"
    log_entries = []
    
    # Initialize rating
    rating = get_rating()
    print(f"Your current rating: {rating}")

    while not game_over:
        print_board(board)
        
        # Check for king capture
        result = check_for_win(board)
        if not result:
            if is_checkmate(board, current_turn):
                winner = 'Black' if current_turn == 'white' else 'White'
                result = f"{winner} wins by checkmate!"
            else:
                result = "Draw"

        # Check checkmate
        if is_checkmate(board, current_turn):
            winner = 'Black' if current_turn == 'white' else 'White'
            print(f"\n*** CHECKMATE! {winner} wins! ***")
            game_over = True
            break

        # Check and announce checks
        check_status = []
        if is_in_check(board, 'white'):
            game_stats['checks'] += 1
            check_status.append("White king in check!")
        if is_in_check(board, 'black'):
            game_stats['checks'] += 1
            check_status.append("Black king in check!")
        if check_status:
            print("\n" + " | ".join(check_status))

        # AI turn
        if mode == '1' and current_turn != player_color:
            print(f"\n{current_turn.capitalize()} AI's turn...")
            time.sleep(1)
            
            valid_move_made = False
            for _ in range(3):  # Try 3 times to find valid move
                move = None
                if ai_difficulty == 'easy':
                    move = generate_random_move(board, current_turn)
                elif ai_difficulty == 'medium':
                    move = generate_medium_move(board, current_turn)
                elif ai_difficulty == 'hard':
                    move = generate_hard_move(board, current_turn, memory)

                if move:
                    start, end = move
                    # Validate move doesn't leave AI in check
                    temp_board = simulate_move(board, start, end)
                    if not is_in_check(temp_board, current_turn):
                        # Log the move
                        fen_before = board_to_fen(board, current_turn)
                        start_pos = coordinates_to_notation(*start)
                        end_pos = coordinates_to_notation(*end)
                        log_entries.append(f"Move:{fen_before}:{start_pos}{end_pos}")
                        
                        # Execute move
                        piece = board[start[0]][start[1]]
                        target = board[end[0]][end[1]]
                        
                        move_piece(board, start, end)
                        game_stats['moves'] += 1
                        
                        if target != '.':
                            color = 'white' if target.islower() else 'black'
                            game_stats['captures'][color] += 1
                            print(f"AI captured {target}!")

                        # Handle pawn promotion for AI
                        if (piece in ['P', 'p']) and ((end[0] == 0 and piece == 'P') or (end[0] == 7 and piece == 'p')):
                            board[end[0]][end[1]] = 'Q' if piece == 'P' else 'q'
                            game_stats['promotions'] += 1
                        
                        valid_move_made = True
                        break
                        
            if not valid_move_made:
                winner = 'White' if current_turn == 'black' else 'Black'
                print(f"\n{RED_COLOR}*** {winner} WINS! AI has no valid moves! ***{RESET_COLOR}")
                game_over = True
            
            current_turn = 'white' if current_turn == 'black' else 'black'
            continue

        # Human player's turn
        print(f"\n{current_turn.capitalize()}'s turn (or type 'quit' to exit):")
        move_input = input("Enter move (e.g. 'e2e4'), square (e.g. 'e2'), or piece (e.g. 'N'): ").strip().lower()

        # Handle quit command
        if move_input == 'quit':
            print("\nGame ended by user request")
            game_over = True
            break

        if not move_input:
            print("Please enter a valid input")
            continue

        # Handle square input
        if len(move_input) == 2:
            try:
                col = ord(move_input[0]) - 97
                row = 8 - int(move_input[1])
                
                if not (0 <= col < 8) or not (0 <= row < 8):
                    raise ValueError()
                
                piece = board[row][col]
                if piece == '.':
                    print("Empty square selected")
                    continue
                
                if (current_turn == 'white' and piece.islower()) or (current_turn == 'black' and piece.isupper()):
                    print("That's not your piece!")
                    continue
                
                legal_moves = show_legal_moves(board, (row, col))
                if legal_moves:
                    print(f"Legal moves for {move_input.upper()}:")
                    for x, y in legal_moves:
                        print(f"  → {coordinates_to_notation(x, y)}")
                else:
                    print(f"No legal moves for {piece.upper()} at {move_input.upper()}")
                
                continue
                
            except (ValueError, IndexError):
                print("Invalid square format. Use format like 'a2'")
                continue

        # Handle piece input
        if len(move_input) == 1:
            valid_pieces = ['k','q','r','b','n','p']
            if move_input not in valid_pieces:
                print("Invalid piece. Valid pieces: K, Q, R, B, N, P")
                continue
            
            search_piece = move_input.upper() if current_turn == 'white' else move_input.lower()
            positions = []
            for i in range(8):
                for j in range(8):
                    if board[i][j] == search_piece:
                        positions.append((i, j))
            
            if not positions:
                print(f"No {search_piece} found on the board")
                continue
            
            all_moves = []
            for pos in positions:
                moves = show_legal_moves(board, pos)
                all_moves.extend([(pos, move) for move in moves])
            
            if not all_moves:
                print(f"No legal moves available for {search_piece}")
                continue
            
            print(f"Legal moves for {search_piece}:")
            for start, end in all_moves:
                start_not = coordinates_to_notation(*start)
                end_not = coordinates_to_notation(*end)
                print(f"  {start_not} → {end_not}")
            continue

        # Handle full move input
        try:
            start, end = notation_to_coordinates(move_input)
            start_row, start_col = start
            end_row, end_col = end
            
            # Validate starting piece
            piece = board[start_row][start_col]
            if piece == '.':
                print("No piece at starting position")
                continue
                
            # Validate piece color
            if (current_turn == 'white' and piece.islower()) or (current_turn == 'black' and piece.isupper()):
                print("That's not your piece!")
                continue
                
            # Validate move legality
            legal_moves = show_legal_moves(board, start)
            if end not in legal_moves:
                print("Invalid move for this piece")
                continue
                
            # Check if move exposes king
            temp_board = simulate_move(board, start, end)
            if is_in_check(temp_board, current_turn):
                print("Invalid move - would leave king in check!")
                continue
                
            # Log the move
            fen_before = board_to_fen(board, current_turn)
            log_entries.append(f"Move:{fen_before}:{move_input}")
            
            # Execute move
            target = board[end_row][end_col]
            move_piece(board, start, end)
            
            if target != '.':
                print(f"You captured {target}!")
                # Update capture statistics
                captured_color = 'white' if target.islower() else 'black'
                game_stats['captures'][captured_color] += 1
            
            # Check pawn promotion
            if (piece == 'P' and end_row == 0) or (piece == 'p' and end_row == 7):
                new_piece = input("Promote to (Q/R/B/N): ").upper()
                while new_piece not in ['Q', 'R', 'B', 'N']:
                    new_piece = input("Invalid choice. Promote to (Q/R/B/N): ").upper()
                board[end_row][end_col] = new_piece if piece.isupper() else new_piece.lower()
                game_stats['promotions'] += 1
                print(f"Pawn promoted to {new_piece}!")

            game_stats['moves'] += 1
            current_turn = 'black' if current_turn == 'white' else 'black'
        
        except Exception as e:
            print(f"Invalid move: {str(e)}")

    # Game over statistics
    print("\n=== Game Statistics ===")
    print(f"Total moves: {game_stats['moves']}")
    print(f"White captures: {game_stats['captures']['white']}")
    print(f"Black captures: {game_stats['captures']['black']}")
    print(f"Pawn promotions: {game_stats['promotions']}")
    print(f"Checks occurred: {game_stats['checks']}")
    print(f"Game duration: {time.time() - game_stats['start_time']:.1f} seconds")
    print_board(board)
    
    # Save game log
    result = check_for_win(board) or "Draw"
    print(f"\nGame result: {result}")
    
    with open(game_filename, 'w') as f:
        f.write(f"Players: {'Player vs AI' if mode == '1' else 'Two Player'}\n")
        f.write(f"Difficulty: {ai_difficulty.capitalize() if mode == '1' else 'N/A'}\n")
        f.write(f"Result: {result}\n")
        f.write("\n".join(log_entries) + "\n")

    # Update rating for Player vs AI games
    if mode == '1':
        if "wins" in result.lower():
            player_result = 'win' if player_color in result.lower() else 'loss'
        else:
            player_result = 'draw'
        new_rating = update_rating(player_result, ai_difficulty)
        print(f"Your new rating: {new_rating}")
    
# Run the game
if __name__ == "__main__":
    game_loop()

    # it keesp saying draw even though it's a win and at the star tof all hard mode match it prints the past captires of all the past games