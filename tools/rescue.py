from ._common import _add_paths, _remove_paths, _build_state, _result, PLAN_DIR, EXAMPLES


def handle_rescue(params: dict, **kwargs) -> dict:
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.rescue.domain.rescue_actions import actions
        from examples.rescue.domain.rescue_methods import methods
        from examples.rescue.problem.rescue_problem_1 import init_state as default_state
        from ipyhop import IPyHOP

        state = _build_state(params["state"]) if params.get("state") else default_state

        if params.get("tasks"):
            tasks = []
            for t in params["tasks"]:
                args = []
                for a in t[1:]:
                    args.append(tuple(a) if isinstance(a, list) else a)
                tasks.append((t[0], *args))
        else:
            task = str(params.get("task", "survey")).strip()
            task_map = {
                "move":   [("move_task",   "r1", (5, 5))],
                "survey": [("survey_task", "a1", (2, 2))],
            }
            if task not in task_map:
                return {"error": f"'task' must be one of {sorted(task_map)}"}
            tasks = task_map[task]

        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        note = params.get("note") or ("custom" if params.get("state") or params.get("tasks") else f"task={params.get('task','survey')}")
        return _result(planner, plan, state, note=note)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)
