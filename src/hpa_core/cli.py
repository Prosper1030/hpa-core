"""Thin command line for the dual-beam kernel.

Deliberately limited to three steps:

    serialization -> kernel -> presentation

It builds nothing. There is no configuration, no aircraft construction, no
material database and no workflow logic here, and none should be added: those
belong to the application layer that produces the model in the first place.

    hpa-core inspect model.json
    hpa-core run model.json
    hpa-core run model.json --mode dual_beam_robustness --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hpa_core.dual_beam_mainline import (
    load_dual_beam_mainline_model,
    run_dual_beam_mainline_kernel,
)

__all__ = ["main", "result_summary"]


def result_summary(result: Any) -> dict[str, Any]:
    """Reduce a kernel result to the handful of numbers a reader wants first."""
    report = result.report
    recovery = result.recovery
    feasibility = result.feasibility
    return {
        "mode": result.mode_definition.mode.value,
        "root_bc": result.constraint_mode.root_bc.value,
        "wire_bc": result.constraint_mode.wire_bc.value,
        "link_mode": result.constraint_mode.link_mode.value,
        "tip_deflection_main_m": report.tip_deflection_main_m,
        "tip_deflection_rear_m": report.tip_deflection_rear_m,
        "max_vertical_displacement_m": report.max_vertical_displacement_m,
        "max_vm_main_pa": recovery.max_vm_main_pa,
        "max_vm_rear_pa": recovery.max_vm_rear_pa,
        "failure_index": recovery.failure_index,
        "spar_tube_mass_half_kg": recovery.spar_tube_mass_half_kg,
        "spar_tube_mass_full_kg": recovery.spar_tube_mass_full_kg,
        "root_reaction_main_fz_n": float(report.root_reaction_main_n[2]),
        "root_reaction_rear_fz_n": float(report.root_reaction_rear_n[2]),
        "wire_reaction_total_n": report.wire_reaction_total_n,
        "max_wire_tension_n": recovery.max_wire_tension_n,
        "max_wire_tension_utilization": recovery.max_wire_tension_utilization,
        "analysis_succeeded": feasibility.analysis_succeeded,
        "overall_hard_feasible": feasibility.overall_hard_feasible,
        "hard_failures": list(feasibility.hard_failures),
    }


def _print_summary(summary: dict[str, Any]) -> None:
    print(f"mode                     {summary['mode']}")
    print(f"root BC / wire BC        {summary['root_bc']} / {summary['wire_bc']}")
    print(f"link mode                {summary['link_mode']}")
    print()
    print(f"tip deflection main      {summary['tip_deflection_main_m'] * 1e3:12.3f} mm")
    print(f"tip deflection rear      {summary['tip_deflection_rear_m'] * 1e3:12.3f} mm")
    print(f"max von Mises main       {summary['max_vm_main_pa'] / 1e6:12.3f} MPa")
    print(f"max von Mises rear       {summary['max_vm_rear_pa'] / 1e6:12.3f} MPa")
    print(f"failure index            {summary['failure_index']:12.6f}   (<= 0 passes)")
    print(f"spar tube mass full      {summary['spar_tube_mass_full_kg']:12.4f} kg")
    print(f"max wire tension         {summary['max_wire_tension_n']:12.2f} N")
    print()
    print(f"analysis succeeded       {summary['analysis_succeeded']}")
    print(f"overall hard feasible    {summary['overall_hard_feasible']}")
    if summary["hard_failures"]:
        print(f"hard failures            {summary['hard_failures']}")


def _cmd_inspect(args: argparse.Namespace) -> int:
    model = load_dual_beam_mainline_model(args.model)
    info = {
        "model": str(args.model),
        "nodes_per_spar": int(model.y_nodes_m.size),
        "half_span_m": float(model.y_nodes_m[-1]),
        "main_segments": int(model.main_t_seg_m.size),
        "rear_segments": int(model.rear_t_seg_m.size),
        "joint_nodes": list(model.joint_node_indices),
        "wire_nodes": list(model.wire_node_indices),
        "gravity_scale": model.gravity_scale,
    }
    if args.json:
        print(json.dumps(info, indent=2, sort_keys=True))
    else:
        for key, value in info.items():
            print(f"{key:24s} {value}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    model = load_dual_beam_mainline_model(args.model)
    result = run_dual_beam_mainline_kernel(model=model, mode=args.mode)
    summary = result_summary(result)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        _print_summary(summary)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hpa-core", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="describe a serialized model without solving")
    inspect.add_argument("model", type=Path)
    inspect.add_argument("--json", action="store_true")
    inspect.set_defaults(func=_cmd_inspect)

    run = sub.add_parser("run", help="solve a serialized model and summarise the result")
    run.add_argument("model", type=Path)
    run.add_argument("--mode", default="dual_beam_production")
    run.add_argument("--json", action="store_true")
    run.set_defaults(func=_cmd_run)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
