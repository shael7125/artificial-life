# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

# # -----------------------
# # Simulation parameters
# # -----------------------
# N = 120                 # number of T cells
# L = 10.0                # domain size
# dt = 0.05
# steps = 600

# perception_radius = 1.0
# separation_radius = 0.3

# max_speed = 2.0

# # Boids weights
# w_sep = 1.5
# w_align = 0.4
# w_coh = 0.2
# w_chem = 1.2
# w_noise = 0.3

# # Infection site (chemokine source)
# infection_site = np.array([5.0, 5.0])

# # -----------------------
# # Initialization
# # -----------------------
# pos = np.random.rand(N, 2) * L
# vel = (np.random.rand(N, 2) - 0.5)

# # -----------------------
# # Helper functions
# # -----------------------
# def limit_speed(v, max_speed):
#     speed = np.linalg.norm(v)
#     if speed > max_speed:
#         return v / speed * max_speed
#     return v

# def chemokine_force(p):
#     direction = infection_site - p
#     dist = np.linalg.norm(direction) + 1e-6
#     return direction / dist

# # -----------------------
# # Update rule
# # -----------------------
# def update():
#     global pos, vel

#     new_vel = np.zeros_like(vel)

#     for i in range(N):
#         diff = pos - pos[i]
#         dist = np.linalg.norm(diff, axis=1)

#         neighbors = (dist > 0) & (dist < perception_radius)
#         close = (dist > 0) & (dist < separation_radius)

#         v = vel[i]

#         # Separation (contact inhibition)
#         if np.any(close):
#             sep = -np.sum(diff[close] / (dist[close][:, None] + 1e-6), axis=0)
#         else:
#             sep = np.zeros(2)

#         # Alignment
#         if np.any(neighbors):
#             align = np.mean(vel[neighbors], axis=0) - v
#         else:
#             align = np.zeros(2)

#         # Cohesion
#         if np.any(neighbors):
#             coh = np.mean(pos[neighbors], axis=0) - pos[i]
#         else:
#             coh = np.zeros(2)

#         # Chemotaxis
#         chem = chemokine_force(pos[i])

#         # Random motility
#         noise = np.random.randn(2)

#         # Combine forces
#         v_new = (
#             v
#             + w_sep * sep
#             + w_align * align
#             + w_coh * coh
#             + w_chem * chem
#             + w_noise * noise
#         )

#         new_vel[i] = limit_speed(v_new, max_speed)

#     vel = new_vel
#     pos += vel * dt

#     # Periodic boundaries (tissue-like domain)
#     pos %= L

# # -----------------------
# # Animation
# # -----------------------
# fig, ax = plt.subplots(figsize=(6, 6))
# scat = ax.scatter(pos[:, 0], pos[:, 1], s=20, c="green", alpha=0.8)
# ax.scatter(*infection_site, c="red", s=100, marker="x", label="Infection")
# ax.set_xlim(0, L)
# ax.set_ylim(0, L)
# ax.set_title("T-cell–like Collective Migration")
# ax.legend()

# def animate(frame):
#     update()
#     scat.set_offsets(pos)
#     return scat,

# ani = FuncAnimation(fig, animate, frames=steps, interval=30)
# plt.show()

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -----------------------
# Simulation parameters
# -----------------------
N = 120
L = 10.0
dt = 0.05
steps = 800

perception_radius = 1.0
separation_radius = 0.3
max_speed = 2.0

# Boids weights
w_sep = 1.5
w_align = 0.4
w_coh = 0.2
w_chem = 1.2
w_noise = 0.3

# -----------------------
# Chemokine dynamics
# -----------------------
chem_on = False
chem_level = 0.0
chem_rise = 0.05
chem_decay = 0.02

# Infection site (starts centered)
infection_site = np.array([L / 2, L / 2])

# Timing (frames)
chem_on_frames = [100, 450]   # when chemokine turns on
chem_off_frames = [300, 650]  # when chemokine turns off

# -----------------------
# Initialization
# -----------------------
pos = np.random.rand(N, 2) * L
vel = (np.random.rand(N, 2) - 0.5)

# -----------------------
# Helper functions
# -----------------------
def limit_speed(v):
    speed = np.linalg.norm(v)
    if speed > max_speed:
        return v / speed * max_speed
    return v

def chemokine_force(p):
    direction = infection_site - p
    dist = np.linalg.norm(direction) + 1e-6
    return direction / dist

def update_chemokine(frame):
    global chem_on, chem_level, infection_site

    # Turn chemokine ON
    if frame in chem_on_frames:
        chem_on = True
        # First time: center; later times: random
        if frame != chem_on_frames[0]:
            infection_site = np.random.rand(2) * L

    # Turn chemokine OFF
    if frame in chem_off_frames:
        chem_on = False

    # Smooth rise / decay
    if chem_on:
        chem_level += chem_rise * (1.0 - chem_level)
    else:
        chem_level -= chem_decay * chem_level

    chem_level = np.clip(chem_level, 0.0, 1.0)

# -----------------------
# Boids update
# -----------------------
def update():
    global pos, vel

    new_vel = np.zeros_like(vel)

    for i in range(N):
        diff = pos - pos[i]
        dist = np.linalg.norm(diff, axis=1)

        neighbors = (dist > 0) & (dist < perception_radius)
        close = (dist > 0) & (dist < separation_radius)

        # Separation
        sep = np.zeros(2)
        if np.any(close):
            sep = -np.sum(
                diff[close] / (dist[close][:, None] + 1e-6),
                axis=0
            )

        # Alignment
        align = np.zeros(2)
        if np.any(neighbors):
            align = np.mean(vel[neighbors], axis=0) - vel[i]

        # Cohesion
        coh = np.zeros(2)
        if np.any(neighbors):
            coh = np.mean(pos[neighbors], axis=0) - pos[i]

        # Chemotaxis (scaled dynamically)
        chem = chem_level * chemokine_force(pos[i])

        # Noise
        noise = np.random.randn(2)

        v_new = (
            vel[i]
            + w_sep * sep
            + w_align * align
            + w_coh * coh
            + w_chem * chem
            + w_noise * noise
        )

        new_vel[i] = limit_speed(v_new)

    vel = new_vel
    pos += vel * dt
    pos %= L  # periodic boundaries

# -----------------------
# Animation
# -----------------------
fig, ax = plt.subplots(figsize=(6, 6))
scat = ax.scatter(pos[:, 0], pos[:, 1], s=20, c="green", alpha=0.8)
site = ax.scatter(*infection_site, c="red", s=120, marker="x")

ax.set_xlim(0, L)
ax.set_ylim(0, L)
ax.set_title("T-cell Boids with Dynamic Chemokine")

def animate(frame):
    update_chemokine(frame)
    update()

    scat.set_offsets(pos)
    site.set_offsets(infection_site)

    ax.set_title(
        f"T-cell Migration | Chemokine = {chem_level:.2f}"
    )

    return scat, site

ani = FuncAnimation(fig, animate, frames=steps, interval=30)
plt.show()
