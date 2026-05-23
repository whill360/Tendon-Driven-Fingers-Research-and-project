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
(τ\_MCP, τ\_PIP, τ\_DIP) torque space. The 3 unreachable octants
correspond exactly to the three classical IP-joint deformities — swan
neck (`+-+`), boutonniere (`-+-`), mallet (`--+`). The same anatomical
constraints that make those postures clinical *deformities* (rather than
volitional postures) are what make those octants unreachable in the model.
