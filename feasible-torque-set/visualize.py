"""3D visualization of feasible torque sets."""
from __future__ import annotations

import itertools
import math
from typing import List, Optional, Sequence, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Patch
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
from scipy.spatial import ConvexHull

from torque_space import FeasibleTorqueSet, OBB_EDGES, obb_corners


OCTANT_SIGNS = list(itertools.product((-1, 1), repeat=3))
OCTANT_LABELS = [
    "".join("+" if v > 0 else "-" for v in s) for s in OCTANT_SIGNS
]


def _draw_octant_indicators(ax, fts, extent, color) -> None:
    """8 corner dots in (MCP, PIP, DIP) space — lit in `color` if the hull
    reaches that octant, hollow grey otherwise."""
    reached = fts.octants_reached
    for signs in OCTANT_SIGNS:
        pos = np.array(signs, dtype=float) * extent
        if signs in reached:
            ax.scatter(
                *pos, s=70, color=color, edgecolors="black",
                linewidths=0.8, depthshade=False, zorder=20,
            )
        else:
            ax.scatter(
                *pos, s=45, facecolors="none", edgecolors="grey",
                linewidths=1.0, depthshade=False, zorder=20,
            )


def _grid_shape(n: int) -> Tuple[int, int]:
    """Subplot grid layout for n panels: row layout up to 3, then square-ish."""
    if n <= 3:
        return 1, n
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    return rows, cols


def _polytope_edges(hull: ConvexHull, parallel_tol: float = 1e-6) -> List[Tuple[int, int]]:
    """Return only the *real* polytope edges of a convex hull.

    ConvexHull triangulates faces into simplices, so adjacent simplices on a
    coplanar face share a triangulation-diagonal edge that isn't part of the
    actual polytope. A real polytope edge is one where the two adjacent
    simplices have non-parallel face normals.

    Special case: when the hull is essentially planar (rank-2, only became
    full-rank via Qhull's QJ joggle), the normal-parallelism filter is too
    aggressive and drops nearly every edge. Detect that case and return the
    2D perimeter of the planar polygon instead.
    """
    hull_pts = hull.points[hull.vertices]
    if len(hull_pts) >= 3:
        centered = hull_pts - hull_pts.mean(axis=0)
        _, sv, vt = np.linalg.svd(centered, full_matrices=False)
        if sv[0] > 0 and sv[2] / sv[0] < 1e-3:
            # Planar: project to the plane's 2D coords and take the 2D hull.
            proj_2d = centered @ vt[:2].T
            try:
                hull2d = ConvexHull(proj_2d)
            except Exception:
                hull2d = None
            if hull2d is not None:
                ordered = [int(hull.vertices[k]) for k in hull2d.vertices]
                m = len(ordered)
                return [(ordered[k], ordered[(k + 1) % m]) for k in range(m)]

    edge_to_simplices: dict = {}
    for s_idx, simplex in enumerate(hull.simplices):
        for i, j in [(0, 1), (1, 2), (0, 2)]:
            key = tuple(sorted((int(simplex[i]), int(simplex[j]))))
            edge_to_simplices.setdefault(key, []).append(s_idx)

    real = []
    for edge, simplex_indices in edge_to_simplices.items():
        if len(simplex_indices) < 2:
            real.append(edge)
            continue
        normals = [hull.equations[idx, :3] for idx in simplex_indices]
        n0 = normals[0]
        all_parallel = all(
            abs(abs(float(np.dot(n0, n))) - 1.0) < parallel_tol for n in normals[1:]
        )
        if not all_parallel:
            real.append(edge)
    return real


def _draw_edges(ax, vertices: np.ndarray, hull: ConvexHull, color: str,
                linewidth: float = 1.2, alpha: float = 1.0) -> None:
    edges = _polytope_edges(hull)
    if not edges:
        return
    segments = [(vertices[a], vertices[b]) for a, b in edges]
    lc = Line3DCollection(segments, colors=color, linewidths=linewidth, alpha=alpha)
    ax.add_collection3d(lc)


