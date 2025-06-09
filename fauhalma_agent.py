# FAUhalma AI Agent Project

import json
from typing import List, Dict, Tuple, Set
import math
import random

# ------------------------- CONSTANTS -------------------------
PLAYER_A = 'A'
PLAYER_B = 'B'
PLAYER_C = 'C'
ALL_PLAYERS = [PLAYER_A, PLAYER_B, PLAYER_C]

# Hex direction vectors
HEX_DIRECTIONS = [
    [1, -1], [1, 0], [0, 1],
    [-1, 1], [-1, 0], [0, -1]
]

# Center tile (not allowed)
CENTER = [0, 0]

# Define player home zones (must be filled based on real board)
HOME_ZONES = {
    'A': [ [-3,3], [-3,2], [-3,1], [-3,0], [-2,3], [-2,2], [-2,1], [-1,3], [-1,2], [0,3] ],
    'B': [ [3,-3], [3,-2], [3,-1], [3,0], [2,-3], [2,-2], [2,-1], [1,-3], [1,-2], [0,-3] ],
    'C': [ [0,0] ]  # Not accurate; for simplification. Replace with true C zone.
}

# ------------------------- HELPER FUNCTIONS -------------------------

def add_coords(a, b):
    return [a[0]+b[0], a[1]+b[1]]

def distance(pos1, pos2):
    return (abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) + abs(pos1[0] + pos1[1] - pos2[0] - pos2[1])) // 2

# ------------------------- GAME LOGIC -------------------------

def generate_simple_moves(position: Dict[str, List[List[int]]], player: str, peg: List[int]) -> List[List[List[int]]]:
    moves = []
    all_occupied = {tuple(p) for pl in ALL_PLAYERS for p in position[pl]}
    for dir in HEX_DIRECTIONS:
        target = add_coords(peg, dir)
        if target == CENTER or tuple(target) in all_occupied:
            continue
        moves.append([peg, target])
    return moves

def generate_hop_chains(position: Dict[str, List[List[int]]], player: str, start: List[int]) -> List[List[List[int]]]:
    all_occupied = {tuple(p) for pl in ALL_PLAYERS for p in position[pl]}
    results = []
    visited = set()

    def dfs(path):
        last = path[-1]
        for dir in HEX_DIRECTIONS:
            mid = add_coords(last, dir)
            end = add_coords(mid, dir)
            if tuple(mid) not in all_occupied:
                continue
            if tuple(end) in all_occupied or end == CENTER or tuple(end) in visited:
                continue
            visited.add(tuple(end))
            new_path = path + [end]
            results.append(new_path)
            dfs(new_path)

    dfs([start])
    return results

def generate_legal_moves(position: Dict[str, List[List[int]]], player: str) -> List[List[List[int]]]:
    legal_moves = []
    for peg in position[player]:
        legal_moves.extend(generate_simple_moves(position, player, peg))
        legal_moves.extend(generate_hop_chains(position, player, peg))
    return legal_moves

# ------------------------- GREEDY AGENT -------------------------

def get_goal_zone(player: str) -> List[List[int]]:
    if player == 'A':
        return HOME_ZONES['B']
    elif player == 'B':
        return HOME_ZONES['C']
    elif player == 'C':
        return HOME_ZONES['A']


def evaluate_move(move: List[List[int]], player: str, goal_zone: List[List[int]]) -> int:
    start = move[0]
    end = move[-1]
    best_goal = min(goal_zone, key=lambda g: distance(end, g))
    return -distance(end, best_goal)  # Negative for greedy (closer is better)


def choose_greedy_move(position: Dict[str, List[List[int]]], player: str) -> List[List[int]]:
    legal_moves = generate_legal_moves(position, player)
    goal_zone = get_goal_zone(player)
    best_move = max(legal_moves, key=lambda m: evaluate_move(m, player, goal_zone))
    return best_move

def choose_minimax_move(position: Dict[str, List[List[int]]], player: str, depth=2) -> List[List[int]]:
    _, move = max(position, depth, player, True)
    return move if move else choose_greedy_move(position, player)

# ------------------------- SERVER INTERFACE -------------------------

def make_move(position: Dict[str, List[List[int]]]) -> List[List[int]]:
    return choose_greedy_move(position, PLAYER_A)

# ------------------------- MAIN FOR LOCAL TESTING -------------------------
if __name__ == "__main__":
    sample_position = {
        "A": [[1, 0], [1, 2], [0, 3]],
        "B": [[2, -2], [1, -2]],
        "C": [[-1, 2], [0, 1]]
    }
    move = make_move(sample_position)
    print("Chosen Move:", move)

