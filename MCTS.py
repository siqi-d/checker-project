import math
import time

class CheckersGame:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_turn = "AI"
        self.ai_type = "MCTS"  # AI vs AI only, so we assume MCTS AI
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

    def get_opponent_color(self, color):
        return 'b' if color == 'w' else 'w'

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

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if piece.lower() in ["b", "w"] else []
        if piece == "w":
            directions = [(-1, -1), (-1, 1)]
        elif piece == "b":
            directions = [(1, -1), (1, 1)]

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
    
    
    def evaluate_move(self, move):
        # The start and end positions of the move
        start, end = move
        sr, sc = start  # Start row and column
        er, ec = end    # End row and column
        piece = self.board[sr][sc]  # Gets the piece being moved

        score = 0 

        # Checks if the move is a capture move
        if abs(er - sr) == 2: 
            score += 1.5

        # Checks if the move results in a promotion for white
        elif piece.lower() == "w" and er == 0:
            score += 1.5

        # Checks if the move results in a promotion for black
        elif piece.lower() == "b" and er == 7: 
            score += 1.5

        # Add a mobility score based on the number of possible moves after this move
        mobility_score = len(self.get_piece_moves(er, ec))  # Count possible moves for the piece after moving
        score += mobility_score * 0.1  # Add mobility score with a weight of 0.1

        return score  # Return score for this move

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


    def ai_turn(self, color):
        print(f"{color} AI is thinking...")

        # Use Monte Carlo Tree Search (MCTS) to determine the best move for the AI
        best_move = self.mcts(color)

        # If a valid move is found
        if best_move:
            # Unpack the start and end positions of the best move and make move 
            start, end = best_move
            self.make_move(start, end)

            print(f"{color} AI moved from {start} to {end}")

            # Print the updated state of the board
            self.print_board()


    def play_game(self):
        print("Starting the game!")
        game_results = []
        winner = None

        while True:
            # Alternate between Black AI (b) and White AI (w)
            for player, name in [("b", "Black AI"), ("w", "White AI")]:
                turn_start_time = time.time()  
                print(f"{name}'s turn...")
                self.ai_turn(player)
                turn_end_time = time.time() 
                turn_time = round(turn_end_time - turn_start_time, 6)
            
                
                if self.is_game_over():
                    winner = name
                    break  # Exit the loop when the game ends

            if winner:
                print(f"Game over! {winner} wins!")
                break


        # Logs the result
        result_message = f"Winner: {winner}, Algorithm: MCTS, Time Taken: {turn_time} seconds"
        print(result_message)
        game_results.append(result_message)
        
        with open("Project/game_results.txt", "a") as file:
            for result in game_results:
                file.write(result + "\n")

        print("Game results saved to 'Project/game_results.txt'.")


    def is_game_over(self):
        if not self.get_all_moves("b") or not self.get_all_moves("w"):
            return True
        return False

if __name__ == "__main__":
    game = CheckersGame()
    game.play_game() # Starts MCTS AI vs AI game
