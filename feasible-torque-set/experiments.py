"""Preset tendon configurations from Valero-Cuevas 2007 and extensions.

The paper's central finding (§III, Fig. 4): when EE/DI2/DI3 route through
Winslow's rhombus, the *direction* of the network's torque basis vector
changes with the input tension ratio. Each "state" of the network gives a
different basis vector and therefore a different feasible torque set when
combined with FP and FS. This is the "anatomical computation" claim.

The fixed-direction approximation (treating EE, DI2, DI3 as independent
linear tendons with constant moment arms) is exactly the "simple tendon
paths" comparison case the paper argues *against*. Both are available here
so you can see the difference.

Sign convention: positive = flexion, negative = extension. Units: moment
arms in mm, forces in N, torques in N*mm.

Moment-arm values are approximations consistent with the literature the
paper references (VC 1998 / An et al. 1979). Replace with sourced values
for publication-quality work.
"""
from __future__ import annotations

import numpy as np

from tendon_network import Tendon, TendonNetwork
from torque_space import FeasibleTorqueSet, sample_feasible_set

# 40 N total input == 30% physiological capacity (VC2007 §IIA).
F_MAX = 40.0


# ---------------------------------------------------------------------------
# Single tendons with fixed-direction basis vectors
# ---------------------------------------------------------------------------

# Extrinsic flexors (have simple tendon paths -> fixed basis vectors).
FP = Tendon("FP", moment_arms=[10.0,  8.0,  6.0], max_force=F_MAX)
FS = Tendon("FS", moment_arms=[10.0,  6.0,  0.0], max_force=F_MAX)

# Extrinsic extensor and intrinsics as *simple* tendons (the comparison case
# the paper criticizes). These ignore the hood routing.
EE_SIMPLE  = Tendon("EE(simple)",  moment_arms=[-8.0, -6.0, -4.0], max_force=F_MAX)
DI2_SIMPLE = Tendon("DI2(simple)", moment_arms=[ 6.0, -3.0, -2.0], max_force=F_MAX)
DI3_SIMPLE = Tendon("DI3(simple)", moment_arms=[ 6.0, -3.0, -2.0], max_force=F_MAX)
LU_SIMPLE  = Tendon("LU(simple)",  moment_arms=[ 4.0, -2.0, -1.0], max_force=F_MAX)

# Kept under old names for back-compat with prior runs.
EE, DI2, DI3, LU = EE_SIMPLE, DI2_SIMPLE, DI3_SIMPLE, LU_SIMPLE


# ---------------------------------------------------------------------------
# Winslow's rhombus hood routing (the actual VC2007 model)
# ---------------------------------------------------------------------------
# Moment arms specific to the hood routing model.
R_EE_MCP            = 8.0   # EE on the proximal phalanx -> MCP extension
R_DI_MCP            = 6.0   # DI bony insertion on proximal phalanx -> MCP flexion
R_PROXIMAL_SLIP_PIP = 6.0   # proximal slip -> PIP extension
R_TERMINAL_SLIP_DIP = 4.0   # terminal slip -> DIP extension
NETWORK_TRANSMISSION = 0.85  # fraction of input tension reaching the slips


def hood_proximal_fraction(di_to_ee_ratio: float) -> float:
    """Phenomenological fit to VC2007 Fig. 3 (left): fraction of total slip
    tension that reaches the *proximal* slip (extends PIP), as a function of
    the (DI2+DI3):EE input tension ratio.

    Reproduces the qualitative switching behavior:
      - very low DI:EE  -> mostly terminal slip (PT < 1, DIP extension)
      - moderate DI:EE  -> peak proximal (PT ~ 2.5, PIP extension)
      - very high DI:EE -> plateau (PT ~ 1.5)

    This is NOT a quantitative match. The paper itself notes (§III) that the
    experiment-vs-model ratios differ substantially. Refine if you need
    quantitative agreement.
    """
    r = max(float(di_to_ee_ratio), 1e-9)
    if r < 1.0:
        pt = 0.3 + 1.7 * r              # 0.3 -> 2.0
    elif r < 4.0:
        pt = 2.0 + 0.5 * (r - 1.0) / 3.0  # 2.0 -> 2.5
    elif r < 12.0:
        pt = 2.5 - 1.0 * (r - 4.0) / 8.0  # 2.5 -> 1.5
    else:
        pt = 1.5
    return pt / (pt + 1.0)


def network_basis_vector(ee_fraction: float,
                         total_input_force: float = F_MAX) -> np.ndarray:
    """(MCP, PIP, DIP) torque from EE + DI2 + DI3 through the hood, with the
    given fraction of total input force going to EE (rest split equally
    between DI2, DI3). Matches VC2007's longitudinally-symmetric protocol
    where EE + DI2 + DI3 = total_input_force.
    """
    f_ee = ee_fraction * total_input_force
    f_di_total = (1.0 - ee_fraction) * total_input_force

    # MCP: direct bony insertions, no hood involvement
    tau_mcp = -f_ee * R_EE_MCP + f_di_total * R_DI_MCP

    # PIP / DIP: hood splits total slip tension between the two outputs
    di_to_ee = f_di_total / (f_ee + 1e-9)
    p_frac = hood_proximal_fraction(di_to_ee)
    total_slip = NETWORK_TRANSMISSION * total_input_force
    f_proximal = p_frac * total_slip
    f_terminal = (1.0 - p_frac) * total_slip

    tau_pip = -f_proximal * R_PROXIMAL_SLIP_PIP
    tau_dip = -f_terminal * R_TERMINAL_SLIP_DIP

    return np.array([tau_mcp, tau_pip, tau_dip])


