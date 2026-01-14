import random
import math 
import time


class CheckersGame:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_turn = "Player"
        self.ai_type = self.select_ai()
        self.select_game_mode()
        self.previous_moves = {"AI": None, "Player": None}

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
                self.ai_vs_ai = False
                break
            elif choice == '2':
                self.ai_vs_ai = True
                break
            else:
                print("Invalid selection. Please choose 1 or 2.")

    def get_opponent_color(self, color):
        return 'b' if color == 'w' else 'w'

    def select_ai(self):
        print("Select an AI opponent:")
        print("1. Random AI: Makes random valid moves.")
        print("2. Negamax AI: Evaluates moves to maximize its advantage.")

        print("3. Negamax Alpha-Beta AI: Optimized decision-making using pruning.")
        while True:
            try:
                choice = int(input("Enter the number of the AI you want to play against (1-3): "))
                if 1 <= choice <= 3:
                    print(f"You selected AI {choice}.")
                    return choice
                else:
                    print("Invalid selection. Please choose a number between 1 and 3.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 3.")

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
    
    def negamax(self, depth, color):
        if depth == 0:
            return self.evaluate_board()

        best_value = -math.inf
        for move in self.get_all_moves(color):
            captured_piece, was_promoted = self.make_move(move[0], move[1])
            value = -self.negamax(depth - 1, self.get_opponent_color(color))
            self.undo_move(move[0], move[1], captured_piece, was_promoted)

            best_value = max(best_value, value)

        return best_value

    def negamax_alpha_beta(self, depth, alpha, beta, color):
        if depth == 0:
            return self.evaluate_board()

        best_value = -math.inf
        for move in self.get_all_moves(color):
            captured_piece, was_promoted = self.make_move(move[0], move[1])
            value = -self.negamax(depth - 1, -beta, -alpha, self.get_opponent_color(color))
            self.undo_move(move[0], move[1], captured_piece, was_promoted)

            best_value = max(best_value, value)
            alpha = max(alpha, best_value)

            if beta <= alpha:
                break  

        return best_value

    def player_turn(self):
        print("Player's turn!")
        while True:
            try:
                start_input = input("Enter piece to move (row col) or type 'quit' to end the game: ").strip()
                if start_input.lower() == "quit":
                    print("You ended the game. Thanks for playing!")
                    return False
                start_r, start_c = map(int, start_input.split())
                if self.board[start_r][start_c] != "w":
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
    
    def negamax_ab_ai_turn(self, color, ai_name):
        print(f"{ai_name} is thinking strategically...")
        best_move = None
        best_value = -math.inf
        for move in self.get_all_moves(color):
            captured_piece, was_promoted = self.make_move(move[0], move[1])
            value = -self.negamax(3, -math.inf, math.inf, self.get_opponent_color(color))
            self.undo_move(move[0], move[1], captured_piece, was_promoted)
            if value > best_value:
                best_value = value
                best_move = move
        
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
        print(f"{ai_name} is thinking strategically...")
        best_move = None
        best_value = -math.inf
        for move in self.get_all_moves(color):
            captured_piece, was_promoted = self.make_move(move[0], move[1])
            value = -self.negamax(3, self.get_opponent_color(color))
            self.undo_move(move[0], move[1], captured_piece, was_promoted)
            if value > best_value:
                best_value = value
                best_move = move
        
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

    def ai_turn(self, is_player_ai=False):
        ai_name = "AI (Black)" if self.current_turn == "AI" else "AI (White)"
        print(f"{ai_name}'s turn!")
        color = "b" if self.current_turn == "AI" else "w"
        ai_type = self.ai_type if self.current_turn == "AI" else (2 if self.ai_vs_ai else 1)
        if ai_type == 1:
            return self.random_ai_turn(color, ai_name)
        elif ai_type == 2:
            return self.negamax_ai_turn(color, ai_name)
        else:
            print(f"AI {ai_type} is not implemented yet.")
            print("You win by default!")
            return False

    def play_game(self):
        print("Starting the game!")
        game_results = []
        winner = None
        while True:
            self.print_board()
            # if self.ai_vs_ai:
            #     input("Press Enter to proceed to the next move...")
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


        ai_algorithm = {1: "Random AI", 2: "Negamax AI", 3: " Negamax Alpha-Beta AI"}[self.ai_type]

        end_message = f"Winner: {winner}, Algorithm: {ai_algorithm}, Time Taken: {algorithm_time} seconds"
        print(f"Game over! {end_message}")
        game_results.append(end_message)
        with open("Project/game_results.txt", "a") as file:
            for result in game_results:
                file.write(result + "\n")




if __name__ == "__main__":
    game = CheckersGame()
    game.play_game()
