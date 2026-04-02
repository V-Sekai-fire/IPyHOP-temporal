from typing import Any
import json

from ._common import _add_paths, _remove_paths, _build_state, _result, _recursive_json_parse, PLAN_DIR, EXAMPLES

_PROBLEM_MAP: dict[str, tuple[str, str]] = {
    "1a": ("init_state_1", "goal1a"),
    "1b": ("init_state_1", "goal1b"),
    "2a": ("init_state_2", "goal2a"),
    "2b": ("init_state_2", "goal2b"),
    "3":  ("init_state_3", "goal3"),
}


def handle_blocks_world(params: dict[str, Any], **kwargs: Any) -> str:
    """
    Solve block-stacking puzzles using HTN (Hierarchical Task Network) planning.
    
    Supports 5 standard problems (1a, 1b, 2a, 2b, 3) with block counts from 3 to 19,
    or custom initial states and goals.
    
    Args:
        params: Dictionary containing optional keys:
            - problem: str (internal, default "1b") - problem variant
            - state: dict[str, Any] | None
                Custom initial state with schema:
                {
                    "pos": dict[str, str],           # block -> (block_id | "table")
                    "clear": dict[str, bool],        # block -> is_clear
                    "holding": dict[str, str | bool] # {"hand": block_id | False}
                }
                If None, uses default state for problem.
            - tasks: list[dict | list] | None
                Custom goals in MultiGoal format:
                [
                    {
                        "__multigoal__": True,
                        "goal_tag": "custom_goal",
                        "pos": {...},
                        "clear": {...},
                        ...other state constraints...
                    }
                ]
                If None, uses default goal for problem.
            - note: str | None - optional description for output
        **kwargs: Additional keyword arguments (unused)
    
    Returns:
        str: JSON-serialized dict with keys:
            - plan: list[list] - sequence of actions to execute
            - steps: int - total number of actions
            - iterations: int - planner iterations used
            - note: str | None - optional problem identifier
    
    Example:
        >>> result = handle_blocks_world({
        ...     "problem": "1a",
        ...     "state": None,
        ...     "tasks": None
        ... })
        >>> import json
        >>> output = json.loads(result)
        >>> print(f"Plan has {output['steps']} steps")
    """
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.blocks_world.task_based.blocks_world_actions import actions
        from examples.blocks_world.task_based.blocks_world_methods_1 import methods as tb_methods
        from examples.blocks_world.goal_based.blocks_world_methods import methods as gb_methods
        from examples.blocks_world.goal_based.blocks_world_actions import actions as gb_actions
        import examples.blocks_world.task_based.blocks_world_problem as prob
        from ipyhop import IPyHOP, MultiGoal

        problem: str = str(params.get("problem", "1b")).strip()

        state_data: Any = _recursive_json_parse(params.get("state"))
        if state_data:
            init_state = _build_state(state_data)
        else:
            if problem not in _PROBLEM_MAP:
                return json.dumps({"error": "invalid problem type; see documentation"})
            state_name, _ = _PROBLEM_MAP[problem]
            init_state = getattr(prob, state_name)

        tasks_data: Any = _recursive_json_parse(params.get("tasks"))

        has_multigoal: bool = False
        task_list: list = []
        if tasks_data is not None:
            for t in tasks_data:
                if isinstance(t, dict) and t.get("__multigoal__"):
                    has_multigoal = True
                    mg = MultiGoal(t.get("name", "custom_goal"))
                    mg.goal_tag = t.get("goal_tag", None)
                    for k, v in t.items():
                        if k not in ("__multigoal__", "name", "goal_tag"):
                            setattr(mg, k, v)
                    task_list.append(mg)
                else:
                    task_list.append(tuple(t))
        else:
            _, goal_name = _PROBLEM_MAP.get(problem, ("init_state_1", "goal1b"))
            task_list = [getattr(prob, goal_name)]
            has_multigoal = True

        chosen_methods = gb_methods if has_multigoal else tb_methods
        chosen_actions = gb_actions if has_multigoal else actions
        planner = IPyHOP(chosen_methods, chosen_actions)
        plan = planner.plan(init_state, task_list, verbose=0)
        note: str = params.get("note") or (f"problem={params.get('problem','1b')}" if not state_data else "custom")
        return _result(planner, plan, init_state, note=note)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
    finally:
        _remove_paths(added)
