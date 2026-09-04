"""Beam finite-element primitives used by the dual-beam kernel.

The four element routines keep their original private names because they are
complex-step differentiable and the migration must not rename them. Public
aliases are provided here so callers outside the package do not have to reach
for underscore-prefixed symbols.
"""

from hpa_core.fem.elements import (
    _cs_norm,
    _has_only_finite_values,
    _rotation_matrix,
    _timoshenko_element_stiffness,
    _transform_12x12,
)

cs_norm = _cs_norm
has_only_finite_values = _has_only_finite_values
rotation_matrix = _rotation_matrix
timoshenko_element_stiffness = _timoshenko_element_stiffness
transform_12x12 = _transform_12x12

__all__ = [
    "_cs_norm",
    "_has_only_finite_values",
    "_rotation_matrix",
    "_timoshenko_element_stiffness",
    "_transform_12x12",
    "cs_norm",
    "has_only_finite_values",
    "rotation_matrix",
    "timoshenko_element_stiffness",
    "transform_12x12",
]
