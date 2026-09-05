"""Run the dual-beam kernel on the bundled model snapshot and print a summary.

This is the shortest possible end-to-end use of hpa-core:

    serialization -> kernel -> presentation

It needs nothing but hpa-core's own dependencies (NumPy and SciPy). There is no
configuration, no aircraft definition, no material database and no optimizer:
the model is loaded from a fixture that some application layer produced earlier.

    python examples/run_snapshot.py
    python examples/run_snapshot.py --mode dual_beam_robustness
"""

from __future__ import annotations

import argparse
from pathlib import Path

from hpa_core.dual_beam_mainline import (
    load_dual_beam_mainline_model,
    run_dual_beam_mainline_kernel,
)

DEFAULT_MODEL = (
    Path(__file__).resolve().parents[1]
    / "tests/fixtures/dual_beam_mainline/track_s_rerun_snapshot_model.json"
)


def summarise(result) -> str:
    """Render the parts of a kernel result a human usually wants first."""
    report = result.report
    recovery = result.recovery
    feasibility = result.feasibility
    lines = [
        f"mode                     {result.mode_definition.mode.value}",
        (
            f"root BC / wire BC        {result.constraint_mode.root_bc.value}"
            f" / {result.constraint_mode.wire_bc.value}"
        ),
        f"link mode                {result.constraint_mode.link_mode.value}",
        "",
        "-- deflection ------------------------------------------------",
        f"tip deflection main      {report.tip_deflection_main_m * 1e3:12.3f} mm",
        f"tip deflection rear      {report.tip_deflection_rear_m * 1e3:12.3f} mm",
        (
            f"max vertical             {report.max_vertical_displacement_m * 1e3:12.3f} mm"
            f"  (spar {report.max_vertical_spar}, node {report.max_vertical_node})"
        ),
        "",
        "-- stress and mass -------------------------------------------",
        f"max von Mises main       {recovery.max_vm_main_pa / 1e6:12.3f} MPa",
        f"max von Mises rear       {recovery.max_vm_rear_pa / 1e6:12.3f} MPa",
        f"failure index            {recovery.failure_index:12.6f}   (<= 0 passes)",
        f"spar tube mass half      {recovery.spar_tube_mass_half_kg:12.4f} kg",
        f"spar tube mass full      {recovery.spar_tube_mass_full_kg:12.4f} kg",
        "",
        "-- reactions and wires ---------------------------------------",
        # Root reactions are 6-DOF vectors [Fx, Fy, Fz, Mx, My, Mz]; Fz is the
        # vertical force, which is the number a reader usually wants first.
        f"root reaction main Fz    {float(report.root_reaction_main_n[2]):12.2f} N",
        f"root reaction rear Fz    {float(report.root_reaction_rear_n[2]):12.2f} N",
        f"wire reaction total      {report.wire_reaction_total_n:12.2f} N",
        (
            f"max wire tension         {recovery.max_wire_tension_n:12.2f} N"
            f"  (utilisation {recovery.max_wire_tension_utilization:.3f})"
        ),
        "",
        "-- feasibility -----------------------------------------------",
        f"analysis succeeded       {feasibility.analysis_succeeded}",
        f"overall hard feasible    {feasibility.overall_hard_feasible}",
    ]
    if feasibility.hard_failures:
        lines.append(f"hard failures            {list(feasibility.hard_failures)}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "model", nargs="?", type=Path, default=DEFAULT_MODEL,
        help="serialized DualBeamMainlineModel (defaults to the bundled snapshot)",
    )
    parser.add_argument(
        "--mode", default="dual_beam_production",
        help="analysis mode name (default: dual_beam_production)",
    )
    args = parser.parse_args()

    model = load_dual_beam_mainline_model(args.model)
    print(f"model                    {args.model.name}")
    print(f"nodes per spar           {model.y_nodes_m.size}")
    print(f"half span                {model.y_nodes_m[-1]:.4f} m")
    print()

    result = run_dual_beam_mainline_kernel(model=model, mode=args.mode)
    print(summarise(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
