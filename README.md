# Tendon-Driven Fingers — Research + Project

Undergraduate research notebook and project repo for replicating and
extending Valero-Cuevas et al. 2007, *"The Tendon Network of the Fingers
Performs Anatomical Computation at a Macroscopic Scale"* (IEEE TBME), with
the eventual goal of a physical tendon-driven finger prototype.

## What's in here

- **[`feasible-torque-set/`](feasible-torque-set/)** — Python tool for
  computing and visualizing the 3D feasible torque set of tendon-driven
  finger models. Interactive viewers, hood-routing simulation, octant
  reachability matrix with hover-tooltipped biomechanical descriptions.
  See its [README](feasible-torque-set/README.md) for usage.
- **Research journal** — markdown notes at the root and in topic folders,
  managed in Obsidian and auto-synced via the Obsidian Git plugin.

## Quick start (tool only)

```bash
cd feasible-torque-set
pip install --user numpy scipy matplotlib
python3 main.py
```

## Project status

Currently mid-undergrad (sophomore, ME primary + CS secondary, Auburn).
Reading the Valero-Cuevas et al. 2007 paper now, with several more
biomechanics / tendon-driven-robotics papers queued. A physical v1
prototype is planned for early fall (FP + FS + EE, 2-tendon Bowden-cable
drive) once vault access and 3D-printer time are available.

## Key result from the tool so far

The hood-swept "ideal finger" model reaches **5 of 8 octants** in
(τ\_MCP, τ\_PIP, τ\_DIP) torque space. The 3 unreachable octants are
`-++` (hook grip), `-+-` (boutonniere), and `--+` (mallet finger).

Two of these (boutonniere, mallet) are classical IP-joint deformities —
postures real fingers *also* can't actively produce, because of the same
anatomical coupling that the model encodes geometrically via non-negative
tendon activations. That match is the interesting result.

The model also has two known errors that don't match real biomechanics:

- **Hook grip (`-++`) is unreachable in the model** but trivially
  achievable in real life — caused by missing palmar interossei + no
  passive-MCP mode in the framework.
- **Swan-neck (`+-+`) is reachable in the model** but shouldn't be (it's
  the third classical IP deformity) — caused by the model treating
  proximal-slip and terminal-slip outputs as independent, missing the
  oblique retinacular ligament coupling.

Both are honest framework limitations diagnosed by specific missing
biomechanics. The full story isn't "3 unreachable octants map perfectly
to 3 deformities" — it's "2 of 3 deformity octants are correctly
unreachable, and the framework's 2 known errors are each diagnosable
back to a specific missing anatomical structure."
