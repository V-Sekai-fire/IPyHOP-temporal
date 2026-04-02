from typing import Any
import json

from ._common import _add_paths, _remove_paths, _build_state, _result, PLAN_DIR, EXAMPLES


def handle_simple_travel(params: dict[str, Any], **kwargs: Any) -> str:
    """
    Route people between city locations using HTN planning.
    
    Plans travel for persons (alice, bob) to destination locations using available
    methods: walking (short distances) or taxi (with cash constraints).
    
    Args:
        params: Dictionary containing optional keys:
            - tasks: list[list[str, ...]] | None
                List of travel goals. Default: [["travel", "alice", "park"]]
                Each task is [task_name, arg1, arg2, ...]
                Valid persons: ["alice", "bob"]
                Valid locations: ["home_a", "home_b", "park", "station", "downtown"]
                Example:
                [
                    ["travel", "alice", "park"],
                    ["travel", "bob", "downtown"]
                ]
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
            - plan: list[list] - sequence of actions (walk, call_taxi, ride_taxi, pay_driver)
            - steps: int - total number of actions
            - iterations: int - planner iterations used
    
    Raises:
        Returns error in JSON if:
            - tasks is not a list
            - any task item is not [name, arg, ...]
    
    Example:
        >>> result = handle_simple_travel({
        ...     "tasks": [["travel", "alice", "downtown"]]
        ... })
        >>> import json
        >>> output = json.loads(result)
        >>> print(f"Found plan with {output['steps']} actions")
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