def plot_feasible_set(
    fts: FeasibleTorqueSet,
    ax=None,
    color: str = "C0",
    alpha: float = 0.3,
    show_vertices: bool = True,
    show_axes: bool = True,
    show_info: bool = True,
    show_obb: bool = True,
    show_octants: bool = True,
    octant_extent: Optional[float] = None,
    wireframe: bool = False,
    edge_linewidth: float = 1.0,
    title: Optional[str] = None,
):
    """Draw a single feasible torque set on a 3D matplotlib axes.

    wireframe=True draws only the polytope edges (no filled faces). Useful
    when overlaying nested hulls so inner ones aren't occluded.
    """
    if ax is None:
        fig = plt.figure(figsize=(8, 7))
        ax = fig.add_subplot(111, projection="3d")

    verts = fts.vertices
    hull = fts.hull

    if not wireframe:
        faces = [verts[simplex] for simplex in hull.simplices]
        poly = Poly3DCollection(
            faces, alpha=alpha, facecolor=color, edgecolor="none"
        )
        ax.add_collection3d(poly)

    _draw_edges(ax, verts, hull, color=color,
                linewidth=edge_linewidth, alpha=1.0 if wireframe else 0.8)

    if show_obb:
        corners = obb_corners(fts.hull_points)
        obb_segments = [(corners[a], corners[b]) for a, b in OBB_EDGES]
        obb_lc = Line3DCollection(
            obb_segments, colors=color, linewidths=0.8,
            linestyles="dashed", alpha=0.55,
        )
        ax.add_collection3d(obb_lc)

    if show_octants:
        oct_ext = octant_extent if octant_extent is not None \
            else float(np.max(np.abs(verts))) * 1.1
        _draw_octant_indicators(ax, fts, oct_ext, color)

    if show_vertices and not wireframe:
        hp = fts.hull_points
        ax.scatter(hp[:, 0], hp[:, 1], hp[:, 2], color=color, s=22, depthshade=True)

    if show_axes:
        extent = float(np.max(np.abs(verts))) * 1.1
        for axis_idx in range(3):
            line = np.zeros((2, 3))
            line[1, axis_idx] = extent
            ax.plot(*line.T, color="k", linewidth=0.5, alpha=0.5)
            line[1, axis_idx] = -extent
            ax.plot(*line.T, color="k", linewidth=0.5, alpha=0.5)

    ax.set_xlabel(r"$\tau_{MCP}$ (N$\cdot$mm)")
    ax.set_ylabel(r"$\tau_{PIP}$ (N$\cdot$mm)")
    ax.set_zlabel(r"$\tau_{DIP}$ (N$\cdot$mm)")

    if show_info:
        e = fts.principal_extents
        ax.set_title(
            f"{title or fts.network_name}\n"
            f"vol={fts.volume:.2e}  oct={fts.num_octants_reached}/8  "
            f"flat={fts.flatness:.3f}\n"
            f"extents={e[0]:.0f}×{e[1]:.0f}×{e[2]:.0f} N·mm",
            fontsize=9, family="monospace",
        )
    else:
        ax.set_title(title or fts.network_name)
    return ax


def plot_comparison(
    *sets: FeasibleTorqueSet,
    colors: Optional[Sequence[str]] = None,
    figsize=None,
    panel_size: float = 5.2,
    shared_axes: bool = False,
    zoom: float = 1.3,
):
    """Grid of 3D subplots — wraps to multiple rows for n > 3.

    `shared_axes=False` (default): every panel uses its own tight axis cube so
    each hull fills the frame. Cross-panel scale comparison is then via the
    `extents=` line in each title.

    `shared_axes=True`: every panel uses the same cube sized for the biggest
    hull. Lets you eyeball relative magnitudes, but small hulls look tiny.
    """
    n = len(sets)
    if n == 0:
        raise ValueError("Need at least one feasible set to plot")
    if colors is None:
        colors = [f"C{i}" for i in range(n)]

    rows, cols = _grid_shape(n)
    if figsize is None:
        figsize = (panel_size * cols, panel_size * rows + 0.4)

    if shared_axes:
        all_verts = np.concatenate([s.vertices for s in sets])
        shared_ext = float(np.max(np.abs(all_verts))) * 1.05
    else:
        shared_ext = None

    fig = plt.figure(figsize=figsize)
    axes = []
    for i, (s, c) in enumerate(zip(sets, colors)):
        ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
        if shared_ext is not None:
            ext = shared_ext
        else:
            ext = max(float(np.max(np.abs(s.vertices))) * 1.03, 1.0)
        plot_feasible_set(s, ax=ax, color=c, octant_extent=ext * 0.95)
        ax.set_xlim(-ext, ext)
        ax.set_ylim(-ext, ext)
        ax.set_zlim(-ext, ext)
        ax.set_box_aspect((1, 1, 1), zoom=zoom)
        axes.append(ax)

    fig.subplots_adjust(
        left=0.03, right=0.98, top=0.94, bottom=0.04,
        wspace=0.25, hspace=0.55,
    )
    return fig, axes


def _draw_octant_matrix(ax, sets, colors) -> dict:
    """Render the octant-reached matrix on a given 2D axes.

    Returns:
        {
          "circles": {Circle artist: tooltip},
          "ytick_lookup": {label_text: tooltip},   # by text — looked up at
          "xtick_lookup": {label_text: tooltip},   #   hover time (tick label
                                                   #   artists get replaced).
        }
    """
    n_rows = len(sets)
    radius_on = 0.26
    radius_off = 0.14
    circle_hover: dict = {}

    for row, (s, c) in enumerate(zip(sets, colors)):
        y = n_rows - 1 - row
        reached = s.octants_reached
        for col, signs in enumerate(OCTANT_SIGNS):
            is_on = signs in reached
            circle = Circle(
                (col, y), radius_on if is_on else radius_off,
                facecolor=c if is_on else "none",
                edgecolor="black" if is_on else "lightgrey",
                linewidth=0.8,
            )
            ax.add_patch(circle)
            label = OCTANT_LABELS[col]
            mark = "✓ REACHED" if is_on else "✗ not reached"
            circle_hover[circle] = (
                f"{s.network_name}  ×  octant {label}\n"
                f"{mark}\n"
                f"{OCTANT_DESCRIPTIONS.get(label, '')}"
            )

    ax.set_xlim(-0.6, 7.6)
    ax.set_ylim(-0.6, n_rows - 0.4)
    ax.set_aspect("equal")
    ax.set_xticks(range(8))
    ax.set_xticklabels(OCTANT_LABELS, family="monospace", fontsize=8)
    ax.set_xlabel("octant — signs of (MCP, PIP, DIP) torque", labelpad=3, fontsize=8)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(
        [s.network_name for s in reversed(sets)],
        family="monospace", fontsize=7,
    )
    ax.tick_params(left=False, bottom=False, pad=2)
    for spine in ax.spines.values():
        spine.set_visible(False)

    xtick_lookup = {
        label: f"octant {label}\n{OCTANT_DESCRIPTIONS.get(label, '')}"
        for label in OCTANT_LABELS
    }
    ytick_lookup = {
        s.network_name: (
            f"{s.network_name}\n"
            f"{NETWORK_DESCRIPTIONS.get(s.network_name, '(no description)')}"
        )
        for s in sets
    }

    return {
        "circles": circle_hover,
        "xtick_lookup": xtick_lookup,
        "ytick_lookup": ytick_lookup,
    }


