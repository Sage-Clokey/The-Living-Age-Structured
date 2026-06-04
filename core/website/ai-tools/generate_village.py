#!/usr/bin/env python3
"""
Mycelium Dome Village — top-down community plan.
Multiple dome clusters connected by living network paths.
"""

from PIL import Image, ImageDraw, ImageFilter
import math, os, random, colorsys

random.seed(77)
PHI   = (1 + math.sqrt(5)) / 2
SCALE = 2
OUTPUT = "/mnt/c/Users/SajcS/Desktop/Living works by the word/living_architecture_images/09_dome_village_colony.png"

W, H = 1600*SCALE, 1400*SCALE

# ── Palette ───────────────────────────────────────────────────────────────────
BG          = (8, 18, 8)
GROUND      = (18, 38, 14)
PATH_COL    = (60, 130, 60)
PATH_GLOW   = (30, 90, 30)
WATER_COL   = (20, 60, 90)
WATER_LIGHT = (40, 100, 140)

ZONE_COLORS = {
    "Living":    (180, 120,  60),
    "Gathering": ( 80, 160,  90),
    "Growing":   ( 60, 140,  50),
    "Making":    (140,  90, 160),
    "Healing":   ( 60, 150, 140),
    "Learning":  (180, 150,  50),
}
ZONE_DARK = {k: tuple(int(c*0.55) for c in v) for k, v in ZONE_COLORS.items()}

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ── Village layout ────────────────────────────────────────────────────────────
# 6 clusters arranged in Fibonacci spiral around a central commons
GOLDEN_ANGLE = 2 * math.pi / PHI**2
cx, cy = W//2, H//2

# Central commons cluster
clusters = [
    {"name": "Central Commons", "zone": "Gathering", "n_domes": 7,
     "x": cx, "y": cy, "radius": 95*SCALE, "dome_r": 28*SCALE},
]

# Surrounding clusters
outer_data = [
    ("Living Quarter A",  "Living",    6, 0.54, 310*SCALE, 24*SCALE),
    ("Living Quarter B",  "Living",    5, 0.54, 290*SCALE, 22*SCALE),
    ("The Grove",         "Growing",   8, 0.54, 270*SCALE, 20*SCALE),
    ("Makers Hall",       "Making",    5, 0.54, 300*SCALE, 22*SCALE),
    ("Healing Garden",    "Healing",   6, 0.54, 280*SCALE, 20*SCALE),
    ("Learning Circle",   "Learning",  5, 0.54, 290*SCALE, 22*SCALE),
]

for i, (name, zone, n, frac, dist, dr) in enumerate(outer_data):
    angle = i * GOLDEN_ANGLE + math.pi / 6
    ox = int(cx + dist * math.cos(angle))
    oy = int(cy + dist * math.sin(angle))
    inner_r = int(dr * (n**0.5) * 0.9)
    clusters.append({"name": name, "zone": zone, "n_domes": n,
                      "x": ox, "y": oy, "radius": inner_r, "dome_r": dr})

# ── Build canvas ──────────────────────────────────────────────────────────────
img  = Image.new("RGB", (W, H), BG)
d    = ImageDraw.Draw(img)

# Background — dark forest floor with subtle texture
for y in range(0, H, 4):
    noise = random.randint(-3, 3)
    g = GROUND[1] + noise
    d.line([(0,y),(W,y)], fill=(GROUND[0], max(0,g), GROUND[2]))

# ── Water feature (central stream) ────────────────────────────────────────────
stream_pts = []
for i in range(60):
    t   = i / 59
    sx  = int(W * 0.08 + W * 0.84 * t)
    sy  = int(cy + 200*SCALE * math.sin(t * math.pi * 1.8) + 60*SCALE * math.sin(t * 6))
    stream_pts.append((sx, sy))

# Draw stream (glow + sharp)
for pass_w, pass_col, pass_a in [(18, WATER_LIGHT, 0.3), (8, WATER_COL, 1.0), (3, WATER_LIGHT, 1.0)]:
    for j in range(1, len(stream_pts)):
        d.line([stream_pts[j-1], stream_pts[j]], fill=pass_col, width=pass_w)

