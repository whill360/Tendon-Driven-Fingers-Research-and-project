# Research roadmap — reading queue + lab pitch

Planning doc for the tendon-driven finger project. Two parts: (1) the finalized
summer reading queue with per-paper extraction targets, and (2) the lab-placement
strategy. Synthesized across two Claude planning passes; the analysis section at
the bottom records *why* the queue landed where it did.

## Where I'm starting from

- Read **Shirafuji, Ikemoto & Hosoda 2014, IJRR** — *Development of a Tendon-Driven
  Robotic Finger for an Anthropomorphic Robotic Hand* (lumbrical equivalent +
  virtual tendon Jacobian for the extensor mechanism). Note: filename says 2012,
  but the journal version is 2014 — cite as 2014.
- Read **Valero-Cuevas et al. 2007, IEEE TBME** — *The Tendon Network of the Fingers
  Performs Anatomical Computation at a Macroscopic Scale*.
- Built a Python **feasible-torque-set tool** (`feasible-torque-set/`) that
  replicates VC2007's 5/8-octant reachability result and maps the three
  unreachable octants to the three classical IP-joint deformities (mallet,
  boutonniere, swan-neck). Has both fixed-direction (simple-paths) and hood-swept
  (deformable-network) modes.

## Project commitments

- Physical prototype: **2-tendon Bowden-cable single finger** → iterate → hand.
- Goal: research pitch by **fall** → lab placement → finger v1.
- Resources: RTX 4090, printer lab, SolidWorks + Fusion, ~$2k worst-case
  out-of-pocket budget.
- Auburn ME + CS sophomore.

---

## The 8-paper queue

Read in this order. Three flagged **read 2×**: ORCA (the *what*), Inouye (the *why*
of routing), Palli (the *why* of transmission). Those three cover target, design
optimization, and what physical reality does to the design.

