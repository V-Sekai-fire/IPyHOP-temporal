from ._common import _add_paths, _remove_paths, _build_state, _result, PLAN_DIR, EXAMPLES


def handle_robosub(params: dict, **kwargs) -> dict:
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.robosub.domain.robosub_mod_actions import actions
        from examples.robosub.domain.robosub_mod_methods import methods
        from examples.robosub.problem.robosub_mod_problem import (
            init_state as default_state, task_list_1, task_list_2,
        )
        from ipyhop import IPyHOP

        state = _build_state(params["state"]) if params.get("state") else default_state

        if params.get("tasks"):
            tasks = [tuple(t) for t in params["tasks"]]
        else:
            task = str(params.get("task", "full")).strip()
            if task not in ("full", "staged"):
                return {"error": "'task' must be 'full' or 'staged'"}
            tasks = task_list_1 if task == "full" else task_list_2

        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        note = params.get("note") or ("custom" if params.get("state") or params.get("tasks") else f"task={params.get('task','full')}")
        return _result(planner, plan, state, note=note)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)