# ── Mycelium network paths between clusters ───────────────────────────────────
def bezier_path(p1, p2, ctrl_offset=80*SCALE):
    """Draw an organic curved path between two points."""
    dx, dy = p2[0]-p1[0], p2[1]-p1[1]
    dist   = math.hypot(dx, dy)
    # Perpendicular offset for organic curve
    perp_x = -dy / dist * ctrl_offset * (0.5 + random.random())
    perp_y =  dx / dist * ctrl_offset * (0.5 + random.random())
    mx, my = (p1[0]+p2[0])//2 + int(perp_x), (p1[1]+p2[1])//2 + int(perp_y)
    pts = []
    for k in range(40):
        t  = k / 39
        bx = int((1-t)**2*p1[0] + 2*(1-t)*t*mx + t**2*p2[0])
        by = int((1-t)**2*p1[1] + 2*(1-t)*t*my + t**2*p2[1])
        pts.append((bx, by))
    return pts

# Glow layer for paths
glow_layer = Image.new("RGB", (W, H), (0,0,0))
d_glow     = ImageDraw.Draw(glow_layer)

# Connect all clusters to central commons + nearest neighbour
for i, cl in enumerate(clusters[1:], 1):
    p1 = (clusters[0]["x"], clusters[0]["y"])
    p2 = (cl["x"], cl["y"])
    pts = bezier_path(p1, p2, ctrl_offset=int(60*SCALE*(0.5+random.random())))
    for j in range(1, len(pts)):
        d.line([pts[j-1], pts[j]], fill=PATH_COL, width=4)
        d_glow.line([pts[j-1], pts[j]], fill=(40, 120, 40), width=10)

# Cross-connections (neighbours)
for i in range(1, len(clusters)):
    for j in range(i+1, len(clusters)):
        dist = math.hypot(clusters[i]["x"]-clusters[j]["x"],
                          clusters[i]["y"]-clusters[j]["y"])
        if dist < 380*SCALE:
            p1 = (clusters[i]["x"], clusters[i]["y"])
            p2 = (clusters[j]["x"], clusters[j]["y"])
            pts = bezier_path(p1, p2, ctrl_offset=50*SCALE)
            for k in range(1, len(pts)):
                d.line([pts[k-1], pts[k]], fill=PATH_GLOW, width=2)

# Apply glow
glow_blur = glow_layer.filter(ImageFilter.GaussianBlur(radius=8))
img = Image.blend(img, glow_blur, 0.45)
d   = ImageDraw.Draw(img)

