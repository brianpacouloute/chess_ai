import random
import time

# ANSI escape codes for color
WHITE_PIECE_COLOR = "\033[97m"  # White color for pieces
BLACK_PIECE_COLOR = "\033[30m"  # Black color for pieces
COLUMN_COLOR = "\033[34m"  # Blue for column letters
ROW_COLOR = "\033[32m"  # Green for row numbers
RESET_COLOR = "\033[0m"         # Reset to default color

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

def check_for_win(board):
    # We just check if either king is still on the board
    white_king = any(piece == 'K' for row in board for piece in row)
    black_king = any(piece == 'k' for row in board for piece in row)
    
    if not white_king:
        return "Black wins!"
    elif not black_king:
        return "White wins!"
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

def generate_hard_move(board, color):
    """Simple piece-value based moves"""
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
                    
                    # Simple positional bonus
                    if color == 'white':
                        current_value += (7 - end[0]) * 0.1  # Encourage advancing
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
def move_piece(board, start, end):
    start_row, start_col = start
    end_row, end_col = end
    
    piece = board[start_row][start_col]
    target_piece = board[end_row][end_col]
    
    if target_piece != '.':
        print(f"{get_piece_color(piece)}{piece}{RESET_COLOR} captured {get_piece_color(target_piece)}{target_piece}{RESET_COLOR}!")
    
    # Move the piece
    board[end_row][end_col] = piece
    board[start_row][start_col] = '.'

# Generate random moves (easy AI)
def generate_random_move(board, color):
    moves = []
    for i in range(8):
        for j in range(8):
            if (board[i][j].isupper() and color == 'white') or (board[i][j].islower() and color == 'black'):
                piece = board[i][j]
                # For simplicity, just add moves that are in bounds (you'd need more logic here)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    x, y = i + dx, j + dy
                    if is_in_bounds(x, y) and board[x][y] == '.':
                        moves.append(((i, j), (x, y)))
    if moves:
        return random.choice(moves)
    return None

# Show legal moves for a piece
def show_legal_moves(board, start):
    legal_moves = []
    x, y = start
    piece = board[x][y]
    
    # Pawn movement
    if piece == 'P' or piece == 'p':
        if piece == 'P':  # White pawn
            # Single step forward
            if is_in_bounds(x-1, y) and board[x-1][y] == '.':
                legal_moves.append((x-1, y))
                # Double step from starting position
                if x == 6 and board[x-2][y] == '.':
                    legal_moves.append((x-2, y))
            # Diagonal captures
            for dy in [-1, 1]:
                if is_in_bounds(x-1, y+dy):
                    target = board[x-1][y+dy]
                    if target != '.' and target.islower():
                        legal_moves.append((x-1, y+dy))
        else:  # Black pawn
            # Single step forward
            if is_in_bounds(x+1, y) and board[x+1][y] == '.':
                legal_moves.append((x+1, y))
                # Double step from starting position
                if x == 1 and board[x+2][y] == '.':
                    legal_moves.append((x+2, y))
            # Diagonal captures
            for dy in [-1, 1]:
                if is_in_bounds(x+1, y+dy):
                    target = board[x+1][y+dy]
                    if target != '.' and target.isupper():
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

# Game loop
def game_loop():
    board = initialize_board()
    print("Welcome to Chess!")
    
    # Game mode selection
    while True:
        mode = input("Choose game mode (1 - Player vs AI, 2 - Two Player): ").strip()
        if mode in ['1', '2']:
            break
        print("Invalid input. Enter 1 or 2")

    ai_difficulty = None
    player_color = None
    if mode == '1':
        ai_difficulty = set_difficulty()
        while True:
            color_choice = input("Choose your color (w/b): ").strip().lower()
            if color_choice in ['w', 'b']:
                player_color = 'white' if color_choice == 'w' else 'black'
                break
            print("Invalid input. Enter 'w' or 'b'")

    current_turn = 'white'
    
    while True:
        # Check win condition before turn starts
        result = check_for_win(board)
        if result:
            print_board(board)
            print(f"\n{'*' * 40}")
            print(f"*** GAME OVER *** {result}")
            print(f"{'*' * 40}\n")
            break

        # Print board once at start of turn
        print_board(board)
        
        # AI turn handling
        if mode == '1' and current_turn != player_color:
            print(f"\n{current_turn.capitalize()} AI's turn...")
            time.sleep(1)  # Simulate thinking
            
            # Generate AI move based on difficulty
            if ai_difficulty == 'easy':
                move = generate_random_move(board, current_turn)
            elif ai_difficulty == 'medium':
                move = generate_medium_move(board, current_turn)
            else:
                move = generate_hard_move(board, current_turn)

            if move:
                start, end = move
                start_pos = coordinates_to_notation(*start)
                end_pos = coordinates_to_notation(*end)
                piece = board[start[0]][start[1]]
                target = board[end[0]][end[1]]
                
                move_piece(board, start, end)
                print(f"AI moved {piece} from {start_pos} to {end_pos}")
                if target != '.':
                    print(f"AI captured your {target}!")
            else:
                print("AI has no valid moves!")
            
            current_turn = 'white' if current_turn == 'black' else 'black'
            continue

        # Human player's turn
        print(f"\n{current_turn.capitalize()}'s turn:")
        move_input = input("Enter move (e.g. 'e2e4'), square (e.g. 'e2'), or piece (e.g. 'N'): ").strip().lower()

        # Handle square input (2 characters)
        if len(move_input) == 2:
            try:
                col = ord(move_input[0]) - 97
                row = 8 - int(move_input[1])
                
                if not (0 <= col < 8) or not (0 <= row < 8):
                    raise ValueError("Invalid coordinates")
                
                piece = board[row][col]
                if piece == '.':
                    print("Empty square selected")
                    continue
                
                if (current_turn == 'white' and piece.islower()) or (current_turn == 'black' and piece.isupper()):
                    print("That's not your piece!")
                    continue
                
                legal_moves = show_legal_moves(board, (row, col))
                if legal_moves:
                    print(f"\nLegal moves for {move_input.upper()}:")
                    for x, y in legal_moves:
                        print(f"  → {coordinates_to_notation(x, y)}")
                else:
                    print(f"\nNo legal moves for {piece.upper()} at {move_input.upper()}")
                
                continue  # Skip turn switch
                
            except (ValueError, IndexError):
                print("Invalid square format. Use format like 'a2'")
                continue

        # Handle single piece input (1 character)
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
            
            print(f"\nLegal moves for {search_piece}:")
            for start, end in all_moves:
                start_not = coordinates_to_notation(*start)
                end_not = coordinates_to_notation(*end)
                print(f"  {start_not} → {end_not}")
            
            continue  # Skip turn switch

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
                
            # Execute move
            target = board[end_row][end_col]
            move_piece(board, start, end)
            
            if target != '.':
                print(f"You captured {target}!")
            
            # Switch turns only after successful move
            current_turn = 'black' if current_turn == 'white' else 'black'
            
        except Exception as e:
            print(f"Invalid move: {str(e)}")

# Run the game
if __name__ == "__main__":
    game_loop()