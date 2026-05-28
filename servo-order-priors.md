# Servo order — priors & double-check sheet

**Date:** 2026-05-27
**Purpose:** Hand-off to the Claude holding the full tendon-driven-finger project context.
Audit the reasoning below against the actual project plan BEFORE the order is placed.
Everything here was produced by a session that only knew the project from the
"Research roadmap — reading queue + lab pitch" doc, not the full planning passes.

---

## The order as configured (ROBOTIS US checkout)

| Item | Qty | Line total |
|---|---|---|
| DYNAMIXEL XC330-M288-T | 4 | $413.56 |
| DYNAMIXEL U2D2 | 1 | $36.92 |
| Subtotal | | $450.48 |
| Sales tax | | $34.91 |
| Shipping | | not yet calculated ("--") |
| **Total (USD)** | | **$485.39** |

Account: lanyhill05@gmail.com · Ship-to: United States · Budget ceiling: ~$2k → this is ~24% of it.

---

## The decision

Buy **4× XC330-M288-T + 1× U2D2** now from ROBOTIS US. Use case is a **single
tendon-driven pointer finger** (2-tendon Bowden-cable prototype), NOT a full hand.

## Why this, not the alternatives (reasoning priors — check these)

1. **Order early ONLY the lead-time-risky part.** The Dynamixel is the part with
   stock risk; Feetech STS3215 (ORCA's BOM) is never out of stock, so it can be a
   zero-risk August decision. Front-running the Dynamixel is the entire point of
   ordering now. → *Confirmed in practice: the U2D2 is the actual bottleneck (see caveats).*
2. **Torque headroom so the actuator isn't the confound.** The core experiment is
   Bowden transmission loss (Palli) vs. FTS force prediction. A weak servo widens the
   "my optimizer says it works / the cable just stretched" gap in a way you can't
   diagnose. XC330's 0.92 Nm metal-gear gives margin so misses attribute to
   transmission, not the motor.
3. **XL330 Lite ($24) rejected:** plastic gears strip under the repeated load-cycling
   of iterative tensioning; false economy for a research rig.
4. **XM430 ($310) rejected:** 4.1 Nm is ~4× what one finger needs, it's 12V (separate
   PSU), and physically bulky (~82 g) — awkward at finger scale. Revisit only if
   scaling to a multi-finger / long-Bowden forearm rig.
5. **Quantity = 4:** covers a 2-tendon true-antagonist finger on up to 2 actuated
   joints, OR a 1-tendon+spring v0 with 3 spares. Spares hedge a fried unit mid-summer.

## Verified facts (as of 2026-05-27)

XC330-M288-T: **5V** input, **0.92 Nm** stall, 1.8A stall current, metal gear, 4096-step,
current-based position control supported. $103.39 ea at ROBOTIS US, in stock.
U2D2: $36.92 at ROBOTIS US, **backordered — ships mid-June**. USB-C version.

For comparison: XL330-M288-T (5V, 0.52 Nm, plastic, ~$24) · XM430-W350-T (12V, 4.1 Nm, ~$310).

---

## Assumptions to verify against the full plan (the actual double-check)

- [ ] **Joint/tendon count.** Qty 4 assumes ≤2 actuated joints with antagonist pairs,
      or fewer joints + spares. If the real plan is a 3-joint fully-antagonist finger,
      4 is short (need ~6). If v0/v1 stays single-joint single-tendon+spring, 4 is
      generous (good — spares). **Confirm the Birglen-scheme decision hasn't already
      been made in a direction that changes the count.**
- [ ] **Voltage rail = 5V.** The cart has the **M288 (5V)** variant. There is an
      11.1V sibling (XC330-T288-T, same 0.92 Nm class). If the bench/power plan is
      built around 12V for other reasons, flag the mismatch now — don't feed 5V motor
      12V. LEAP runs the M288 at 5V via its power hub, which is the validated config.
- [ ] **Pulley/spool radius gives adequate tendon tension.** 0.92 Nm ÷ spool radius =
      tendon tension. At 5 mm → 184 N; at 10 mm → 92 N. Both fine for a finger, but
      this depends on the CAD that isn't drawn yet. Just sanity-check once the spool
      is designed.
- [ ] **Current-based control is the intended tension-control path** for FTS force
      validation (it's supported; confirm it's the plan, not external load cells).

