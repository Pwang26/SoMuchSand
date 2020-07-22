#!/usr/bin/env python3



import sys
import tkinter
import random
import datetime


def do_move(grid, x1, y1, x2, y2):
    # By moving whatever is in coordinate (x, y), you are able to create the motion of sand.
    move = grid[y1][x1]
    grid[y1][x1] = grid[y2][x2]
    grid[y2][x2] = move
    return grid






def check_move(grid, x1, y1, x2, y2):
    # checks to see if sand is able to move to the given spot
    if x2 < 0 or y2 < 0:
        return False
    if x2 >= (len(grid[0])): # sand can't go past canvas
        return False
    if y2 >= (len(grid)):
        return False
    if grid[y2][x2] != None: # if another block is present, don't move there
        return False
    if x1 != x2:
        if grid[y1][x2] != None:
            return False
    return True






def do_gravity(grid, x, y):
   # creates gravity by making all sand move in some sort of downward motion
    if grid[y][x] == 's':
        if check_move(grid, x, y, x, y + 1):
            return do_move(grid, x, y, x, y + 1)
        if check_move(grid, x, y, x -1, y + 1):
            return do_move(grid, x, y, x - 1, y + 1)
        if check_move(grid, x, y, x + 1, y + 1):
            return do_move(grid, x, y, x + 1, y + 1)
    return grid



def do_brownian(grid, x, y, brownian):
    # sand is not still, so brownian makes it more realistic by "shaking" the sand
    if grid[y][x] == 's':
        num = random.randrange(0, 100)
        if num < brownian:
            coin = random.randrange(2)
            if coin == 0:
                if check_move(grid, x, y, x - 1, y):
                    do_move(grid, x, y, x - 1, y)
            if coin == 1:
                if check_move(grid, x, y, x + 1, y):
                    do_move(grid, x, y, x + 1, y)

        if num >= brownian:
            return grid




def do_whole_grid(grid, brownian):

    rows = len(grid)
    for i in reversed(range(rows)):
        cols = len(grid[0])
        for j in range(cols):
            do_gravity(grid, j, i)
            do_brownian(grid, j, i, brownian)
    return grid




def draw_grid_canvas(grid, canvas, scale):

    # pixel size of canvas
    cwidth = len(grid[0]) * scale + 2
    cheight = len(grid) * scale + 2

    canvas.delete('all')
    # draw black per spot
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            val = grid[y][x]
            if val:
                if val == 'r':
                    color = 'black'
                else:
                    color = 'yellow'
                rx = 1 + x * scale
                ry = 1 + y * scale
                canvas.create_rectangle(rx, ry, rx + scale, ry + scale, fill=color, outline='black')

    canvas.create_rectangle(0, 0, cwidth-1, cheight-1, outline='blue')
    canvas.update()


fps_enable = True
fps_count = 0
fps_start = 0


def fps_update():
    global fps_enable, fps_count, fps_start, fps_label
    if not fps_enable:
        return
    fps_count += 1
    if fps_count == 40:
        now = datetime.datetime.now().timestamp()
        delta = now - fps_start
        fps_start = now
        fps = int(1 / (delta / fps_count))
        # print(fps)
        fps_label.config(text=str(fps))
        fps_count = 0


# Global pointers to GUI elements we need in various callbacks
gravity = None
content = None
brownian_on = None
brownian_val = None
fps_label = None

SIDE = 14  # pixels across of one square (set in main() too)
SHIFT = 6


# provided function to build the GUI
def make_gui(top, width, height):
    """
    Set up the GUI elements for the Sand window, returning the Canvas to use.
    top is TK root, width/height is canvas size.
    """

    global gravity, content, brownian_on, brownian_val, fps_label
    gravity = tkinter.IntVar()
    content = tkinter.StringVar()
    brownian_on = tkinter.IntVar()
    brownian_val = tkinter.IntVar()

    top.title('Sand')

    # gravity checkbox
    gcheck = tkinter.Checkbutton(top, text='Gravity', name='gravity', variable=gravity)
    gcheck.grid(row=0, column=0, sticky='w')
    gravity.set(1)

    scheck = tkinter.Checkbutton(top, text='Brownian', name='brownian', variable=brownian_on)
    scheck.grid(row=0, column=1, sticky='w')
    brownian_on.set(1)

    scale = tkinter.Scale(top, from_=0, to=100, orient=tkinter.HORIZONTAL, variable=brownian_val)
    scale.grid(row=0, column=2, sticky='w')
    brownian_val.set(20)

    # content variable = state of radio button
    sand = tkinter.Radiobutton(top, text="Sand", variable=content, value='s')
    sand.grid(row=0, column=3, sticky='w')

    rock = tkinter.Radiobutton(top, text="Rock", variable=content, value='r')
    rock.grid(row=0, column=4, sticky='w')

    erase = tkinter.Radiobutton(top, text="Erase", variable=content, value='erase')
    erase.grid(row=0, column=5, sticky='w')

    bigerase = tkinter.Radiobutton(top, text="BigErase", variable=content, value='bigerase')
    bigerase.grid(row=0, column=6, sticky='w')

    content.set('s')

    fps_label = tkinter.Label(top, text="0", fg='lightgray')  # ugh 'fg' not a great name for this!
    fps_label.grid(row=0, column=7, sticky='w')

    # canvas for drawing
    canvas = tkinter.Canvas(top, width=width, height=height, name='canvas')

    canvas.xview_scroll(SHIFT, "units")  # hack so (0, 0) works correctly
    canvas.yview_scroll(SHIFT, "units")

    canvas.grid(row=1, columnspan=12, sticky='w', padx=20, ipady=5)

    top.update()
    return canvas


