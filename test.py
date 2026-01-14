import random
import math
import time

class CheckersGame:
    def __init__(self, black_ai_type=None, white_ai_type=None, ai_vs_ai=None):
        if black_ai_type is None:
            black_ai_type = self.select_ai("Black")
        self.black_ai_type = black_ai_type

        if white_ai_type is None:
            white_ai_type = self.select_ai("White")
        self.white_ai_type = white_ai_type

        if ai_vs_ai is None:
            ai_vs_ai = self.select_game_mode()
        self.ai_vs_ai = ai_vs_ai

        self.board = self.initialize_board()
        self.current_turn = "Player"
        self.previous_moves = {"AI": None, "Player": None}
        self.transposition_table = {}
        self.max_depth = 10  # Maximum depth for the simulation to avoid infinite recursion


    def initialize_board(self):
        board = [[" " for _ in range(8)] for _ in range(8)]
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = "b"
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = "w"
        return board

    def select_game_mode(self):
        print("Select game mode:")
        print("1. Player vs AI")
        print("2. AI vs AI")
        while True:
            choice = input("Enter the number of the game mode you want to play (1 or 2): ")
            if choice == '1':
                return False
            elif choice == '2':
                return True
            else:
                print("Invalid selection. Please choose 1 or 2.")

    def get_opponent_color(self, color):
        return 'b' if color == 'w' else 'w'

    def select_ai(self, color):
        print(f"Select an AI opponent for {color}:")
        print("1. Random AI")
        print("2. Minimax AI")
        print("3. Alpha-Beta AI")
        print("4. Negamax AI")
        print("5. Negascout AI")
        print("6. MCTS AI") 
        while True:
            try:
                choice = int(input(f"Enter the number of the AI for {color} (1-6): "))
                if 1 <= choice <= 6:
                    print(f"You selected AI {choice} for {color}.")
                    return choice
                else:
                    print("Invalid selection. Please choose a number between 1 and 6.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 6.")


    def print_board(self):
        print("  " + " ".join(map(str, range(8))))
        for i, row in enumerate(self.board):
            print(f"{i} " + " ".join(row))
        print()

    def get_piece_moves(self, r, c):
        moves = []
        piece = self.board[r][c]
        if piece == " ":
            return moves

        if piece == "W" or piece == "B":
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece == "w":
            directions = [(-1, -1), (-1, 1)]
        elif piece == "b":
            directions = [(1, -1), (1, 1)]
        else:
            return moves

        opponent_color = self.get_opponent_color(piece.lower())

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == " ":
                moves.append((nr, nc))

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            jump_r, jump_c = r + 2 * dr, c + 2 * dc
            if (
                0 <= nr < 8 and 0 <= nc < 8 and
                0 <= jump_r < 8 and 0 <= jump_c < 8 and
                self.board[nr][nc].lower() == opponent_color and self.board[jump_r][jump_c] == " "
            ):
                moves.append((jump_r, jump_c))

        return moves

    def get_all_moves(self, color):
        moves = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c].lower() == color:
                    piece_moves = self.get_piece_moves(r, c)
                    for move in piece_moves:
                        moves.append(((r, c), move))
        return moves

    def make_move(self, start, end):
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]
        self.board[er][ec] = piece
        self.board[sr][sc] = " "
        captured_piece = None
        if abs(er - sr) == 2:
            captured_r, captured_c = (sr + er) // 2, (sc + ec) // 2
            captured_piece = self.board[captured_r][captured_c]
            self.board[captured_r][captured_c] = " "
        promoted = False
        if piece == "w" and er == 0:
            self.board[er][ec] = "W"
            promoted = True
        elif piece == "b" and er == 7:
            self.board[er][ec] = "B"
            promoted = True
        self.previous_moves[self.current_turn] = (start, end)
        return captured_piece, promoted

    def undo_move(self, start, end, captured_piece=None, was_promoted=False):
        sr, sc = start
        er, ec = end
        piece = self.board[er][ec]
        if was_promoted:
            piece = piece.lower()
        self.board[sr][sc] = piece
        self.board[er][ec] = " "
        if captured_piece:
            captured_r, captured_c = (sr + er) // 2, (sc + ec) // 2
            self.board[captured_r][captured_c] = captured_piece

    def evaluate_move(self, move):
        start, end = move
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]
        opponent_color = self.get_opponent_color(piece.lower())
        
        # More advanced heuristics can be used, for simplicity we keep the old logic:
        if abs(er - sr) == 2:
            captured_r, captured_c = (sr + er) // 2, (sc + ec) // 2
            captured_piece = self.board[captured_r][captured_c]
            if captured_piece.lower() == opponent_color:
                return 100
        if (piece == "w" and er == 0) or (piece == "b" and er == 7):
            return 50
        return 10 - abs(4 - ec)

    def evaluate_board(self):
        player_score = 0
        ai_score = 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == "w":
                    player_score += 1 + (0.5 if r < 3 else 0)
                elif piece == "W":
                    player_score += 1.5 + 0.1 * (4 - abs(4 - c))
                elif piece == "b":
                    ai_score += 1 + (0.5 if r > 4 else 0)
                elif piece == "B":
                    ai_score += 1.5 + 0.1 * (4 - abs(4 - c))
        return ai_score - player_score

    def minimax(self, depth, is_maximizing, color):
        if depth == 0:
            return self.evaluate_board(), None
        moves = self.get_all_moves(color)
        if not moves:
            return (-math.inf if is_maximizing else math.inf), None
        best_move = None
        previous_move = self.previous_moves[self.current_turn]
        if is_maximizing:
            max_eval = -math.inf
            for start, end in moves:
                if previous_move and end == previous_move[0] and start == previous_move[1]:
                    continue
                captured_piece, was_promoted = self.make_move(start, end)
                eval, _ = self.minimax(depth - 1, False, self.get_opponent_color(color))
                self.undo_move(start, end, captured_piece, was_promoted)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (start, end)
            return max_eval, best_move
        else:
            min_eval = math.inf
            for start, end in moves:
                if previous_move and end == previous_move[0] and start == previous_move[1]:
                    continue
                captured_piece, was_promoted = self.make_move(start, end)
                eval, _ = self.minimax(depth - 1, True, self.get_opponent_color(color))
                self.undo_move(start, end, captured_piece, was_promoted)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (start, end)
            return min_eval, best_move

    def negamax(self, depth, alpha, beta, color):
        if depth == 0:
            return self.evaluate_board()
        
        best_value = -math.inf
        moves = self.get_all_moves(color)
        moves.sort(key=lambda move: self.evaluate_move(move), reverse=True)
        
        for move in moves:
            captured_piece, was_promoted = self.make_move(move[0], move[1])
            value = -self.negamax(depth - 1, -beta, -alpha, self.get_opponent_color(color))
            self.undo_move(move[0], move[1], captured_piece, was_promoted)
            best_value = max(best_value, value)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        
        return best_value

    def alpha_beta(self, depth, alpha, beta, is_maximizing, color):
        if depth == 0:
            return self.evaluate_board(), None
        moves = self.get_all_moves(color)
        if not moves:
            return (-math.inf if is_maximizing else math.inf), None
        best_move = None
        if is_maximizing:
            max_eval = -math.inf
            for start, end in moves:
                captured_piece, was_promoted = self.make_move(start, end)
                eval, _ = self.alpha_beta(depth - 1, alpha, beta, False, self.get_opponent_color(color))
                self.undo_move(start, end, captured_piece, was_promoted)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (start, end)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for start, end in moves:
                captured_piece, was_promoted = self.make_move(start, end)
                eval, _ = self.alpha_beta(depth - 1, alpha, beta, True, self.get_opponent_color(color))
                self.undo_move(start, end, captured_piece, was_promoted)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (start, end)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
    def mcts(self, color, simulations=100):
            # Initialize variables to track the best move and its score
            best_move = None
            best_score = -math.inf 
            all_moves = self.get_all_moves(color)

            # If no moves are available, return None
            if not all_moves:
                return best_move

            # Sort moves based on their evaluation scores in descending order (higher scores first)
            move_order = sorted(all_moves, key=lambda move: self.evaluate_move(move), reverse=True)

            # Perform the specified number of simulations
            for _ in range(simulations):
                # Iterate through the pre-sorted moves
                for start, end in move_order:
                    # Execute the move and record any captured piece or promotion
                    captured_piece, promoted = self.make_move(start, end)

                    # Hash the current board state for caching purposes
                    board_hash = str(self.board)

                    # Check if the score for this board state is already cached
                    if board_hash in self.transposition_table:
                        score = self.transposition_table[board_hash]  # Retrieve score
                    else:
                        # Simulate the game from the opponent's perspective and store the score
                        score = self.simulate_game(self.get_opponent_color(color), depth=0)
                        self.transposition_table[board_hash] = score  # Cache the computed score

                    # Undo the move to restore the board to its original state (backtrack)
                    self.undo_move(start, end, captured_piece, promoted)

                    # Update the best move and score if the current score is higher
                    if score > best_score:
                        best_score = score
                        best_move = (start, end)

            # Return the best move found during the simulations
            return best_move
    def mcts_ai_turn(self, color, ai_name):
        print(f"{ai_name} is thinking with MCTS...")
        best_move = self.mcts(color)  # Use MCTS to find the best move
        if best_move:
            start, end = best_move
            self.make_move(start, end)
            print(f"{ai_name} moved from {start} to {end}")
            return True
        else:
            print(f"No valid moves available for {ai_name}.")
            return False
    def simulate_game(self, color, depth=0):
        # Generate a unique hash for the current board state
        board_hash = str(self.board)

        # Check if the board state and depth are already in the transposition table
        if (board_hash, depth) in self.transposition_table:
            return self.transposition_table[(board_hash, depth)]

        # If the maximum depth is reached, return the board evaluation
        if depth >= self.max_depth:
            return self.evaluate_board()

        # Get all valid moves for the current player
        valid_moves = self.get_all_moves(color)

        # If no valid moves are available, return the board evaluation
        if not valid_moves:
            return self.evaluate_board()

        # Sorts the valid moves based on their evaluated score in descending order
        move_order = sorted(valid_moves, key=lambda move: self.evaluate_move(move), reverse=True)

        # Select the best move and makes move on the board (highest score from sorted list)
        start, end = move_order[0]
        captured_piece, promoted = self.make_move(start, end)

        # Recursively simulate the game for the opponent's turn, increasing depth
        score = self.simulate_game(self.get_opponent_color(color), depth + 1)

        # Undo the move to restore the board to its previous state
        self.undo_move(start, end, captured_piece, promoted)

        # Store the computed score in the transposition table to avoid recomputation
        self.transposition_table[(board_hash, depth)] = score

        # Return the computed score for this board state
        return score

    def negascout(self, depth, alpha, beta, color):
        color_factor = 1 if color == 'b' else -1  # Add this line
        if depth == 0:
            return color_factor * self.evaluate_board(), None  # Modify this line

        moves = self.get_all_moves(color)
        if not moves:
            return -math.inf, None  # Modify this line

        # The rest of the negascout function remains unchanged
        moves.sort(key=lambda move: self.evaluate_move(move), reverse=True)

        best_move = None
        is_first_child = True

        for move in moves:
            captured_piece, was_promoted = self.make_move(move[0], move[1])

            if is_first_child:
                # Full-width window for the first child
                value, _ = self.negascout(depth - 1, -beta, -alpha, self.get_opponent_color(color))
                value = -value
            else:
                # Null-window search for subsequent children
                value, _ = self.negascout(depth - 1, -alpha - 1, -alpha, self.get_opponent_color(color))
                value = -value
                if alpha < value < beta:
                    # Re-search with full window if null-window search fails
                    value, _ = self.negascout(depth - 1, -beta, -value, self.get_opponent_color(color))
                    value = -value

            self.undo_move(move[0], move[1], captured_piece, was_promoted)

            if value > alpha:
                alpha = value
                best_move = move

            if alpha >= beta:
                # Beta cutoff
                break

            is_first_child = False

        return alpha, best_move





    def player_turn(self):
        print("Player's turn!")
        while True:
            try:
                start_input = input("Enter piece to move (row col) or type 'quit' to end the game: ").strip()
                if start_input.lower() == "quit":
                    print("You ended the game. Thanks for playing!")
                    return False
                start_r, start_c = map(int, start_input.split())
                if self.board[start_r][start_c] not in ["w", "W"]:
                    print("You must select one of your own pieces. Try again.")
                    continue
                valid_moves = self.get_piece_moves(start_r, start_c)
                if not valid_moves:
                    print("This piece has no valid moves. Try another piece.")
                    continue
                print("Valid moves:", valid_moves)
                end_input = input("Enter target position (row col) or type 'quit' to end the game: ").strip()
                if end_input.lower() == "quit":
                    print("You ended the game. Thanks for playing!")
                    return False
                end_r, end_c = map(int, end_input.split())
                if (end_r, end_c) in valid_moves:
                    self.make_move((start_r, start_c), (end_r, end_c))
                    self.print_board()
                    if abs(end_r - start_r) == 2:
                        more_captures = self.get_piece_moves(end_r, end_c)
                        if any(abs(m[0] - end_r) == 2 for m in more_captures):
                            print("You have another capture! Continue moving.")
                            start_r, start_c = end_r, end_c
                            continue
                    break
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Enter row and column as numbers.")
        return True

    def random_ai_turn(self, color, ai_name):
        valid_moves = self.get_all_moves(color)
        if not valid_moves:
            print(f"No valid moves available for {ai_name}.")
            return False
        move = random.choice(valid_moves)
        self.make_move(move[0], move[1])
        print(f"{ai_name} moved from {move[0]} to {move[1]}")
        return True

    def minimax_ai_turn(self, color, ai_name):
        print(f"{ai_name} is thinking strategically...")
        _, best_move = self.minimax(3, True, color)
        if not best_move:
            print(f"No valid moves available for {ai_name}.")
            return False
        self.make_move(best_move[0], best_move[1])
        print(f"{ai_name} moved from {best_move[0]} to {best_move[1]}")
        start_r, start_c = best_move[1]
        while True:
            additional_moves = self.get_piece_moves(start_r, start_c)
            capture_moves = [m for m in additional_moves if abs(m[0] - start_r) == 2]
            if capture_moves:
                next_move = capture_moves[0]
                self.make_move((start_r, start_c), next_move)
                print(f"{ai_name} continued capturing to {next_move}")
                start_r, start_c = next_move
            else:
                break
        return True

    def negamax_ai_turn(self, color, ai_name):
        print(f"{ai_name} is thinking strategically with Negamax...")
        start_time = time.time()  # Start timing
        best_move = None
        best_value = -math.inf

        for move in self.get_all_moves(color):
            captured_piece, was_promoted = self.make_move(move[0], move[1])
            value = -self.negamax(3, -math.inf, math.inf, self.get_opponent_color(color))
            self.undo_move(move[0], move[1], captured_piece, was_promoted)
            if value > best_value:
                best_value = value
                best_move = move

        end_time = time.time()  # End timing
        algorithm_time = round(end_time - start_time, 6)  # Calculate elapsed time
        print(f"{ai_name} Negamax time taken: {algorithm_time} seconds")

        # Write the timing to a text file
        with open("Project/win_results.txt", "a") as file:
            file.write(f"Negamax AI time taken: {algorithm_time} seconds\n")

        if not best_move:
            print(f"No valid moves available for {ai_name}.")
            return False

        self.make_move(best_move[0], best_move[1])
        print(f"{ai_name} moved from {best_move[0]} to {best_move[1]}")

        start_r, start_c = best_move[1]
        while True:
            additional_moves = self.get_piece_moves(start_r, start_c)
            capture_moves = [m for m in additional_moves if abs(m[0] - start_r) == 2]
            if capture_moves:
                next_move = capture_moves[0]
                self.make_move((start_r, start_c), next_move)
                print(f"{ai_name} continued capturing to {next_move}")
                start_r, start_c = next_move
            else:
                break

        return True


    def alpha_beta_ai_turn(self, color, ai_name):
        print(f"{ai_name} is thinking with Alpha-Beta pruning...")
        #You can change the depth of the search here, functions best up to 8 depth, then struggles.
        _, best_move = self.alpha_beta(3, -math.inf, math.inf, True, color)
        if not best_move:
            print(f"No valid moves available for {ai_name}.")
            return False
        self.make_move(best_move[0], best_move[1])
        print(f"{ai_name} moved from {best_move[0]} to {best_move[1]}")
        start_r, start_c = best_move[1]
        while True:
            additional_moves = self.get_piece_moves(start_r, start_c)
            capture_moves = [m for m in additional_moves if abs(m[0] - start_r) == 2]
            if capture_moves:
                next_move = capture_moves[0]
                self.make_move((start_r, start_c), next_move)
                print(f"{ai_name} continued capturing to {next_move}")
                start_r, start_c = next_move
            else:
                break
        return True

    def negascout_ai_turn(self, color, ai_name):
        print(f"{ai_name} is thinking with Negascout...")
        
        # Start timing the Negascout computation
        start_time = time.time()
        score, best_move = self.negascout(3, -math.inf, math.inf, color)
        end_time = time.time()
        
        # Calculate the time taken for Negascout
        algorithm_time = round(end_time - start_time, 6)
        print(f"{ai_name} Negascout time taken: {algorithm_time} seconds")
        
        # Write the recorded time to a new file
        with open("negascout_times.txt", "a") as file:
            file.write(f"Negascout Time: {algorithm_time} seconds\n")

        # Handle the case where no valid moves are available
        if not best_move:
            print(f"No valid moves available for {ai_name}.")
            return False

        # Make the move selected by Negascout
        self.make_move(best_move[0], best_move[1])
        print(f"{ai_name} moved from {best_move[0]} to {best_move[1]}") 

        # Check for additional captures
        start_r, start_c = best_move[1]
        while True:
            additional_moves = self.get_piece_moves(start_r, start_c)
            capture_moves = [m for m in additional_moves if abs(m[0] - start_r) == 2]
            if capture_moves:
                next_move = capture_moves[0]
                self.make_move((start_r, start_c), next_move)
                print(f"{ai_name} continued capturing to {next_move}")
                start_r, start_c = next_move
            else:
                break

        return True



    def ai_turn(self, is_player_ai=False):
        if self.current_turn == "AI":
            ai_name = "AI (Black)"
            color = "b"
            ai_type = self.black_ai_type
        else:
            ai_name = "AI (White)"
            color = "w"
            ai_type = self.white_ai_type if self.ai_vs_ai else self.black_ai_type

        print(f"{ai_name}'s turn!")

        if ai_type == 1:
            return self.random_ai_turn(color, ai_name)
        elif ai_type == 2:
            return self.minimax_ai_turn(color, ai_name)
        elif ai_type == 3:
            return self.alpha_beta_ai_turn(color, ai_name)
        elif ai_type == 4:
            return self.negamax_ai_turn(color, ai_name)
        elif ai_type == 5:
            return self.negascout_ai_turn(color, ai_name)
        elif ai_type == 6:
            return self.mcts_ai_turn(color, ai_name)  
        else:
            print(f"AI {ai_type} is not implemented yet.")
            print("You win by default!")
            return False


    def play_game(self):
        print("Starting the game!")
        game_results = []
        winner = None
        algorithm_time = 0

        ai_algorithm = {
            1: "Random AI",
            2: "Minimax AI",
            3: "Alpha-Beta AI",
            4: "Negamax AI",
            5: "Negascout AI",
            6: "MCTS AI" 

        }
        
        while True:
            self.print_board()
            if self.current_turn == "Player":
                if self.ai_vs_ai:
                    if not self.ai_turn(is_player_ai=True):
                        winner = "AI (Black)"
                        break
                else:
                    if not self.player_turn():
                        winner = "AI (Black)"
                        break
                self.current_turn = "AI"
            else:
                start_time = time.time()
                if not self.ai_turn():
                    winner = "Player (White)"
                    break
                end_time = time.time()
                algorithm_time = round(end_time - start_time, 6)
                self.current_turn = "Player"

        black_ai_name = ai_algorithm[self.black_ai_type]
        white_ai_name = ai_algorithm[self.white_ai_type]
        end_message = f"Winner: {winner}, Black AI: {black_ai_name}, White AI: {white_ai_name}, Time Taken: {algorithm_time} seconds"
        print(f"Game over! {end_message}")
        game_results.append(end_message)
        with open("Project/win_results.txt", "a") as file:
            for result in game_results:
                file.write(result + "\n")



