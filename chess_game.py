import chess
import sys

class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.player_is_white = True  # Default value, will be set properly later
        
    def get_computer_move(self):
        # Get all legal moves
        legal_moves = list(self.board.legal_moves)
        # Convert moves to algebraic notation and sort
        move_list = sorted([self.board.san(move) for move in legal_moves], key=str.lower)
        
        # Print all moves
        print("Possible moves:")
        # faster to use array slices but whatever
        for i, move in enumerate(move_list):
            # Determine if this is the middle move
            if i == len(move_list) // 2:
                print("[%s] " % move, end='')
            else:
                print("%s " % move, end='')
        print() # end the line

        # Select middle move (rounding down)
        middle_index = len(move_list) // 2
        chosen_san = move_list[middle_index]
        
        # Convert back to a move object
        for move in legal_moves:
            if self.board.san(move) == chosen_san:
                return move
                
    def find_shortest_checkmate(self):
        print("Choose your color (white/black):")
        while True:
            color = input().lower().strip()
            if color in ['white', 'black']:
                break
            print("Please enter 'white' or 'black':")
        
        self.player_is_white = color == 'white'

        from collections import deque
        from copy import deepcopy

        # Queue will store (board_state, move_history) tuples
        queue = deque([(deepcopy(self.board), [])])
        seen_positions = set()  # Track seen positions to avoid cycles
        checkmate_histories = []  # Store all checkmate sequences
        checkmate_depth = float('inf')
        current_depth = 0

        while queue:
            current_board, move_history = queue.popleft()
            
            # If we're starting a new depth and we've found checkmates, we're done
            if len(move_history) > current_depth and checkmate_histories:
                break
            current_depth = len(move_history)
            
            # Skip if we're already deeper than a found checkmate
            if len(move_history) > checkmate_depth:
                continue

            # Get current position FEN (excluding move counters)
            fen_parts = current_board.fen().split(' ')
            position_key = ' '.join(fen_parts[:4])
            if position_key in seen_positions:
                continue
            seen_positions.add(position_key)

            # Get all legal moves for current position
            legal_moves = list(current_board.legal_moves)
            move_list = sorted([current_board.san(move) for move in legal_moves], key=str.lower)
            
            # If it's computer's turn, only make the middle move
            if (len(move_history) % 2) == (1 if self.player_is_white else 0):
                middle_index = len(move_list) // 2
                move_list = [move_list[middle_index]]

            # Try each move
            for san_move in move_list:
                # Find the actual move object
                for move in legal_moves:
                    if current_board.san(move) == san_move:
                        # Create new board state
                        new_board = deepcopy(current_board)
                        new_board.push(move)
                        new_history = move_history + [(san_move, new_board.is_checkmate())]

                        # If this move results in checkmate
                        if new_board.is_checkmate():
                            checkmate_histories.append(new_history)
                            checkmate_depth = len(new_history)
                        # If no checkmate yet or at same depth as other checkmates, continue searching
                        elif len(new_history) < checkmate_depth:
                            queue.append((new_board, new_history))
                        break

        # Print results
        if checkmate_histories:
            print(f"\nFound {len(checkmate_histories)} checkmate sequence(s) in {checkmate_depth} moves!")
            for i, history in enumerate(checkmate_histories, 1):
                print(f"\nCheckmate sequence #{i}:")
                move_output = []
                for j, (move, is_mate) in enumerate(history):
                    move_number = (j // 2) + 1
                    if j % 2 == 0:
                        move_output.append(f"{move_number}. {move}")
                    else:
                        move_output[-1] += f" {move}"
                print(" ".join(move_output))
        else:
            print("\nNo checkmate found in searched positions!")

    def choose_game_mode(self):
        while True:
            print("Choose game mode:")
            print("1. Play interactively")
            print("2. Find shortest path to checkmate")
            try:
                mode = int(input("Enter 1 or 2: ").strip())
                if mode == 1:
                    return self.play_interactive_game()
                elif mode == 2:
                    return self.find_shortest_checkmate()
                else:
                    print("Invalid choice. Please enter 1 or 2.")
            except ValueError:
                print("Please enter a valid number.")

    def play_interactive_game(self):
        print("Welcome to Chess!")
        print("Choose your color (white/black):")
        
        while True:
            color = input().lower().strip()
            if color in ['white', 'black']:
                break
            print("Please enter 'white' or 'black':")
        
        self.player_is_white = color == 'white'
        
        # If player is black, computer (white) moves first
        if not self.player_is_white:
            computer_move = self.get_computer_move()
            print(f"Computer's move: {self.board.san(computer_move)}")
            self.board.push(computer_move)
            print(self.board)
            
        while not self.board.is_game_over():
            if self.player_is_white == self.board.turn:
                print("\nEnter your move (in algebraic notation, e.g., 'e4', 'Nf3'):")
                while True:
                    try:
                        move_san = input().strip()
                        # Try to parse the move
                        move = self.board.parse_san(move_san)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                            break
                        else:
                            print("Illegal move. Try again:")
                    except ValueError:
                        print("Invalid move format. Try again:")
            else:
                computer_move = self.get_computer_move()
                print(f"\nComputer's move: {self.board.san(computer_move)}")
                self.board.push(computer_move)
            
            print(self.board)
            
        # Game over
        result = self.board.outcome()
        if result.winner is None:
            print("Game Over - Draw!")
        else:
            winner = "White" if result.winner else "Black"
            print(f"Game Over - {winner} wins!")

    def play_game(self):
        self.choose_game_mode()

if __name__ == "__main__":
    game = ChessGame()
    game.play_game()
