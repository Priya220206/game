# streamlit_mastermind_no_itertools.py
import streamlit as st
import random

CODE_LENGTH = 4
COLORS = ["R","G","B","Y","O","P"]

def generate_code():
    return random.sample(COLORS, CODE_LENGTH)

def get_feedback(secret, guess):
    correct = sum(s == g for s, g in zip(secret, guess))
    # Count total common colors
    common = sum(min(secret.count(c), guess.count(c)) for c in COLORS)
    return {"correct": correct, "close": common - correct}

def all_combinations(colors, length):
    # Generate all combinations without itertools (recursive)
    if length == 0:
        return [""]
    smaller = all_combinations(colors, length - 1)
    return [s + c for s in smaller for c in colors]

def filter_pool(pool, last_guess, fb):
    return [
        cand for cand in pool
        if get_feedback(list(last_guess), list(cand)) == fb
    ]

# --- Streamlit app ---
st.title("🎯 Mastermind")

# Initialize game state
if 'secret' not in st.session_state:
    st.session_state.secret = generate_code()
    st.session_state.pool = all_combinations(COLORS, CODE_LENGTH)
    st.session_state.guesses = []

# User input
guess = st.text_input(f"Enter a guess ({CODE_LENGTH} letters, {COLORS}):", max_chars=CODE_LENGTH).upper()

if st.button("Submit"):
    if len(guess) != CODE_LENGTH or any(c not in COLORS for c in guess):
        st.error("Invalid! Use exactly 4 letters from: " + ", ".join(COLORS))
    else:
        fb = get_feedback(st.session_state.secret, list(guess))
        st.session_state.guesses.append((guess, fb))
        st.session_state.pool = filter_pool(st.session_state.pool, guess, fb)

# Display guess history
if st.session_state.guesses:
    st.markdown("**Your guesses so far:**")
    for i, (g, fb) in enumerate(st.session_state.guesses, 1):
        st.write(f"{i}. {g} → ✅ {fb['correct']} | 🔁 {fb['close']}")

# Solver hint
if st.session_state.pool:
    st.info(f"Solver suggests: **{st.session_state.pool[0]}** (remaining possibilities: {len(st.session_state.pool)})")
else:
    st.warning("No possibilities left—unlucky!")

# Win condition
if st.session_state.guesses and st.session_state.guesses[-1][1]["correct"] == CODE_LENGTH:
    st.balloons()
    st.success(f"🎉 You cracked it! Secret was `{''.join(st.session_state.secret)}`")
    if st.button("Play again"):
        for key in ['secret', 'pool', 'guesses']:
            del st.session_state[key]
        st.experimental_rerun()

