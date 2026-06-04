#!/usr/bin/env python3
"""
Mycelium Dome — 3D living structure.
Projects the 2D mycelium branching network onto a hemisphere.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import random, math, os

random.seed(42)
np.random.seed(42)

OUTPUT = "/mnt/c/Users/SajcS/Desktop/Living works by the word/living_architecture_images/07_mycelium_dome_3d.png"

R = 1.0          # dome radius
PHI_G = (1 + math.sqrt(5)) / 2

# ── 1. Generate 2D branching network inside unit disk ────────────────────────
class Segment:
    def __init__(self, x1, y1, x2, y2, depth):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.depth = depth

class Node:
    def __init__(self, x, y, depth):
        self.x, self.y = x, y
        self.depth = depth

segments = []
nodes    = []

def branch(x, y, angle, length, depth, spread=0.42):
    if depth == 0 or length < 0.012:
        nodes.append(Node(x, y, depth))
        return
    x2 = x + length * math.cos(angle)
    y2 = y + length * math.sin(angle)
    # keep inside unit disk
    r  = math.hypot(x2, y2)
    if r > 0.96:
        x2, y2 = x2 * 0.96/r, y2 * 0.96/r
    segments.append(Segment(x, y, x2, y2, depth))
    jit = (random.random() - 0.5) * 0.28
    branch(x2, y2, angle - spread + jit, length * 0.67, depth - 1, spread * 0.93)
    branch(x2, y2, angle + spread + jit, length * 0.67, depth - 1, spread * 0.93)
    if depth >= 4 and random.random() < 0.38:
        branch(x2, y2, angle + jit*1.6, length * 0.52, depth - 2, spread)

# 6 primary arms from apex
primary_angles = [i * math.pi/3 for i in range(6)]
for pa in primary_angles:
    branch(0, 0, pa, 0.38, depth=8, spread=0.40)

# ── 2. Map (x, y) inside unit disk → point on dome hemisphere ────────────────
# Azimuthal equal-area-like:
#   r_2d ∈ [0,1]  →  polar angle theta ∈ [0, pi/2]
#   phi stays the same

INTERP = 20   # sub-samples per segment for geodesic accuracy

def to_sphere(x, y):
    """2D disk point → 3D hemisphere point."""
    rd  = min(math.hypot(x, y), 1.0)
    phi = math.atan2(y, x)
    # Linear mapping: r=0 → top (theta=0), r=1 → equator (theta=pi/2)
    theta = rd * math.pi / 2
    X = R * math.sin(theta) * math.cos(phi)
    Y = R * math.sin(theta) * math.sin(phi)
    Z = R * math.cos(theta)
    return X, Y, Z

def geodesic_pts(x1, y1, x2, y2, n=INTERP):
    """Sample n+1 points along the dome between two 2D disk positions."""
    pts = []
    for k in range(n + 1):
        t  = k / n
        xi = x1 + (x2 - x1) * t
        yi = y1 + (y2 - y1) * t
        pts.append(to_sphere(xi, yi))
    return pts

# ── 3. Colour helpers ─────────────────────────────────────────────────────────
MAX_DEPTH = 8

def branch_color(depth, alpha_scale=1.0):
    """Gold (shallow) → teal-green (deep tips)."""
    t = depth / MAX_DEPTH
    r = 0.95 - 0.35 * t
    g = 0.60 + 0.35 * t
    b = 0.10 + 0.55 * t
    a = (0.35 + 0.55 * (depth / MAX_DEPTH)) * alpha_scale
    return (r, g, b, a)

def node_color(depth):
    t = 1 - depth / MAX_DEPTH
    r = int(80  + 150*t)
    g = int(200 +  50*t)
    b = int(150 - 100*t)
    return (r/255, g/255, b/255)

# ── 4. Build 3D collections ───────────────────────────────────────────────────
# Segments, grouped by depth for Line3DCollection layers
depth_segs = {d: [] for d in range(MAX_DEPTH + 1)}
for seg in segments:
    pts = geodesic_pts(seg.x1, seg.y1, seg.x2, seg.y2)
    for k in range(len(pts) - 1):
        depth_segs[seg.depth].append([pts[k], pts[k+1]])

# ── 5. Plot ───────────────────────────────────────────────────────────────────
BG = "#050D05"

fig = plt.figure(figsize=(18, 18), facecolor=BG)
ax  = fig.add_subplot(111, projection="3d", computed_zorder=False)
ax.set_facecolor(BG)
ax.patch.set_facecolor(BG)

# ── 5a. Dome mesh (semi-transparent layered surfaces) ────────────────────────
phi_d   = np.linspace(0, 2*np.pi, 120)
theta_d = np.linspace(0, np.pi/2, 60)
Phi, Theta = np.meshgrid(phi_d, theta_d)

Xd = R * np.sin(Theta) * np.cos(Phi)
Yd = R * np.sin(Theta) * np.sin(Phi)
Zd = R * np.cos(Theta)

# Outer shell — very faint organic green
ax.plot_surface(Xd, Yd, Zd,
                facecolor=(0.06, 0.22, 0.10),
                alpha=0.18, linewidth=0, antialiased=True, zorder=1)

# Latitude rings (structural ribs)
for theta_val in np.linspace(0.1, np.pi/2, 7):
    xr = R * np.sin(theta_val) * np.cos(phi_d)
    yr = R * np.sin(theta_val) * np.sin(phi_d)
    zr = np.full_like(phi_d, R * np.cos(theta_val))
    ax.plot(xr, yr, zr, color="#1A4A2A", lw=0.5, alpha=0.35, zorder=2)

# Longitude ribs
for phi_val in np.linspace(0, 2*np.pi, 13):
    xm = R * np.sin(theta_d) * np.cos(phi_val)
    ym = R * np.sin(theta_d) * np.sin(phi_val)
    zm = R * np.cos(theta_d)
    ax.plot(xm, ym, zm, color="#1A4A2A", lw=0.4, alpha=0.25, zorder=2)

# ── 5b. Ground ring ───────────────────────────────────────────────────────────
t_ring = np.linspace(0, 2*np.pi, 300)
ax.plot(np.cos(t_ring), np.sin(t_ring), np.zeros(300),
        color="#52B788", lw=2.5, alpha=0.80, zorder=10)

# Ground disc (very subtle)
r_disc  = np.linspace(0, 1, 30)
phi_disc= np.linspace(0, 2*np.pi, 120)
Rd, Pd  = np.meshgrid(r_disc, phi_disc)
Xgr = Rd * np.cos(Pd)
Ygr = Rd * np.sin(Pd)
Zgr = np.zeros_like(Xgr)
ax.plot_surface(Xgr, Ygr, Zgr, facecolor=(0.06, 0.18, 0.08),
                alpha=0.30, linewidth=0, zorder=0)

# ── 5c. Glow pass — thick blurred lines per depth ────────────────────────────
for depth in range(1, MAX_DEPTH + 1):
    segs = depth_segs[depth]
    if not segs:
        continue
    col  = branch_color(depth, alpha_scale=0.12)
    lc   = Line3DCollection(segs, colors=[col]*len(segs),
                             linewidths=depth * 0.9 + 3, zorder=3)
    ax.add_collection3d(lc)

# ── 5d. Primary branch lines ─────────────────────────────────────────────────
for depth in range(1, MAX_DEPTH + 1):
    segs = depth_segs[depth]
    if not segs:
        continue
    col  = branch_color(depth, alpha_scale=1.0)
    lw   = max(0.4, (depth / MAX_DEPTH) * 2.8)
    lc   = Line3DCollection(segs, colors=[col]*len(segs),
                             linewidths=lw, zorder=4)
    ax.add_collection3d(lc)

# ── 5e. Root system below equator (mirrored, dim) ────────────────────────────
root_segs = []
for seg in segments:
    if seg.depth >= 5:   # only deep branches become roots
        pts = geodesic_pts(seg.x1, seg.y1, seg.x2, seg.y2, n=8)
        for k in range(len(pts)-1):
            p1, p2 = pts[k], pts[k+1]
            # Flip Z, scale outward slightly, drop below ground
            r1 = (p1[0]*1.05, p1[1]*1.05, -abs(p1[2])*0.6)
            r2 = (p2[0]*1.05, p2[1]*1.05, -abs(p2[2])*0.6)
            root_segs.append([r1, r2])

if root_segs:
    root_lc = Line3DCollection(root_segs,
                               colors=[(0.3, 0.6, 0.25, 0.25)]*len(root_segs),
                               linewidths=0.6, zorder=1)
    ax.add_collection3d(root_lc)

# ── 5f. Terminal room nodes ───────────────────────────────────────────────────
room_labels = [
    "Living", "Kitchen", "Study", "Bed 1", "Bed 2", "Dining",
    "Bath", "Garden", "Library", "Studio", "Workshop", "Atrium",
    "Office", "Play", "Pantry",
]

node_scatter_x, node_scatter_y, node_scatter_z = [], [], []
node_colors_list = []
node_sizes  = []

for i, nd in enumerate(nodes):
    X3, Y3, Z3 = to_sphere(nd.x, nd.y)
    node_scatter_x.append(X3)
    node_scatter_y.append(Y3)
    node_scatter_z.append(Z3)
    node_colors_list.append(node_color(nd.depth))
    node_sizes.append(max(12, 60 * (1 - nd.depth/MAX_DEPTH)**1.5))

ax.scatter(node_scatter_x, node_scatter_y, node_scatter_z,
           c=node_colors_list, s=node_sizes, alpha=0.95,
           edgecolors=(1,1,1,0.3), linewidths=0.5, zorder=8)

# Label a selection of terminal nodes
labeled = 0
for i, nd in enumerate(nodes):
    if nd.depth == 0 and labeled < len(room_labels):
        X3, Y3, Z3 = to_sphere(nd.x, nd.y)
        label = room_labels[labeled]
        ax.text(X3*1.07, Y3*1.07, Z3*1.04, label,
                fontsize=7, color="#A0EFC0", ha="center", va="center",
                fontfamily="monospace", alpha=0.85, zorder=9)
        labeled += 1

# ── 5g. Apex node ─────────────────────────────────────────────────────────────
ax.scatter([0], [0], [R], c=["#DFFFEF"], s=220, zorder=12,
           edgecolors=["#80FFB0"], linewidths=2)
ax.text(0, 0, R + 0.07, "APEX\n(Core)", color="#DFFFEF", fontsize=9,
        ha="center", va="bottom", fontweight="bold", fontfamily="monospace")

# ── 5h. Scale bar & compass at base ──────────────────────────────────────────
ax.plot([-1.0, -0.5], [-1.15, -1.15], [0, 0], color="#52B788", lw=2)
ax.text(-0.75, -1.22, 0, "50 m", color="#52B788", fontsize=9,
        ha="center", va="top", fontfamily="monospace")

# ── 6. Axes & camera ─────────────────────────────────────────────────────────
ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-1.3, 1.3)
ax.set_zlim(-0.5, 1.5)
ax.set_box_aspect([1, 1, 1])
ax.set_axis_off()

# Camera
ax.view_init(elev=22, azim=-52)
ax.dist = 7.5

# ── 7. Lighting simulation — overlay a radial gradient ───────────────────────
# (Fake ambient occlusion: darken edges via a PNG overlay drawn on the axes)

# ── 8. Title & annotation ────────────────────────────────────────────────────
fig.text(0.50, 0.94,
         "Mycelium Dome  —  3D Living Architecture",
         ha="center", va="center",
         color="#90EF90", fontsize=26, fontweight="bold", fontfamily="monospace")

fig.text(0.50, 0.895,
         "Branching networks grow along the dome surface · Terminal nodes are rooms · Roots anchor below grade",
         ha="center", va="center",
         color="#5ABF7A", fontsize=12, fontfamily="monospace")

fig.text(0.50, 0.055,
         '"Life is not a block you carve into shape; it is a spiral you cultivate."'
         '  —  Bioinformatics as Stewardship of Living Order',
         ha="center", va="center",
         color="#3A8A4A", fontsize=10, fontstyle="italic", fontfamily="monospace")

# ── 9. Save ───────────────────────────────────────────────────────────────────
plt.savefig(OUTPUT, dpi=220, facecolor=BG, bbox_inches="tight",
            pad_inches=0.2)
plt.close()
print(f"Saved: {OUTPUT}")
