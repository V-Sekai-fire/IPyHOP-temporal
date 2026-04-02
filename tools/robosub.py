from typing import Any
import json

from ._common import _add_paths, _remove_paths, _build_state, _result, PLAN_DIR, EXAMPLES


def handle_robosub(params: dict[str, Any], **kwargs: Any) -> str:
    """
    Plan underwater AUV (Autonomous Underwater Vehicle) missions.
    
    Plans complex multi-zone objectives for a submarine robot including gate crossing,
    object localization, vampire slaying, coffin filling, and Dracula staking.
    Mission objectives must be completed in correct dependency order.
    
    Args:
        params: Dictionary containing optional keys:
            - task: str | None
                Planning mode. Default: "full"
                Options (not exposed directly):
                  - "full": Complete all zones in a single plan
                  - "staged": Plan one zone at a time
                  Other values return error.
            - tasks: list[list] | None
                Custom task list (overrides task param). Each task is (task_name, args...)
                Example:
                [
                    ["pinger_task"],
                    ["main_task", ["l0", "l1", "l2", "l3", "l4", "l5"]]
                ]
            - state: dict[str, Any] | None
                Custom initial state with schema:
                {
                    "loc": dict[str, str],                  # entity -> location_id
                    "found": dict[str, bool],               # object/zone -> found
                    "crossed_gate": dict[str, bool],
                    "traversed_path": dict[str, bool],
                    "vampire_touched": dict[str, bool],
                    "coffin_filled": dict[str, list],       # coffin -> [garlic_items]
                    "staked_dracula": dict[str, list],      # dracula -> [torpedoes]
                    "decapitated": dict[str, bool],
                    "surfaced": dict[str, bool],
                    "rigid.adj": dict[str, list],           # location -> [adjacent_locs]
                    "rigid.type": dict[str, str]            # entity -> type_label
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
    
    Available Actions:
        - a_search_for(loc): reveal adjacent objects
        - a_localize(obj): locate specific object
        - a_move(loc): navigate to adjacent location
        - a_cross_gate_40(gate), a_cross_gate_60(gate): cross gate (40/60 points)
        - a_pick(obj): retrieve object
        - a_trace_guide_path(gp): follow guide path
        - a_touch_back_v(v), a_touch_front_v(v): vampire interactions
        - a_drop_garlic_open_coffin(gm, c): fill open coffin with garlic
        - a_decap_d(d): decapitate Dracula
        - a_stake_decap_d(t, d): stake decapitated Dracula with torpedo
        - a_surface(cm, s): surface at zone with coffin marker
    
    Entities:
        - Robot: r (AUV)
        - Torpedoes: t1, t2
        - Locations: l0..l5 (zones)
        - Objects: g (garlic), gm1/gm2 (garlic markers), cm1/cm2 (coffin markers),
                   gp1/gp2 (guide paths), v1/v2 (vampires), c1 (coffin),
                   ap1/ap2 (acoustic pingers), d1 (Dracula), s1 (surfacing zone)
    
    Example:
        >>> result = handle_robosub({"task": "full"})
        >>> import json
        >>> output = json.loads(result)
        >>> print(f\"Mission plan: {output['steps']} actions to complete\")
    """
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.robosub.domain.robosub_mod_actions import actions
        from examples.robosub.domain.robosub_mod_methods import methods
        from examples.robosub.problem.robosub_mod_problem import (
            init_state as default_state, task_list_1, task_list_2,
        )
        from ipyhop import IPyHOP

        state = _build_state(params["state"]) if params.get("state") else default_state

        tasks: list[tuple]
        if params.get("tasks") is not None:
            tasks = [tuple(t) for t in params["tasks"]]
        else:
            task: str = str(params.get("task", "full")).strip()
            if task not in ("full", "staged"):
                return json.dumps({"error": "'task' must be 'full' or 'staged'"})
            tasks = task_list_1 if task == "full" else task_list_2

        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        note: str = params.get("note") or ("custom" if params.get("state") or params.get("tasks") else f"task={params.get('task','full')}")
        return _result(planner, plan, state, note=note)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
    finally:
        _remove_paths(added)
