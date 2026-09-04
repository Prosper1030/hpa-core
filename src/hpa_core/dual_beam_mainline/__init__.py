"""Physics-first dual-beam mainline analysis kernel."""

from importlib import import_module

__all__ = [
    "AnalysisModeDefinition",
    "AnalysisModeName",
    "AnalysisOwnership",
    "BeamLine",
    "ConstraintAssemblyResult",
    "DualBeamConstraintMode",
    "DualBeamMainlineModel",
    "DualBeamMainlineResult",
    "EquivalentGateResult",
    "ExplicitWireSupportResult",
    "FeasibilitySummary",
    "GeometryValidityMargins",
    "GlobalObservableReadinessResult",
    "LinkMode",
    "LoadSplitResult",
    "NumericalConsistencyResult",
    "OptimizerFacingMetrics",
    "ReactionRecoveryResult",
    "RecoveryResult",
    "ReportMetrics",
    "RootBCMode",
    "SmoothAggregationResult",
    "SmoothScaleConfig",
    "TorqueInputDefinition",
    "TorqueReferenceMode",
    "WireBCMode",
    "WireSupportValidityResult",
    "dump_dual_beam_mainline_model",
    "get_analysis_mode_definition",
    "load_dual_beam_mainline_model",
    "run_dual_beam_mainline_kernel",
]

_KERNEL_MODULE = "hpa_core.dual_beam_mainline.kernel"
_SERIALIZATION_MODULE = "hpa_core.dual_beam_mainline.serialization"
_TYPES_MODULE = "hpa_core.dual_beam_mainline.types"
_LAZY_IMPORTS = {
    "run_dual_beam_mainline_kernel": (_KERNEL_MODULE, "run_dual_beam_mainline_kernel"),
    "dump_dual_beam_mainline_model": (
        _SERIALIZATION_MODULE,
        "dump_dual_beam_mainline_model",
    ),
    "load_dual_beam_mainline_model": (
        _SERIALIZATION_MODULE,
        "load_dual_beam_mainline_model",
    ),
    "AnalysisModeDefinition": (_TYPES_MODULE, "AnalysisModeDefinition"),
    "AnalysisModeName": (_TYPES_MODULE, "AnalysisModeName"),
    "AnalysisOwnership": (_TYPES_MODULE, "AnalysisOwnership"),
    "BeamLine": (_TYPES_MODULE, "BeamLine"),
    "ConstraintAssemblyResult": (_TYPES_MODULE, "ConstraintAssemblyResult"),
    "DualBeamConstraintMode": (_TYPES_MODULE, "DualBeamConstraintMode"),
    "DualBeamMainlineModel": (_TYPES_MODULE, "DualBeamMainlineModel"),
    "DualBeamMainlineResult": (_TYPES_MODULE, "DualBeamMainlineResult"),
    "EquivalentGateResult": (_TYPES_MODULE, "EquivalentGateResult"),
    "ExplicitWireSupportResult": (_TYPES_MODULE, "ExplicitWireSupportResult"),
    "FeasibilitySummary": (_TYPES_MODULE, "FeasibilitySummary"),
    "GeometryValidityMargins": (_TYPES_MODULE, "GeometryValidityMargins"),
    "GlobalObservableReadinessResult": (_TYPES_MODULE, "GlobalObservableReadinessResult"),
    "LinkMode": (_TYPES_MODULE, "LinkMode"),
    "LoadSplitResult": (_TYPES_MODULE, "LoadSplitResult"),
    "NumericalConsistencyResult": (_TYPES_MODULE, "NumericalConsistencyResult"),
    "OptimizerFacingMetrics": (_TYPES_MODULE, "OptimizerFacingMetrics"),
    "ReactionRecoveryResult": (_TYPES_MODULE, "ReactionRecoveryResult"),
    "RecoveryResult": (_TYPES_MODULE, "RecoveryResult"),
    "ReportMetrics": (_TYPES_MODULE, "ReportMetrics"),
    "RootBCMode": (_TYPES_MODULE, "RootBCMode"),
    "SmoothAggregationResult": (_TYPES_MODULE, "SmoothAggregationResult"),
    "SmoothScaleConfig": (_TYPES_MODULE, "SmoothScaleConfig"),
    "TorqueInputDefinition": (_TYPES_MODULE, "TorqueInputDefinition"),
    "TorqueReferenceMode": (_TYPES_MODULE, "TorqueReferenceMode"),
    "WireBCMode": (_TYPES_MODULE, "WireBCMode"),
    "WireSupportValidityResult": (_TYPES_MODULE, "WireSupportValidityResult"),
    "get_analysis_mode_definition": (_TYPES_MODULE, "get_analysis_mode_definition"),
}


def _import_submodule(name: str):
    """Return a submodule of this package, or None when it does not exist."""
    qualified_name = f"{__name__}.{name}"
    try:
        return import_module(qualified_name)
    except ModuleNotFoundError as exc:
        if exc.name == qualified_name:
            return None
        raise


def __getattr__(name: str):
    target = _LAZY_IMPORTS.get(name)
    if target is None:
        submodule = _import_submodule(name)
        if submodule is None:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
        globals()[name] = submodule
        return submodule
    module_name, attribute_name = target
    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
