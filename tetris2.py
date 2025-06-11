import random
import time
import os
import sys
import tty
import termios
import select

def getch():
    """
    Check if a key has been pressed without waiting.
    This allows the game to keep running while checking for player input.
    Returns: the key that was pressed, or None if no key was pressed
    """
    # Check if there's input available without blocking the program
    if select.select([sys.stdin], [], [], 0)[0]:  # 0 = don't wait at all
        return sys.stdin.read(1)  # Read one character
    return None  # No key was pressed

def render(cells, settled_cells, temp_colors=None):
    if temp_colors is None:
        temp_colors = {}
    
    os.system('clear')
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            if (x, y) in cells:
                colour = temp_colors.get((x,y), cell_colours.get((x,y), COLOURS['WHITE']))
                row.append(f'{colour}██{COLOURS["RESET"]}')
            elif (x, y) in settled_cells:
                colour = cell_colours.get((x,y), COLOURS['WHITE'])
                row.append(f'{colour}██{COLOURS["RESET"]}')
            else:
                row.append('▒▒')
        print("".join(row))

def can_move(cells, dx, dy, settled_cells):
    """Check if a piece can move in a given direction without colliding."""
    new_cells = [(x + dx, y + dy) for x, y in cells]
    return all(0 <= x < WIDTH and y < HEIGHT and (x, y) not in settled_cells for x, y in new_cells)

HEIGHT = 20
WIDTH = 10

SHAPES = {
    1: [[(0,0), (1,0), (0,1), (1,1)]],
    2: [[(0,0), (0,1), (0,2), (0,3)], [(0,0), (1,0), (2,0), (3,0)]],
    3: [[(1,0), (0,1), (1,1), (2,1)], [(1,0), (0,1), (1,1), (1,2)], [(0,0), (1,0), (2,0), (1,1)], [(0,0), (0,1), (0,2), (1,1)]],
    4: [[(1,0), (2,0), (0,1), (1,1)], [(0,0), (0,1), (1,1), (1,2)]],
    5: [[(0,0), (1,0), (1,1), (2,1)], [(1,0), (0,1), (1,1), (0,2)]],
    6: [[(0,0), (0,1), (1,1), (2,1)], [(1,0), (2,0), (1,1), (1,2)], [(0,0), (1,0), (2,0), (2,1)], [(1,0), (1,1), (0,2), (1,2)]],
    7: [[(2,0), (0,1), (1,1), (2,1)], [(1,0), (1,1), (1,2), (2,2)], [(0,0), (1,0), (2,0), (0,1)], [(0,0), (1,0), (1,1), (1,2)]]
}

COLOURS = {
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
    'CYAN': '\033[96m',
    'ORANGE': '\033[38;5;208m',
    'WHITE': '\033[97m',
    'RESET': '\033[0m'
}

SHAPE_COLOURS = {
    1: COLOURS['YELLOW'],
    2: COLOURS['CYAN'],
    3: COLOURS['MAGENTA'],
    4: COLOURS['GREEN'],
    5: COLOURS['RED'],
    6: COLOURS['BLUE'],
    7: COLOURS['ORANGE']
}

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
tty.setcbreak(fd)

try:
    shape_queue = random.sample(list(SHAPES.keys()), 4)
    shape = shape_queue.pop(0)
    shapequeue1, shapequeue2, shapequeue3 = shape_queue
    shape_colour = SHAPE_COLOURS[shape]
    settled_cells = set()
    cell_colours = {}
    last_move_time = time.time()
    fall_period = 1

    while True:
        cellxpos = 4
        cellypos = 0
        orientation = 0
        active = True
        
        initial_cells = [(cellxpos + dx, cellypos + dy) for dx, dy in SHAPES[shape][orientation]]
        if any((x, y) in settled_cells for x, y in initial_cells):
            print("GAME OVER!")
            raise KeyboardInterrupt

        while active:
            cells = [(cellxpos + dx, cellypos + dy) for dx, dy in SHAPES[shape][orientation]]
            
            # Create temporary colors for the current falling piece
            temp_cell_colors = cell_colours.copy()
            for cell in cells:
                temp_cell_colors[cell] = shape_colour
            
            render(set(cells), settled_cells, temp_cell_colors)
            
            print("Use A/D to move left/right, S to drop faster, W to rotate, Q to quit")
            
            key = getch()
            if key:
                if key.lower() == 'a' and can_move(cells, -1, 0, settled_cells):
                    # Move left
                    cellxpos -= 1
                elif key.lower() == 'd' and can_move(cells, 1, 0, settled_cells):
                    # Move right
                    cellxpos += 1
                elif key.lower() == 's' and can_move(cells, 0, 1, settled_cells):
                    # Soft drop (move down faster)
                    cellypos += 1
                    last_move_time = time.time()  # Reset fall timer
                elif key.lower() == 'w':
                    # Rotate piece
                    new_orientation = (orientation + 1) % len(SHAPES[shape])
                    new_cells = [(cellxpos + dx, cellypos + dy) for dx, dy in SHAPES[shape][new_orientation]]
                    if can_move(new_cells, 0, 0, settled_cells):
                        orientation = new_orientation
                elif key.lower() == 'q':
                    print("\nGame ended by player.")
                    raise KeyboardInterrupt

            if time.time() - last_move_time >= fall_period:
                if can_move(cells, 0, 1, settled_cells):
                    cellypos += 1
                    last_move_time = time.time()
                else:
                    settled_cells.update(cells)
                    for cell in cells:
                        cell_colours[cell] = shape_colour

                    active = False
                    shape_queue = [shapequeue1, shapequeue2, shapequeue3]
                    shape = shape_queue.pop(0)
                    shape_queue.append(random.choice(list(SHAPES.keys())))
                    shapequeue1, shapequeue2, shapequeue3 = shape_queue
                    shape_colour = SHAPE_COLOURS[shape]  # Update color for new shape

            time.sleep(0.05)

except KeyboardInterrupt:
    pass
finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)