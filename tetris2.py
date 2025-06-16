import random
import time
import os
import sys
import tty
import termios
import select
import pygame

pygame.init()
pygame.mixer.init()

theme = pygame.mixer.Sound('audio_assets/tetris_theme.mp3')
clear_sound = pygame.mixer.Sound('audio_assets/tetris_clear.mp3')
place = pygame.mixer.Sound('audio_assets/tetris_block_place.mp3')

class Soundfx:
    def __init__(self, sound=None):
        """
        Create a new sound controller.
        sound: the audio file to control (can be None for no sound)
        """
        self.sound = sound
    
    def play(self, loops):
        """
        Play the sound.
        loops: how many times to repeat (e.g: -1 = forever, 0 = play once)
        """
        if self.sound: 
            self.sound.play(loops)
    
    def pause(self):
        """Pause all currently playing sounds"""
        pygame.mixer.pause()
    
    def stop(self):
        """Stop playing this specific sound"""
        if self.sound:
            self.sound.stop()

    def set_volume(self, volume):
        """
        Set how loud this sound should be.
        volume: number between 0.0 (silent) and 1.0 (full volume)
        """
        if self.sound:
            self.sound.set_volume(volume)

bg_sound = Soundfx(theme) 
bg_sound.set_volume(0.5)     
clearfx = Soundfx(clear_sound)     
placefx = Soundfx(place)

def getch():
    """
    Check if a key has been pressed without waiting.
    This allows the game to keep running while checking for player input.
    Returns: the key that was pressed, or None if no key was pressed
    """
    
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

def clear():
    os.system('clear')

def render(cells, settled_cells, temp_colors=None, highlight_rows=None, highlight_frame=0):
    if temp_colors is None:
        temp_colors = {}
    if highlight_rows is None:
        highlight_rows = set()
    clear()
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            if y in highlight_rows:
                # Flashing effect: alternate between white and original color
                if highlight_frame % 2 == 0:
                    colour = COLOURS['WHITE']
                else:
                    colour = temp_colors.get((x, y), cell_colours.get((x, y), COLOURS['WHITE']))
                row.append(f'{colour}██{COLOURS["RESET"]}')
            elif (x, y) in cells:
                colour = temp_colors.get((x, y), cell_colours.get((x, y), COLOURS['WHITE']))
                row.append(f'{colour}██{COLOURS["RESET"]}')
            elif (x, y) in settled_cells:
                colour = cell_colours.get((x, y), COLOURS['WHITE'])
                row.append(f'{colour}██{COLOURS["RESET"]}')
            else:
                row.append('▒▒')
        print("".join(row))

def can_move(cells, dx, dy, settled_cells):
    """Check if a piece can move in a given direction without colliding."""
    new_cells = [(x + dx, y + dy) for x, y in cells]
    return all(0 <= x < WIDTH and y < HEIGHT and (x, y) not in settled_cells for x, y in new_cells)

def find_full_rows(settled_cells):
    """
    Find all rows that are completely filled and ready to be cleared.
    settled_cells: positions of all landed pieces
    Returns: list of row numbers that are full
    """
    full_rows = []
    for y in range(HEIGHT):
        row_cells = [(x, y) for x in range(WIDTH)]
        if all((x, y) in settled_cells for x, y in row_cells):
            full_rows.append(y)
    return full_rows

def animate_row_clearing(settled_cells, cell_colors, full_rows, shape_queue):
    """
    Show a brief animation when rows are being cleared.
    This makes the line clearing more visually satisfying.
    """
    highlight_rows = set(full_rows)
    for frame in range(6):
        # Alternate highlight for flashing effect
        render(set(), settled_cells, cell_colors, highlight_rows, frame)
        print(f"Use A/D to move left/right, S to drop faster, W to rotate, Q to quit")
        print(f"Clearing {len(full_rows)} row(s)!")
        time.sleep(0.12)

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

    bg_sound.play(-1)
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
                    cellxpos -= 1
                elif key.lower() == 'd' and can_move(cells, 1, 0, settled_cells):
                    cellxpos += 1
                elif key.lower() == 's' and can_move(cells, 0, 1, settled_cells):
                    cellypos += 1
                    last_move_time = time.time()
                elif key.lower() == 'w':
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

                    placefx.play(0)

                    active = False

                    full_rows = find_full_rows(settled_cells)
                    if full_rows:
                        clearfx.play(0)

                        animate_row_clearing(settled_cells, cell_colours, full_rows, [shapequeue1, shapequeue2, shapequeue3])

                        # Remove full rows and shift above cells down
                        for row in sorted(full_rows):
                            # Remove all cells in the full row
                            for x in range(WIDTH):
                                settled_cells.discard((x, row))
                                cell_colours.pop((x, row), None)
                            # Move all cells above down by 1
                            new_settled = set()
                            new_colours = {}
                            for (x, y) in settled_cells:
                                if y < row:
                                    new_settled.add((x, y + 1))
                                    if (x, y) in cell_colours:
                                        new_colours[(x, y + 1)] = cell_colours[(x, y)]
                                else:
                                    new_settled.add((x, y))
                                    if (x, y) in cell_colours:
                                        new_colours[(x, y)] = cell_colours[(x, y)]
                            settled_cells = new_settled
                            cell_colours = new_colours

                    shape_queue = [shapequeue1, shapequeue2, shapequeue3]
                    shape = shape_queue.pop(0)
                    shape_queue.append(random.choice(list(SHAPES.keys())))
                    shapequeue1, shapequeue2, shapequeue3 = shape_queue
                    shape_colour = SHAPE_COLOURS[shape] 

            time.sleep(0.05)

except KeyboardInterrupt:
    pass
finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)