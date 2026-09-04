"""hpa-core: the trusted dual-beam structural analysis kernel.

This package holds the computational kernel that is mature enough that
experimental development must not modify it in passing. It depends only on
NumPy and SciPy, and it never reads configuration, files, or aircraft
definitions: callers hand it an already-built `DualBeamMainlineModel`.

The application layer that builds that model lives outside this package.
"""

from importlib import import_module

__version__ = "0.1.0"

__all__ = [
    "G_STANDARD",
    "DualBeamMainlineModel",
    "DualBeamMainlineResult",
    "load_dual_beam_mainline_model",
    "run_dual_beam_mainline_kernel",
]

_LAZY_IMPORTS = {
    "G_STANDARD": ("hpa_core.constants", "G_STANDARD"),
    "DualBeamMainlineModel": ("hpa_core.dual_beam_mainline.types", "DualBeamMainlineModel"),
    "DualBeamMainlineResult": ("hpa_core.dual_beam_mainline.types", "DualBeamMainlineResult"),
    "load_dual_beam_mainline_model": (
        "hpa_core.dual_beam_mainline.serialization",
        "load_dual_beam_mainline_model",
    ),
    "run_dual_beam_mainline_kernel": (
        "hpa_core.dual_beam_mainline.kernel",
        "run_dual_beam_mainline_kernel",
    ),
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
