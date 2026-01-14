# Checkers AI Engine Python

A Python-based Checkers 8×8 game engine featuring multiple adversarial search agents and an automated AI-vs-AI benchmarking pipeline.

This project implements classic decision-making algorithms for turn-based zero-sum games and provides utilities to compare performance across different strategies.


# Features

- Full Checkers game engine 8×8 board, move generation, captures, and king promotion
- Multiple AI agents:
    - Random baseline
    - Minimax
    - Alpha-Beta Pruning
    - Negamax
    - Negascout
    - MCTS
- AI vs AI benchmarking:
    - Tracks winner and runtime per match
    - Logs results for analysis


# Project Structure

- main.py
  Runs an AI-vs-AI match using selectable adversarial search algorithms (excluding MCTS).

- MCTS.py 
  Runs an AI-vs-AI match using Monte Carlo Tree Search MCTS.

- test.py  
  Runs tournaments between different AI agents and records outcomes.

- results/
  Stores experiment logs such as runtime and win results.



# How to Run

1 Run a single AI-vs-AI match Search Agents
```bash
python main.py
