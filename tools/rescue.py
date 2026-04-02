from typing import Any
import json

from ._common import _add_paths, _remove_paths, _build_state, _result, PLAN_DIR, EXAMPLES


def handle_rescue(params: dict[str, Any], **kwargs: Any) -> str:
    """
    Coordinate multi-robot rescue operations using HTN planning.
    
    Plans rescue missions for heterogeneous robots (wheeled robots and drones)
    with different capabilities. Available preset scenarios: move, survey.
    
    Args:
        params: Dictionary containing optional keys:
            - task: str | None
                Preset scenario. Default: "survey"
                Options (not exposed directly):
                  - "survey": Drone surveys location (2, 2)
                  - "move": Wheeled robot moves to location (5, 5)
                  Other values return error.
            - tasks: list[list] | None
                Custom task list (overrides task param). Each task is tuple of (name, args...)
                Example:
                [
                    ["move_task", "r1", [5, 5]],
                    ["survey_task", "a1", [2, 2]]
                ]
            - state: dict[str, Any] | None
                Custom initial state with schema:
                {
                    "loc": dict[str, tuple[int, int]],       # entity -> (x, y)
                    "robot_type": dict[str, str],            # robot -> "wheeled" | "uav"
                    "has_medicine": dict[str, int],
                    "status": dict[str, str],
                    "altitude": dict[str, str],
                    "current_image": dict[str, Any],
                    "rigid.obstacles": set,
                    "rigid.wheeled_robots": tuple,
                    "rigid.drones": tuple
                }
                If None, uses default state.
            - note: str | None - optional description for output
        **kwargs: Additional keyword arguments (unused)
    
    Returns:
        str: JSON-serialized dict with keys:
            - plan: list[list] - sequence of robot actions
            - steps: int - total number of actions
            - iterations: int - planner iterations used
            - note: str | None - optional problem identifier
    
    Entities:
        - Wheeled robots: r1, w1 (carry medicine, navigate ground)
        - Drones: a1 (survey from air, capture images)
        - Persons: p1 (rescue target)
    
    Example:
        >>> result = handle_rescue({"task": "survey"})
        >>> import json
        >>> output = json.loads(result)
        >>> print(f"Rescue plan: {output['steps']} actions")
    """
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.rescue.domain.rescue_actions import actions
        from examples.rescue.domain.rescue_methods import methods
        from examples.rescue.problem.rescue_problem_1 import init_state as default_state
        from ipyhop import IPyHOP

        state = _build_state(params["state"]) if params.get("state") else default_state

        tasks: list[tuple]
        if params.get("tasks") is not None:
            tasks = []
            for t in params["tasks"]:
                args: list = [tuple(a) if isinstance(a, list) else a for a in t[1:]]
                tasks.append((t[0], *args))
        else:
            task: str = str(params.get("task", "survey")).strip()
            task_map: dict[str, list[tuple]] = {
                "move":   [("move_task",   "r1", (5, 5))],
                "survey": [("survey_task", "a1", (2, 2))],
            }
            if task not in task_map:
                return json.dumps({"error": "invalid task type; see documentation"})
            tasks = task_map[task]

        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        note: str = params.get("note") or ("custom" if params.get("state") or params.get("tasks") else f"task={params.get('task','survey')}")
        return _result(planner, plan, state, note=note)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
    finally:
        _remove_paths(added)