def network_state_tendon(ee_fraction: float,
                         total_input_force: float = F_MAX) -> Tendon:
    """Wraps one hood state as a virtual fixed-direction tendon.

    The basis direction is the network's torque output for the given EE:DI
    input ratio. Activating this "tendon" from 0 to max_force corresponds
    to ramping the network's total input tension from 0 to total_input_force
    while *holding the EE:DI ratio constant* — this is the assumption
    underlying each "state" in VC2007 Fig. 4.
    """
    basis = network_basis_vector(ee_fraction, total_input_force)
    return Tendon(
        f"net(ee={ee_fraction:.2f})",
        moment_arms=basis / total_input_force,
        max_force=total_input_force,
    )


def vc2007_state(ee_fraction: float) -> TendonNetwork:
    """Feasible-set configuration for one hood state, combined with FP + FS.
    This is what each of the colored hulls in VC2007 Fig. 4 (bottom) represents.
    """
    label = f"FP+FS+net(ee={ee_fraction:.2f})"
    return TendonNetwork(label, [FP, FS, network_state_tendon(ee_fraction)])


# Three states sampling the input-ratio range. ee_fraction = EE / (EE+DI).
# Names chosen so they sort sensibly in the legend.
def vc2007_state_a() -> TendonNetwork:
    return vc2007_state(0.15)   # DI-dominant: DI:EE ~ 5.7

def vc2007_state_b() -> TendonNetwork:
    return vc2007_state(0.35)   # balanced:    DI:EE ~ 1.9

def vc2007_state_c() -> TendonNetwork:
    return vc2007_state(0.65)   # EE-dominant: DI:EE ~ 0.54


# ---------------------------------------------------------------------------
# Legacy "simple tendon paths" presets (the comparison case)
# ---------------------------------------------------------------------------

def simple_three_tendon() -> TendonNetwork:
    """FP + FS + EE — three simple antagonist tendons, no intrinsics."""
    return TendonNetwork("FP+FS+EE", [FP, FS, EE])


def simple_paths_no_lu() -> TendonNetwork:
    """The 'simple tendon paths' approximation of VC2007 (EE, DI2, DI3 as
    independent fixed-direction tendons). The paper's point is that this
    model misses the network's switching behavior."""
    return TendonNetwork("simple-paths VC2007", [EE, DI2, DI3])


def simple_paths_with_lu() -> TendonNetwork:
    """Simple-paths VC2007 + LU."""
    return TendonNetwork("simple-paths VC2007 + LU", [EE, DI2, DI3, LU])


def full_finger() -> TendonNetwork:
    """All six tendons treated as fixed-direction (simple paths)."""
    return TendonNetwork("full finger (simple)", [FP, FS, EE, DI2, DI3, LU])


PRESETS = {
    # VC2007 actual model (hood-routed, three states)
    "state_a": vc2007_state_a,
    "state_b": vc2007_state_b,
    "state_c": vc2007_state_c,
    # Comparison: simple tendon paths
    "simple":       simple_three_tendon,
    "simple_paths": simple_paths_no_lu,
    "simple_lu":    simple_paths_with_lu,
    "full":         full_finger,
    # Ideal case: full 5-tendon activation sweep through the hood (returns
    # a pre-computed FeasibleTorqueSet, not a TendonNetwork).
    "ideal":        lambda: ideal_finger_set(),
}


# ---------------------------------------------------------------------------
# "Ideal finger" — union of reachable torques across the whole activation
# space, with FP + FS direct and EE + DI2 + DI3 routed through the hood.
# This approximates "what the nervous system can in principle ask the finger
# to produce", giving the maximum octant coverage the framework supports.
# ---------------------------------------------------------------------------

def _ideal_finger_routing(forces):
    """5-tendon torque function for sample_feasible_set.

    forces = [f_FP, f_FS, f_EE, f_DI2, f_DI3]. FP and FS contribute directly
    via their fixed moment arms; EE/DI tensions route through the Winslow
    rhombus to produce extension at PIP/DIP plus direct MCP effects.
    """
    f_fp, f_fs, f_ee, f_di2, f_di3 = forces

    # Direct extrinsic flexor contributions
    tau = f_fp * FP.moment_arms + f_fs * FS.moment_arms

    # Extensor system through the hood
    f_di_total = f_di2 + f_di3
    tau_mcp_ext = -f_ee * R_EE_MCP + f_di_total * R_DI_MCP

    di_to_ee = f_di_total / (f_ee + 1e-9)
    p_frac = hood_proximal_fraction(di_to_ee)
    total_slip = NETWORK_TRANSMISSION * (f_ee + f_di_total)
    f_prox = p_frac * total_slip
    f_term = (1.0 - p_frac) * total_slip

    tau_pip_ext = -f_prox * R_PROXIMAL_SLIP_PIP
    tau_dip_ext = -f_term * R_TERMINAL_SLIP_DIP

    tau = tau + np.array([tau_mcp_ext, tau_pip_ext, tau_dip_ext])
    return tau


def ideal_finger_set() -> FeasibleTorqueSet:
    """All 5 modeled muscles, hood-routed, swept across the activation space.
    Returns a pre-computed FeasibleTorqueSet (not a TendonNetwork) since the
    polytope comes from sampling, not fixed-direction Minkowski summation.
    """
    base = TendonNetwork("ideal finger", [FP, FS, EE, DI2, DI3])
    fts = sample_feasible_set(base, _ideal_finger_routing, n_samples_per_axis=5)
    # Pretty-print name (overrides "ideal finger (sampled)")
    fts.network_name = "ideal finger (hood-swept)"
    return fts
