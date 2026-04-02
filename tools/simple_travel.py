from typing import Any
import json

from ._common import _add_paths, _remove_paths, _build_state, _result, PLAN_DIR, EXAMPLES


def handle_simple_travel(params: dict[str, Any], **kwargs: Any) -> str:
    tasks_raw = params.get("tasks") or [["travel", "alice", "park"]]
    if not isinstance(tasks_raw, list):
        return json.dumps({"error": "tasks must be a list"})
    tasks: list[tuple] = []
    for item in tasks_raw:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            return json.dumps({"error": f"each task must be [name, arg, ...], got {item!r}"})
        tasks.append(tuple(item))
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.simple_travel.task_based.simple_travel_domain import actions, methods
        from examples.simple_travel.task_based.simple_travel_problem import init_state
        from ipyhop import IPyHOP
        state = _build_state(params["state"]) if params.get("state") else init_state
        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        return _result(planner, plan, state)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
    finally:
        _remove_paths(added)
