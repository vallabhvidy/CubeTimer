import random
from pathlib import Path
import os
from math import ceil

data_dir = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local/share')) / 'flatpak' / 'apps' / 'cube-timer' / 'CubeTimer'
data_dir.mkdir(parents=True, exist_ok=True)
scores_file_path = data_dir / 'scores.json'

opposing_faces = {
    "U": "D",
    "D": "U",
    "R": "L",
    "L": "R",
    "F": "B",
    "B": "F"
}

_4_5_moves = (
    'U', 'Uw',
    'D', 'Dw',
    'R', 'Rw',
    'L', 'Lw',
    'F', 'Fw',
    'B', 'Bw'
)
_6_7_moves = (
    'U', 'Uw', '3Uw',
    'D', 'Dw', '3Dw',
    'R', 'Rw', '3Rw',
    'L', 'Lw', '3Lw',
    'F', 'Fw', '3Fw',
    'B', 'Bw', '3Bw'
)

def calc_time(time):
    minutes = time // 6000
    seconds = (time % 6000) // 100
    milisec = (time % 6000) % 100 // 1

    return minutes, seconds, milisec

def time_string(time):
    if time == -1:
        return "-"

    if time == 0:
        return "DNF"

    minutes = time // 6000
    seconds = (time % 6000) // 100
    milisec = (time % 6000) % 100 // 1

    time_str = "{minutes:02d}:{seconds:02d}.{milisec:02d}".format(minutes=minutes, seconds=seconds, milisec=milisec)

    return time_str

def get_nxn_face(move):
    for i in move:
        if i in opposing_faces:
            return i

def pyraminx_skewb_scramble(scramble_length, dim="Pyraminx"):
    # NOTE: Assume a scramble length of 20, then scale

    directions = ("", "'")
    moves = ('U', 'R', 'L', 'B')
    tip_moves = ('l', 'r', 'b', 'u')

    scramble_length = ceil(scramble_length / 2)

    scramble = []
    previous = None
    for n in range(scramble_length):
        # Create a list of allowed moves
        allowed = list(range(len(moves)))
        if previous != None:
            allowed.pop(previous)

        # Get a random move from the above list
        next_indice = random.choice(allowed)
        move = moves[next_indice]

        # Get a random direction
        direction = random.choice(directions)

        scramble.append(move + direction)

        # Update the previous move
        previous = next_indice

    if dim == "Pyraminx":
        for i in tip_moves:
            tip_move = random.randint(1, 3)
            if tip_move == 2:
                scramble.append(i)
            elif tip_move == 3:
                scramble.append(i + "'")

    return "  ".join(scramble)

def scramble_gen(scramble_length, dim="3x3x3"):
    # NOTE: Assume a scramble length of 20, then scale

    directions = ("", "'", "2")

    moves = (
        'U',
        'D',
        'R',
        'L',
        'F',
        'B'
    )
    if dim == "2x2x2":
        scramble_length = ceil(scramble_length / 2)
    elif dim == "4x4x4":
        scramble_length *= 2
        moves = _4_5_moves
    elif dim == "5x5x5":
        scramble_length *= 3
        moves = _4_5_moves
    elif dim == "6x6x6":
        scramble_length *= 4
        moves = _6_7_moves
    elif dim == "7x7x7":
        scramble_length *= 5
        moves = _6_7_moves
    elif dim == "Pyraminx" or dim == "Skewb":
        return pyraminx_skewb_scramble(scramble_length, dim)
    elif dim != "3x3x3":
        return "error"

    scramble = []
    previous = []
    for n in range(scramble_length):
        # Create a list of allowed moves
        allowed = list(range(len(moves)))
        for i in range(len(previous)):
            allowed.pop(previous[i])

        # Get a random move from the above list
        next_indice = random.choice(allowed)
        move = moves[next_indice]

        # Get a random direction
        direction = random.choice(directions)

        scramble.append(move + direction)

        # Check if the move will reset the previous move list
        passes = False
        face = get_nxn_face(move)
        if len(previous) != 0:
            test_face = get_nxn_face(moves[previous[0]])
            if face == test_face or face == opposing_faces[test_face]: # new face
                passes = True

        # Update the previous move list
        if passes:
            previous.append(next_indice)
            previous = sorted(previous, reverse=True)
        else:
            previous = [next_indice]

    return "  ".join(scramble)
