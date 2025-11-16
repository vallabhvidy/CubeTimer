import random
from pathlib import Path
import os

data_dir = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local/share')) / 'flatpak' / 'apps' / 'cube-timer' / 'CubeTimer'
data_dir.mkdir(parents=True, exist_ok=True)
scores_file_path = data_dir / 'scores.json'

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

def scramble_gen(scramble_length, dim="3x3x3"):

    directions = ["", "'", "2"]

    if dim == "3x3x3":
        moves = [
            ('U', 'U'),
            ('R', 'R'),
            ('L', 'L'),
            ('F', 'F'),
            ('D', 'D'),
            ('B', 'B')
        ]
    elif dim == "2x2x2":
        scramble_length /= 2
        moves = [
            ('U', 'U'),
            ('R', 'R'),
            ('L', 'L'),
            ('F', 'F'),
            ('D', 'D'),
            ('B', 'B')
        ]
    elif dim == "4x4x4":
        scramble_length *= 2
        moves = [
            ('U', 'U'), ('Uw', 'U'),
            ('D', 'D'), ('Dw', 'D'),
            ('R', 'R'), ('Rw', 'R'),
            ('L', 'L'), ('Lw', 'L'),
            ('F', 'F'), ('Fw', 'F'),
            ('B', 'B'), ('Bw', 'B')
        ]
    elif dim == "5x5x5":
        scramble_length *= 3
        moves = [
            ('U', 'U'), ('Uw', 'U'),
            ('D', 'D'), ('Dw', 'D'),
            ('R', 'R'), ('Rw', 'R'),
            ('L', 'L'), ('Lw', 'L'),
            ('F', 'F'), ('Fw', 'F'),
            ('B', 'B'), ('Bw', 'B')
        ]
    elif dim == "6x6x6":
        scramble_length *= 4
        moves = [
            ('U', 'U'), ('Uw', 'U'), ('3Uw', 'U'),
            ('D', 'D'), ('Dw', 'D'), ('3Dw', 'D'),
            ('R', 'R'), ('Rw', 'R'), ('3Rw', 'R'),
            ('L', 'L'), ('Lw', 'L'), ('3Lw', 'L'),
            ('F', 'F'), ('Fw', 'F'), ('3Fw', 'F'),
            ('B', 'B'), ('Bw', 'B'), ('3Bw', 'B')
        ]
    elif dim == "7x7x7":
        scramble_length *= 4.5
        moves = [
            ('U', 'U'), ('Uw', 'U'), ('3Uw', 'U'),
            ('D', 'D'), ('Dw', 'D'), ('3Dw', 'D'),
            ('R', 'R'), ('Rw', 'R'), ('3Rw', 'R'),
            ('L', 'L'), ('Lw', 'L'), ('3Lw', 'L'),
            ('F', 'F'), ('Fw', 'F'), ('3Fw', 'F'),
            ('B', 'B'), ('Bw', 'B'), ('3Bw', 'B')
        ]
    else:
        return "error"

    scramble = []
    prev = None
    while len(scramble) < scramble_length:
        move, face = random.choice(moves)
        if face == prev:
            continue

        direction = random.choice(directions)
        scramble.append(move + direction)
        prev = face

    return "  ".join(scramble)


