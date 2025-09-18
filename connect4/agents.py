import random
import time


class Agent:
    ident = 2

    def __init__(self):
        self.id = Agent.ident
        Agent.ident += 1

    def get_chosen_column(self, state, max_depth):
        pass



class MiniMaxAgent(Agent):
    def __init__(self):
        # self.difficulty = difficulty
        super().__init__()

    def get_chosen_column(self, state, max_depth, difficulty, opponent):
        best_move = self.minimax(state, max_depth, difficulty, opponent, True, -float('inf'), float('inf'))
        return best_move['column'] if best_move['column'] is not None else random.choice(self.get_valid_moves(state))

    def minimax(self, state, depth, difficulty, opponent, maximizing_player, alpha, beta):
        valid_moves = self.get_valid_moves(state)
        
        # Base case: return the evaluation score if at max depth or no valid moves
        is_terminal = self.check_for_winner(state, self.id) or self.check_for_winner(state, opponent) or not valid_moves
        if depth == 0 or is_terminal:
            if self.check_for_winner(state, self.id):
                return {'column': None, 'score': float('inf')}  # AI wins
            elif self.check_for_winner(state, opponent):
                return {'column': None, 'score': -float('inf')}  # Opponent wins
            elif not valid_moves:
                return {'column': None, 'score': 0}  # Draw
            return {'column': None, 'score': self.evaluate_board(state, difficulty)}

        if maximizing_player:
            best_move = {'column': None, 'score': -float('inf')}
            for move in valid_moves:
                new_state = self.simulate_move(state, move, self.id)
                result = self.minimax(new_state, depth - 1, difficulty, opponent, False, alpha, beta)

                if result['score'] > best_move['score']:
                    best_move = {'column': move, 'score': result['score']}
                alpha = max(alpha, best_move['score'])
                if beta <= alpha:
                    break  # Alpha-beta pruning
        else:
            best_move = {'column': None, 'score': float('inf')}
            for move in valid_moves:
                new_state = self.simulate_move(state, move, opponent)
                result = self.minimax(new_state, depth - 1, difficulty, opponent, True, alpha, beta)

                if result['score'] < best_move['score']:
                    best_move = {'column': move, 'score': result['score']}
                beta = min(beta, best_move['score'])
                if beta <= alpha:
                    break  # Alpha-beta pruning

        # Ensure a valid column is always returned, even as a fallback
        if best_move['column'] is None and valid_moves:
            best_move['column'] = random.choice(valid_moves)

        return best_move

    def simulate_move(self, state, column, player_id):
        new_state = [row[:] for row in state]  # Create a copy of the board
        for row in reversed(range(len(state))):  # Drop piece from the bottom
            if new_state[row][column] == 0:  # Find the first empty row in the column
                new_state[row][column] = player_id
                break
        return new_state

    def get_valid_moves(self, state):
        return [col for col in range(len(state[0])) if state[0][col] == 0]  # If the top row is empty

    def check_for_winner(self, state, player_id):
        # Horizontal check
        for row in range(6):
            for col in range(4):
                if all(state[row][col + i] == player_id for i in range(4)):
                    return True
        # Vertical check
        for col in range(7):
            for row in range(3):
                if all(state[row + i][col] == player_id for i in range(4)):
                    return True
        # Diagonal checks
        for row in range(3):
            for col in range(4):
                if all(state[row + i][col + i] == player_id for i in range(4)):
                    return True
            for col in range(3, 7):
                if all(state[row + i][col - i] == player_id for i in range(4)):
                    return True
        return False

    def evaluate_board(self, state, difficulty):
        score = 0
        score += self.evaluate_center(state)
        score += self.evaluate_rows(state, difficulty)
        score += self.evaluate_columns(state, difficulty)
        score += self.evaluate_diagonals(state, difficulty)
        return score

    def evaluate_center(self, state):
        # Prioritize placing pieces in the center column
        center_column = [state[row][3] for row in range(6)]
        center_count = center_column.count(self.id)
        return center_count * 3  # Assign a high score for center column occupancy

    def evaluate_rows(self, state, difficulty):
        score = 0
        for row in state:
            for col in range(len(row) - 3):
                window = row[col:col + 4]
                score += difficulty.evaluate_window(window, self.id)
        return score

    def evaluate_columns(self, state, difficulty):
        score = 0
        for col in range(len(state[0])):
            for row in range(len(state) - 3):
                window = [state[row + i][col] for i in range(4)]
                score += difficulty.evaluate_window(window, self.id)
        return score

    def evaluate_diagonals(self, state, difficulty):
        score = 0
        for row in range(len(state) - 3):
            for col in range(len(state[0]) - 3):
                window = [state[row + i][col + i] for i in range(4)]
                score += difficulty.evaluate_window(window, self.id)
            for col in range(3, len(state[0])):
                window = [state[row + i][col - i] for i in range(4)]
                score += difficulty.evaluate_window(window, self.id)
        return score



