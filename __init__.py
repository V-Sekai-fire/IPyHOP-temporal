from .tools import (
    handle_simple_travel,
    handle_blocks_world,
    handle_rescue,
    handle_robosub,
    handle_healthcare,
    handle_temporal_travel,
    handle_replan,
    handle_simulate,
)

_TOOLS = [
    (
        "plan_simple_travel",
        {
            "name": "plan_simple_travel",
            "description": (
                "HTN planner: simple travel domain. "
                "Finds a plan for one or more people to travel to destinations by walking or taxi. "
                "Walking chosen when dist(x,y) <= 2; taxi when cash >= fare (1.5 + 0.5*dist). "
                "Persons: alice (starts home_a, cash=$20), bob (starts home_b, cash=$15). "
                "Locations: home_a, home_b, park, station, downtown. "
                "Taxis: taxi1 (starts park), taxi2 (starts station). "
                "State variables: loc (position), cash, owe. "
                "Actions: a_walk(p,x,y), a_call_taxi(p,x), a_ride_taxi(p,y), a_pay_driver(p,y). "
                "Task: travel(p, destination)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": (
                            "List of travel tasks. Each task is [\"travel\", person, destination]. "
                            "Persons: alice, bob. "
                            "Destinations: home_a, home_b, park, station, downtown. "
                            "Default: [[\"travel\", \"alice\", \"park\"]]"
                        ),
                        "items": {"type": "array"},
                    },
                },
                "required": [],
            },
        },
        handle_simple_travel,
    ),
    (
        "plan_blocks_world",
        {
            "name": "plan_blocks_world",
            "description": (
                "HTN planner: blocks world domain. "
                "Rearranges blocks on a table to match a MultiGoal configuration using a robotic hand. "
                "State variables: pos (block -> block|'table'), clear (block -> bool), holding (hand -> block|False). "
                "Actions: a_pickup(b), a_unstack(b,c), a_putdown(b), a_stack(b,c). "
                "Tasks: move_blocks(goal), move_one(b,dest), get(b), put(b,dest). "
                "Problems — 1a: 3 blocks [a,b,c], full goal (c on b on a, hand empty); "
                "1b: 3 blocks, partial goal (c on b on a); "
                "2a: 4 blocks [a,b,c,d], full goal; "
                "2b: 4 blocks, partial goal; "
                "3: 19 blocks, large rearrangement."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Which problem to solve: '1a', '1b', '2a', '2b', or '3'. Default: '1b'.",
                    },
                },
                "required": [],
            },
        },
        handle_blocks_world,
    ),
    (
        "plan_rescue",
        {
            "name": "plan_rescue",
            "description": (
                "HTN planner: rescue domain. "
                "Coordinates wheeled robots (r1, w1) and a drone (a1) to locate and assist injured person p1 on a 2D grid. "
                "State variables: loc (entity->(x,y)), robot_type, has_medicine, status, altitude, current_image. "
                "Actions: a_move_euclidean/manhattan/curved(r,l,l_,dist), a_move_fly(r,l,l_), "
                "a_change_altitude(r,alt), a_capture_image(r,camera,l), a_inspect_person(r,p), "
                "a_support_person(r,p), a_inspect_location(r,l), a_replenish_supplies(r), "
                "a_engage_robot(r), a_free_robot(r), a_check_real(l). "
                "Tasks: move_task(r,l), survey_task(r,l), rescue_task(r,p), help_person_task(r,p), get_supplies_task(r). "
                "Variants: 'move' (r1 moves to (5,5)), 'survey' (a1 surveys (2,2) for p1)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "'move' or 'survey'. Default: 'survey'.",
                    },
                },
                "required": [],
            },
        },
        handle_rescue,
    ),
    (
        "plan_robosub",
        {
            "name": "plan_robosub",
            "description": (
                "HTN planner: underwater robot (RoboSub) domain. "
                "Navigates an AUV through 5 competition zones (l1-l5) completing objectives in each. "
                "Entities: robot r, torpedoes t1/t2, zones l0-l5, gate g, garlic markers gm1/gm2, "
                "coffin markers cm1/cm2, guide paths gp1/gp2, vampires v1/v2, coffin c1, "
                "acoustic pingers ap1/ap2, dracula d1, surfacing zone s1. "
                "State variables: loc, found, crossed_gate, traversed_path, vampire_touched, "
                "coffin_filled, staked_dracula, decapitated, surfaced, rigid.adj, rigid.type. "
                "Actions: a_search_for(loc), a_localize(obj), a_localize_ap(ap), a_move(loc), "
                "a_cross_gate_40/60(gate), a_pick(obj), a_trace_guide_path(gp), "
                "a_touch_back/front_v(v), a_open_c(c), a_drop_garlic_open/closed_coffin(gm,c), "
                "a_decap_d(d), a_stake_decap/norm_d(t,d), a_surface(cm,s). "
                "Top-level tasks: pinger_task(), main_task(loc_list). "
                "Variants: 'full' (single task list for all zones), 'staged' (one task per zone)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "'full' or 'staged'. Default: 'full'.",
                    },
                },
                "required": [],
            },
        },
        handle_robosub,
    ),
    (
        "plan_healthcare",
        {
            "name": "plan_healthcare",
            "description": (
                "HTN temporal planner: healthcare scheduling domain. "
                "Schedules surgical workflows in operating rooms with ISO-8601 start/end times per action. "
                "Origin time: 2025-01-15T08:00:00Z. "
                "Rooms: OR1 (cardiac), OR2 (orthopedic), OR3 (cardiac, pre-cleaned). "
                "Patients: patient1 (cardiac/OR1), patient2 (orthopedic/OR2), patient3 (cardiac/OR3). "
                "State variables: room_status, room_equipment, patient_location, patient_surgery_type, surgery_complete. "
                "Actions (all temporal): a_prepare_room(room,surgery_type) PT30M, "
                "a_perform_surgery(patient,room,surgery_type) PT2H, "
                "a_recover_patient(patient,room) PT15M, a_clean_room(room) PT20M. "
                "Task: schedule_surgery(patient, room, surgery_type). "
                "Variants: 'single' (patient1/OR1), 'two' (patient1+2), 'shared_room' (patient1+3 both cardiac)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "'single', 'two', or 'shared_room'. Default: 'single'.",
                    },
                },
                "required": [],
            },
        },
        handle_healthcare,
    ),
    (
        "plan_temporal_travel",
        {
            "name": "plan_temporal_travel",
            "description": (
                "HTN temporal planner: simple travel with ISO-8601 timestamps. "
                "Same domain as plan_simple_travel — persons alice/bob, locations home_a/home_b/park/station/downtown. "
                "Each action carries start_time and end_time. Origin time: 2025-01-01T10:00:00Z. "
                "Action durations: a_call_taxi PT0S, a_ride_taxi PT10M, a_pay_driver PT0S, a_walk PT5M. "
                "State variables: loc, cash, owe, rigid.types, rigid.dist. "
                "Task: travel(p, destination)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": (
                            "List of travel tasks. Each task is [\"travel\", person, destination]. "
                            "Persons: alice, bob. Destinations: home_a, home_b, park, station, downtown. "
                            "Default: [[\"travel\", \"alice\", \"park\"]]"
                        ),
                        "items": {"type": "array"},
                    },
                },
                "required": [],
            },
        },
        handle_temporal_travel,
    ),
    (
        "plan_replan",
        {
            "name": "plan_replan",
            "description": (
                "Replan from a failure node in a prior planning session. "
                "Use when an action in a previously generated plan fails at execution time. "
                "Provide the session_id from any plan_* call and the fail_node_id (integer) "
                "from the sol_tree. Optionally blacklist specific actions to prevent them "
                "from being chosen again. Returns a revised plan on the same session_id."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "session_id returned by a prior plan_* call.",
                    },
                    "fail_node_id": {
                        "type": "integer",
                        "description": "Node id in the solution tree that failed.",
                    },
                    "blacklist": {
                        "type": "array",
                        "description": (
                            "Optional list of action tuples to blacklist before replanning. "
                            "Each entry is a list, e.g. [\"a_walk\", \"alice\", \"home_a\", \"park\"]."
                        ),
                        "items": {"type": "array"},
                    },
                },
                "required": ["session_id", "fail_node_id"],
            },
        },
        handle_replan,
    ),
    (
        "plan_simulate",
        {
            "name": "plan_simulate",
            "description": (
                "Simulate execution of a previously generated plan, returning the sequence "
                "of world states the system transitions through. "
                "Use start_index to simulate from a mid-plan step (e.g. after partial execution). "
                "Returns each state snapshot as a dict alongside the plan slice being simulated."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "session_id returned by a prior plan_* or plan_replan call.",
                    },
                    "start_index": {
                        "type": "integer",
                        "description": "Step index to start simulation from (default 0 = full plan).",
                    },
                },
                "required": ["session_id"],
            },
        },
        handle_simulate,
    ),
]


def register(ctx):
    for name, schema, handler in _TOOLS:
        ctx.register_tool(name, schema, handler)
