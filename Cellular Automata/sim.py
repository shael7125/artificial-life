import numpy as np
import tkinter as tk

# ================== USER INPUT (TERMINAL) ==================
print("Select neuronal mode:")
print("1) Healthy")
print("2) Epileptic")

mode = input("Enter 1 or 2: ").strip()

if mode == "1":
    MODE_NAME = "Healthy"
    THRESHOLD = 2
    REFRACTORY = 6
    SPONTANEOUS = 0.0005
elif mode == "2":
    MODE_NAME = "Epileptic"
    THRESHOLD = 1
    REFRACTORY = 2
    SPONTANEOUS = 0.01
else:
    raise ValueError("Invalid selection.")

UPDATE_MS = int(input("Enter update rate in milliseconds (e.g. 40): "))

print("\nStarting simulation with:")
print(f"Mode        : {MODE_NAME}")
print(f"Threshold   : {THRESHOLD}")
print(f"Refractory  : {REFRACTORY}")
print(f"Spontaneous : {SPONTANEOUS}")
print(f"Update (ms) : {UPDATE_MS}")
print("-----------------------------------")

# ================== PARAMETERS ==================
N = 40  # grid size

# ================== STATES ==================
REST = 0
FIRE = 1
# 2..REFRACTORY = refractory

grid = np.zeros((N, N), dtype=int)

# ================== TKINTER SETUP ==================
CELL_SIZE = 15
WIDTH = N * CELL_SIZE
HEIGHT = N * CELL_SIZE

root = tk.Tk()
root.title(f"Neuronal Cellular Automaton ({MODE_NAME})")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

rects = [[None for _ in range(N)] for _ in range(N)]
for i in range(N):
    for j in range(N):
        x1 = j * CELL_SIZE
        y1 = i * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        rects[i][j] = canvas.create_rectangle(
            x1, y1, x2, y2, outline="", fill="red"
        )

# ================== CA LOGIC ==================
def count_firing_neighbors(g, i, j):
    total = 0
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni, nj = (i + di) % N, (j + dj) % N
            if g[ni, nj] == FIRE:
                total += 1
    return total


def step():
    global grid
    new_grid = grid.copy()

    for i in range(N):
        for j in range(N):
            state = grid[i, j]

            if state == REST:
                if count_firing_neighbors(grid, i, j) >= THRESHOLD:
                    new_grid[i, j] = FIRE
                elif np.random.rand() < SPONTANEOUS:
                    new_grid[i, j] = FIRE

            elif state == FIRE:
                new_grid[i, j] = 2

            else:
                if state < REFRACTORY:
                    new_grid[i, j] += 1
                else:
                    new_grid[i, j] = REST

    grid = new_grid

    # Update visualization
    for i in range(N):
        for j in range(N):
            state = grid[i, j]
            if state == REST:
                color = "red"
            elif state == FIRE:
                color = "green"
            else:
                color = "yellow"
            canvas.itemconfig(rects[i][j], fill=color)

    root.after(UPDATE_MS, step)

# ================== START ==================
step()
root.mainloop()
