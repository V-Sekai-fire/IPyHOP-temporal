from typing import Any
import json

from ._common import _add_paths, _remove_paths, _build_state, _result, PLAN_DIR, EXAMPLES


def handle_temporal_travel(params: dict[str, Any], **kwargs: Any) -> str:
    """
    Route people between city locations with temporal planning (time-aware).
    
    Identical to simple_travel but returns ISO-8601 timestamps and durations
    for each action in the plan.
    
    Args:
        params: Dictionary containing optional keys:
            - tasks: list[list[str, ...]] | None
                List of travel goals. Default: [["travel", "alice", "park"]]
                Each task is [task_name, arg1, arg2, ...]
                Valid persons: ["alice", "bob"]
                Valid locations: ["home_a", "home_b", "park", "station", "downtown"]
            - state: dict[str, Any] | None
                Custom initial state with schema:
                {
                    "loc": dict[str, str],      # entity -> location
                    "cash": dict[str, float],   # person -> amount
                    "owe": dict[str, float],    # person -> amount owed
                    "rigid.types": dict[str, list],
                    "rigid.dist": dict[tuple, int]
                }
                If None, uses default state (alice & bob at home_a/home_b).
        **kwargs: Additional keyword arguments (unused)
    
    Returns:
        str: JSON-serialized dict with keys:
            - plan: list[list | dict] - sequence of actions with temporal metadata:
                Each action is either:
                [action_name, arg1, arg2, ...]
                OR
                {"action": [...], "temporal": {"duration": "PT5M", "start_time": "...", "end_time": "..."}}
            - steps: int - total number of actions
            - iterations: int - planner iterations used
            - note: str | None - optional
    
    Temporal Action Durations:
        - a_walk(p, x, y): PT5M per unit distance
        - a_call_taxi(p, x): PT0S (instant)
        - a_ride_taxi(p, y): PT10M
        - a_pay_driver(p, y): PT0S (instant)
    
    Raises:
        Returns error in JSON if:
            - tasks is not a list
            - any task item is not [name, arg, ...]
    
    Example:
        >>> result = handle_temporal_travel({
        ...     "tasks": [["travel", "alice", "downtown"]]
        ... })
        >>> import json
        >>> output = json.loads(result)
        >>> for action in output["plan"]:
        ...     if isinstance(action, dict):
        ...         print(f"{action['action']} at {action['temporal']['start_time']}")
    """
    tasks_raw = params.get("tasks") if params.get("tasks") is not None else [["travel", "alice", "park"]]
    if not isinstance(tasks_raw, list):
        return json.dumps({"error": "tasks must be a list"})
    tasks: list[tuple] = []
    for item in tasks_raw:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            return json.dumps({"error": f"each task must be [name, arg, ...], got {item!r}"})
        tasks.append(tuple(item))
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.temporal_travel.task_based.temporal_travel_domain import actions, methods
        from examples.temporal_travel.task_based.temporal_travel_problem import init_state as default_state
        from ipyhop import IPyHOP
        state = _build_state(params["state"]) if params.get("state") else default_state
        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        return _result(planner, plan, state)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
    finally:
        _remove_paths(added)