if __name__ == "__main__":
    print("Select AI for Black side:")
    black_ai_type = None
    while black_ai_type is None:
        try:
            black_ai_type = int(input("Enter the AI type for Black (1-6): "))
            if not (1 <= black_ai_type <= 6):
                print("Please choose a valid number between 1 and 6.")
                black_ai_type = None
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 6.")

    print("Select AI for White side:")
    white_ai_type = None
    while white_ai_type is None:
        try:
            white_ai_type = int(input("Enter the AI type for White (1-6): "))
            if not (1 <= white_ai_type <= 6):
                print("Please choose a valid number between 1 and 6.")
                white_ai_type = None
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 6.")

    print("Select game mode:")
    print("1. Player vs AI")
    print("2. AI vs AI")
    ai_vs_ai = None
    while ai_vs_ai is None:
        choice = '2'
        # choice = input("Enter the number of the game mode you want to play (1 or 2): ")
        if choice == '1':
            ai_vs_ai = False
        elif choice == '2':
            ai_vs_ai = True
        else:
            print("Invalid selection. Please choose 1 or 2.")

    # Run the game 10 times with the chosen AI settings
    for i in range(30):
        print(f"\n--- Running game {i+1} with Black AI type {black_ai_type} and White AI type {white_ai_type} ---")
        game = CheckersGame(black_ai_type=black_ai_type, white_ai_type=white_ai_type, ai_vs_ai=ai_vs_ai)
        game.play_game()

    print("\nAll 10 games have been completed!")

