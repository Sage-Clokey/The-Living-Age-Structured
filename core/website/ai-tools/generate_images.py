#!/usr/bin/env python3
"""Generate 5 living architecture images using Pillow procedural art."""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os, random, colorsys

random.seed(42)

PHI   = (1 + math.sqrt(5)) / 2
OUTDIR = "/mnt/c/Users/SajcS/Desktop/Living works by the word/living_architecture_images"
os.makedirs(OUTDIR, exist_ok=True)
SCALE = 2   # 2× supersampling for anti-aliasing

def save(img, fname):
    p = os.path.join(OUTDIR, fname)
    img.save(p, quality=95)
    print(f"  ✓  {fname}")

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def gradient_rect(draw, x1, y1, x2, y2, c1, c2, vertical=True):
    steps = int(y2-y1) if vertical else int(x2-x1)
    for i in range(steps):
        t = i / max(steps, 1)
        c = lerp_color(c1, c2, t)
        if vertical:
            draw.line([(x1, y1+i), (x2, y1+i)], fill=c)
        else:
            draw.line([(x1+i, y1), (x1+i, y2)], fill=c)

def aa_img(img):
    W, H = img.size
    return img.resize((W//SCALE, H//SCALE), Image.LANCZOS)

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE 1 — Fibonacci Spiral House (floor plan)
# ══════════════════════════════════════════════════════════════════════════════
def image1():
    W, H = 1400*SCALE, 1000*SCALE
    img = Image.new("RGB", (W, H), "#F5ECD7")
    d   = ImageDraw.Draw(img)

    # parchment texture — faint horizontal bands
    for y in range(0, H, 3*SCALE):
        lum = 242 + random.randint(-3,3)
        d.line([(0,y),(W,y)], fill=(lum, int(lum*0.94), int(lum*0.82)), width=2)

    margin   = 80  * SCALE
    title_h  = 70  * SCALE
    aw, ah   = W - 2*margin, H - 2*margin - title_h

    # Fibonacci tiling of a 55 × 34 grid  (verified: 1870 = 55×34 ✓)
    # Squares: 34,21,13,8,5,3,2,1,1  (areas sum to 1870)
    rooms = [
        #  fx   fy   fw  fh   label              fill
        (  0,   0,  34, 34, "Living Room",   "#C8916B"),
        ( 34,   0,  21, 21, "Garden Studio", "#7B9E6A"),
        ( 42,  21,  13, 13, "Dining Room",   "#D4A96A"),
        ( 34,  26,   8,  8, "Master Bed",    "#9B856E"),
        ( 34,  21,   5,  5, "Kitchen",       "#8FA86A"),
        ( 39,  21,   3,  3, "Study",         "#B09565"),
        ( 40,  24,   2,  2, "Bathroom",      "#6A8A7B"),
        ( 39,  24,   1,  1, "Entry",         "#C4A070"),
        ( 39,  25,   1,  1, "Hall",          "#A07850"),
    ]

    unit = min(aw/55, ah/34)
    ox   = margin + (aw - 55*unit) / 2
    oy   = margin + title_h + (ah - 34*unit) / 2

    def px(fx, fy):
        return (ox + fx*unit, oy + fy*unit)

    def rbox(fx, fy, fw, fh):
        x1, y1 = px(fx, fy)
        return [x1, y1, x1+fw*unit, y1+fh*unit]

    # Draw rooms
    for (fx, fy, fw, fh, lbl, col) in rooms:
        b = rbox(fx, fy, fw, fh)
        d.rectangle(b, fill=col)
        # Subtle inner shadow
        sw = max(2, int(unit/20))
        d.rectangle(b, outline="#2D1A0E", width=sw)
        if fw >= 8 and fh >= 8:
            cx = (b[0]+b[2])/2
            cy = (b[1]+b[3])/2
            d.text((cx, cy), lbl, fill="#1A0E06", anchor="mm")
        elif fw >= 3 and fh >= 3:
            cx = (b[0]+b[2])/2
            cy = (b[1]+b[3])/2
            d.text((cx, cy), lbl, fill="#1A0E06", anchor="mm")

    # Golden spiral — logarithmic spiral centred at convergence point
    # Convergence point of this Fibonacci tiling: ≈ (39.8, 24.8) in fib units
    cx_f, cy_f = 39.8, 24.8
    cx_s, cy_s = ox + cx_f*unit, oy + cy_f*unit

    b_sp  = math.log(PHI) / (math.pi/2)   # growth constant
    a_sp  = 34*unit / math.exp(b_sp * 2.5*math.pi)  # scaled so max r≈34 units

    pts = []
    steps = 3000
    for i in range(steps):
        theta = -0.5*math.pi + (i/steps)*5.5*math.pi
        r = a_sp * math.exp(b_sp * theta)
        pts.append((cx_s + r*math.cos(theta+math.pi),
                    cy_s + r*math.sin(theta+math.pi)))

    sw = max(4, int(unit/6))
    col_sp = "#1B4332"
    for i in range(1, len(pts)):
        p1, p2 = pts[i-1], pts[i]
        if all(0 <= v <= W or 0 <= v <= H for v in [p1[0],p2[0],p1[1],p2[1]]):
            d.line([p1, p2], fill=col_sp, width=sw)

    # Title
    d.text((W/2, margin/2),        "The Fibonacci House — Living Floor Plan",
           fill="#1B4332", anchor="mm")
    d.text((W/2, margin/2+36*SCALE),
           "Rooms follow the Golden Ratio · Every space spirals from the living heart",
           fill="#5A7A4A", anchor="mm")

    # Decorative double-border
    bd = 18*SCALE
    d.rectangle([bd,   bd,   W-bd,   H-bd  ], outline="#2D6A4F", width=4)
    d.rectangle([bd+9, bd+9, W-bd-9, H-bd-9], outline="#52B788", width=2)

    return aa_img(img)

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE 2 — Mycelium Network Floor Plan  (dark, glowing)
# ══════════════════════════════════════════════════════════════════════════════
def image2():
    W, H = 1200*SCALE, 1200*SCALE
    # Build two layers: sharp lines + glow
    base  = Image.new("RGB", (W, H), "#060C06")
    glow  = Image.new("RGB", (W, H), "#000000")
    d_base = ImageDraw.Draw(base)
    d_glow = ImageDraw.Draw(glow)

    # Subtle radial vignette background
    cx, cy = W//2, H//2
    for rad in range(max(W,H)//2, 0, -2*SCALE):
        t = rad / (max(W,H)/2)
        c = lerp_color((6,18,6), (0,5,0), 1-t)
        d_base.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=c)

    GOLD_BRIGHT = (255, 210, 90)
    GOLD_DIM    = (160, 120, 40)
    GREEN_GLOW  = (80, 200, 100)
    TEAL_NODE   = (60, 180, 150)

    # Recursive branching function
    def branch(draw_b, draw_g, x, y, angle, length, depth, spread=0.45):
        if depth == 0 or length < 4*SCALE:
            # Terminal node — room blob
            r_node = int(length * 0.8)
            col = TEAL_NODE if depth == 0 else GOLD_BRIGHT
            draw_b.ellipse([x-r_node, y-r_node, x+r_node, y+r_node], fill=col)
            draw_g.ellipse([x-r_node*2, y-r_node*2, x+r_node*2, y+r_node*2],
                           fill=(40, 120, 90))
            return
        x2 = x + length * math.cos(angle)
        y2 = y + length * math.sin(angle)
        w = max(1, int(depth * SCALE * 0.7))
        draw_b.line([(x, y), (x2, y2)], fill=GOLD_BRIGHT, width=w)
        draw_g.line([(x, y), (x2, y2)], fill=GOLD_DIM,    width=w+2*SCALE)
        jitter = (random.random() - 0.5) * 0.3
        branch(draw_b, draw_g, x2, y2,
               angle - spread + jitter,
               length * 0.68, depth-1, spread * 0.92)
        branch(draw_b, draw_g, x2, y2,
               angle + spread + jitter,
               length * 0.68, depth-1, spread * 0.92)
        # Occasional third branch
        if depth >= 3 and random.random() < 0.4:
            branch(draw_b, draw_g, x2, y2,
                   angle + jitter * 2,
                   length * 0.55, depth-2, spread)

    # Grow 6 trees from a central node
    central_x, central_y = W//2, H//2
    angles = [i * math.pi/3 - math.pi/6 for i in range(6)]
    for ang in angles:
        branch(d_base, d_glow, central_x, central_y,
               ang, 200*SCALE, depth=7, spread=0.38)

    # Central node
    d_base.ellipse([cx-20*SCALE, cy-20*SCALE, cx+20*SCALE, cy+20*SCALE],
                   fill=(200, 240, 180))
    d_glow.ellipse([cx-35*SCALE, cy-35*SCALE, cx+35*SCALE, cy+35*SCALE],
                   fill=(100, 200, 100))

    # Apply glow
    glow_blur = glow.filter(ImageFilter.GaussianBlur(radius=8*SCALE))
    base = Image.blend(base, glow_blur, 0.55)

    # Second sharp pass
    d2 = ImageDraw.Draw(base)
    for ang in angles:
        branch(d2, ImageDraw.Draw(Image.new("RGB",(1,1))), central_x, central_y,
               ang, 200*SCALE, depth=7, spread=0.38)
    d2.ellipse([cx-18*SCALE, cy-18*SCALE, cx+18*SCALE, cy+18*SCALE],
               fill=(210, 255, 190))

    # Title
    d2.text((W/2, 40*SCALE),
            "Mycelium Network — Living Floor Plan",
            fill=(180, 240, 160), anchor="mm")
    d2.text((W/2, 80*SCALE),
            "Rooms grow as terminal nodes of an organic network · No dead corridors",
            fill=(120, 180, 110), anchor="mm")

    # Border
    d2.rectangle([15*SCALE, 15*SCALE, W-15*SCALE, H-15*SCALE],
                 outline=(50, 120, 50), width=3)

    return aa_img(base)

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE 3 — Living Facade  (building elevation with organic growth)
# ══════════════════════════════════════════════════════════════════════════════
def image3():
    W, H = 1000*SCALE, 1400*SCALE
    img = Image.new("RGB", (W, H), "#D0E8F5")
    d   = ImageDraw.Draw(img)

    # Sky gradient
    sky_top = hex2rgb("#7EC8E3")
    sky_bot = hex2rgb("#D0E8F5")
    gradient_rect(d, 0, 0, W, H//2, sky_top, sky_bot)

    # Ground
    ground_top = hex2rgb("#4A7A3A")
    ground_bot = hex2rgb("#2D4A1A")
    gradient_rect(d, 0, H-120*SCALE, W, H, ground_top, ground_bot)

    # Building silhouette — organic, slightly curved
    bx1, bx2 = int(W*0.10), int(W*0.90)
    by_top, by_bot = int(H*0.10), int(H-110*SCALE)
    bw = bx2 - bx1

    # Curved top arch (arched roofline)
    def arch_pts(x1, x2, y_base, sag):
        pts = []
        for i in range(100):
            t  = i/99
            x  = x1 + (x2-x1)*t
            dy = sag * math.sin(t * math.pi)
            pts.append((x, y_base - dy))
        return pts

    # Draw facade body
    facade_col = hex2rgb("#C8B08A")
    facade_shad= hex2rgb("#A08860")
    gradient_rect(d, bx1, by_top, bx2, by_bot, facade_shad, facade_col, vertical=False)

    # Arched roof
    roof_arch = arch_pts(bx1, bx2, by_top, 80*SCALE)
    roof_poly  = [(bx1, by_top)] + roof_arch + [(bx2, by_top)]
    d.polygon(roof_poly, fill="#7B9E6A")

    # Floor lines (slightly wavy)
    floors = 6
    for i in range(1, floors):
        fy = by_top + (by_bot - by_top) * i // floors
        pts_f = []
        for x in range(bx1, bx2, 3*SCALE):
            wave = int(2*SCALE * math.sin((x - bx1)*0.02 + i))
            pts_f.append((x, fy + wave))
        for j in range(1, len(pts_f)):
            d.line([pts_f[j-1], pts_f[j]], fill=(80,60,40), width=2)

    # Organic cell-like windows (ellipses, golden-ratio proportions)
    WIN_FILL   = hex2rgb("#8BCCE0")
    WIN_BORDER = hex2rgb("#2D5A70")
    WIN_GLARE  = hex2rgb("#DDEFFF")

    win_w = int(bw / 5.5)
    win_h = int(win_w * PHI)

    for col_i, wx in enumerate([bx1 + int(bw*0.12),
                                  bx1 + int(bw*0.32),
                                  bx1 + int(bw*0.52),
                                  bx1 + int(bw*0.72),
                                  bx1 + int(bw*0.89)]):
        for row_i in range(1, floors):
            wy = by_top + (by_bot - by_top)*row_i//floors - int(win_h*0.6)
            # Slight organic offset
            off_x = int(8*SCALE*math.sin(col_i*1.3 + row_i*2.1))
            off_y = int(5*SCALE*math.cos(col_i*2.7 + row_i*1.4))
            wx_ = wx + off_x
            wy_ = wy + off_y
            # Leafy arch top
            ww2, wh2 = win_w//2, win_h//2
            # Outer arch (pointed top, organic)
            arch_h = int(wh2 * 0.35)
            d.ellipse([wx_-ww2, wy_, wx_+ww2, wy_+win_h], fill=WIN_FILL)
            d.ellipse([wx_-ww2, wy_-arch_h, wx_+ww2, wy_+arch_h], fill=WIN_FILL)
            d.ellipse([wx_-ww2, wy_, wx_+ww2, wy_+win_h], outline=WIN_BORDER, width=2)
            d.ellipse([wx_-ww2, wy_-arch_h, wx_+ww2, wy_+arch_h], outline=WIN_BORDER, width=2)
            # Glare
            gx = wx_ - ww2//3
            gy = wy_ + 4*SCALE
            d.ellipse([gx, gy, gx+ww2//2, gy+wh2//3], fill=WIN_GLARE)

    # Vine / root growth along sides
    def draw_vine(draw, x_start, y_start, angle_start, steps, vigor=1.0):
        x, y = float(x_start), float(y_start)
        angle = angle_start
        for _ in range(steps):
            angle += (random.random()-0.4)*0.4
            length = random.uniform(12, 28) * SCALE * vigor
            x2 = x + length * math.cos(angle)
            y2 = y + length * math.sin(angle)
            green = (random.randint(40,80), random.randint(100,160), random.randint(30,70))
            w = max(1, int(2*SCALE*vigor))
            draw.line([(x,y),(x2,y2)], fill=green, width=w)
            # Occasional leaf (small ellipse)
            if random.random() < 0.35:
                lx, ly = int((x+x2)/2), int((y+y2)/2)
                lr = int(8*SCALE*vigor*random.uniform(0.5,1.2))
                lc = (random.randint(50,100), random.randint(140,200), random.randint(40,80))
                draw.ellipse([lx-lr, ly-int(lr*1.6), lx+lr, ly+int(lr*1.6)], fill=lc)
            x, y = x2, y2
            vigor *= 0.97

    random.seed(7)
    for i in range(8):
        draw_vine(d, bx1, by_bot - i*60*SCALE, -math.pi/5 + random.uniform(-0.3,0.3),
                  30, vigor=0.9)
        draw_vine(d, bx2, by_bot - i*60*SCALE, -3*math.pi/5 + random.uniform(-0.3,0.3),
                  30, vigor=0.9)
    # Rooftop greenery
    for i in range(12):
        tx = bx1 + random.randint(50, bw-50)*SCALE//SCALE
        ty = int(by_top - 60*SCALE)
        draw_vine(d, tx, ty, -math.pi/2 + random.uniform(-0.5,0.5), 15, vigor=0.7)

    # Building outline
    d.rectangle([bx1, by_top, bx2, by_bot], outline=(80, 55, 30), width=3)

    # Title
    d.text((W//2, 35*SCALE),
           "The Living Facade",
           fill=(30, 70, 40), anchor="mm")
    d.text((W//2, 68*SCALE),
           "Organic windows · Root networks · Breathing walls",
           fill=(50, 100, 60), anchor="mm")

    bd = 18*SCALE
    d.rectangle([bd, bd, W-bd, H-bd], outline=(40,100,50), width=3)
    d.rectangle([bd+8, bd+8, W-bd-8, H-bd-8], outline=(80,160,90), width=1)

    return aa_img(img)

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE 4 — Branching Tree Structure  (building elevation, structural)
# ══════════════════════════════════════════════════════════════════════════════
def image4():
    W, H = 1100*SCALE, 1400*SCALE
    img = Image.new("RGB", (W, H), "#F0EDE6")
    d   = ImageDraw.Draw(img)

    # Blueprint-style crosshatch background
    for y in range(0, H, 16*SCALE):
        d.line([(0,y),(W,y)], fill=(220,215,205), width=1)
    for x in range(0, W, 16*SCALE):
        d.line([(x,0),(x,H)], fill=(220,215,205), width=1)

    ground_y = H - 120*SCALE

    # Ground strip
    gradient_rect(d, 0, ground_y, W, H,
                  hex2rgb("#5A7A3A"), hex2rgb("#3A5A20"))

    # Floor plates
    floors_y = [ground_y - int((H-200*SCALE) * i / 6) for i in range(7)]
    for fy in floors_y:
        plate_pts = []
        for x in range(int(W*0.08), int(W*0.92), 2*SCALE):
            wave = int(3*SCALE * math.sin(x * 0.003))
            plate_pts.append((x, fy + wave))
        for i in range(1, len(plate_pts)):
            d.line([plate_pts[i-1], plate_pts[i]], fill=(90, 70, 50), width=4)
            d.line([plate_pts[i-1], (plate_pts[i-1][0], plate_pts[i-1][1]+2*SCALE)],
                   fill=(60,45,30), width=4)

    # Recursive tree column
    def tree_col(draw, x, y_base, height, depth, angle=math.pi/2, width_fac=1.0):
        if depth == 0 or height < 8*SCALE:
            # Canopy blob
            r = int(height * 0.9)
            shade = (random.randint(40,70), random.randint(100,150), random.randint(30,60))
            draw.ellipse([x-r, y_base-r, x+r, y_base+r], fill=shade)
            return
        x2 = int(x + height * math.cos(angle))
        y2 = int(y_base - height * math.sin(angle))
        w  = max(1, int(depth * SCALE * 1.4 * width_fac))
        # Gradient wood tone
        bark1 = (int(80*width_fac), int(50*width_fac), int(25*width_fac))
        bark2 = (int(100*width_fac), int(65*width_fac), int(30*width_fac))
        for seg in range(8):
            t  = seg / 7
            sx = int(x  + (x2 -x )*t)
            sy = int(y_base + (y2-y_base)*t)
            sx2= int(x  + (x2 -x )*(t+1/7))
            sy2= int(y_base + (y2-y_base)*(t+1/7))
            cc = lerp_color(bark1, bark2, t)
            draw.line([(sx,sy),(sx2,sy2)], fill=cc, width=w)

        spread = 0.52 if depth > 2 else 0.38
        jit = (random.random()-0.5)*0.15
        tree_col(draw, x2, y2, height*0.62, depth-1,
                 angle - spread + jit, width_fac*0.75)
        tree_col(draw, x2, y2, height*0.62, depth-1,
                 angle + spread + jit, width_fac*0.75)
        if depth >= 3 and random.random() < 0.5:
            tree_col(draw, x2, y2, height*0.45, depth-2,
                     angle + jit*2, width_fac*0.6)

    random.seed(12)
    column_xs = [int(W*f) for f in [0.15, 0.35, 0.50, 0.65, 0.85]]
    col_h = int((ground_y - floors_y[-1]) * 0.72)

    for cx in column_xs:
        tree_col(d, cx, ground_y, col_h, depth=7, angle=math.pi/2)

    # Horizontal structural cables connecting trees (catenary curves)
    for i in range(1, len(column_xs)):
        x1, x2 = column_xs[i-1], column_xs[i]
        for fy in floors_y[1:]:
            cat_pts = []
            for seg in range(40):
                t = seg/39
                x  = x1 + (x2-x1)*t
                sag = int(20*SCALE * math.sin(t * math.pi))
                cat_pts.append((int(x), fy + sag))
            for j in range(1, len(cat_pts)):
                d.line([cat_pts[j-1], cat_pts[j]], fill=(100,80,60), width=2)

    # Roots at base
    random.seed(99)
    for cx in column_xs:
        for _ in range(5):
            angle = math.pi + random.uniform(-0.6, 0.6)
            rx, ry = float(cx), float(ground_y)
            for _ in range(20):
                angle += random.uniform(-0.15, 0.15)
                length = random.uniform(8, 18)*SCALE
                rx2 = rx + length * math.cos(angle)
                ry2 = ry + length * abs(math.sin(angle)) * 0.5  # mostly sideways
                ry2 = min(ry2, ground_y + 40*SCALE)
                w   = max(1, random.randint(1,3))
                d.line([(rx,ry),(rx2,ry2)], fill=(90,60,30), width=w)
                rx, ry = rx2, ry2

    # Title
    d.text((W//2, 30*SCALE),
           "Branching Tree Structure — Living Elevation",
           fill=(40, 80, 40), anchor="mm")
    d.text((W//2, 62*SCALE),
           "Columns branch like trees · Roots anchor like forests · No dead steel",
           fill=(70, 110, 60), anchor="mm")

    # Labels
    for i, fy in enumerate(floors_y[1:], 1):
        d.text((18*SCALE, fy), f"Floor {i}", fill=(80,60,40), anchor="lm")

    bd = 18*SCALE
    d.rectangle([bd, bd, W-bd, H-bd], outline=(60,100,50), width=3)
    d.rectangle([bd+8, bd+8, W-bd-8, H-bd-8], outline=(100,160,80), width=1)

    return aa_img(img)

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE 5 — Sunflower / Fibonacci Spiral Room Arrangement  (top view)
# ══════════════════════════════════════════════════════════════════════════════
def image5():
    W, H = 1200*SCALE, 1200*SCALE
    img = Image.new("RGB", (W, H), "#F7F3EA")
    d   = ImageDraw.Draw(img)

    # Subtle concentric ring guides
    cx, cy = W//2, H//2
    for r_guide in range(50*SCALE, 560*SCALE, 50*SCALE):
        d.ellipse([cx-r_guide, cy-r_guide, cx+r_guide, cy+r_guide],
                  outline=(220,210,195), width=1)

    GOLDEN_ANGLE = 2 * math.pi / (PHI**2)   # ≈ 137.508°

    room_names = [
        "Living", "Kitchen", "Master Bed", "Garden", "Study", "Dining",
        "Bath 1", "Bed 2", "Library", "Workshop", "Pantry", "Studio",
        "Bath 2", "Bed 3", "Atrium", "Garage", "Gym", "Play Room",
        "Office", "Laundry", "Bed 4", "Storage",
    ]

    hues = [0.08, 0.28, 0.55, 0.38, 0.12, 0.45, 0.60, 0.20, 0.50, 0.33,
            0.15, 0.65, 0.70, 0.40, 0.25, 0.05, 0.48, 0.58, 0.18, 0.62,
            0.35, 0.10]

    N = len(room_names)
    room_scale = 500*SCALE  # controls how spread out the rooms are

    connections = []   # (i, j) pairs for corridors

    room_positions = []
    for n in range(N):
        theta  = n * GOLDEN_ANGLE
        radius = room_scale * math.sqrt(n + 0.5) / math.sqrt(N)
        rx = int(cx + radius * math.cos(theta))
        ry = int(cy + radius * math.sin(theta))
        room_positions.append((rx, ry))

    # Draw connection paths first (behind rooms)
    # Connect each room to its nearest neighbours (simple nearest-N)
    for i, (rx, ry) in enumerate(room_positions):
        # Connect to 2–3 nearest
        dists = [(math.hypot(rx-room_positions[j][0], ry-room_positions[j][1]), j)
                 for j in range(N) if j != i]
        dists.sort()
        for _, j in dists[:2]:
            p1 = room_positions[i]
            p2 = room_positions[j]
            # Organic curved path: midpoint with perpendicular offset
            mx = (p1[0]+p2[0])//2
            my = (p1[1]+p2[1])//2
            perp_x = -(p2[1]-p1[1])//8
            perp_y =  (p2[0]-p1[0])//8
            pts_path = []
            for seg in range(20):
                t  = seg/19
                t2 = t*t
                bx = int((1-t)**2 * p1[0] + 2*(1-t)*t*(mx+perp_x) + t2*p2[0])
                by = int((1-t)**2 * p1[1] + 2*(1-t)*t*(my+perp_y) + t2*p2[1])
                pts_path.append((bx, by))
            for k in range(1, len(pts_path)):
                d.line([pts_path[k-1], pts_path[k]], fill=(180,160,130), width=2*SCALE)

    # Draw rooms as organic ellipses
    for n, (rx, ry) in enumerate(room_positions):
        r_room = int(room_scale * 0.13 * (0.7 + 0.5 * (n%5)/5))
        h_room, s_room, v_room = hues[n % len(hues)], 0.35, 0.85
        rgb = tuple(int(c*255) for c in colorsys.hsv_to_rgb(h_room, s_room, v_room))
        border = tuple(int(c*0.65) for c in rgb)

        # Slight squish to make it feel organic
        wr = int(r_room * (1 + 0.2*math.sin(n*1.7)))
        hr = int(r_room * (1 + 0.2*math.cos(n*2.3)))
        d.ellipse([rx-wr, ry-hr, rx+wr, ry+hr], fill=rgb)
        d.ellipse([rx-wr, ry-hr, rx+wr, ry+hr], outline=border, width=2*SCALE)

        # Label
        lbl = room_names[n % len(room_names)]
        d.text((rx, ry), lbl, fill=(30,20,10), anchor="mm")

    # Central hub (heart of the spiral)
    hub_r = int(room_scale * 0.055)
    d.ellipse([cx-hub_r, cy-hub_r, cx+hub_r, cy+hub_r], fill=(50,130,70))
    d.ellipse([cx-hub_r, cy-hub_r, cx+hub_r, cy+hub_r], outline=(30,90,50), width=3)
    d.text((cx, cy), "Atrium", fill=(255,240,200), anchor="mm")

    # Draw golden spiral guide
    b_sp = math.log(PHI) / (math.pi/2)
    a_sp = 12*SCALE
    sp_pts = []
    for i in range(1500):
        theta = i * math.pi / 150
        r     = a_sp * math.exp(b_sp * theta)
        if r > room_scale * 1.05:
            break
        sp_pts.append((cx + r*math.cos(theta), cy + r*math.sin(theta)))
    for i in range(1, len(sp_pts)):
        d.line([sp_pts[i-1], sp_pts[i]], fill=(80,140,90,120), width=2)

    # Title
    d.text((W//2, 32*SCALE),
           "Fibonacci Spiral Room Arrangement — Top View",
           fill=(40,90,50), anchor="mm")
    d.text((W//2, 66*SCALE),
           "Rooms placed on the sunflower spiral · 137.5° golden angle between each space",
           fill=(70,120,70), anchor="mm")

    # Compass
    comp_cx, comp_cy = W - 90*SCALE, H - 90*SCALE
    comp_r = 40*SCALE
    d.ellipse([comp_cx-comp_r, comp_cy-comp_r, comp_cx+comp_r, comp_cy+comp_r],
              fill=(240,235,225), outline=(60,100,50), width=2)
    d.line([(comp_cx, comp_cy-comp_r+4*SCALE), (comp_cx, comp_cy+comp_r-4*SCALE)],
           fill=(60,100,50), width=2)
    d.line([(comp_cx-comp_r+4*SCALE, comp_cy), (comp_cx+comp_r-4*SCALE, comp_cy)],
           fill=(60,100,50), width=2)
    d.text((comp_cx, comp_cy-comp_r-10*SCALE), "N", fill=(60,100,50), anchor="mm")

    bd = 18*SCALE
    d.rectangle([bd, bd, W-bd, H-bd], outline=(60,110,55), width=3)
    d.rectangle([bd+8, bd+8, W-bd-8, H-bd-8], outline=(100,170,90), width=1)

    return aa_img(img)

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE 6 — Bonus: Spiral vs Block Contrast  (manifesto diagram)
# ══════════════════════════════════════════════════════════════════════════════
def image6():
    W, H = 1400*SCALE, 800*SCALE
    img  = Image.new("RGB", (W, H), "#F5F0E8")
    d    = ImageDraw.Draw(img)

    half = W // 2

    # LEFT HALF — Block world (cold grey)
    gradient_rect(d, 0, 0, half, H, hex2rgb("#D0C8C0"), hex2rgb("#B8AFA5"))

    # Grid of blocks
    block_cols = (120, 115, 110)
    block_border = (80, 75, 70)
    bsize = 70*SCALE
    for row in range(2, 9):
        for col in range(1, 8):
            bx = col * bsize + 20*SCALE
            by = row * bsize + 60*SCALE
            if bx + bsize < half - 20*SCALE:
                d.rectangle([bx, by, bx+bsize-8*SCALE, by+bsize-8*SCALE],
                             fill=block_cols, outline=block_border, width=2)

    # LEFT label
    d.text((half//2, 30*SCALE), "THE BLOCK", fill=(60,55,50), anchor="mm")
    d.text((half//2, 58*SCALE),
           "Rigid · Dead matter · Control · Conformity",
           fill=(100,95,90), anchor="mm")
    d.text((half//2, H-35*SCALE),
           '"Cubes produce despair."  — The Spiral Steward',
           fill=(100,95,90), anchor="mm")

    # RIGHT HALF — Living spiral (warm green)
    gradient_rect(d, half, 0, W, H, hex2rgb("#2D5A2A"), hex2rgb("#1A3A18"))

    # Golden spiral on right half
    cx_s = half + (W - half)//2
    cy_s = H // 2
    b_sp = math.log(PHI) / (math.pi/2)
    a_sp = 8*SCALE

    sp_pts = []
    for i in range(2500):
        theta = i * math.pi / 250
        r_s   = a_sp * math.exp(b_sp * theta)
        if r_s > min(W-half, H) * 0.50:
            break
        sp_pts.append((cx_s + r_s*math.cos(theta), cy_s + r_s*math.sin(theta)))

    # Glow pass
    glow_layer = Image.new("RGB", (W, H), "#000000")
    d_g = ImageDraw.Draw(glow_layer)
    for i in range(1, len(sp_pts)):
        d_g.line([sp_pts[i-1], sp_pts[i]], fill=(80,200,80), width=8)
    glow_b = glow_layer.filter(ImageFilter.GaussianBlur(radius=6*SCALE))
    img    = Image.blend(img, glow_b, 0.4)
    d      = ImageDraw.Draw(img)

    # Sharp spiral
    for i in range(1, len(sp_pts)):
        d.line([sp_pts[i-1], sp_pts[i]], fill=(150,255,130), width=3)

    # Fibonacci dots on spiral
    fib_ns = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
    for fn in fib_ns:
        if fn - 1 < len(sp_pts):
            px_s, py_s = sp_pts[fn-1]
            r_d = max(3, int(math.log(fn+1)*3)) * SCALE
            d.ellipse([px_s-r_d, py_s-r_d, px_s+r_d, py_s+r_d],
                      fill=(200,255,180), outline=(100,200,100), width=2)

    # RIGHT labels
    d.text((cx_s, 30*SCALE), "THE SPIRAL", fill=(180,255,160), anchor="mm")
    d.text((cx_s, 58*SCALE),
           "Growth · Living matter · Emergence · Freedom",
           fill=(130,210,120), anchor="mm")
    d.text((cx_s, H-35*SCALE),
           '"The Fibonacci spiral is the shape of freedom."  — The Spiral Steward',
           fill=(120,200,110), anchor="mm")

    # Centre divider line
    for y in range(0, H, 3):
        d.line([(half, y), (half, y+1)], fill=(200,200,180), width=2)

    # Main title
    d.text((W//2, H//2 - 25*SCALE),
           "BLOCK  vs  SPIRAL",
           fill=(240,230,200), anchor="mm")
    d.text((W//2, H//2 + 15*SCALE),
           "Two philosophies of design · Two futures for humanity",
           fill=(210,205,195), anchor="mm")

    bd = 18*SCALE
    d.rectangle([bd, bd, W-bd, H-bd], outline=(100,150,80), width=3)

    return aa_img(img)

# ══════════════════════════════════════════════════════════════════════════════
#  RUN ALL
# ══════════════════════════════════════════════════════════════════════════════
print("Generating living architecture images…\n")

save(image1(), "01_fibonacci_spiral_house.png")
save(image2(), "02_mycelium_network_plan.png")
save(image3(), "03_living_facade.png")
save(image4(), "04_branching_tree_structure.png")
save(image5(), "05_sunflower_room_spiral.png")
save(image6(), "06_block_vs_spiral_manifesto.png")

print(f"\nAll 6 images saved to:\n  {OUTDIR}")
