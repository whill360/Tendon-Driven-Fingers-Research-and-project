# Tendon Driven Fingers Research + Project

My undergrad research notes and project repo, working through *"The Tendon Network of the Fingers Performs Anatomical Computation at a Macroscopic Scale"* (Valero-Cuevas et al., 2007, IEEE TBME) plus prior work from Shirafuji and others. End goal: a physical tendon driven finger prototype.

## What's in here

- **[`feasible-torque-set/`](feasible-torque-set/)**: Python tool that computes and visualizes the 3D feasible torque set of tendon driven finger models. Interactive viewers, hood routing sim, octant reachability matrix with biomechanical tooltips. Usage in its [README](feasible-torque-set/README.md).
- **Research journal**: markdown notes at the root and in topic folders, kept in Obsidian.

## Quick start (tool only)

```bash
cd feasible-torque-set
pip install --user numpy scipy matplotlib
python3 main.py
```

## Status

Junior summer at Auburn (ME primary, CS secondary). Reading the Valero-Cuevas 2007 paper with more biomechanics and tendon driven robotics papers queued. Physical v1 (FP + FS + EE, 2 tendon Bowden cable drive) planned for early fall once I get vault access and printer time.

## Key result so far

The hood swept "ideal finger" model hits **5 of 8 octants** in (τ\_MCP, τ\_PIP, τ\_DIP) torque space. The 3 it misses: `-++` (hook grip), `-+-` (boutonniere), `--+` (mallet finger).

Boutonniere and mallet are real IP joint deformities, postures real fingers *also* can't actively make, thanks to the same anatomical coupling the model captures geometrically via nonnegative tendon activations.

Two spots where the model disagrees with biology:

- **Hook grip (`-++`)**: unreachable here, trivial in real life. Probably missing palmar interossei plus no way to treat MCP as a passive joint.
- **Swan neck (`+-+`)**: reachable here but shouldn't be (third classical IP deformity). The model treats proximal slip and terminal slip outputs as independent (they aren't), missing how the oblique retinacular ligament ties PIP and DIP motion together.

Both have clear biomechanical explanations.