def big_erase(grid, x, y, canvas):
    """Erase big red circle in the given grid centered on x,y"""
    rad = 4
    # Compute circle around x,y in grid coords
    x1 = x - rad  # this can be out of bounds
    y1 = y - rad

    x2 = x + rad
    y2 = y + rad

    # Draw a red circle .. will be erased by later updates
    # Need to be consistent about grid -> pixel mapping
    canvas.create_oval(1 + x1 * SIDE, 1 + y1 * SIDE, 1 + x2 * SIDE, 1 + y2 * SIDE,
                       fill='red', outline='')
    canvas.update()

    for ey in range(y1, y2 + 1):
        for ex in range(x1, x2 + 1):
            # circle around x,y
            if not (ex < 0 or ex >= len(grid[0]) or ey < 0 or ey >= len(grid)) and abs(x-ex)**2 + abs(y-ey)**2 <= rad ** 2:
                grid[ey][ex] = None


# delay between calling the timer
TIMER_MS = 1


def start_timer(top, fn):
    """Start the my_timer system, calls given fn"""
    top.after(TIMER_MS, lambda: my_timer(top, fn))


def my_timer(top, fn):
    """my_timer callbback, re-posts itself."""
    fn()
    top.after(TIMER_MS, lambda: my_timer(top, fn))


def sand_action(grid, canvas, scale):
    """This function runs on timer for all periodic tasks."""
    global gravity
    global mouse_fn
    global brownian_on
    global brownian_val

    if mouse_fn:
        mouse_fn()

    if gravity.get():
        if not brownian_on.get():
            val = 0
        else:
            val = brownian_val.get()
        do_whole_grid(grid, val)
    draw_grid_canvas(grid, canvas, scale)
    fps_update()


# global mouse sand_action function pointer
# set on mouse down, cleared on mouse-up
mouse_fn = None


def do_mouse_up(event):
    global mouse_fn
    mouse_fn = None


def do_mouse(event, grid, scale, canvas):
    """Callback for mouse click/move"""
    global mouse_fn
    mouse_fn = lambda: do_mouse(event, grid, scale, canvas)

    x = (event.x - SHIFT // 2) // scale
    y = (event.y - SHIFT // 2) // scale
    if not (x < 0 or x >= len(grid[0]) or y < 0 or y >= len(grid)):
        global content
        val = content.get()  # 's' 'r' None
        if val == 's' or val == 'r':
            grid[y][x] = val
        elif val == 'erase':
            grid[y][x] = None
        elif val == 'bigerase':
            big_erase(grid, x, y, canvas)
    # print('click', event.x, event.y)


def main():
    args = sys.argv[1:]

    # Size in squares of world, override from command line
    width = 50
    height = 50
    if len(args) >= 2:
        width = int(args[0])
        height = int(args[1])

    # Size of one square in pixels, override from command line
    global SIDE
    SIDE = 14
    if len(args) == 3:
        SIDE = int(args[2])

    top = tkinter.Tk()
    canvas = make_gui(top, width * SIDE + 2, height * SIDE + 2)
    grid = [[None] * width for _ in range(height)]

    canvas.bind("<B1-Motion>", lambda evt: do_mouse(evt, grid, SIDE, canvas))
    canvas.bind("<Button-1>", lambda evt: do_mouse(evt, grid, SIDE, canvas))
    canvas.bind("<ButtonRelease-1>", lambda evt: do_mouse_up(evt))

    start_timer(top, lambda: sand_action(grid, canvas, SIDE))

    tkinter.mainloop()


if __name__ == '__main__':
    main()
