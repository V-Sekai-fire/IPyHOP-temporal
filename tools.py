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
import json
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


def _coerce_keys(obj):
    """Convert string-repr tuple keys (JSON limitation) back to real tuples."""
    if not isinstance(obj, dict):
        return obj
    import ast
    result = {}
    for k, v in obj.items():
        if isinstance(k, str) and k.startswith("(") and k.endswith(")"):
            try:
                k = ast.literal_eval(k)
            except (ValueError, SyntaxError):
                pass
        result[k] = _coerce_keys(v)
    return result


def _build_state(state_dict, name: str = "custom_state"):
    """Build an IPyHOP State from a plain dict."""
    from ipyhop import State
    s = State(name)
    for key, val in state_dict.items():
        setattr(s, key, _coerce_keys(val))
    return s


def _serialize_val(v):
    """Recursively make a value JSON-safe, stringifying tuple keys in dicts."""
    from ipyhop import State
    if isinstance(v, State):
        return _serialize_state(v)
    if isinstance(v, dict):
        return {str(dk): _serialize_val(dv) for dk, dv in v.items()}
    if isinstance(v, (list, tuple)):
        return [_serialize_val(i) for i in v]
    return v



def _recursive_json_parse(obj):
    """Recursively parse JSON strings in nested structures."""
    if isinstance(obj, str):
        try:
            parsed = json.loads(obj)
            return _recursive_json_parse(parsed)
        except (json.JSONDecodeError, ValueError):
            return obj
    elif isinstance(obj, dict):
        return {k: _recursive_json_parse(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_recursive_json_parse(item) for item in obj]
    return obj

def _serialize_state(s) -> dict:
    """Serialize a State snapshot to a JSON-safe dict, stringifying tuple keys."""
    result = {}
    for k, v in vars(s).items():
        if k.startswith("_"):
            continue
        result[k] = _serialize_val(v)
    return result


def _store(planner, init_state) -> str:
    sid = str(uuid.uuid4())[:8]
    _SESSIONS[sid] = {"planner": planner, "init_state": init_state}
    return sid


def _result(planner, plan, init_state, note=None) -> dict:
    plan = plan or []
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

def handle_simple_travel(args: dict, **kwargs) -> dict:
    """
    params:
      tasks      — [[\"travel\", person, destination], ...]
                   default: [[\"travel\", \"alice\", \"park\"]]
      state      — optional dict override for the initial state
    """
    tasks_raw = args.get("tasks") or [["travel", "alice", "park"]]
    if not isinstance(tasks_raw, list):
        return {"error": "tasks must be a list"}
    tasks = []
    for item in tasks_raw:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            return {"error": f"each task must be [name, arg, ...], got {item!r}"}
        tasks.append(tuple(item))
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.simple_travel.task_based.simple_travel_domain import actions, methods
        from examples.simple_travel.task_based.simple_travel_problem import init_state
        from ipyhop import IPyHOP
        state = _build_state(args["state"]) if args.get("state") else init_state
        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        return _result(planner, plan, state)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_blocks_world
# ---------------------------------------------------------------------------

def handle_blocks_world(args: dict, **kwargs) -> dict:
    """
    params:
      problem — "1a" | "1b" | "2a" | "2b" | "3"  (default "1b")
      state   — optional dict override: {pos:{b:dest,...}, clear:{b:bool,...}, holding:{hand:False}}
      tasks   — optional list override: pass a MultiGoal-like dict or task tuples
                e.g. [{"__multigoal__": true, "goal_tag": "g", "pos": {"a": "b"}}]
    """

    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.blocks_world.task_based.blocks_world_actions import actions
        from examples.blocks_world.task_based.blocks_world_methods_1 import methods as tb_methods
        from examples.blocks_world.goal_based.blocks_world_methods import methods as gb_methods
        from examples.blocks_world.goal_based.blocks_world_actions import actions as gb_actions
        import examples.blocks_world.task_based.blocks_world_problem as prob
        from ipyhop import IPyHOP, MultiGoal
        # Parse state if it's a string (Hermes may pass JSON as string)
        state_data = _recursive_json_parse(args.get("state"))
        # Build state
        if state_data:
            init_state = _build_state(state_data)
        else:
            problem = str(args.get("problem", "1b")).strip()
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
            init_state = getattr(prob, state_name)

        # Parse tasks if it's a string (Hermes may pass JSON as string)
        tasks_data = _recursive_json_parse(args.get("tasks"))

        # Build task list — detect if any MultiGoal dicts are present
        has_multigoal = False
        if tasks_data:
            task_list = []
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
            problem = str(args.get("problem", "1b")).strip()
            problem_map = {
                "1a": ("init_state_1", "goal1a"),
                "1b": ("init_state_1", "goal1b"),
                "2a": ("init_state_2", "goal2a"),
                "2b": ("init_state_2", "goal2b"),
                "3":  ("init_state_3", "goal3"),
            }
            _, goal_name = problem_map.get(problem, ("init_state_1", "goal1b"))
            task_list = [getattr(prob, goal_name)]
            has_multigoal = True  # built-in goals are MultiGoals

        # Use goal_based methods for MultiGoal tasks, task_based otherwise
        chosen_methods = gb_methods if has_multigoal else tb_methods
        chosen_actions = gb_actions if has_multigoal else actions
        planner = IPyHOP(chosen_methods, chosen_actions)
        plan = planner.plan(init_state, task_list, verbose=0)
        note = args.get("note") or (f"problem={args.get('problem','1b')}" if not state_data else "custom")
        return _result(planner, plan, init_state, note=note)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_rescue
# ---------------------------------------------------------------------------

def handle_rescue(args: dict, **kwargs) -> dict:
    """
    params:
      task  — "move" | "survey"  (default "survey")
      state — optional dict override for the initial state
      tasks — optional list of task tuples, e.g. [["move_task","r1",[3,4]]]
    """
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.rescue.domain.rescue_actions import actions
        from examples.rescue.domain.rescue_methods import methods
        from examples.rescue.problem.rescue_problem_1 import init_state as default_state
        from ipyhop import IPyHOP

        state = _build_state(args["state"]) if args.get("state") else default_state

        if args.get("tasks"):
            # tuples may contain lists as args (e.g. coords) — convert inner lists to tuples
            tasks = []
            for t in args["tasks"]:
                args = []
                for a in t[1:]:
                    args.append(tuple(a) if isinstance(a, list) else a)
                tasks.append(tuple([t[0]] + args))
        else:
            task = str(args.get("task", "survey")).strip()
            task_map = {
                "move":   [("move_task",   "r1", (5, 5))],
                "survey": [("survey_task", "a1", (2, 2))],
            }
            if task not in task_map:
                return {"error": f"'task' must be one of {sorted(task_map)}"}
            tasks = task_map[task]

        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        note = args.get("note") or ("custom" if args.get("state") or args.get("tasks") else f"task={args.get('task','survey')}")
        return _result(planner, plan, state, note=note)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_robosub
# ---------------------------------------------------------------------------

def handle_robosub(args: dict, **kwargs) -> dict:
    """
    params:
      task  — "full" | "staged"  (default "full")
      state — optional dict override for the initial state
      tasks — optional list of task tuples, e.g. [["pinger_task"], ["main_task", ["l1","l2"]]]
    """
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.robosub.domain.robosub_mod_actions import actions
        from examples.robosub.domain.robosub_mod_methods import methods
        from examples.robosub.problem.robosub_mod_problem import (
            init_state as default_state, task_list_1, task_list_2,
        )
        from ipyhop import IPyHOP

        state = _build_state(args["state"]) if args.get("state") else default_state

        if args.get("tasks"):
            tasks = [tuple(t) for t in args["tasks"]]
        else:
            task = str(args.get("task", "full")).strip()
            if task not in ("full", "staged"):
                return {"error": "'task' must be 'full' or 'staged'"}
            tasks = task_list_1 if task == "full" else task_list_2

        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        note = args.get("note") or ("custom" if args.get("state") or args.get("tasks") else f"task={args.get('task','full')}")
        return _result(planner, plan, state, note=note)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_healthcare
# ---------------------------------------------------------------------------

def handle_healthcare(args: dict, **kwargs) -> dict:
    """
    params:
      task  — "single" | "two" | "shared_room"  (default "single")
      state — optional dict override for the initial state
      tasks — optional list of task tuples,
               e.g. [["schedule_surgery","patient1","OR1","cardiac"]]
    """
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.healthcare_scheduling.task_based.healthcare_domain import actions, methods
        from examples.healthcare_scheduling.task_based import healthcare_problem as prob
        from ipyhop import IPyHOP

        state = _build_state(args["state"]) if args.get("state") else prob.init_state

        if args.get("tasks"):
            tasks = [tuple(t) for t in args["tasks"]]
        else:
            task = str(args.get("task", "single")).strip()
            task_map = {
                "single":      "task_list_1",
                "two":         "task_list_2",
                "shared_room": "task_list_3",
            }
            if task not in task_map:
                return {"error": f"'task' must be one of {sorted(task_map)}"}
            tasks = getattr(prob, task_map[task])

        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        note = args.get("note") or ("custom" if args.get("state") or args.get("tasks") else f"task={args.get('task','single')}")
        return _result(planner, plan, state, note=note)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_temporal_travel
# ---------------------------------------------------------------------------

def handle_temporal_travel(args: dict, **kwargs) -> dict:
    """
    params:
      tasks — [["travel", person, destination], ...]
              default: [["travel", "alice", "park"]]
      state — optional dict override for the initial state
    """
    tasks_raw = args.get("tasks") or [["travel", "alice", "park"]]
    if not isinstance(tasks_raw, list):
        return {"error": "tasks must be a list"}
    tasks = []
    for item in tasks_raw:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            return {"error": f"each task must be [name, arg, ...], got {item!r}"}
        tasks.append(tuple(item))
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.temporal_travel.task_based.temporal_travel_domain import actions, methods
        from examples.temporal_travel.task_based.temporal_travel_problem import init_state as default_state
        from ipyhop import IPyHOP
        state = _build_state(args["state"]) if args.get("state") else default_state
        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        return _result(planner, plan, state)
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        _remove_paths(added)


# ---------------------------------------------------------------------------
# plan_replan — replan from a failure node in a prior session
# ---------------------------------------------------------------------------

def handle_replan(args: dict, **kwargs) -> dict:
    """
    params:
      session_id   — from a prior plan_* call
      fail_node_id — integer node id in sol_tree that failed
      blacklist    — optional list of action tuples to blacklist before replanning,
                     e.g. [["a_walk", "alice", "home_a", "park"]]
    """
    # Defensive: accept args as first positional or via kwargs
    if not isinstance(args, dict):
        # Try to parse as JSON string
        try:
            args = json.loads(args) if isinstance(args, str) else {}
        except:
            return {"error": "args must be a dict or JSON string"}
    
    sid = str(args.get("session_id", "")).strip()
    if not sid or sid not in _SESSIONS:
        return {"error": f"Unknown session_id '{sid}'. Run a plan_* tool first."}

    fail_node_raw = args.get("fail_node_id")
    if fail_node_raw is None:
        return {"error": "'fail_node_id' is required"}
    try:
        fail_node_id = int(fail_node_raw)
    except (TypeError, ValueError):
        return {"error": "'fail_node_id' must be an integer"}

    session = _SESSIONS[sid]
    planner    = session["planner"]
    init_state = session["init_state"]

    blacklist = args.get("blacklist") or []
    for cmd in blacklist:
        planner.blacklist_command(tuple(cmd))

    try:
        plan = planner.replan(init_state, fail_node_id, verbose=0)
    except Exception as exc:
        return {"error": f"replan failed: {exc}"}

    plan = plan or []
    # Update cache with new planner state (same sid — it's the same session)
    _SESSIONS[sid] = {"planner": planner, "init_state": init_state}
    return {
        "session_id": sid,
        "plan":       _plan_to_json(plan),
        "steps":      len(plan),
        "iterations": planner.iterations,
        "blacklisted": [list(c) for c in planner.blacklist],
    }




def handle_simulate(args: dict, **kwargs) -> dict:
    """
    params:
      session_id  — from a prior plan_* or plan_replan call
      start_index — step index to simulate from (default 0 = full plan)
    """
    # Defensive: accept args as first positional or via kwargs
    if not isinstance(args, dict):
        # Try to parse as JSON string
        try:
            args = json.loads(args) if isinstance(args, str) else {}
        except:
            return {"error": "args must be a dict or JSON string"}
    
    sid = str(args.get("session_id", "")).strip()
    if not sid or sid not in _SESSIONS:
        return {"error": f"Unknown session_id '{sid}'. Run a plan_* tool first."}

    start_index_raw = args.get("start_index", 0)
    try:
        start_index = int(start_index_raw) if start_index_raw is not None else 0
    except (TypeError, ValueError):
        return {"error": "'start_index' must be an integer"}

    session    = _SESSIONS[sid]
    planner    = session["planner"]
    init_state = session["init_state"]

    if planner.sol_plan is None:
        return {"error": "No plan in this session. Run plan_* first."}

    try:
        states = planner.simulate(init_state, start_ind=start_index)
    except Exception as exc:
        return {"error": f"simulate failed: {exc}"}

    # Render each state snapshot as a dict of its __dict__ (excluding private keys)
    snapshots = [_serialize_state(s) for s in states]

    # Defensive: ensure sol_plan is sliceable
    sol_plan = list(planner.sol_plan) if hasattr(planner.sol_plan, '__iter__') else []
    plan_slice = _plan_to_json(sol_plan[start_index:])

    return {
        "session_id":  sid,
        "start_index": start_index,
        "steps":       len(plan_slice),
        "plan":        plan_slice,
        "states":      snapshots,
    }



