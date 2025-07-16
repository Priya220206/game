# streamlit_tictactoe_ml.py
import streamlit as st
import random
import numpy as np

# --- Minimax implementation ---
def check_winner(board, p):
    wins = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    return any(all(board[i]==p for i in trip) for trip in wins)

def is_full(board):
    return all(c is not None for c in board)

def minimax(board, player):
    if check_winner(board, 'X'): return +1
    if check_winner(board, 'O'): return -1
    if is_full(board): return 0

    if player == 'X':
        best = -2
        for i in range(9):
            if board[i] is None:
                board[i] = 'X'
                score = minimax(board, 'O')
                board[i] = None
                best = max(best, score)
        return best
    else:
        best = +2
        for i in range(9):
            if board[i] is None:
                board[i] = 'O'
                score = minimax(board, 'X')
                board[i] = None
                best = min(best, score)
        return best

def ai_move(board):
    best, idx = -2, None
    for i in range(9):
        if board[i] is None:
            board[i] = 'X'
            score = minimax(board, 'O')
            board[i] = None
            if score > best:
                best, idx = score, i
    return idx

# --- Q-Learning agent ---
class QAgent:
    def __init__(self, alpha=0.1, gamma=0.9, eps=0.2):
        self.Q = {}  # state_str -> 9-length array
        self.alpha, self.gamma, self.eps = alpha, gamma, eps

    def get_Q(self, state):
        s = ''.join(c or '_' for c in state)
        if s not in self.Q:
            self.Q[s] = [0]*9
        return self.Q[s]

    def select(self, state):
        Q = self.get_Q(state)
        if random.random() < self.eps:
            return random.choice([i for i,c in enumerate(state) if c is None])
        else:
            moves = [i for i,c in enumerate(state) if c is None]
            q_moves = [(Q[i], i) for i in moves]
            _, choice = max(q_moves)
            return choice

    def update(self, s, a, r, s2):
        Q = self.get_Q(s)
        Q2 = self.get_Q(s2)
        Q[a] += self.alpha * (r + self.gamma * max(Q2) - Q[a])

# --- Streamlit UI & game loop ---
st.title("🔲 Tic-Tac-Toe: Minimax AI + Q-Learning")

if 'board' not in st.session_state:
    st.session_state.board = [None]*9
    st.session_state.turn = 'human'
    st.session_state.agent = QAgent()
    st.session_state.history = []

def reset():
    st.session_state.board = [None]*9
    st.session_state.turn = 'human'
    st.session_state.history = []

st.button("🔁 Reset Game", on_click=reset)

board = st.session_state.board

# Display grid of buttons
for i in range(3):
    cols = st.columns(3)
    for j in range(3):
        idx = i*3 + j
        label = board[idx] or " "
        if cols[j].button(label, key=f"b{idx}") and board[idx] is None and st.session_state.turn=='human':
            board[idx] = 'O'
            st.session_state.history.append(('human', board.copy()))
            st.session_state.turn = 'ai'

# AI move logic
if st.session_state.turn == 'ai' and not (check_winner(board, 'O') or check_winner(board, 'X') or is_full(board)):
    # Can switch between minimax and Q-agent
    if random.random() < 0.5:
        mv = ai_move(board)  # perfect play
    else:
        mv = st.session_state.agent.select(board)
    board[mv] = 'X'
    st.session_state.history.append(('ai', board.copy()))
    st.session_state.turn = 'human'

# Check for end-game
if check_winner(board, 'O'):
    st.success("You win!")
elif check_winner(board, 'X'):
    st.error("AI wins!")
elif is_full(board):
    st.info("Draw!")

# Q-learning update after game end
if (check_winner(board,'O') or check_winner(board,'X') or is_full(board)) and st.session_state.history:
    reward = 0
    if check_winner(board,'O'): reward = +1
    elif check_winner(board,'X'): reward = -1
    # propagate through history
    hist = st.session_state.history
    for i in range(len(hist)-1):
        turn, state = hist[i]
        _, next_state = hist[i+1]
        act = [j for j,(a,b) in enumerate(zip(state, next_state)) if b!=a][0]
        s_str = ''.join(c or '_' for c in state)
        st.session_state.agent.update(state, act, reward, next_state)
    # erase history to prevent double updates
    st.session_state.history = []