OCTANT_DESCRIPTIONS = {
    "+++":
        "MCP +flex,  PIP +flex,  DIP +flex\n"
        "power grip / fist / closed hand",
    "++-":
        "MCP +flex,  PIP +flex,  DIP -extend\n"
        "pinch with straight fingertip;\n"
        "holding a card or coin between pads",
    "+-+":
        "MCP +flex,  PIP -extend,  DIP +flex\n"
        "*** SWAN-NECK DEFORMITY ***\n"
        "Not reachable by a healthy finger — central slip + lateral\n"
        "band coupling prevents PIP hyperextension while DIP flexes.\n"
        "Occurs clinically from volar plate laxity, intrinsic tightness,\n"
        "or chronic mallet-finger sequelae.",
    "+--":
        "MCP +flex,  PIP -extend,  DIP -extend\n"
        "intrinsic-plus / lumbrical posture —\n"
        "MCP flexed, both IPs straight (deck-of-cards hold)",
    "-++":
        "MCP -extend,  PIP +flex,  DIP +flex\n"
        "hook grip — flat knuckles, curled IPs\n"
        "(carrying a bag handle)",
    "-+-":
        "MCP -extend,  PIP +flex,  DIP -extend\n"
        "*** BOUTONNIERE DEFORMITY ***\n"
        "Not reachable by a healthy finger — needs central slip\n"
        "rupture so EE tension routes only to the terminal slip.\n"
        "Classic extensor-hood injury (PIP pokes through like a button).",
    "--+":
        "MCP -extend,  PIP -extend,  DIP +flex\n"
        "*** MALLET FINGER ***\n"
        "Not reachable by a healthy finger — needs terminal slip\n"
        "detachment / FDP avulsion. Finger straight except the tip\n"
        "drops into passive flexion. Common in 'jammed' fingertip injuries.",
    "---":
        "MCP -extend,  PIP -extend,  DIP -extend\n"
        "full extension / open hand",
}

TENDON_DESCRIPTIONS = {
    "FP":
        "FLEXOR PROFUNDUS  (FDP — Flexor Digitorum Profundus)\n"
        "Deep extrinsic flexor — flexes MCP, PIP, AND DIP.\n"
        "Inserts on the distal phalanx (only muscle that flexes DIP).\n"
        "Origin: ulna + interosseous membrane.\n"
        "If FDP is cut you lose active DIP flexion — finger goes\n"
        "limp at the tip even though grip works.",
    "FS":
        "FLEXOR SUPERFICIALIS  (FDS — Flexor Digitorum Superficialis)\n"
        "Surface extrinsic flexor — flexes MCP and PIP only.\n"
        "Inserts on the middle phalanx via a split tendon.\n"
        "Origin: medial epicondyle of the humerus.\n"
        "Testable in isolation by holding the other fingers extended\n"
        "(removes FDP, which shares a muscle belly).",
    "EE":
        "EXTRINSIC EXTENSOR  (ED — Extensor Digitorum)\n"
        "Extends all three joints via the central band of the hood.\n"
        "Inserts on the dorsum of all three phalanges (via slips).\n"
        "Origin: lateral epicondyle of the humerus.\n"
        "In VC2007's hood model EE's tension is routed through the\n"
        "rhombus, not delivered directly to each joint.",
    "DI2":
        "SECOND DORSAL INTEROSSEOUS\n"
        "Intrinsic on the radial side of the middle finger.\n"
        "Bony insertion on the proximal phalanx → flexes MCP\n"
        "(and abducts radially in a 4-DoF model).\n"
        "Sends a slip into the hood's lateral band → contributes\n"
        "to PIP/DIP extension via the network's tension routing.\n"
        "Origin: bipennate from MC2 and MC3.",
    "DI3":
        "THIRD DORSAL INTEROSSEOUS\n"
        "Mirror of DI2 — inserts on the ulnar side of the middle\n"
        "finger. Same biomechanical role: MCP flex (+ ulnar abduction)\n"
        "+ PIP/DIP extension via the lateral band.\n"
        "Origin: bipennate from MC3 and MC4.",
    "LU":
        "LUMBRICAL\n"
        "Unusual intrinsic — NO bony origin. Arises from the FDP\n"
        "tendon in the palm and inserts into the hood's lateral\n"
        "band on the radial side only (asymmetric).\n"
        "Small MCP flexor + PIP/DIP extensor via the hood.\n"
        "Can 'sense' FDP tension (proprioceptive role).\n"
        "VC2007 excluded LU to keep the rhombus symmetric.",
}


