import turtle
import math as math
import tkinter as tk

# Ellipse boundary
ELLIPSE_CENTER = (0, 0)
ELLIPSE_RX = 100
ELLIPSE_RY = 150

# ---------- L-system generation ----------
def apply_rules(axiom, rules, iterations):
    sequence = axiom
    for _ in range(iterations):
        next_seq = ""
        for char in sequence:
            if char in rules:
                next_seq += rules[char]
            else:
                next_seq += char
        sequence = next_seq
    return sequence

# enforce geometry
def inside_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx)**2) / (rx**2) + ((y - cy)**2) / (ry**2) <= 1


# draw geometry
def draw_ellipse(cx, cy, rx, ry):
    turtle.penup()
    turtle.goto(cx, cy - ry)
    turtle.pendown()
    turtle.color("gray")
    turtle.pensize(2)

    for angle in range(-90, 271):
        turtle.goto(
            cx + rx * math.cos(math.radians(angle)),
            cy + ry * math.sin(math.radians(angle))
        )

    turtle.color("black")

def compute_sa_volume_ratio(sequence, step, base_thickness, shrink):
    stack = []
    alive = True

    total_sa = 0.0
    total_vol = 0.0

    for char in sequence:
        depth = len(stack)
        thickness = max(1, base_thickness * (shrink ** depth))
        radius = thickness / 2

        if char == "F" and alive:
            # branch segment as cylinder
            h = step
            total_sa += 2 * math.pi * radius * h
            total_vol += math.pi * radius**2 * h

        elif char == "[":
            stack.append((depth, alive))
        elif char == "]":
            depth, alive = stack.pop()

    if total_vol == 0:
        return float("inf")
    return total_sa / total_vol



# ---------- Drawing routine ----------
def draw_lsystem(sequence, angle, step, base_thickness, shrink, batch_update=5):
    turtle.reset()
    turtle.hideturtle()
    turtle.speed(0)        # max speed
    turtle.penup()

    # ---- Draw ellipse instantly ----
    turtle.tracer(0)       # disable animation for ellipse
    draw_ellipse(ELLIPSE_CENTER[0], ELLIPSE_CENTER[1],
                 ELLIPSE_RX, ELLIPSE_RY)
    turtle.update()        # flush ellipse to screen

    # ---- Prepare for tree drawing ----
    turtle.color("black")
    turtle.pensize(base_thickness)

    cx, cy = ELLIPSE_CENTER
    start_x = cx
    epsilon = 1.0
    start_y = cy - ELLIPSE_RY + epsilon

    turtle.goto(start_x, start_y)
    turtle.setheading(90)  # point upwards
    turtle.pendown()

    stack = []
    alive = True
    step_count = 0

    turtle.tracer(0)  # disable auto-refresh for tree, we'll update manually

    for char in sequence:
        depth = len(stack)
        thickness = max(1, base_thickness * (shrink ** depth))
        turtle.pensize(thickness)

        if char == "F" and alive:
            x, y = turtle.position()
            heading = math.radians(turtle.heading())

            # predict next point
            nx = x + step * math.cos(heading)
            ny = y + step * math.sin(heading)

            if not inside_ellipse(nx, ny, cx, cy, ELLIPSE_RX, ELLIPSE_RY):
                alive = False
                turtle.penup()
            else:
                turtle.pendown()
                turtle.goto(nx, ny)

            # batch screen update for speed
            step_count += 1
            if step_count % batch_update == 0:
                turtle.update()

        elif char == "+" and alive:
            turtle.right(angle)
        elif char == "-" and alive:
            turtle.left(angle)
        elif char == "[":
            stack.append((turtle.position(), turtle.heading(), alive))
        elif char == "]":
            pos, heading, alive = stack.pop()
            turtle.penup()
            turtle.setposition(pos)
            turtle.setheading(heading)
            turtle.pendown() if alive else turtle.penup()

    # final flush
    turtle.update()

    for char in sequence:
        depth = len(stack)
        thickness = max(1, base_thickness * (shrink ** depth))
        turtle.pensize(thickness)
        if char == "F" and alive:
            x, y = turtle.position()
            heading = math.radians(turtle.heading())

            # predict next point WITHOUT moving
            nx = x + step * math.cos(heading)
            ny = y + step * math.sin(heading)

            if not inside_ellipse(nx, ny, *ELLIPSE_CENTER, ELLIPSE_RX, ELLIPSE_RY):
                alive = False
                turtle.penup()   # kill this branch
            else:
                turtle.pendown()
                turtle.goto(nx, ny)


        elif char == "+" and alive:
            turtle.right(angle)

        elif char == "-" and alive:
            turtle.left(angle)

        elif char == "[":
            stack.append((turtle.position(), turtle.heading(), alive))

        elif char == "]":
            pos, heading, alive = stack.pop()
            turtle.penup()
            turtle.setposition(pos)
            turtle.setheading(heading)
            turtle.pendown() if alive else turtle.penup()



# ---------- GUI callback ----------


def generate_tree():
    angle = angle_slider.get()
    step = step_slider.get()
    iterations = iter_slider.get()
    base_thickness = thickness_slider.get()
    shrink = shrink_slider.get()

    axiom = "F"
    rules = {
        "F": "FF-[-F+F+F]+[+F-F-F]"
    }

    sequence = apply_rules(axiom, rules, iterations)

    draw_lsystem(sequence, angle, step, base_thickness, shrink)

    ratio = compute_sa_volume_ratio(sequence, step, base_thickness, shrink)
    print()


    status_label.config(
        text=f"Surface area / Volume ratio: {ratio:.3f}"
    )

# ---------- Build GUI ----------
root = tk.Tk()
root.title("Fractal Tree Generator (L-System)")

# Branch angle slider (0–90, 0.5 increments)
tk.Label(root, text="Branch angle (degrees)").grid(row=0, column=0, sticky="w")
angle_slider = tk.Scale(
    root,
    from_=0,
    to=90,
    orient=tk.HORIZONTAL,
    resolution=0.5,
    length=300
)
angle_slider.set(22.5)
angle_slider.grid(row=0, column=1)

# Step length slider (1–10 integer)
tk.Label(root, text="Step length").grid(row=1, column=0, sticky="w")
step_slider = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL)
step_slider.set(5)
step_slider.grid(row=1, column=1)

# Iterations slider (1–5 integer)
tk.Label(root, text="Iterations").grid(row=2, column=0, sticky="w")
iter_slider = tk.Scale(root, from_=1, to=5, orient=tk.HORIZONTAL)
iter_slider.set(4)
iter_slider.grid(row=2, column=1)

# Base branch thickness (1–20)
tk.Label(root, text="Base thickness").grid(row=3, column=0, sticky="w")
thickness_slider = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL)
thickness_slider.set(8)
thickness_slider.grid(row=3, column=1)

# Shrink factor (0.5–0.95, 0.01 increments)
tk.Label(root, text="Shrink per level").grid(row=4, column=0, sticky="w")
shrink_slider = tk.Scale(
    root,
    from_=0.5,
    to=0.95,
    orient=tk.HORIZONTAL,
    resolution=0.01,
    length=300
)
shrink_slider.set(0.75)
shrink_slider.grid(row=4, column=1)

# Generate button
generate_button = tk.Button(root, text="Generate Tree", command=generate_tree)
generate_button.grid(row=5, column=0, columnspan=2, pady=10)

status_label = tk.Label(root, text="")
status_label.grid(row=6, column=0, columnspan=2)

root.mainloop()
