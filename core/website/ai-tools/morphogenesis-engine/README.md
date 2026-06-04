# morphogenetic-designer

A morphogenesis-based 3D modeling engine in Python.

Geometry emerges from biological growth simulation — cells grow, interact physically, and divide, producing complex 3D forms.  Natural language prompts control growth behaviour through a rule-based interpreter that generates structured **GrowthPrograms**.

---

## Purpose

Traditional 3D modeling tools require direct vertex manipulation.  This system instead defines growth *rules* and lets the geometry emerge from simulation, the same way biological organisms develop from a handful of cells into complex structures.

You describe what you want in plain English:

```
grow upward with branching and thick core
```

The system translates that into physics parameters, runs a cell-division simulation, extracts a mesh, and saves an OBJ file.

---

## Installation

Requires Python 3.9+.

```bash
cd morphogenetic-designer
pip install -r requirements.txt
```

Dependencies:
- **numpy** — vector math and array operations
- **trimesh** — mesh construction and OBJ export
- **scipy** — (available for optional spatial queries)

---

## Usage

### Interactive mode

```bash
python main.py
```

You will be prompted:

```
Enter prompt: grow upward with branching and thick core
```

The simulation runs, then saves the mesh to `outputs/organism.obj`.

### Examples

```bash
# Isotropic blob (no prompt)
python examples/basic_growth.py

# Branching tree-like form
python examples/branching_growth.py
```

---

## Example Prompts

| Prompt | Effect |
|---|---|
| `grow upward with branching and thick core` | Tall branching form, large cells |
| `spread outward flat and stiff` | Wide flat disc, rigid cells |
| `branching noisy random` | Chaotic fractal-like growth |
| `slow compact tight` | Dense, slow-growing clump |
| `fast upward tall` | Rapid vertical column |
| `soft loose sideways` | Floppy horizontal spread |

---

## Keyword Reference

| Keyword | Parameter affected | Effect |
|---|---|---|
| `branch`, `branching`, `divid` | `division_size_multiplier` | Cells divide more frequently |
| `thick`, `wide`, `fat`, `fast` | `growth_rate_multiplier` | Cells grow faster |
| `slow` | `growth_rate_multiplier` | Cells grow slower |
| `stiff`, `rigid` | `stiffness_multiplier` | Cells repel harder |
| `soft`, `loose` | `stiffness_multiplier` | Cells are compliant |
| `spread`, `flat`, `stick` | `adhesion_multiplier` | Cells cling together more |
| `compact`, `tight` | `adhesion_multiplier` | Cells push apart |
| `upward`, `tall` | anisotropy (+Y) | Growth biased upward |
| `downward`, `deep` | anisotropy (−Y) | Growth biased downward |
| `sideways`, `outward` | anisotropy (+X) | Growth biased sideways |
| `noisy`, `random` | `noise_strength` | More stochastic branching |
| `smooth`, `quiet` | `noise_strength` | More ordered growth |

---

## Project Structure

```
morphogenetic-designer/
│
├── main.py                   # Interactive entry point
│
├── morpho/
│   ├── __init__.py           # Public API
│   ├── cell.py               # Cell class (position, radius, grow, divide)
│   ├── state.py              # SimulationState container
│   ├── program.py            # GrowthProgram (parameter modifiers)
│   ├── forces.py             # Repulsion, adhesion, noise, anisotropy
│   ├── division.py           # Division logic
│   ├── simulation.py         # Core simulation loop (Euler integration)
│   ├── interpreter.py        # Natural language → GrowthProgram
│   ├── geometry.py           # Cells → trimesh mesh
│   ├── export.py             # Mesh → OBJ / STL / PLY
│   ├── constraints.py        # Bounding box, ground plane
│   └── utils.py              # Math helpers, spatial grid
│
├── examples/
│   ├── basic_growth.py       # Simple isotropic blob
│   └── branching_growth.py   # Upward branching structure
│
├── outputs/                  # Generated meshes saved here
│
└── requirements.txt
```

---

## How It Works

### 1. Cell physics

Each cell is a sphere with:
- **position**, **velocity**, **radius**
- **growth_rate**: how fast the radius increases
- **division_radius**: when to split
- **stiffness**: repulsion strength when overlapping
- **adhesion**: attraction to nearby cells

### 2. Forces (per timestep)

For each pair of nearby cells:
- **Repulsion**: pushes overlapping cells apart (Hertz-like, proportional to overlap)
- **Adhesion**: pulls cells that are close but not overlapping
- **Noise**: Brownian random force (enables asymmetry, branching)
- **Anisotropy**: directional bias (e.g. always push cells slightly upward)

### 3. Integration

Simple Euler integration with velocity damping (overdamped dynamics, simulating a viscous biological medium).

### 4. Division

Cells that exceed their `division_radius` split into two, each at half the parent radius, offset in a random direction.  The daughter inherits the parent's growth parameters.

### 5. Mesh extraction

Each cell becomes an icosphere.  All spheres are concatenated into a single `trimesh.Trimesh` and exported as OBJ.

---

## Performance

- Spatial grid acceleration: O(N) neighbour lookups per step
- Supports 500+ cells comfortably
- Cell cap: 2000 (configurable in `morpho/division.py`)
- For GPU-accelerated simulation (10,000+ cells), a PyTorch/Taichi backend can be added

---

## Output

Meshes are saved to the `outputs/` directory:

```
outputs/organism.obj          # from main.py
outputs/basic_growth.obj      # from examples/basic_growth.py
outputs/branching_growth.obj  # from examples/branching_growth.py
```

Open with Blender, MeshLab, or any OBJ viewer.
