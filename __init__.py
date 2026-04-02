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
        "plan_sample_simple_travel",
        {
            "name": "plan_sample_simple_travel",
            "description": (
                "Plan travel routes for people in a simple city domain. "
                "Use when you need to find a sequence of actions (walk or taxi) to move people between locations. "
                "Automatically chooses walking for short distances (<=2 units) and taxis for longer distances if cash >= fare. "
                "Returns ordered actions like [a_call_taxi, a_ride_taxi, a_pay_driver] or [a_walk]. "
                "Persons: alice ($20), bob ($15). Locations: home_a, home_b, park, station, downtown. "
                "Use for pathfinding with limited resources and multiple transport options."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": 'List of ["travel", person, destination] tasks. Default: [["travel", "alice", "park"]]',
                        "items": {"type": "array"},
                    },
                },
                "required": [],
            },
        },
        handle_simple_travel,
    ),
    (
        "plan_sample_blocks_world",
        {
            "name": "plan_sample_blocks_world",
            "description": (
                "Solve block-stacking puzzles using a robotic hand. "
                "Use when you need to rearrange blocks to achieve a goal configuration. "
                "Handles pickup, unstack, putdown, stack with preconditions (only clear blocks, only on clear surfaces). "
                "Returns action sequences to transform initial to goal state. "
                "Problems: 1a/1b (3 blocks), 2a/2b (4 blocks), 3 (19 blocks). "
                "Use for classical planning with physical constraints and ordering dependencies. "
                "Supports custom states and goals via state and tasks parameters for testing impossible configurations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Problem identifier: '1a', '1b', '2a', '2b', or '3'. Default: '1b'.",
                    },
                    "state": {
                        "type": "object",
                        "description": "Custom initial state override. Format: {'pos': {block: position, ...}, 'clear': {block: bool, ...}, 'holding': {'hand': bool}}. Position can be another block or 'table'.",
                        "properties": {
                            "pos": {
                                "type": "object",
                                "description": "Map of block -> position (another block or 'table')",
                            },
                            "clear": {
                                "type": "object",
                                "description": "Map of block -> boolean (is block clear)",
                            },
                            "holding": {
                                "type": "object",
                                "description": "Map of 'hand' -> boolean (is hand holding something)",
                            },
                        },
                    },
                    "tasks": {
                        "type": "array",
                        "description": "Custom goal tasks. For MultiGoal: [{'__multigoal__': true, 'goal_tag': 'name', 'pos': {...}, 'clear': {...}, 'holding': {...}}]. For simple tasks: [['task_name', arg1, arg2], ...].",
                        "items": {},
                    },
                },
                "required": [],
            },
        },
        handle_blocks_world,
    ),
    (
        "plan_sample_rescue",
        {
            "name": "plan_sample_rescue",
            "description": (
                "Coordinate multi-robot rescue operations with wheeled robots and drones. "
                "Use when planning search-and-rescue with heterogeneous robot capabilities. "
                "Drones fly and capture images; wheeled robots carry medicine. "
                "Handles movement, altitude changes, image capture, person inspection, medical support. "
                "Returns coordinated action sequences for all robots (r1, w1, a1). "
                "Use for multi-agent coordination with different capabilities."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task type: 'move' (robot moves to location) or 'survey' (drone surveys for person). Default: 'survey'.",
                    },
                },
                "required": [],
            },
        },
        handle_rescue,
    ),
    (
        "plan_sample_robosub",
        {
            "name": "plan_sample_robosub",
            "description": (
                "Plan underwater robot missions for AUV competitions. "
                "Use when navigating through multiple zones with objectives: cross gates, pick objects, trace paths, "
                "touch vampires, fill coffins with garlic, defeat Dracula. "
                "Handles zone navigation, object localization, complex multi-step tasks. "
                "Returns complete mission plans with 30+ actions. "
                "Use for multi-zone navigation with interdependent objectives."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task mode: 'full' (all zones in one plan) or 'staged' (one zone at a time). Default: 'full'.",
                    },
                },
                "required": [],
            },
        },
        handle_robosub,
    ),
    (
        "plan_sample_healthcare",
        {
            "name": "plan_sample_healthcare",
            "description": (
                "Schedule surgical procedures in operating rooms with temporal constraints. "
                "Use when creating time-aware surgery schedules respecting room availability and equipment. "
                "Returns temporally-annotated plans with ISO-8601 timestamps (prepare PT30M, surgery PT2H, recover PT15M, clean PT20M). "
                "Rooms: OR1/OR3 (cardiac), OR2 (orthopedic). Patients: patient1/2/3. "
                "Use for scheduling where action durations matter and resources allocated over time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Scenario: 'single' (patient1/OR1), 'two' (patient1+2), 'shared_room' (patient1+3 both cardiac). Default: 'single'.",
                    },
                },
                "required": [],
            },
        },
        handle_healthcare,
    ),
    (
        "plan_sample_temporal_travel",
        {
            "name": "plan_sample_temporal_travel",
            "description": (
                "Plan travel routes with explicit timing information. "
                "Same domain as plan_simple_travel but returns temporally-annotated actions with ISO-8601 start/end times. "
                "Use when you need action timing, not just sequence (walk PT5M, taxi PT10M). "
                "Returns actions with duration, start_time, end_time fields. "
                "Use for time-aware pathfinding where arrival times matter."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": 'List of ["travel", person, destination] tasks. Default: [["travel", "alice", "park"]]',
                        "items": {"type": "array"},
                    },
                },
                "required": [],
            },
        },
        handle_temporal_travel,
    ),
    (
        "plan_sample_replan",
        {
            "name": "plan_sample_replan",
            "description": (
                "Generate alternative plan after a previous plan failed during execution. "
                "Use when you have session_id from prior planning and an action failed at runtime. "
                "Provides failed node ID and optionally blacklists actions to avoid. "
                "Returns revised plan that works around the failure. "
                "Use for dynamic replanning in uncertain environments where preconditions change."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "session_id from a prior plan_* call.",
                    },
                    "fail_node_id": {
                        "type": "integer",
                        "description": "Node ID in the solution tree that failed.",
                    },
                    "blacklist": {
                        "type": "array",
                        "description": 'Optional list of action tuples to avoid. E.g. [["a_walk", "alice", "home_a", "park"]].',
                        "items": {"type": "array"},
                    },
                },
                "required": [],
            },
        },
        handle_replan,
    ),
    (
        "plan_sample_simulate",
        {
            "name": "plan_sample_simulate",
            "description": (
                "Step through a plan to see how world state changes after each action. "
                "Use to verify plans, debug failures, or understand intermediate states. "
                "Returns sequence of state snapshots showing loc, cash, pos, clear, etc. after each action. "
                "Use for plan verification, debugging, and educational purposes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "session_id from a prior plan_* or plan_replan call.",
                    },
                    "start_index": {
                        "type": "integer",
                        "description": "Step index to start simulation from. Default: 0 (full plan).",
                    },
                },
                "required": [],
            },
        },
        handle_simulate,
    ),
]


def register(ctx):
    plugin_name = ctx.plugin_name
    for name, schema, handler in _TOOLS:
        ctx.register_tool(name, plugin_name, schema, handler)