class NegascoutAgent(Agent):
    def __init__(self):
        super().__init__()

    def get_chosen_column(self, state, max_depth, difficulty, opponent):
        best_move = self.negascout(state, max_depth, -float('inf'), float('inf'), 1, difficulty, opponent)
        return best_move['column'] if best_move['column'] is not None else random.choice(self.get_valid_moves(state))

    def negascout(self, state, depth, alpha, beta, color, difficulty, opponent):
        valid_moves = self.get_valid_moves(state)
        
        # Base case: return the evaluation score if at max depth or no valid moves
        is_terminal = self.check_for_winner(state, self.id) or self.check_for_winner(state, opponent) or not valid_moves
        if depth == 0 or is_terminal:
            if self.check_for_winner(state, self.id):
                return {'column': None, 'score': color * float('inf')}  # AI wins
            elif self.check_for_winner(state, opponent):
                return {'column': None, 'score': color * -float('inf')}  # Opponent wins
            elif not valid_moves:
                return {'column': None, 'score': 0}  # Draw
            return {'column': None, 'score': color * self.evaluate_board(state, difficulty)}

        best_move = {'column': None, 'score': -float('inf')}
        for i, move in enumerate(valid_moves):
            new_state = self.simulate_move(state, move, self.id if color == 1 else opponent)
            if i == 0:
                score = -self.negascout(new_state, depth - 1, -beta, -alpha, -color, difficulty, opponent)['score']
            else:
                score = -self.negascout(new_state, depth - 1, -alpha - 1, -alpha, -color, difficulty, opponent)['score']
                if alpha < score < beta:
                    score = -self.negascout(new_state, depth - 1, -beta, -score, -color, difficulty, opponent)['score']

            if score > best_move['score']:
                best_move = {'column': move, 'score': score}

            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Beta cutoff

        # Ensure a valid column is always returned, even as a fallback
        if best_move['column'] is None and valid_moves:
            best_move['column'] = random.choice(valid_moves)

        return best_move

    def simulate_move(self, state, column, player_id):
        new_state = [row[:] for row in state]  # Create a copy of the board
        for row in reversed(range(len(state))):  # Drop piece from the bottom
            if new_state[row][column] == 0:  # Find the first empty row in the column
                new_state[row][column] = player_id
                break
        return new_state

    def get_valid_moves(self, state):
        return [col for col in range(len(state[0])) if state[0][col] == 0]  # If the top row is empty

    def check_for_winner(self, state, player_id):
        # Horizontal check
        for row in range(6):
            for col in range(4):
                if all(state[row][col + i] == player_id for i in range(4)):
                    return True
        # Vertical check
        for col in range(7):
            for row in range(3):
                if all(state[row + i][col] == player_id for i in range(4)):
                    return True
        # Diagonal checks
        for row in range(3):
            for col in range(4):
                if all(state[row + i][col + i] == player_id for i in range(4)):
                    return True
            for col in range(3, 7):
                if all(state[row + i][col - i] == player_id for i in range(4)):
                    return True
        return False

    def evaluate_board(self, state, difficulty):
        score = 0
        score += self.evaluate_center(state)
        score += self.evaluate_rows(state, difficulty)
        score += self.evaluate_columns(state, difficulty)
        score += self.evaluate_diagonals(state, difficulty)
        return score

    def evaluate_center(self, state):
        # Prioritize placing pieces in the center column
        center_column = [state[row][3] for row in range(6)]
        center_count = center_column.count(self.id)
        return center_count * 3  # Assign a high score for center column occupancy

    def evaluate_rows(self, state, difficulty):
        score = 0
        for row in state:
            for col in range(len(row) - 3):
                window = row[col:col + 4]
                score += difficulty.evaluate_window(window, self.id)
        return score

    def evaluate_columns(self, state, difficulty):
        score = 0
        for col in range(len(state[0])):
            for row in range(len(state) - 3):
                window = [state[row + i][col] for i in range(4)]
                score += difficulty.evaluate_window(window, self.id)
        return score

    def evaluate_diagonals(self, state, difficulty):
        score = 0
        for row in range(len(state) - 3):
            for col in range(len(state[0]) - 3):
                window = [state[row + i][col + i] for i in range(4)]
                score += difficulty.evaluate_window(window, self.id)
            for col in range(3, len(state[0])):
                window = [state[row + i][col - i] for i in range(4)]
                score += difficulty.evaluate_window(window, self.id)
        return score