def _tendon_tooltip(name: str) -> str:
    if name in TENDON_DESCRIPTIONS:
        return TENDON_DESCRIPTIONS[name]
    # Virtual network tendon, e.g. "net(ee=0.15)"
    if name.startswith("net(ee="):
        try:
            ee = float(name[len("net(ee="):].rstrip(")"))
        except ValueError:
            ee = None
        if ee is not None:
            di_ee = (1.0 - ee) / ee if ee > 0 else float("inf")
            return (
                "VIRTUAL NETWORK TENDON\n"
                f"Combined EE+DI2+DI3 output at ee_fraction={ee:.2f}\n"
                f"(DI:EE ratio ≈ {di_ee:.2f}).\n"
                "Direction is determined by hood routing — it ROTATES\n"
                "with the input ratio. This is the whole point of\n"
                "VC2007's 'anatomical computation' argument.\n"
                "NOT a real muscle — collapsed network for the figure."
            )
    return f"tendon: {name}\n(no description available)"


NETWORK_DESCRIPTIONS = {
    "FP+FS+net(ee=0.15)":
        "VC2007 hood STATE A  (ee_fraction=0.15, DI:EE ≈ 5.7)\n"
        "muscles: FP + FS + (EE+DI2+DI3 through hood)\n"
        "DI-dominant input: dorsal interossei pull hard, EE quiet.\n"
        "Network basis points to (+MCP, -PIP, -DIP) — DI's bony\n"
        "insertion flexes MCP while the hood routes most tension to\n"
        "proximal slip, extending PIP.\n"
        "WHY: one of VC2007 Fig.4's three labeled states. Demonstrates\n"
        "that the network's basis vector rotates with input ratio —\n"
        "the 'anatomical computation' headline result.",
    "FP+FS+net(ee=0.35)":
        "VC2007 hood STATE B  (ee_fraction=0.35, DI:EE ≈ 1.9)\n"
        "muscles: FP + FS + (EE+DI2+DI3 through hood)\n"
        "Balanced input. Proximal:terminal slip tension ratio is near\n"
        "its peak (~2.5:1 per Fig.3), so the hood routes most extension\n"
        "tension to PIP, less to DIP.\n"
        "WHY: mid-range state showing how the hood differentially\n"
        "actuates PIP vs DIP based on input distribution rather than\n"
        "neural control alone.",
    "FP+FS+net(ee=0.65)":
        "VC2007 hood STATE C  (ee_fraction=0.65, DI:EE ≈ 0.54)\n"
        "muscles: FP + FS + (EE+DI2+DI3 through hood)\n"
        "EE-dominant input. Network basis flips to all-extension\n"
        "(-MCP, -PIP, -DIP) — this is the state that lets the finger\n"
        "fully open (reaches the --- octant).\n"
        "WHY: extreme state on the other end of the ratio sweep.\n"
        "Compare to State A: same muscles, very different feasible set.",
    "FP+FS+EE":
        "Minimal antagonist set: FP + FS + EE only.\n"
        "muscles: flexor profundus, flexor superficialis, extrinsic\n"
        "extensor — no intrinsics (DI/LU), no hood routing.\n"
        "WHY: simplest possible finger. Reaches only +++ and --- (the\n"
        "flex/extend diagonal). This is the baseline that proves\n"
        "intrinsics are required for fingertip force in arbitrary\n"
        "directions — and motivates the rest of the analysis.",
    "simple-paths VC2007":
        "Paper's CRITIQUE CASE: EE + DI2 + DI3 as fixed-direction\n"
        "tendons (no hood routing). No flexors included.\n"
        "muscles: extrinsic extensor + 2 dorsal interossei.\n"
        "Rank-2 in the 3-joint model (DI2 and DI3 identical) — the\n"
        "polytope is a flat parallelogram with effectively zero volume.\n"
        "WHY: this is the standard biomechanical modeling assumption\n"
        "VC2007 argues AGAINST. Showing its degeneracy is the paper's\n"
        "rhetorical move: the simplification loses the network's reach.",
    "simple-paths VC2007 + LU":
        "VC2007 simple paths plus the lumbrical (LU).\n"
        "muscles: EE + DI2 + DI3 + LU as fixed-direction tendons.\n"
        "LU's asymmetric DIP moment arm breaks the rank-2 collapse —\n"
        "the polytope is now genuinely 3D but extremely thin (slab,\n"
        "flatness ≈ 0.014).\n"
        "WHY: tests whether anatomical asymmetry alone fixes the\n"
        "simple-paths model. Answer: no — still only 2 octants reached.\n"
        "The hood structure is doing real work that asymmetry can't\n"
        "replace.",
    "full finger (simple)":
        "All 6 modeled muscles as fixed-direction simple paths:\n"
        "FP + FS + EE + DI2 + DI3 + LU. No hood routing — pure\n"
        "Minkowski sum of basis vectors.\n"
        "WHY: most 'complete' fixed-direction model — comparable to\n"
        "the An et al. 1979 normative-hand approach and most pre-2007\n"
        "biomechanical simulations. Reaches 3 octants — better than\n"
        "subsets, but still understates real-finger capability per\n"
        "VC2007's argument.",
    "ideal finger (hood-swept)":
        "Ideal/envelope model: FP + FS direct + (EE,DI2,DI3) routed\n"
        "through the Winslow rhombus, sampled across the FULL 5-D\n"
        "activation space (5^5 = 3125 patterns).\n"
        "Approximates the UNION of reachable torques across all\n"
        "possible neural control strategies — the true envelope of\n"
        "what this finger model can in principle produce.\n"
        "WHY: best estimate of real-finger capability in this\n"
        "framework. Reaches 5 octants including both +++ and ---.\n"
        "The volume ≈ full-finger (simple) but octant coverage is\n"
        "much higher — the hood adds reach, not size.",
}


