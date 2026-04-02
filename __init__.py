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
                "Finds a plan for one or more people to travel to destinations using walking or taxis. "
                "Chooses walking if the distance is ≤2, taxi otherwise (if the person has enough cash). "
                "People: alice (home_a, $20), bob (home_b, $15). "
                "Locations: home_a, home_b, park, station, downtown."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": (
                            "List of travel tasks. Each task is [\"travel\", person, destination]. "
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
                "Finds a plan to rearrange blocks on a table to match a goal configuration. "
                "Problems: 1a (3 blocks, full goal), 1b (3 blocks, partial goal), "
                "2a (4 blocks, full goal), 2b (4 blocks, partial goal), 3 (19 blocks, large problem)."
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
                "Coordinates robots and drones to locate and assist an injured person. "
                "Tasks: 'move' (robot r1 moves to location (5,5)) or "
                "'survey' (drone a1 surveys location (2,2) to check for injured persons)."
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
                "Navigates an autonomous underwater vehicle through a series of competition zones. "
                "Tasks: 'full' (all 5 zones in one task list) or 'staged' (each zone as a separate task)."
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
                "Schedules surgeries in operating rooms with temporal constraints (start/end times). "
                "Tasks: 'single' (patient1 in OR1), 'two' (patient1 + patient2), "
                "'shared_room' (patient1 + patient3 competing for cardiac rooms)."
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
                "Same travel domain as plan_simple_travel but each action includes "
                "start_time and end_time in the result. Origin time: 2025-01-01T10:00:00Z."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": (
                            "List of travel tasks. Each task is [\"travel\", person, destination]. "
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