## Known caveats / deliberately NOT in this order

- **U2D2 backorder (mid-June).** It's the $37 adapter, not the $100 servos, that's the
  bottleneck. Faster US sources worth checking for in-stock: Trossen Robotics, RobotShop,
  Mouser, DigiKey. Even worst case mid-June lands before the August assemble-month, so
  it doesn't block the v0 timeline either way.
- **5V bench supply needed** (the XC330 is 5V — do NOT use 12V). Never out of stock; buy anytime.
- **JST / Dynamixel daisy-chain cables** — buy anytime, not stock-limited.
- **Feetech STS3215 path stays open.** ORCA's BOM uses it (~$15/ea); if after the ORCA
  re-read the design pivots to Feetech, that's a no-risk August buy. Buying Dynamixel now
  does not foreclose it — they just don't physically interchange.

---

# Full-context audit (2026-05-27, session holding the complete planning history)

**Verdict: the cart is correctly specced for the Dynamixel/LEAP path and won't be
wasted — but the sequencing is backwards relative to the roadmap. Decision: HOLD the
buy until after the ORCA read.**

## The four checklist items, resolved

- [x] **Joint/tendon count (Qty 4) — PASS.** The prototype is committed to **2 tendons
      total** (2-tendon Bowden-cable), not 2-per-joint. Max draw = 2 servos → 4 = 2
      working + 2 spares. The open Birglen scheme decision does NOT create a shortfall:
      even the most servo-hungry near-term config (2-tendon antagonist, 2 joints) is
      covered by 4, and the committed September v0 (single-tendon + spring) leaves 3
      spares. Not short. Safe.
- [x] **Voltage rail = 5V — PASS.** No 12V dependency anywhere in the plan. M288 (5V)
      matches LEAP's validated config (paper #2 in the queue). Buy a 5V bench supply,
      not 12V.
- [x] **Spool radius / tendon tension — PASS (sanity-check later).** 92–184 N is 2–4×
      the ~40 N regime the FTS work (VC2007) operates at — 30% of muscle capacity. The
      servo will not be the confound, which is the point of the torque-headroom
      argument. Re-check once spool CAD exists.
- [x] **Current-based control — PARTIAL GAP (BOM, not servo).** Fine as the command/
      *input* path. But the core experiment (Bowden loss vs. FTS prediction) needs
      BOTH ends: input tension (motor current → torque → spool) AND delivered output
      tension. Current control gives only the input side. VC2007 measured output with
      buckle transducers + a 6-axis F/T sensor. **Add an independent output-side force
      sensor** (inline tendon load cell or fingertip F/T sensor) to the BOM now so it's
      not a September surprise. Does not change the servo order.

## The issue not on the original checklist (the real one)

**This $485 bets entirely on the Dynamixel/LEAP ecosystem — placed BEFORE the ORCA
read, which is the #1 June task and the thing meant to decide the build direction.**

- ORCA (the stated north star, the paper that got the project started *because it was
  cheap*) runs **Feetech STS3215 at ~$15/ea**, never out of stock. XC330 is **$103/ea**
  — 7×. Feetech is a big part of why ORCA is cheap.
- Both cart items (XC330 + U2D2) are Dynamixel-specific; the U2D2 doesn't work with
  Feetech. So this is a directional bet on LEAP, not a neutral hedge.
- The lead-time argument partly defeats itself: the **XC330 is in stock today**, so it
  can be ordered after the ORCA read and still make the August assembly window. The
  only backordered item (U2D2, $37) is itself Dynamixel-only, so it doesn't hedge the
  Feetech path either.

## Recommendation (adopted: HOLD)

1. **Read ORCA first, then order.** One evening, already #1 in the queue, directly
   settles the $103-vs-$15 servo-ecosystem question. If ORCA → Feetech, save ~$430 and
   stay closer to the design that inspired the project. If ORCA confirms Dynamixel
   (defensible — better metal gears + current control for a research rig), order this
   exact cart with confidence.
2. **Order now only as a conscious LEAP-path commitment**, not as a "lead-time hedge"
   (there's little lead time to hedge while the XC330 is in stock).
3. **Add an output-side force sensor to the BOM** regardless of servo choice — required
   for the transmission-loss experiment.

**Status: buy on hold pending ORCA read (June).**