def _attach_hover_tooltips(ax, fig, hover_spec) -> None:
    """Wire up motion_notify_event so hovering over circle patches or tick
    labels in the octant matrix displays a tooltip.

    hover_spec = dict returned by _draw_octant_matrix:
      circles:      {Circle: tooltip_text}        (looked up by artist ref)
      ytick_lookup: {label_text: tooltip_text}    (looked up by text content
      xtick_lookup: {label_text: tooltip_text}     each event, since tick
                                                   label artists get replaced)

    Tooltip flips to the left side when cursor is in the right half of the
    figure so it can't run off the page.
    """
    circles = hover_spec["circles"]
    xtick_lookup = hover_spec["xtick_lookup"]
    ytick_lookup = hover_spec["ytick_lookup"]

    # Figure-level Text so the tooltip is never clipped by the axes bbox
    # (tick labels live outside the axes rectangle).
    tooltip = fig.text(
        0.5, 0.5, "", visible=False, zorder=200,
        bbox=dict(boxstyle="round,pad=0.4", fc="lightyellow",
                  ec="grey", alpha=0.96),
        fontsize=8, family="monospace", ha="left", va="bottom",
    )
    last = [None]

    def _on_move(event):
        if event.x is None or event.y is None:
            return

        found_text = None

        for circle, text in circles.items():
            try:
                if circle.contains(event)[0]:
                    found_text = text
                    break
            except Exception:
                continue

        if found_text is None:
            for yl in ax.get_yticklabels():
                try:
                    if yl.contains(event)[0]:
                        found_text = ytick_lookup.get(yl.get_text())
                        if found_text:
                            break
                except Exception:
                    continue

        if found_text is None:
            for xl in ax.get_xticklabels():
                try:
                    if xl.contains(event)[0]:
                        found_text = xtick_lookup.get(xl.get_text())
                        if found_text:
                            break
                except Exception:
                    continue

        if found_text is not None:
            fx = event.x / fig.bbox.width
            fy = event.y / fig.bbox.height
            if fx > 0.5:
                tooltip.set_position((fx - 0.005, fy + 0.01))
                tooltip.set_ha("right")
            else:
                tooltip.set_position((fx + 0.005, fy + 0.01))
                tooltip.set_ha("left")
            if last[0] != found_text:
                tooltip.set_text(found_text)
                last[0] = found_text
            if not tooltip.get_visible():
                tooltip.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if tooltip.get_visible():
                tooltip.set_visible(False)
                last[0] = None
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", _on_move)


