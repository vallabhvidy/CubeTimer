from random import choice, randint
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

_2_3_moves = (
    'U',
    'D',
    'R',
    'L',
    'F',
    'B'
)
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
directions_3 = ("", "'")
directions_4 = ("", "'", "2")

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


# Scrambling

def get_nxn_face(move):
    for i in move:
        if i in opposing_faces:
            return i
    raise LookupError(f"Turn {move} does not have a face. Is this an NxN move?")


pyraminx_moves = ('L', 'R', 'B', 'U')
pyraminx_tip_moves = ('l', 'r', 'b', 'u')
def pyraminx_skewb_scramble(scramble_length, dim="Pyraminx"):
    # NOTE: Assume a scramble length of 20, then scale

    scramble_length = ceil(scramble_length / 2)

    scramble = []
    previous = None
    for n in range(scramble_length):
        # Create a list of allowed moves
        allowed = list(range(len(pyraminx_moves)))
        if previous != None:
            allowed.pop(previous)

        # Get a random move from the above list
        next_indice = choice(allowed)
        move = pyraminx_moves[next_indice]

        # Get a random direction
        direction = choice(directions_3)

        scramble.append(move + direction)

        # Update the previous move
        previous = next_indice

    if dim == "Pyraminx":
        for i in pyraminx_tip_moves:
            tip_move = randint(1, 3)
            if tip_move == 2:
                scramble.append(i)
            elif tip_move == 3:
                scramble.append(i + "'")

    return "  ".join(scramble)


megaminx_directions_large = ("--", "+\u2060+")
megaminx_moves_large = ("R", "D")
def megaminx_scramble():
    scramble = []
    for i in range(7):
        # Large moves
        for j in range(10):
            direction = choice(megaminx_directions_large)
            scramble.append(megaminx_moves_large[j % 2] + direction)

        # Face move
        direction = choice(directions_3)
        scramble.append("U" + direction)

    return "  ".join(scramble)


def clock_num_to_rotation(num):
    string = str(abs(num))
    if num >= 0:
        return string + "+"
    else:
        return string + "-"

clock_moves_set1 = (
    "UR",
    "DR",
    "DL",
    "UL"
)
clock_moves_set2 = (
    "U",
    "R",
    "D",
    "L",
    "ALL"
)
def clock_scramble():
    scramble = []
    for i in clock_moves_set1:
        scramble.append(i + clock_num_to_rotation(randint(-5, 6)))

    for i in range(2):
        for j in clock_moves_set2:
            scramble.append(j + clock_num_to_rotation(randint(-5, 6)))
        scramble.append("y2")

    scramble.pop(-1)
    return "  ".join(scramble)


def scramble_gen(scramble_length, dim="3x3x3"):
    # NOTE: Assume a scramble length of 20, then scale

    moves = _2_3_moves
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
    elif dim == "Megaminx":
        return megaminx_scramble()
    elif dim == "Clock":
        return clock_scramble()
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
        next_indice = choice(allowed)
        move = moves[next_indice]

        # Get a random direction
        direction = choice(directions_4)

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
