"""
plan plugin tools — one dedicated handler per IPyHOP example domain.

Tools exposed:
  plan_simple_travel        — person travels home→destination (task-based)
  plan_blocks_world         — rearrange blocks to match a goal state (goal-based)
  plan_rescue               — robot/drone survey-and-rescue mission (task-based)
  plan_robosub              — underwater robot navigation tasks (task-based)
  plan_healthcare           — temporal surgical scheduling (task-based, temporal)
  plan_temporal_travel      — simple_travel with ISO-8601 timestamps (temporal)
"""

import sys
from pathlib import Path

PLAN_DIR  = Path(__file__).parent
EXAMPLES  = PLAN_DIR / "examples"


def _add_paths(*dirs):
    added = []
    for d in dirs:
        s = str(d)
        if s not in sys.path:
            sys.path.insert(0, s)
            added.append(s)
    return added


def _remove_paths(added):
    for s in added:
        try:
            sys.path.remove(s)
        except ValueError:
            pass


def _plan_to_json(plan) -> list:
    result = []
    for item in plan:
        if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], dict):
            result.append({"action": list(item[0]), "temporal": item[1]})
        else:
            result.append(list(item))
    return result


def _result(planner, plan, note=None):
    if plan is False or plan is None:
        return {"plan": None, "note": "No plan found"}
    r = {"plan": _plan_to_json(plan), "steps": len(plan), "iterations": planner.iterations}
    if note:
        r["note"] = note
    return r


# ---------------------------------------------------------------------------
# simple_travel (task-based)
# ---------------------------------------------------------------------------

def handle_simple_travel(params: dict) -> dict:
    """
    params:
      tasks  — list of travel tasks, e.g. [["travel","alice","park"]]
               defaults to [["travel","alice","park"]]
    """
    tasks_raw = params.get("tasks") or [["travel", "alice", "park"]]
    tasks = [tuple(t) for t in tasks_raw]

    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.simple_travel.task_based.simple_travel_domain import actions, methods
        from examples.simple_travel.task_based.simple_travel_problem import init_state
        from ipyhop import IPyHOP

        planner = IPyHOP(methods, actions)
        plan = planner.plan(init_state, tasks, verbose=0)
        return _result(planner, plan)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# blocks_world (task-based, uses goal-state MultiGoal)
# ---------------------------------------------------------------------------

def handle_blocks_world(params: dict) -> dict:
    """
    params:
      problem  — "1a" | "1b" | "2a" | "2b" | "3"  (default "1b")
                 selects which init_state + goal pair to solve
    """
    problem = str(params.get("problem", "1b")).strip()

    problem_map = {
        "1a": ("init_state_1", "goal1a"),
        "1b": ("init_state_1", "goal1b"),
        "2a": ("init_state_2", "goal2a"),
        "2b": ("init_state_2", "goal2b"),
        "3":  ("init_state_3", "goal3"),
    }
    if problem not in problem_map:
        return {"error": f"'problem' must be one of {sorted(problem_map)}"}

    state_name, goal_name = problem_map[problem]

    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.blocks_world.task_based.blocks_world_actions import actions
        from examples.blocks_world.task_based.blocks_world_methods_1 import methods
        import examples.blocks_world.task_based.blocks_world_problem as prob
        from ipyhop import IPyHOP

        init_state = getattr(prob, state_name)
        goal       = getattr(prob, goal_name)

        planner = IPyHOP(methods, actions)
        plan = planner.plan(init_state, [goal], verbose=0)
        return _result(planner, plan, note=f"problem={problem} ({state_name} → {goal_name})")
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# rescue (task-based)
# ---------------------------------------------------------------------------

def handle_rescue(params: dict) -> dict:
    """
    params:
      task  — "move" | "survey"  (default "survey")
              "move"   → move robot r1 to (5,5)
              "survey" → drone a1 surveys location (2,2)
    """
    task = str(params.get("task", "survey")).strip()

    task_map = {
        "move":   [("move_task",   "r1", (5, 5))],
        "survey": [("survey_task", "a1", (2, 2))],
    }
    if task not in task_map:
        return {"error": f"'task' must be one of {sorted(task_map)}"}

    tasks = task_map[task]

    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.rescue.domain.rescue_actions import actions
        from examples.rescue.domain.rescue_methods import methods
        from examples.rescue.problem.rescue_problem_1 import init_state
        from ipyhop import IPyHOP

        planner = IPyHOP(methods, actions)
        plan = planner.plan(init_state, tasks, verbose=0)
        return _result(planner, plan, note=f"task={task}")
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# robosub (task-based)
# ---------------------------------------------------------------------------

def handle_robosub(params: dict) -> dict:
    """
    params:
      task  — "full" | "staged"  (default "full")
              "full"   → pinger + all 5 zones in one task list
              "staged" → pinger + each zone as a separate task
    """
    task = str(params.get("task", "full")).strip()
    if task not in ("full", "staged"):
        return {"error": "'task' must be 'full' or 'staged'"}

    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.robosub.domain.robosub_mod_actions import actions
        from examples.robosub.domain.robosub_mod_methods import methods
        from examples.robosub.problem.robosub_mod_problem import (
            init_state, task_list_1, task_list_2
        )
        from ipyhop import IPyHOP

        tasks = task_list_1 if task == "full" else task_list_2
        planner = IPyHOP(methods, actions)
        plan = planner.plan(init_state, tasks, verbose=0)
        return _result(planner, plan, note=f"task={task}")
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# healthcare scheduling (temporal)
# ---------------------------------------------------------------------------

def handle_healthcare(params: dict) -> dict:
    """
    params:
      task  — "single" | "two" | "shared_room"  (default "single")
              "single"      → schedule patient1 in OR1
              "two"         → schedule patient1 + patient2
              "shared_room" → patient1 + patient3 both needing cardiac room
    """
    task = str(params.get("task", "single")).strip()

    task_map = {
        "single":      "task_list_1",
        "two":         "task_list_2",
        "shared_room": "task_list_3",
    }
    if task not in task_map:
        return {"error": f"'task' must be one of {sorted(task_map)}"}

    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.healthcare_scheduling.task_based.healthcare_domain import actions, methods
        from examples.healthcare_scheduling.task_based import healthcare_problem as prob
        from ipyhop import IPyHOP

        tasks = getattr(prob, task_map[task])
        planner = IPyHOP(methods, actions)
        plan = planner.plan(prob.init_state, tasks, verbose=0)
        return _result(planner, plan, note=f"task={task}")
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# temporal_travel (temporal, ISO-8601 timestamps)
# ---------------------------------------------------------------------------

def handle_temporal_travel(params: dict) -> dict:
    """
    params:
      tasks  — list of travel tasks (default [["travel","alice","park"]])
               each step returns start_time + end_time in the temporal metadata
    """
    tasks_raw = params.get("tasks") or [["travel", "alice", "park"]]
    tasks = [tuple(t) for t in tasks_raw]

    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.temporal_travel.task_based.temporal_travel_domain import actions, methods
        from examples.temporal_travel.task_based.temporal_travel_problem import init_state
        from ipyhop import IPyHOP

        planner = IPyHOP(methods, actions)
        plan = planner.plan(init_state, tasks, verbose=0)
        return _result(planner, plan)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)
