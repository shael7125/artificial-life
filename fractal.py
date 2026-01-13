import turtle
import tkinter as tk

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

# ---------- Drawing routine ----------
def draw_lsystem(sequence, angle, step, base_thickness, shrink):
    turtle.reset()
    turtle.speed(0)
    turtle.hideturtle()
    turtle.left(90)
    turtle.penup()
    turtle.goto(0, -300)
    turtle.pendown()

    stack = []

    turtle.tracer(False)

    for char in sequence:
        # set thickness based on depth
        depth = len(stack)
        thickness = max(1, base_thickness * (shrink ** depth))
        turtle.pensize(thickness)

        if char == "F":
            turtle.forward(step)

        elif char == "+":
            turtle.right(angle)

        elif char == "-":
            turtle.left(angle)

        elif char == "[":
            pos = turtle.position()
            heading = turtle.heading()
            stack.append((pos, heading))

        elif char == "]":
            pos, heading = stack.pop()
            turtle.penup()
            turtle.setposition(pos)
            turtle.setheading(heading)
            turtle.pendown()

    turtle.tracer(True)

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

    status_label.config(
        text=f"Generated with angle={angle}, step={step}, iter={iterations}, "
             f"thickness={base_thickness}, shrink={shrink}"
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