# ── Draw each cluster ─────────────────────────────────────────────────────────
for cl in clusters:
    zone   = cl["zone"]
    fill_c = ZONE_COLORS[zone]
    dark_c = ZONE_DARK[zone]
    dr     = cl["dome_r"]
    n      = cl["n_domes"]
    cx_cl  = cl["x"]
    cy_cl  = cl["y"]

    # Territory circle (soft glow)
    terr_r = cl["radius"] + 20*SCALE
    for ring in range(terr_r, terr_r - 30*SCALE, -3):
        t = (terr_r - ring) / (30*SCALE)
        rc = lerp_color(fill_c, BG, 0.7 + 0.3*t)
        d.ellipse([cx_cl-ring, cy_cl-ring, cx_cl+ring, cy_cl+ring],
                  outline=rc, width=1)

    # Ground fill for cluster territory
    d.ellipse([cx_cl-terr_r, cy_cl-terr_r, cx_cl+terr_r, cy_cl+terr_r],
              fill=lerp_color(GROUND, fill_c, 0.18))

    # Individual domes placed in Fibonacci spiral within cluster
    dome_positions = []
    if n == 1:
        dome_positions = [(cx_cl, cy_cl)]
    else:
        for k in range(n):
            angle_k = k * GOLDEN_ANGLE
            r_k     = cl["radius"] * 0.65 * math.sqrt(k) / math.sqrt(n)
            dome_positions.append((
                int(cx_cl + r_k * math.cos(angle_k)),
                int(cy_cl + r_k * math.sin(angle_k))
            ))

    # Connect domes within cluster (thin threads)
    for k in range(1, len(dome_positions)):
        p1, p2 = dome_positions[k-1], dome_positions[k]
        mx, my = (p1[0]+p2[0])//2, (p1[1]+p2[1])//2
        jx = random.randint(-10, 10)*SCALE
        jy = random.randint(-10, 10)*SCALE
        d.line([p1, (mx+jx, my+jy), p2], fill=lerp_color(fill_c, (20,20,20), 0.5), width=2)

    # Draw each dome
    for k, (dx, dy) in enumerate(dome_positions):
        # Outer ring (root spread)
        root_r = int(dr * 1.5)
        d.ellipse([dx-root_r, dy-root_r, dx+root_r, dy+root_r],
                  fill=lerp_color(dark_c, GROUND, 0.4))
        # Dome body
        d.ellipse([dx-dr, dy-dr, dx+dr, dy+dr], fill=fill_c)
        # Dome shadow
        d.ellipse([dx-dr, dy-dr, dx+dr, dy+dr], outline=dark_c, width=2)
        # Highlight (bioluminescent cap)
        cap_r = dr // 3
        d.ellipse([dx-cap_r, dy-cap_r-dr//4, dx+cap_r, dy+cap_r-dr//4],
                  fill=lerp_color(fill_c, (255,255,255), 0.45))
        # Fibonacci spiral mark on dome
        if dr >= 16*SCALE:
            b_sp  = math.log(PHI) / (math.pi/2)
            a_sp  = dr * 0.08
            sp_pts = []
            for s in range(80):
                theta = s * math.pi/20
                r_s   = a_sp * math.exp(b_sp * theta)
                if r_s > dr * 0.75:
                    break
                sp_pts.append((dx + r_s*math.cos(theta), dy + r_s*math.sin(theta)))
            for s in range(1, len(sp_pts)):
                d.line([sp_pts[s-1], sp_pts[s]], fill=dark_c, width=max(1, SCALE//2))

    # Cluster label
    lbl_y = cy_cl + cl["radius"] + 22*SCALE
    d.text((cx_cl, lbl_y), cl["name"],  fill=fill_c,   anchor="mm")
    d.text((cx_cl, lbl_y + 16*SCALE), f"[{zone}]", fill=lerp_color(fill_c,(40,40,40),0.4), anchor="mm")

# ── Legend ────────────────────────────────────────────────────────────────────
leg_x, leg_y = 28*SCALE, H - 180*SCALE
d.text((leg_x, leg_y - 22*SCALE), "ZONE KEY", fill=(160,220,160), anchor="lm")
for i, (zone, col) in enumerate(ZONE_COLORS.items()):
    y_l = leg_y + i * 22*SCALE
    d.ellipse([leg_x, y_l-7*SCALE, leg_x+14*SCALE, y_l+7*SCALE], fill=col)
    d.text((leg_x + 22*SCALE, y_l), zone, fill=col, anchor="lm")

# ── Compass ───────────────────────────────────────────────────────────────────
comp_cx, comp_cy = W - 70*SCALE, 70*SCALE
comp_r = 40*SCALE
d.ellipse([comp_cx-comp_r, comp_cy-comp_r, comp_cx+comp_r, comp_cy+comp_r],
          fill=(15,35,15), outline=(60,140,60), width=2)
d.line([(comp_cx, comp_cy-comp_r+6*SCALE),(comp_cx, comp_cy+comp_r-6*SCALE)],
       fill=(60,140,60), width=2)
d.line([(comp_cx-comp_r+6*SCALE, comp_cy),(comp_cx+comp_r-6*SCALE, comp_cy)],
       fill=(60,140,60), width=2)
d.text((comp_cx, comp_cy-comp_r-10*SCALE), "N", fill=(120,220,120), anchor="mm")

# ── Scale bar ─────────────────────────────────────────────────────────────────
sb_x1, sb_x2 = 28*SCALE, 228*SCALE
sb_y = H - 45*SCALE
d.line([(sb_x1, sb_y),(sb_x2, sb_y)], fill=(80,160,80), width=3)
d.line([(sb_x1, sb_y-8*SCALE),(sb_x1, sb_y+8*SCALE)], fill=(80,160,80), width=3)
d.line([(sb_x2, sb_y-8*SCALE),(sb_x2, sb_y+8*SCALE)], fill=(80,160,80), width=3)
d.text(((sb_x1+sb_x2)//2, sb_y-14*SCALE), "200 m", fill=(80,160,80), anchor="mm")

# ── Title ─────────────────────────────────────────────────────────────────────
d.text((W//2, 34*SCALE),
       "Mycelium Dome Village — Living Colony Plan",
       fill=(160, 240, 160), anchor="mm")
d.text((W//2, 62*SCALE),
       "Six functional clusters · Fibonacci spiral arrangement · Connected by living mycelium network paths",
       fill=(100, 180, 100), anchor="mm")

# ── Border ────────────────────────────────────────────────────────────────────
bd = 16*SCALE
d.rectangle([bd, bd, W-bd, H-bd], outline=(50,120,50), width=3)
d.rectangle([bd+8, bd+8, W-bd-8, H-bd-8], outline=(30,80,30), width=1)

# ── Save ──────────────────────────────────────────────────────────────────────
out = img.resize((W//SCALE, H//SCALE), Image.LANCZOS)
out.save(OUTPUT)
print(f"Saved: {OUTPUT}")
