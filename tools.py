"""
plan plugin tools — IPyHOP HTN planner with plan / replan / simulate.

Domain tools (each returns a session_id for follow-up calls):
  plan_simple_travel
  plan_blocks_world
  plan_rescue
  plan_robosub
  plan_healthcare
  plan_temporal_travel

Follow-up tools (operate on a cached planner by session_id):
  plan_replan   — replan from a failure node in a prior session
  plan_simulate — simulate a prior plan forward from a given step index
"""

import sys
import uuid
from pathlib import Path

PLAN_DIR = Path(__file__).parent
EXAMPLES = PLAN_DIR / "examples"

# ---------------------------------------------------------------------------
# Planner cache  { session_id -> {"planner": IPyHOP, "init_state": State} }
# ---------------------------------------------------------------------------
_SESSIONS: dict = {}


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


def _store(planner, init_state) -> str:
    sid = str(uuid.uuid4())[:8]
    _SESSIONS[sid] = {"planner": planner, "init_state": init_state}
    return sid


def _result(planner, plan, init_state, note=None) -> dict:
    if plan is False or plan is None:
        return {"plan": None, "note": "No plan found"}
    sid = _store(planner, init_state)
    r = {
        "session_id": sid,
        "plan":       _plan_to_json(plan),
        "steps":      len(plan),
        "iterations": planner.iterations,
    }
    if note:
        r["note"] = note
    return r


# ---------------------------------------------------------------------------
# plan_simple_travel
# ---------------------------------------------------------------------------

def handle_simple_travel(params: dict) -> dict:
    """
    params:
      tasks — [["travel", person, destination], ...]
              default: [["travel", "alice", "park"]]
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
        return _result(planner, plan, init_state)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_blocks_world
# ---------------------------------------------------------------------------

def handle_blocks_world(params: dict) -> dict:
    """
    params:
      problem — "1a" | "1b" | "2a" | "2b" | "3"  (default "1b")
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
        return _result(planner, plan, init_state,
                       note=f"problem={problem} ({state_name} → {goal_name})")
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_rescue
# ---------------------------------------------------------------------------

def handle_rescue(params: dict) -> dict:
    """
    params:
      task — "move" | "survey"  (default "survey")
    """
    task = str(params.get("task", "survey")).strip()
    task_map = {
        "move":   [("move_task",   "r1", (5, 5))],
        "survey": [("survey_task", "a1", (2, 2))],
    }
    if task not in task_map:
        return {"error": f"'task' must be one of {sorted(task_map)}"}
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.rescue.domain.rescue_actions import actions
        from examples.rescue.domain.rescue_methods import methods
        from examples.rescue.problem.rescue_problem_1 import init_state
        from ipyhop import IPyHOP
        planner = IPyHOP(methods, actions)
        plan = planner.plan(init_state, task_map[task], verbose=0)
        return _result(planner, plan, init_state, note=f"task={task}")
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_robosub
# ---------------------------------------------------------------------------

def handle_robosub(params: dict) -> dict:
    """
    params:
      task — "full" | "staged"  (default "full")
    """
    task = str(params.get("task", "full")).strip()
    if task not in ("full", "staged"):
        return {"error": "'task' must be 'full' or 'staged'"}
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.robosub.domain.robosub_mod_actions import actions
        from examples.robosub.domain.robosub_mod_methods import methods
        from examples.robosub.problem.robosub_mod_problem import (
            init_state, task_list_1, task_list_2,
        )
        from ipyhop import IPyHOP
        tasks = task_list_1 if task == "full" else task_list_2
        planner = IPyHOP(methods, actions)
        plan = planner.plan(init_state, tasks, verbose=0)
        return _result(planner, plan, init_state, note=f"task={task}")
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_healthcare
# ---------------------------------------------------------------------------

def handle_healthcare(params: dict) -> dict:
    """
    params:
      task — "single" | "two" | "shared_room"  (default "single")
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
        return _result(planner, plan, prob.init_state, note=f"task={task}")
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_temporal_travel
# ---------------------------------------------------------------------------

def handle_temporal_travel(params: dict) -> dict:
    """
    params:
      tasks — [["travel", person, destination], ...]
              default: [["travel", "alice", "park"]]
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
        return _result(planner, plan, init_state)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_replan — replan from a failure node in a prior session
# ---------------------------------------------------------------------------

def handle_replan(params: dict) -> dict:
    """
    params:
      session_id   — from a prior plan_* call
      fail_node_id — integer node id in sol_tree that failed
      blacklist    — optional list of action tuples to blacklist before replanning,
                     e.g. [["a_walk", "alice", "home_a", "park"]]
    """
    sid = str(params.get("session_id", "")).strip()
    if not sid or sid not in _SESSIONS:
        return {"error": f"Unknown session_id '{sid}'. Run a plan_* tool first."}

    fail_node_raw = params.get("fail_node_id")
    if fail_node_raw is None:
        return {"error": "'fail_node_id' is required"}
    try:
        fail_node_id = int(fail_node_raw)
    except (TypeError, ValueError):
        return {"error": "'fail_node_id' must be an integer"}

    session = _SESSIONS[sid]
    planner    = session["planner"]
    init_state = session["init_state"]

    blacklist = params.get("blacklist") or []
    for cmd in blacklist:
        planner.blacklist_command(tuple(cmd))

    try:
        plan = planner.replan(init_state, fail_node_id, verbose=0)
    except Exception as exc:
        return {"error": f"replan failed: {exc}"}

    if plan is False or plan is None:
        return {"session_id": sid, "plan": None, "note": "No replan found"}

    # Update cache with new planner state (same sid — it's the same session)
    _SESSIONS[sid] = {"planner": planner, "init_state": init_state}
    return {
        "session_id": sid,
        "plan":       _plan_to_json(plan),
        "steps":      len(plan),
        "iterations": planner.iterations,
        "blacklisted": [list(c) for c in planner.blacklist],
    }


# ---------------------------------------------------------------------------
# plan_simulate — simulate a prior plan from a given step
# ---------------------------------------------------------------------------

def handle_simulate(params: dict) -> dict:
    """
    params:
      session_id  — from a prior plan_* or plan_replan call
      start_index — step index to simulate from (default 0 = full plan)
    """
    sid = str(params.get("session_id", "")).strip()
    if not sid or sid not in _SESSIONS:
        return {"error": f"Unknown session_id '{sid}'. Run a plan_* tool first."}

    start_index = int(params.get("start_index", 0))

    session    = _SESSIONS[sid]
    planner    = session["planner"]
    init_state = session["init_state"]

    if not planner.sol_plan:
        return {"error": "No plan in this session. Run plan_* first."}

    try:
        states = planner.simulate(init_state, start_ind=start_index)
    except Exception as exc:
        return {"error": f"simulate failed: {exc}"}

    # Render each state snapshot as a dict of its __dict__ (excluding private keys)
    snapshots = []
    for s in states:
        snap = {k: v for k, v in vars(s).items() if not k.startswith("_")}
        snapshots.append(snap)

    plan_slice = _plan_to_json(planner.sol_plan[start_index:])

    return {
        "session_id":  sid,
        "start_index": start_index,
        "steps":       len(plan_slice),
        "plan":        plan_slice,
        "states":      snapshots,
    }
