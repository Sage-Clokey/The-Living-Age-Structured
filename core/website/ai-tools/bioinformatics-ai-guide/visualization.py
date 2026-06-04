"""
visualization.py — Real-time 3D renderer for the coral morphogenesis engine.

Wraps PyVista's interactive plotter to display the growing coral as a lit,
smooth-shaded tube mesh on a dark background, updated live each animation
frame.

Memory management
-----------------
The previous mesh actor is explicitly removed before each new mesh is added.
This prevents GPU memory accumulation across hundreds of animation frames.

Lighting
--------
Two lights simulate an underwater ambient field:
  - Warm fill from upper-left  (diffuse ocean light penetrating from above)
  - Cool rim from behind-below (scattered bioluminescence / deep blue shift)
"""

from __future__ import annotations

from typing import Optional

import pyvista as pv


class CoralVisualizer:
    """
    Live 3D visualizer for coral morphogenesis.

    Usage
    -----
    >>> viz = CoralVisualizer()
    >>> viz.plotter.add_callback(my_update_fn, interval=50)
    >>> viz.plotter.show()   # blocking — drives the event loop
    """

    # Warm coral-orange colour (approximates natural Acropora millepora pigment)
    CORAL_COLOR: str = "#E8572A"

    def __init__(self, background_color: str = "#08080F") -> None:
        """
        Initialise the plotter, scene, lights, and static UI elements.

        Parameters
        ----------
        background_color : str
            HTML hex background colour. Deep near-black reads well against
            warm coral tones.
        """
        self.plotter = pv.Plotter(
            window_size=(1280, 800),
            title="Coral Morphogenesis — Living Architecture",
            lighting="none",  # we supply custom lights below
        )
        self.plotter.set_background(background_color)

        # Replaceable actors — removed and re-added each frame
        self._mesh_actor: Optional[pv.Actor] = None
        self._status_actor: Optional[pv.Actor] = None

        self.frame: int = 0

        self._setup_scene()

    # ------------------------------------------------------------------
    # Scene setup
    # ------------------------------------------------------------------

    def _setup_scene(self) -> None:
        """Add lights, camera position, ground plane, and static UI text."""

        # ---- Lighting ------------------------------------------------
        # Warm fill: models sunlight diffusing down through shallow water
        self.plotter.add_light(pv.Light(
            position=(12, 22, 10),
            focal_point=(0, 5, 0),
            color=[1.0, 0.92, 0.80],
            intensity=1.1,
            light_type="scene light",
        ))

        # Cool rim: scattered blue ambient from behind
        self.plotter.add_light(pv.Light(
            position=(-10, 4, -14),
            focal_point=(0, 4, 0),
            color=[0.35, 0.55, 1.0],
            intensity=0.45,
            light_type="scene light",
        ))

        # Soft floor bounce
        self.plotter.add_light(pv.Light(
            position=(0, -8, 0),
            focal_point=(0, 3, 0),
            color=[0.5, 0.7, 0.6],
            intensity=0.2,
            light_type="scene light",
        ))

        # ---- Camera --------------------------------------------------
        # 3/4 oblique angle: looks down-and-across at the growing coral
        self.plotter.camera_position = [
            (18.0, 11.0, 18.0),   # eye
            (0.0,  5.0,  0.0),    # focal point (slightly above base)
            (0.0,  1.0,  0.0),    # up vector
        ]

        # ---- Ground plane -------------------------------------------
        # Subtle dark substrate gives the coral a surface to grow from
        ground = pv.Plane(
            center=(0.0, -0.05, 0.0),
            direction=(0.0, 1.0, 0.0),
            i_size=22,
            j_size=22,
        )
        self.plotter.add_mesh(
            ground,
            color="#141428",
            opacity=0.85,
            show_edges=False,
        )

        # ---- Static title -------------------------------------------
        self.plotter.add_text(
            "CORAL MORPHOGENESIS",
            position="upper_left",
            font_size=13,
            color="white",
            font="courier",
        )

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def update(
        self,
        mesh: pv.DataSet,
        n_nodes: int,
        n_tips: int,
        max_nodes: int = 800,
    ) -> None:
        """
        Replace the current coral mesh actor and refresh the status overlay.

        Called every animation frame. The old actor is removed before the
        new one is added to prevent GPU memory accumulation.

        Parameters
        ----------
        mesh      : Current tube mesh from CoralSimulation.to_polydata().
        n_nodes   : Total node count — displayed in the HUD.
        n_tips    : Active tip count — displayed in the HUD.
        max_nodes : Node cap — used to compute progress percentage.
        """
        # Remove stale actors
        if self._mesh_actor is not None:
            self.plotter.remove_actor(self._mesh_actor)
        if self._status_actor is not None:
            self.plotter.remove_actor(self._status_actor)

        # Add updated coral mesh
        if mesh.n_points > 0:
            self._mesh_actor = self.plotter.add_mesh(
                mesh,
                color=self.CORAL_COLOR,
                smooth_shading=True,
                pbr=True,           # physically based rendering
                metallic=0.0,       # calcium carbonate is non-metallic
                roughness=0.55,     # slight surface texture
                ambient=0.12,
            )

        # HUD status line
        progress = min(100, n_nodes * 100 // max(max_nodes, 1))
        self._status_actor = self.plotter.add_text(
            f"Nodes: {n_nodes:4d}  │  Tips: {n_tips:3d}  │  "
            f"Frame: {self.frame:4d}  │  Growth: {progress:3d}%",
            position="lower_left",
            font_size=10,
            color="#00FFCC",
            font="courier",
        )

        self.plotter.render()
        self.frame += 1

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def save_screenshot(self, path: str = "outputs/coral_final.png") -> None:
        """Write the current frame to a PNG file."""
        self.plotter.screenshot(path)
        print(f"  Screenshot saved → {path}")

    def close(self) -> None:
        """Cleanly shut down the plotter."""
        self.plotter.close()
