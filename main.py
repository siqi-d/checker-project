import random
import math
import time

class CheckersGame:
    def __init__(self, ai_type=None, ai_vs_ai=None):
        # If ai_type and ai_vs_ai are not given, ask the user
        if ai_type is None:
            ai_type = self.select_ai()
        self.ai_type = ai_type

        if ai_vs_ai is None:
            ai_vs_ai = self.select_game_mode()
        self.ai_vs_ai = ai_vs_ai

        # White always starts
        self.board = self.initialize_board()
        self.current_turn = "Player"
        self.previous_moves = {"AI": None, "Player": None}

    def initialize_board(self):
        # Creates an 8x8 board
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
        # This is ignored now, as all games are AI vs AI
        # Originally this function was used to choose the game mode between AI or Player turns for white
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

    def select_ai(self):
        # Allows player to select which AI to play against
        print("Select an AI opponent:")
        print("1. Random AI")
        print("2. Minimax AI")
        print("3. Alpha-Beta AI")
        print("4. Negamax AI")
        print("5. Negascout AI")
        while True:
            try:
                choice = int(input("Enter the number of the AI you want to play against (1-5): "))
                if 1 <= choice <= 5:
                    print(f"You selected AI {choice}.")
                    return choice
                else:
                    print("Invalid selection. Please choose a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 5.")

    def print_board(self):
        print("  " + " ".join(map(str, range(8))))
        for i, row in enumerate(self.board):
            print(f"{i} " + " ".join(row))
        print()

    def get_piece_moves(self, r, c):
        # Gets all valid moves for a piece given the row and column
        moves = []
        piece = self.board[r][c]
        if piece == " ":
            return moves

        # Determines the moves a piece can make based on it being kinged or not and by color
        if piece == "W" or piece == "B":
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece == "w":
            directions = [(-1, -1), (-1, 1)]
        elif piece == "b":
            directions = [(1, -1), (1, 1)]
        else:
            return moves

        opponent_color = self.get_opponent_color(piece.lower())

        # Check for moves
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == " ":
                moves.append((nr, nc))
        # Check for jumps
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
        # Handles the moves
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
        # Handles promotion
        if piece == "w" and er == 0:
            self.board[er][ec] = "W"
            promoted = True
        elif piece == "b" and er == 7:
            self.board[er][ec] = "B"
            promoted = True
        self.previous_moves[self.current_turn] = (start, end)
        return captured_piece, promoted

    def undo_move(self, start, end, captured_piece=None, was_promoted=False):
        # Reverts the moves when needed
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
        # Heuristic evaluation of the board, increases values for kinged pieces 
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
        # Minimax algorithm, using above heuristic
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
        # Uses zero sum to calculate the minimax algorithm
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
        # Uses the alpha beta function discussed in class
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

    def negascout(self, depth, alpha, beta, color):
        # Uses negascout algorithm, which is a variation of PVS
        # Used the premise introduced in chess programming wiki, and adjusted it to checkers
        # https://www.chessprogramming.org/Principal_Variation_Search
        color_factor = 1 if color == 'b' else -1  
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
            # Dominates alpha beta, so it should always perform the same or better
            if value > alpha:
                alpha = value
                best_move = move

            if alpha >= beta:
                break

            is_first_child = False

        return alpha, best_move





    def player_turn(self):
        # Runs most the game logic for a player turn/game
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
        # Handles random ai 
        valid_moves = self.get_all_moves(color)
        if not valid_moves:
            print(f"No valid moves available for {ai_name}.")
            return False
        move = random.choice(valid_moves)
        self.make_move(move[0], move[1])
        print(f"{ai_name} moved from {move[0]} to {move[1]}")
        return True

    def minimax_ai_turn(self, color, ai_name):
        # Handles minimax and provides some feedback to user so they know what AI is doing
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
        # Handles negamax and provides some feedback to user so they know what AI is doing
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
        with open("Project/game_results.txt", "a") as file:
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
        # We can change the depth of the search here, functions best up to 8 depth, then struggles afterwards
        # For testing we used depth of 3 for easier comparison and handling
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
        # Handles negascout, which must use a different timing method because of the window search 
        print(f"{ai_name} is thinking with Negascout...")
        
        # Start timing the Negascout computation
        start_time = time.time()
        score, best_move = self.negascout(3, -math.inf, math.inf, color)
        end_time = time.time()
        
        # Calculate the time taken for Negascout
        algorithm_time = round(end_time - start_time, 6)
        print(f"{ai_name} Negascout time taken: {algorithm_time} seconds")
        
        # Write the recorded time to a new file, which was used to determine average 
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
        # Handles the generic AI turn and passes to the individual function
        ai_name = "AI (Black)" if self.current_turn == "AI" else "AI (White)"
        print(f"{ai_name}'s turn!")
        color = "b" if self.current_turn == "AI" else "w"
        ai_type = self.ai_type if self.current_turn == "AI" else (2 if self.ai_vs_ai else 1)
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
        else:
            print(f"AI {ai_type} is not implemented yet.")
            print("You win by default!")
            return False

    def play_game(self):
        # Starts the game and handles the game loop until a winner is determined or the game ends
        print("Starting the game!")
        game_results = []
        winner = None
        algorithm_time = 0
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

        ai_algorithm = {1: "Random AI", 2: "Minimax AI", 3: "Alpha-Beta AI",4: "Negamax AI",5: "Negascout AI"}[self.ai_type]
        end_message = f"Winner: {winner}, Algorithm: {ai_algorithm}, Time Taken: {algorithm_time} seconds"
        print(f"Game over! {end_message}")
        game_results.append(end_message)
        with open("Project/game_results.txt", "a") as file:
            for result in game_results:
                file.write(result + "\n")


if __name__ == "__main__":
    # Let the user choose AI and game mode once
    print("Select an AI opponent:")
    print("1. Random AI")
    print("2. Minimax AI")
    print("3. Alpha-Beta AI")
    print("4. Negamax AI")
    print("5. Negascout AI")
    while True:
        try:
            chosen_ai = int(input("Enter the number of the AI you want to play against (1-5): "))
            if 1 <= chosen_ai <= 5:
                break
            else:
                print("Invalid selection. Please choose a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")


    while True:
        choice = '2'
        #choice = input("Enter the number of the game mode you want to play (1 or 2): ")
        if choice == '1':
            chosen_game_mode = False
            break
        elif choice == '2':
            chosen_game_mode = True
            break
        else:
            print("Invalid selection. Please choose 1 or 2.")

    # Run the chosen AI n times
    for i in range(1):
        print(f"\n--- Running game {i+1} with AI type {chosen_ai} ---")
        game = CheckersGame(ai_type=chosen_ai, ai_vs_ai=chosen_game_mode)
        game.play_game()
