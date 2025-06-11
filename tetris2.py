import random
import time
import os

def render(cells):
    os.system('clear')
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            if (x, y) in cells:
                row.append('██')
            else:
                row.append('▒▒')
        print("".join(row))

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

shape_queue = random.sample(list(SHAPES.keys()), 4)
shape = shape_queue.pop(0)
shapequeue1, shapequeue2, shapequeue3 = shape_queue

last_move_time = time.time()
fall_period = 1

while True:
    cellxpos = 4
    cellypos = 0
    orientation = 0
    active = True
    while active:
        cells = [(cellxpos + dx, cellypos + dy) for dx, dy in SHAPES[shape][orientation]]

        if time.time() - last_move_time >= fall_period:
            cellypos += 1
            last_move_time = time.time()