def plot_overlay(
    *sets: FeasibleTorqueSet,
    colors: Optional[Sequence[str]] = None,
    figsize=(15, 10),
):
    """Overlay all feasible sets as nested wireframes with a clickable
    monospace-aligned legend table. Octant matrix embedded below.

    Click any legend row (color patch or text, 8 px tolerance) to toggle
    that hull on/off. Toggling only works in interactive matplotlib windows
    — saved PNGs always show every hull.
    """
    if not sets:
        raise ValueError("Need at least one feasible set to overlay")
    if colors is None:
        colors = [f"C{i}" for i in range(len(sets))]
    n = len(sets)

    # Layout: 3D plot fills the left, legend (top-right) + octants (bottom-right).
    # Legend cell is small (sized to fit the table); octants cell takes the
    # rest so the matrix sits flush under the legend instead of in the gutter.
    # Width ratio biased toward the right column + extra wspace so the 3D
    # plot's projected cube can't bleed into the legend/matrix area when the
    # interactive window is resized to a narrower aspect.
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(
        2, 2, width_ratios=[1.8, 1.7], height_ratios=[0.6, 1.4],
        wspace=0.28, hspace=0.0,
    )
    ax3d = fig.add_subplot(gs[:, 0], projection="3d")
    ax_legend = fig.add_subplot(gs[0, 1])
    ax_legend.set_axis_off()
    ax_oct = fig.add_subplot(gs[1, 1])

    # Draw largest hull first so it sits "behind".
    order = sorted(range(n), key=lambda i: -sets[i].volume)
    largest_idx = order[0]
    artists_per_set: dict = {}
    for i in order:
        s, c = sets[i], colors[i]
        artists: List = []
        if i == largest_idx:
            faces = [s.vertices[simplex] for simplex in s.hull.simplices]
            poly = Poly3DCollection(faces, alpha=0.08, facecolor=c, edgecolor="none")
            ax3d.add_collection3d(poly)
            artists.append(poly)
        edges = _polytope_edges(s.hull)
        if edges:
            segments = [(s.vertices[a], s.vertices[b]) for a, b in edges]
            lc = Line3DCollection(segments, colors=c, linewidths=1.6)
            ax3d.add_collection3d(lc)
            artists.append(lc)
        artists_per_set[i] = artists

    # Cube centered on the combined hull bounding box, sized so the longest
    # span fills HULL_FILL of the cube width — same convention as dual_focus.
    HULL_FILL = 1.0
    all_verts = np.concatenate([s.vertices for s in sets])
    pmin = all_verts.min(axis=0)
    pmax = all_verts.max(axis=0)
    center = (pmin + pmax) / 2.0
    max_half_span = float(np.max((pmax - pmin) / 2.0))
    cube_half = max(max_half_span / HULL_FILL, 1.0)
    ax3d.set_xlim(center[0] - cube_half, center[0] + cube_half)
    ax3d.set_ylim(center[1] - cube_half, center[1] + cube_half)
    ax3d.set_zlim(center[2] - cube_half, center[2] + cube_half)
    ax3d.set_xlabel(r"$\tau_{MCP}$ (N$\cdot$mm)")
    ax3d.set_ylabel(r"$\tau_{PIP}$ (N$\cdot$mm)")
    ax3d.set_zlabel(r"$\tau_{DIP}$ (N$\cdot$mm)")
    ax3d.set_title("Overlay (click = toggle, double-click = solo)")
    ax3d.set_box_aspect((1, 1, 1), zoom=1.0)

    # Monospace legend table
    name_w = max(max(len(s.network_name) for s in sets), len("network"))
    header = (
        f"{'network':<{name_w}}   {'vol':>9}   {'area':>9}   "
        f"{'oct':>4}   {'flat':>5}"
    )
    handles = [
        Patch(
            facecolor=c, edgecolor=c, alpha=0.85,
            label=(
                f"{s.network_name:<{name_w}}   "
                f"{s.volume:>9.2e}   "
                f"{s.surface_area:>9.2e}   "
                f"{s.num_octants_reached:>2}/8   "
                f"{s.flatness:>5.3f}"
            ),
        )
        for s, c in zip(sets, colors)
    ]
    legend = ax_legend.legend(
        handles=handles, title=header,
        loc="upper center",
        prop={"family": "monospace", "size": 9},
        title_fontproperties={"family": "monospace", "size": 9, "weight": "bold"},
        frameon=True, handlelength=2.0, borderpad=0.7, labelspacing=0.7,
    )

    legend_patches = legend.get_patches()
    legend_texts = legend.get_texts()
    pickable_to_set: dict = {}
    for i, (lp, lt) in enumerate(zip(legend_patches, legend_texts)):
        lp.set_picker(8)
        lt.set_picker(8)
        pickable_to_set[id(lp)] = i
        pickable_to_set[id(lt)] = i

    def _set_visibility(i: int, visible: bool) -> None:
        arts = artists_per_set[i]
        if not arts:
            return
        for a in arts:
            a.set_visible(visible)
        legend_patches[i].set_alpha(0.85 if visible else 0.18)
        legend_texts[i].set_alpha(1.0 if visible else 0.35)

    def _on_pick(event):
        set_i = pickable_to_set.get(id(event.artist))
        if set_i is None:
            return

        if event.mouseevent.dblclick:
            # Solo: show only this hull, hide all others. (Single-click also
            # fires on the first half of the double-click; the dblclick
            # handler runs after and overrides, so the end state is solo.)
            for i in range(n):
                _set_visibility(i, i == set_i)
        else:
            arts = artists_per_set[set_i]
            if not arts:
                return
            _set_visibility(set_i, not arts[0].get_visible())

        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("pick_event", _on_pick)

    # Octant matrix — anchor top so it sits flush below the legend's frame.
    hover_items = _draw_octant_matrix(ax_oct, sets, colors)
    ax_oct.set_aspect("equal", anchor="N")
    ax_oct.set_title(
        f"Octants reached  "
        f"({sum(len(s.octants_reached) for s in sets)}/{8 * n} cells filled) "
        f"— hover for details",
        fontsize=10, pad=4,
    )
    _attach_hover_tooltips(ax_oct, fig, hover_items)

    fig.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.06)
    return fig, (ax3d, ax_legend, ax_oct)


