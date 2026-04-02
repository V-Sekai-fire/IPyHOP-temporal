from typing import Any
import json

from ._common import _add_paths, _remove_paths, _build_state, _result, PLAN_DIR, EXAMPLES


def handle_healthcare(params: dict[str, Any], **kwargs: Any) -> str:
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.healthcare_scheduling.task_based.healthcare_domain import actions, methods
        from examples.healthcare_scheduling.task_based import healthcare_problem as prob
        from ipyhop import IPyHOP

        state = _build_state(params["state"]) if params.get("state") else prob.init_state

        tasks: list[tuple]
        if params.get("tasks"):
            tasks = [tuple(t) for t in params["tasks"]]
        else:
            task: str = str(params.get("task", "single")).strip()
            task_map: dict[str, str] = {
                "single":      "task_list_1",
                "two":         "task_list_2",
                "shared_room": "task_list_3",
            }
            if task not in task_map:
                return json.dumps({"error": f"'task' must be one of {sorted(task_map)}"})
            tasks = getattr(prob, task_map[task])

        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        note: str = params.get("note") or ("custom" if params.get("state") or params.get("tasks") else f"task={params.get('task','single')}")
        return _result(planner, plan, state, note=note)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
    finally:
        _remove_paths(added)
