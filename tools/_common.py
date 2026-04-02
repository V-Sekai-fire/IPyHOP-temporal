import sys
import json
from pathlib import Path
from typing import Any

PLAN_DIR: Path = Path(__file__).parent.parent
EXAMPLES: Path = PLAN_DIR / "examples"


def _add_paths(*dirs: Path) -> list[str]:
    added: list[str] = []
    for d in dirs:
        s = str(d)
        if s not in sys.path:
            sys.path.insert(0, s)
            added.append(s)
    return added


def _remove_paths(added: list[str]) -> None:
    for s in added:
        try:
            sys.path.remove(s)
        except ValueError:
            pass


def _plan_to_json(plan: list) -> list:
    result: list = []
    for item in plan:
        if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], dict):
            result.append({"action": list(item[0]), "temporal": item[1]})
        else:
            result.append(list(item))
    return result


def _coerce_keys(obj: Any) -> Any:
    """Convert string-repr tuple keys (JSON limitation) back to real tuples."""
    if not isinstance(obj, dict):
        return obj
    import ast
    result: dict = {}
    for k, v in obj.items():
        if isinstance(k, str) and k.startswith("(") and k.endswith(")"):
            try:
                k = ast.literal_eval(k)
            except (ValueError, SyntaxError):
                pass
        result[k] = _coerce_keys(v)
    return result


def _build_state(state_dict: dict, name: str = "custom_state") -> Any:
    """Build an IPyHOP State from a plain dict."""
    from ipyhop import State
    s = State(name)
    for key, val in state_dict.items():
        setattr(s, key, _coerce_keys(val))
    return s


def _serialize_val(v: Any) -> Any:
    """Recursively make a value JSON-safe, stringifying tuple keys in dicts."""
    from ipyhop import State
    if isinstance(v, State):
        return _serialize_state(v)
    if isinstance(v, dict):
        return {str(dk): _serialize_val(dv) for dk, dv in v.items()}
    if isinstance(v, (list, tuple)):
        return [_serialize_val(i) for i in v]
    return v


def _recursive_json_parse(obj: Any) -> Any:
    """Recursively parse JSON strings in nested structures."""
    if isinstance(obj, str):
        try:
            parsed = json.loads(obj)
            return _recursive_json_parse(parsed)
        except (json.JSONDecodeError, ValueError):
            return obj
    elif isinstance(obj, dict):
        return {k: _recursive_json_parse(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_recursive_json_parse(item) for item in obj]
    return obj


def _serialize_state(s: Any) -> dict[str, Any]:
    """Serialize a State snapshot to a JSON-safe dict, stringifying tuple keys."""
    result: dict[str, Any] = {}
    for k, v in vars(s).items():
        if k.startswith("_"):
            continue
        result[k] = _serialize_val(v)
    return result


def _result(planner: Any, plan: list, init_state: Any, note: str | None = None) -> dict[str, Any]:
    plan = plan or []
    r: dict[str, Any] = {
        "plan":       _plan_to_json(plan),
        "steps":      len(plan),
        "iterations": planner.iterations,
    }
    if note:
        r["note"] = note
    return r
