"""Lossless JSON serialization for the dual-beam mainline kernel model.

The kernel tests need a `DualBeamMainlineModel` without rebuilding it through
the config-aware application stack. This module round-trips the dataclass
exactly: float64 values go through CPython's shortest round-tripping repr, so a
loaded model is bit-identical to the one that was written.

It depends only on NumPy and the kernel type definitions, so it stays inside the
kernel dependency boundary.
"""

from __future__ import annotations

import dataclasses
import json
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

from hpa_core.dual_beam_mainline.types import (
    DualBeamMainlineModel,
    TorqueInputDefinition,
    TorqueReferenceMode,
)

# The schema string is deliberately repo-neutral: the same fixture file is read
# by the application repository and by the standalone kernel repository.
SCHEMA = "dual_beam_mainline_model/1"

_DATACLASSES: dict[str, type] = {
    "DualBeamMainlineModel": DualBeamMainlineModel,
    "TorqueInputDefinition": TorqueInputDefinition,
}
_ENUMS: dict[str, type[Enum]] = {
    "TorqueReferenceMode": TorqueReferenceMode,
}

__all__ = [
    "SCHEMA",
    "dump_dual_beam_mainline_model",
    "load_dual_beam_mainline_model",
    "model_from_payload",
    "model_to_payload",
]


def _encode(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Enum):
        return {"__enum__": type(value).__name__, "value": value.value}
    if isinstance(value, np.ndarray):
        return {
            "__ndarray__": {
                "dtype": str(value.dtype),
                "shape": list(value.shape),
                "data": value.reshape(-1).tolist(),
            }
        }
    if isinstance(value, np.generic):
        return _encode(value.item())
    if isinstance(value, tuple):
        return {"__tuple__": [_encode(item) for item in value]}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        name = type(value).__name__
        if name not in _DATACLASSES:
            raise TypeError(f"unsupported dataclass in kernel model payload: {name}")
        return {
            "__dataclass__": name,
            "fields": {
                field.name: _encode(getattr(value, field.name))
                for field in dataclasses.fields(value)
            },
        }
    raise TypeError(f"unsupported value in kernel model payload: {type(value).__name__}")


def _decode(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    if "__ndarray__" in value:
        spec = value["__ndarray__"]
        array = np.asarray(spec["data"], dtype=np.dtype(spec["dtype"]))
        return array.reshape(tuple(spec["shape"]))
    if "__tuple__" in value:
        return tuple(_decode(item) for item in value["__tuple__"])
    if "__enum__" in value:
        return _ENUMS[value["__enum__"]](value["value"])
    if "__dataclass__" in value:
        cls = _DATACLASSES[value["__dataclass__"]]
        return cls(**{key: _decode(item) for key, item in value["fields"].items()})
    return value


def model_to_payload(model: DualBeamMainlineModel) -> dict[str, Any]:
    """Return a JSON-ready payload describing one kernel model exactly."""
    return {
        "schema": SCHEMA,
        "fields": {
            field.name: _encode(getattr(model, field.name))
            for field in dataclasses.fields(model)
        },
    }


def model_from_payload(payload: dict[str, Any]) -> DualBeamMainlineModel:
    """Rebuild a kernel model from a payload produced by `model_to_payload`."""
    schema = payload.get("schema")
    if schema != SCHEMA:
        raise ValueError(f"unsupported kernel model schema: {schema!r} (expected {SCHEMA!r})")
    return DualBeamMainlineModel(
        **{key: _decode(value) for key, value in payload["fields"].items()}
    )


def dump_dual_beam_mainline_model(model: DualBeamMainlineModel, path: str | Path) -> Path:
    """Write one kernel model to `path` as a lossless JSON fixture."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(model_to_payload(model), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def load_dual_beam_mainline_model(path: str | Path) -> DualBeamMainlineModel:
    """Read a kernel model fixture written by `dump_dual_beam_mainline_model`."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"kernel model fixture not found: {source}")
    return model_from_payload(json.loads(source.read_text(encoding="utf-8")))
