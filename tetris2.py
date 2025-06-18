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

    queue_display = render_queue_shapes(shape_queue or [])

    clear()
    for y in range(HEIGHT):
        line = ""
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
                row.append('░░')
        line += "".join(row)
        line += "  " + queue_display[y]
        print(line)

def render_queue_shapes(shape_queue):
    """
    Create the visual display for the next pieces queue.
    shape_queue: list of upcoming piece types
    Returns: list of strings, each representing one line of the queue display
    """
    display_lines = []
    for display_y in range(HEIGHT):
        line = ""
        if display_y == 0:
            line = "    NEXT    "
        elif 1 <= display_y <= 12:
            queue_index = (display_y - 1) // 4
            local_y = (display_y - 1) % 4
            if queue_index < len(shape_queue):
                shape = shape_queue[queue_index]
                shape_color = SHAPE_COLOURS[shape]
                shape_cells = SHAPES[shape][0]
                min_x = min(x for x, y in shape_cells) if shape_cells else 0
                max_x = max(x for x, y in shape_cells) if shape_cells else 0
                min_y = min(y for x, y in shape_cells) if shape_cells else 0
                max_y = max(y for x, y in shape_cells) if shape_cells else 0
                offset_x = 1 - min_x + (1 - (max_x - min_x)) // 2
                offset_y = 1 - min_y + (1 - (max_y - min_y)) // 2
                for display_x in range(6):
                    shape_x = display_x - offset_x - 1
                    shape_y = local_y - offset_y
                    if (shape_x, shape_y) in shape_cells:
                        line += f'{shape_color}██{COLOURS["RESET"]}'
                    else:
                        line += '░░'
            else:
                line += '░░░░░░░░░░░░'
        else:
            line += '            '
        display_lines.append(line)
    return display_lines

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
        if frame % 2 == 0:
            print(f"+{len(full_rows) * 100} pts!")
        else:
            print("")
        time.sleep(0.15)

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
    score = 0

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
            
            temp_cell_colors = cell_colours.copy()
            for cell in cells:
                temp_cell_colors[cell] = shape_colour
            
            render(set(cells), settled_cells, temp_cell_colors)
            
            print("Use A/D to move left/right, S to drop faster, W to rotate, Q to quit")
            print(f"Score: {score}")
            
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
                        score += 100 * len(full_rows)

                        animate_row_clearing(settled_cells, cell_colours, full_rows, [shapequeue1, shapequeue2, shapequeue3])

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