def plot_dual_focus(
    *sets: FeasibleTorqueSet,
    colors: Optional[Sequence[str]] = None,
    initial: Sequence[int] = (0, 1),
    figsize=(16.15, 9.025),     # 5% smaller than 17x9.5
):
    """Side-by-side dual viewer with a swap sidebar.

    Two 3D plots show one hull each, with an explicit circular ARM button
    above each. All other sets appear as a labeled color-chip sidebar on
    the right. Interaction (interactive backends only):
      - Click an ARM circle above a panel -> arms that slot (turns red).
      - Click a sidebar chip -> swaps it into the armed slot. The displaced
        set goes back to the sidebar.
      - Click an armed ARM circle again to un-arm.
      - If nothing armed, sidebar click defaults to replacing the RIGHT panel.
    """
    if not sets:
        raise ValueError("Need at least one feasible set")
    if colors is None:
        colors = [f"C{i}" for i in range(len(sets))]
    n = len(sets)

    slots = [int(initial[0]) if n >= 1 else 0,
             int(initial[1]) if n >= 2 else (0 if n >= 1 else 0)]
    armed = [None]   # 0 or 1 = armed slot

    # Layout: a thin button row above each 3D panel; sidebar spans both rows.
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(
        2, 3, width_ratios=[2.8, 2.8, 1.7], height_ratios=[1.0, 12.0],
        wspace=0.28, hspace=0.0,
    )
    ax_btn_a = fig.add_subplot(gs[0, 0])
    ax_btn_b = fig.add_subplot(gs[0, 1])
    ax_a = fig.add_subplot(gs[1, 0], projection="3d")
    ax_b = fig.add_subplot(gs[1, 1], projection="3d")
    ax_sb = fig.add_subplot(gs[:, 2])

    panels = [ax_a, ax_b]
    button_axes = [ax_btn_a, ax_btn_b]
    button_artists: dict = {}   # id(circle) -> slot_i
    sidebar_artists: dict = {}  # id(artist) -> set_idx
    panel_hovers: dict = {0: {}, 1: {}}   # slot -> {text-artist: tooltip}
    sidebar_hovers: dict = {}              # {artist: tooltip}

    # Hull-fills-cube ratio: hull's longest axis span = HULL_FILL * cube width.
    # 0.75 -> the hull dominates each panel without touching the cube faces.
    HULL_FILL = 0.75

    def _draw_slot(slot_i: int) -> None:
        ax = panels[slot_i]
        ax.clear()
        set_i = slots[slot_i]
        s = sets[set_i]

        # Cube centered on the hull's bounding-box center, sized so the
        # longest hull span fills HULL_FILL of the cube width.
        pmin = s.vertices.min(axis=0)
        pmax = s.vertices.max(axis=0)
        center = (pmin + pmax) / 2.0
        max_half_span = float(np.max((pmax - pmin) / 2.0))
        cube_half = max(max_half_span / HULL_FILL, 1.0)

        plot_feasible_set(
            s, ax=ax, color=colors[set_i],
            show_info=False, show_axes=True, show_obb=True, show_octants=True,
            octant_extent=cube_half * 0.97,
        )
        ax.set_xlim(center[0] - cube_half, center[0] + cube_half)
        ax.set_ylim(center[1] - cube_half, center[1] + cube_half)
        ax.set_zlim(center[2] - cube_half, center[2] + cube_half)
        ax.set_box_aspect((1, 1, 1), zoom=1.0)

        # Basis vectors: arrow from origin to each tendon's max-torque point,
        # with a label at the tip (per VC2007 Fig. 4 top panel).
        panel_hovers[slot_i] = {}
        if s.network is not None:
            for tendon in s.network.tendons:
                tip = tendon.max_torque_vector
                ax.quiver(
                    0.0, 0.0, 0.0,
                    tip[0], tip[1], tip[2],
                    color="black", arrow_length_ratio=0.10,
                    linewidth=1.6, alpha=0.85, zorder=15,
                )
                txt = ax.text(
                    tip[0], tip[1], tip[2], f"  {tendon.name}",
                    fontsize=9, color="black", fontweight="bold",
                    zorder=16,
                )
                panel_hovers[slot_i][txt] = _tendon_tooltip(tendon.name)

        # Diagnostics-only title (set name lives on the ARM button above).
        e = s.principal_extents
        ax.set_title(
            f"vol={s.volume:.2e}  oct={s.num_octants_reached}/8  "
            f"flat={s.flatness:.3f}\n"
            f"extents={e[0]:.0f}×{e[1]:.0f}×{e[2]:.0f} N·mm",
            fontsize=9, family="monospace",
        )

    # Marker size used identically for the A/B button and bench chips (in
    # points^2, so circles match on screen regardless of axes scaling).
    CHIP_SIZE = 1400

    def _draw_button(slot_i: int) -> None:
        ax = button_axes[slot_i]
        ax.clear()
        ax.set_axis_off()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 1)

        set_i = slots[slot_i]
        color = colors[set_i]
        label = "A" if slot_i == 0 else "B"
        is_armed = armed[0] == slot_i

        edge = "crimson" if is_armed else "black"
        edge_w = 3.0 if is_armed else 1.0

        circle_x = 1.0
        sc = ax.scatter(
            [circle_x], [0.5], s=CHIP_SIZE, c=[color],
            edgecolors=edge, linewidths=edge_w,
            picker=10, zorder=10,
        )
        button_artists[id(sc)] = slot_i

        ax.text(
            circle_x, 0.5, label, ha="center", va="center",
            fontsize=13, fontweight="bold", color="white", zorder=11,
        )

        if is_armed:
            status = "▶ ARMED — click a sidebar chip to swap in"
            status_color = "crimson"
        else:
            status = "click to arm  →  then click sidebar chip"
            status_color = "grey"
        text_x = circle_x + 1.0
        ax.text(
            text_x, 0.7, sets[set_i].network_name,
            va="center", ha="left", fontsize=11, fontweight="bold",
            family="monospace",
        )
        ax.text(
            text_x, 0.3, status,
            va="center", ha="left", fontsize=8,
            family="monospace", color=status_color, style="italic",
        )

    def _redraw_sidebar() -> None:
        sidebar_artists.clear()
        ax_sb.clear()
        ax_sb.set_axis_off()
        ax_sb.set_aspect("equal")

        bench = [i for i in range(n) if i not in slots]
        rows = len(bench)

        # Coordinate system: chip-units. Each row is 1.6 units tall.
        row_h = 1.6
        total_h = max(rows * row_h + 2.0, 4.0)
        sidebar_w = 5.0
        ax_sb.set_xlim(0, sidebar_w)
        ax_sb.set_ylim(0, total_h)

        # Header
        ax_sb.text(
            sidebar_w / 2, total_h - 0.5, "BENCH",
            ha="center", va="center",
            fontsize=11, fontweight="bold", family="monospace",
        )
        if armed[0] is not None:
            sub = f"armed: slot {'A' if armed[0] == 0 else 'B'} — click a chip to swap"
            sub_color = "crimson"
        else:
            sub = "no slot armed: click defaults to slot B"
            sub_color = "grey"
        ax_sb.text(
            sidebar_w / 2, total_h - 1.2, sub,
            ha="center", va="center",
            fontsize=8, family="monospace",
            style="italic", color=sub_color,
        )

        if not bench:
            ax_sb.text(
                sidebar_w / 2, (total_h - 2) / 2,
                "(no other sets)",
                ha="center", va="center",
                fontsize=10, family="monospace", color="grey",
            )
            return

        # Chips — scatter with same CHIP_SIZE so they match the A/B buttons.
        sidebar_hovers.clear()
        for j, i in enumerate(bench):
            y = total_h - 2.0 - (j + 0.5) * row_h
            sc = ax_sb.scatter(
                [0.8], [y], s=CHIP_SIZE, c=[colors[i]],
                edgecolors="black", linewidths=0.8,
                picker=10, zorder=10,
            )
            sidebar_artists[id(sc)] = i

            txt = ax_sb.text(
                1.7, y,
                f"{sets[i].network_name}\n"
                f"oct={sets[i].num_octants_reached}/8  "
                f"flat={sets[i].flatness:.2f}",
                va="center", ha="left",
                fontsize=8, family="monospace", picker=10,
            )
            sidebar_artists[id(txt)] = i

            # Hover tooltip = full network description
            tip = (
                f"{sets[i].network_name}\n"
                + NETWORK_DESCRIPTIONS.get(sets[i].network_name, "")
            )
            sidebar_hovers[sc] = tip
            sidebar_hovers[txt] = tip

    def _redraw_all() -> None:
        button_artists.clear()
        for i in (0, 1):
            _draw_slot(i)
            _draw_button(i)
        _redraw_sidebar()
        fig.canvas.draw_idle()

    def _on_pick(event):
        a = event.artist
        if id(a) in button_artists:
            slot_i = button_artists[id(a)]
            armed[0] = None if armed[0] == slot_i else slot_i
            _redraw_all()
            return
        if id(a) in sidebar_artists:
            set_i = sidebar_artists[id(a)]
            target_slot = armed[0] if armed[0] is not None else 1
            slots[target_slot] = set_i
            armed[0] = None
            _redraw_all()
            return

    fig.canvas.mpl_connect("pick_event", _on_pick)
    _redraw_all()

    # Figure-level hover tooltip combining tendon-arrow labels (per panel)
    # and bench chips. Uses display coords so 3D rotation doesn't break it.
    tooltip = fig.text(
        0.5, 0.5, "", visible=False, zorder=200,
        bbox=dict(boxstyle="round,pad=0.4", fc="lightyellow",
                  ec="grey", alpha=0.96),
        fontsize=8, family="monospace", ha="left", va="bottom",
    )
    last_tip = [None]

    def _all_hoverables():
        merged = {}
        merged.update(panel_hovers[0])
        merged.update(panel_hovers[1])
        merged.update(sidebar_hovers)
        return merged

    def _on_move(event):
        if event.x is None or event.y is None:
            return
        found = None
        for artist, text in _all_hoverables().items():
            try:
                contains, _ = artist.contains(event)
            except Exception:
                continue
            if contains:
                found = text
                break
        if found is not None:
            fx = event.x / fig.bbox.width
            fy = event.y / fig.bbox.height
            if fx > 0.5:
                tooltip.set_position((fx - 0.005, fy + 0.01))
                tooltip.set_ha("right")
            else:
                tooltip.set_position((fx + 0.005, fy + 0.01))
                tooltip.set_ha("left")
            if last_tip[0] != found:
                tooltip.set_text(found)
                last_tip[0] = found
            if not tooltip.get_visible():
                tooltip.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if tooltip.get_visible():
                tooltip.set_visible(False)
                last_tip[0] = None
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", _on_move)

    fig.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.04)
    return fig, (ax_a, ax_b, ax_sb)


def plot_octant_summary(
    *sets: FeasibleTorqueSet,
    colors: Optional[Sequence[str]] = None,
    figsize=None,
):
    """Matrix view: which of the 8 (MCP, PIP, DIP) torque-space octants does
    each feasible set reach? Rows = sets, columns = octants labeled by sign
    pattern. Filled dot in the set's color = reached; hollow grey = not.
    """
    if not sets:
        raise ValueError("Need at least one feasible set")
    if colors is None:
        colors = [f"C{i}" for i in range(len(sets))]

    n_rows = len(sets)
    if figsize is None:
        figsize = (9.0, 0.6 + 0.55 * n_rows)

    fig, ax = plt.subplots(figsize=figsize)
    hover_items = _draw_octant_matrix(ax, sets, colors)
    total_filled = sum(len(s.octants_reached) for s in sets)
    ax.set_title(
        f"Octants reached  ({total_filled}/{8 * n_rows} cells filled)",
        fontsize=10,
    )
    _attach_hover_tooltips(ax, fig, hover_items)
    fig.tight_layout()
    return fig, ax
