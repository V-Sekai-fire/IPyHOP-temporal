from typing import Any
import json

from ._common import _add_paths, _remove_paths, _build_state, _result, PLAN_DIR, EXAMPLES


def handle_healthcare(params: dict[str, Any], **kwargs: Any) -> str:
    """
    Schedule surgical procedures in operating rooms with temporal constraints.
    
    Plans surgical workflows for patients in available ORs with equipment constraints.
    Each action has a duration (preparation, surgery, recovery, cleanup).
    
    Args:
        params: Dictionary containing optional keys:
            - task: str | None
                Preset scheduling scenario. Default: "single"
                Options (not exposed directly):
                  - "single": Schedule patient1 in OR1 (cardiac)
                  - "two": Schedule patient1 and patient2
                  - "shared_room": Schedule patient1 and patient3 in same cardiac OR
                  Other values return error.
            - tasks: list[list] | None
                Custom task list (overrides task param). Each task is (patient, room, surgery_type)
                Example:
                [
                    ["schedule_surgery", "patient1", "OR1", "cardiac"],
                    ["schedule_surgery", "patient2", "OR2", "orthopedic"]
                ]
            - state: dict[str, Any] | None
                Custom initial state with schema:
                {
                    "room_status": dict[str, str],          # room -> "available" | "cleaned" | "occupied"
                    "room_equipment": dict[str, str],       # room -> "cardiac" | "orthopedic"
                    "patient_location": dict[str, str],     # patient -> room
                    "patient_surgery_type": dict[str, str], # patient -> surgery_type
                    "surgery_complete": dict[str, bool]
                }
                If None, uses default state.
            - note: str | None - optional description for output
        **kwargs: Additional keyword arguments (unused)
    
    Returns:
        str: JSON-serialized dict with keys:
            - plan: list[list | dict] - sequence of surgical actions with temporal metadata:
                Each action is [action_name, arg1, ...] with optional temporal info
            - steps: int - total number of actions
            - iterations: int - planner iterations used
            - note: str | None - optional problem identifier
    
    Action Durations (ISO 8601):
        - a_prepare_room(room, surgery_type): PT30M
        - a_perform_surgery(patient, room, surgery_type): PT2H
        - a_recover_patient(patient, room): PT15M
        - a_clean_room(room): PT20M
    
    Entities:
        - Rooms: OR1, OR2, OR3
        - Patients: patient1, patient2, patient3
        - Surgery types: cardiac (OR1, OR3), orthopedic (OR2)
    
    Example:
        >>> result = handle_healthcare({"task": "single"})
        >>> import json
        >>> output = json.loads(result)
        >>> print(f\"Surgery schedule: {output['steps']} actions over {len(output['plan'])} steps\")
    """
    added = _add_paths(PLAN_DIR, EXAMPLES)
    try:
        from examples.healthcare_scheduling.task_based.healthcare_domain import actions, methods
        from examples.healthcare_scheduling.task_based import healthcare_problem as prob
        from ipyhop import IPyHOP

        state = _build_state(params["state"]) if params.get("state") else prob.init_state

        tasks: list[tuple]
        if params.get("tasks") is not None:
            tasks = [tuple(t) for t in params["tasks"]]
        else:
            task: str = str(params.get("task", "single")).strip()
            task_map: dict[str, str] = {
                "single":      "task_list_1",
                "two":         "task_list_2",
                "shared_room": "task_list_3",
            }
            if task not in task_map:
                return json.dumps({"error": "invalid task type; see documentation"})
            tasks = getattr(prob, task_map[task])

        planner = IPyHOP(methods, actions)
        plan = planner.plan(state, tasks, verbose=0)
        note: str = params.get("note") or ("custom" if params.get("state") or params.get("tasks") else f"task={params.get('task','single')}")
        return _result(planner, plan, state, note=note)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
    finally:
        _remove_paths(added)