### 1. ORCA — Toshimitsu et al. 2025 · **read 2×**
*ORCA: An Open-Source, Reliable, Cost-Effective, Anthropomorphic Robotic Hand for
Uninterrupted Dexterous Task Learning.* ETH Zurich SRL.
- [arXiv PDF](https://arxiv.org/pdf/2504.04259) · [abstract](https://arxiv.org/abs/2504.04259) · [lab page + CAD/BOM/tutorials](https://srl.ethz.ch/orcahand.html)
- **Extract:** BOM, servo selection, joint structure, abduction mechanism, popping
  joints, tensioning system. This should specify my parts list. Read the lab page
  alongside the paper — it has the practical build detail the paper compresses.

### 2. LEAP Hand — Shaw, Agarwal & Pathak 2023 (RSS)
*LEAP Hand: Low-Cost, Efficient, and Anthropomorphic Hand for Robot Learning.*
CMU. + 30-min skim of LEAP v2 (2024).
- [RSS PDF](https://www.roboticsproceedings.org/rss19/p089.pdf) · [v1.leaphand.com](https://v1.leaphand.com/) · [v2.leaphand.com](https://v2.leaphand.com/)
- **Extract:** comparative design choices vs. ORCA — what's the same, what differs,
  what each lab's choice reveals about trade-offs. v2 skim: what got simplified
  v1→v2 ($200, 8-DoF, hybrid rigid-soft) and why. Lesson on what's worth
  simplifying in a v1.

### 3. Highly Biomimetic Hand — Xu & Todorov 2016 (ICRA)
*Design of a Highly Biomimetic Anthropomorphic Robotic Hand Towards Artificial Limb
Regeneration.* U. Washington.
- [ACM/IEEE](https://dl.acm.org/doi/abs/10.1109/ICRA.2016.7487528) · [Semantic Scholar (PDF)](https://www.semanticscholar.org/paper/Design-of-a-highly-biomimetic-anthropomorphic-hand-Xu-Todorov/a4a9eff18b74cd9c2518c9f3ef164b4aab3ac276)
- **Extract:** which anatomical details actually change manipulation capability vs.
  which are fetish. They laser-cut the extensor hood my FTS tool simulates — fun
  cross-check. Tells me what to keep and what to skip when going anatomical.

### 4. FTS formalism — Valero-Cuevas 2005 (J. Biomechanics 38:673–684)
*An integrative approach to the biomechanical function and neuromuscular control of
the fingers.*
- [ScienceDirect (Auburn proxy)](https://www.sciencedirect.com/science/article/abs/pii/S0021929004001927) · [ResearchGate](https://www.researchgate.net/publication/8020516_An_integrative_approach_to_the_biomechanical_function_and_neuromuscular_control_of_the_fingers)
- **Extract:** formal FTS vocabulary — basis vectors, Minkowski operations,
  feasible-force vs. feasible-torque. Lets me defend design choices in the
  language of the field instead of "my tool says it works."
- *Supplement (optional):* Valero-Cuevas 2015, *Fundamentals of Neuromechanics*
  (Springer Tracts BIB vol. 8), ch. 4–6 — canonical FTS reference. Pull via Auburn
  [SpringerLink](https://link.springer.com/book/10.1007/978-1-4471-6747-1) if
  available. Useful but not obligatory for the pitch.

### 5. Bowden transmission — Palli & Melchiorri 2006 (ICRA) · **read 2×**
*Model and Control of Tendon-Sheath Transmission Systems.*
- [IEEE Xplore](https://ieeexplore.ieee.org/document/1641838/) · [ResearchGate PDF](https://www.researchgate.net/publication/221074092_Model_and_Control_of_Tendon-sheath_Transmission_Systems)
- Follow-up if useful: Palli, Borghesan & Melchiorri 2009/2012, *Tendon-based
  transmission systems for robotic devices: models and control algorithms*.
- **Extract:** tendon-sheath friction, hysteresis, pretension behavior, LuGre
  dynamic friction model. My FTS tool assumes lossless transmission; the actual
  Bowden cable will not be. **Read this BEFORE cutting cable, not after.** This is
  the gap between "my routing optimizer says this works" and "the cable just
  stretched."

### 6. FTS as design tool — Inouye & Valero-Cuevas 2014 (IJRR) · **read 2×**
*Anthropomorphic tendon-driven robotic hands can exceed human grasping capabilities
following optimization.*
- [Valero lab PDF](https://valerolab.org/Papers/2013_IJRR_Inouye_Anthropomorphic_Hand.pdf) · [SAGE](https://journals.sagepub.com/doi/10.1177/0278364913504247)
- **Extract:** FTS-based optimization methodology for tendon routing. This is the
  method that turns my FTS tool from learning exercise → design optimizer. The
  *why* behind which routing to build instead of guessing.

### 7. Underactuation — Birglen, Laliberté & Gosselin 2008 (Springer)
*Underactuated Robotic Hands*, Springer Tracts in Advanced Robotics vol. 40
(kinematics + force analysis chapters).
- [SpringerLink (Auburn proxy)](https://link.springer.com/book/10.1007/978-3-540-77459-4)
- **Extract:** which 2-tendon scheme to actually build — true antagonist vs.
  antagonist-spring vs. coupling tendon. Directly informs the core mechanical
  decision of the prototype.

### 8. Rigid-soft synthesis — 2024 (scan-only)
*Biomimetic rigid-soft finger design for highly dexterous and adaptive robotic
hands.*
- [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12017302/)
- **Extract:** when to use soft vs. rigid components, ligament placement, elastic
  tendon trade-offs. Informs material/component choices. Scan, don't grind.

---

## FTS-tool action item (July, before re-reading #6)

Add a unit test that reproduces a published figure from Inouye 2014 (a Pareto front
or grasp-quality polytope). If the tool independently reproduces an Inouye result,
it has earned promotion from learning exercise → design optimizer — and becomes a
demonstrable artifact for the lab pitch. Do this **before** the Inouye re-read, not
after.

## Backlog (not in the summer queue)

- **Marjaninejad et al. 2019, Nature MI** — *Autonomous functional movements in a
  tendon-driven limb via limited experience.* Beautiful, but motor-babbling is a
  control-policy rabbit hole; the fall artifact is static FTS-validated routing,
  not a learning demo. Spring / lab-onboarding read.
- **Catalano et al. 2014, Pisa/IIT SoftHand (IJRR)** — alternative design school
  (synergistic underactuation). What I'm *not* building and why.
- **Garcia-Elias 1991 I+II; Leijnse 1995/97** — only matter for parameter-tuning
  the FTS sim or fixing its ORL-coupling gap. The physical prototype is Bowden,
  no hood — academic for now.
- **A dexterity benchmark paper** (ASTM/NIST) — for quantifying whether the
  prototype works, when I get there.

---

## Lab-pitch plan

The reading list is table stakes. Three things actually decide lab placement:

### 1. The FTS tool is the real asset
A sophomore who replicated VC2007's octant result in Python is uncommon. PIs hire on
demonstrated execution, not literacy. **Lead the pitch with the tool** — ideally a
60-second screen recording (octant hull rotating in 3D, deformity mappings
labeled). Reading list is trajectory, not credential.

### 2. Specificity beats polish
Generic "I want to work on tendon-driven hands" loses to "I read your 2023 paper on
X, here's the limitation in §IV.B, here's how my FTS tool addresses it, here's what
I'd want to learn from your group in one semester." **One pitch per PI.** Papers 1,
2, 4, 6 each suggest a different *kind* of lab — let the pitch follow from the lab.

### 3. A janky physical v0 by September is a force multiplier
A single-joint, single-tendon 3D-printed finger pulling against a spring with one
Dynamixel changes the conversation from "this person reads" to "this person ships."
Polished version can land by December; pitch-time prototype should exist by
September.

### Lever ranking (qualitative — ignore exact odds)
physical v0 > per-PI specificity > reading list > polish.
A reading queue + FTS demo + per-PI specific pitch + janky v0 is a strong package
at a reachable Auburn lab. Dropping the v0 weakens it most; dropping per-PI
specificity weakens it regardless of everything else.

### Action this week
**Order Dynamixels** (XC330 or XM430 class, 2–4 units) — *after* cross-checking
ORCA's BOM (srl.ethz.ch/orcahand.html) and LEAP's parts list (v1.leaphand.com) to
confirm the exact model. Servo lead times are the silent killer of summer build
plans; everything else can wait, parts can't.

### Fall sequencing
- **June** — Order servos. ORCA → LEAP → Xu & Todorov.
- **July** — VC2005 + Inouye-figure replication in the FTS tool. Single-joint
  mechanical sketch in SolidWorks.
- **August** — Palli (read-twice). Print + assemble v0 single-joint. First Bowden
  routing test. *Plan for one slip month here — first assembly always slips.*
- **September** — Inouye re-read with FTS-as-optimizer. Birglen for the 2-tendon
  scheme decision. Janky v0 working. Begin per-PI pitches.
- **October–November** — Rigid-soft scan. v0 → v1 iterations. Pitch meetings.
- **December** — Polished finger + written research pitch ready.

---

## Analysis — how the queue got here

Two planning passes. The notable revisions from pass 1 → pass 2:

- **Bowden transmission paper promoted from stretch → core read-twice.** Biggest
  catch. The FTS framework assumes lossless transmission; the committed prototype
  is Bowden-cable. Friction/hysteresis is exactly the gap between the tool's
  prediction and physical reality. Should be read before cutting cable.
- **Marjaninejad (Nature MI) demoted to backlog.** Right call for the fall artifact
  — learning-control doesn't change static tendon-routing design. Kept for spring.
- **Birglen underactuation added.** Directly informs the central mechanical
  decision (which 2-tendon scheme), which nothing else in the queue covered.
- **LEAP v2 folded into the LEAP v1 read** rather than a standalone slot — it's a
  workshop paper + website.
- **VC2005 kept** over a pure-recency pick: the right filter is load-bearing-ness,
  not recency. VC2005 is the formal FTS source the whole Valero tradition cites.
- **Yanagisawa/Shirafuji 2016 dropped** — sunk-cost only; the 2014 paper is the
  canonical statement and the follow-up doesn't change any design decision.

Caveats to hold onto: any "calibrated odds" percentages from the planning passes
were vibes, not data — keep the qualitative lever ranking, drop the numbers. And
verify servo models against the actual ORCA/LEAP BOMs before spending money; don't
trust a model number from a planning doc blind.
