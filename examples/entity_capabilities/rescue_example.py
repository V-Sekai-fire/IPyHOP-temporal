#!/usr/bin/env python
"""
Entity-Capabilities Example for IPyHOP-temporal

This example demonstrates the entity-capabilities system with a multi-agent
rescue scenario where different agents have different capabilities.

Scenario:
- Drones can fly but cannot swim
- Boats can swim but cannot fly
- Humans can walk but cannot fly or swim
- Amphibious vehicles can both swim and walk

The planner will automatically select appropriate actions based on each
agent's capabilities.
"""

from ipyhop.actions import Actions
from ipyhop.capabilities import EntityCapabilities
from ipyhop.methods import Methods
from ipyhop.planner import IPyHOP
from ipyhop.state import State

# ============================================================================
# Define Actions
# ============================================================================


def a_fly(agent, from_loc, to_loc):
    """Action: Agent flies from one location to another."""
    if state.loc[agent] == from_loc:
        new_state = State("s")
        new_state.loc = state.loc.copy()
        new_state.loc[agent] = to_loc
        return new_state
    return None


def a_swim(agent, from_loc, to_loc):
    """Action: Agent swims from one location to another."""
    if state.loc[agent] == from_loc:
        new_state = State("s")
        new_state.loc = state.loc.copy()
        new_state.loc[agent] = to_loc
        return new_state
    return None


def a_walk(agent, from_loc, to_loc):
    """Action: Agent walks from one location to another."""
    if state.loc[agent] == from_loc:
        new_state = State("s")
        new_state.loc = state.loc.copy()
        new_state.loc[agent] = to_loc
        return new_state
    return None


# ============================================================================
# Define Methods
# ============================================================================


def m_move(agent, from_loc, to_loc):
    """Method: Move agent from one location to another using any available method."""
    # Try all movement actions - planner will filter based on capabilities
    return [
        ("a_fly", agent, from_loc, to_loc),
        ("a_swim", agent, from_loc, to_loc),
        ("a_walk", agent, from_loc, to_loc),
    ]


# ============================================================================
# Set Up Domain
# ============================================================================

# Create actions container
actions = Actions()
actions.declare_actions([a_fly, a_swim, a_walk])

# Declare action capabilities
actions.declare_action_capabilities({"a_fly": ["fly"], "a_swim": ["swim"], "a_walk": ["walk"]})

# Create methods container
methods = Methods()
methods.declare_task_methods("m_move", [m_move])

# Create entity capabilities manager
entity_caps = EntityCapabilities()

# Assign capabilities to agents
entity_caps.assign_capability("drone_1", "fly")
entity_caps.assign_capability("drone_2", "fly")
entity_caps.assign_capability("boat_1", "swim")
entity_caps.assign_capability("boat_2", "swim")
entity_caps.assign_capability("human_1", "walk")
entity_caps.assign_capability("human_2", "walk")
entity_caps.assign_capabilities("amphibious_vehicle_1", ["swim", "walk"])

print("Entity Capabilities:")
print(entity_caps)
print("\n" + "=" * 60 + "\n")

# Create planner with entity capabilities
planner = IPyHOP(methods, actions, entity_capabilities=entity_caps)

# ============================================================================
# Example 1: Drone flying
# ============================================================================

print("Example 1: Drone flying from base to mountain")
print("-" * 60)

state = State("initial")
state.loc = {"drone_1": "base", "boat_1": "harbor", "human_1": "base"}

task_list = [("m_move", "drone_1", "base", "mountain")]
plan = planner.plan(state, task_list, verbose=1)

print(f"Plan: {plan}\n")

# ============================================================================
# Example 2: Boat swimming
# ============================================================================

print("Example 2: Boat swimming from harbor to offshore")
print("-" * 60)

state2 = State("initial2")
state2.loc = {"drone_1": "base", "boat_1": "harbor", "human_1": "base"}

task_list2 = [("m_move", "boat_1", "harbor", "offshore")]
plan2 = planner.plan(state2, task_list2, verbose=1)

print(f"Plan: {plan2}\n")

# ============================================================================
# Example 3: Human walking
# ============================================================================

print("Example 3: Human walking from base to city")
print("-" * 60)

state3 = State("initial3")
state3.loc = {"drone_1": "base", "boat_1": "harbor", "human_1": "base"}

task_list3 = [("m_move", "human_1", "base", "city")]
plan3 = planner.plan(state3, task_list3, verbose=1)

print(f"Plan: {plan3}\n")

# ============================================================================
# Example 4: Amphibious vehicle (multiple options)
# ============================================================================

print("Example 4: Amphibious vehicle from shore to island")
print("-" * 60)

entity_caps.assign_capabilities("amphibious_1", ["swim", "walk"])

state4 = State("initial4")
state4.loc = {"amphibious_1": "shore"}

task_list4 = [("m_move", "amphibious_1", "shore", "island")]
plan4 = planner.plan(state4, task_list4, verbose=1)

print(f"Plan: {plan4}\n")

# ============================================================================
# Example 5: Capability violation (should fail)
# ============================================================================

print("Example 5: Attempting impossible action (human trying to fly)")
print("-" * 60)

state5 = State("initial5")
state5.loc = {"human_1": "base"}

task_list5 = [("m_move", "human_1", "base", "mountain")]

try:
    plan5 = planner.plan(state5, task_list5, verbose=0)
    print(f"Unexpected success: {plan5}")
except AssertionError as e:
    print("Expected failure: Human cannot fly (no 'fly' capability)")
    print(f"AssertionError: {e}\n")

# ============================================================================
# Summary
# ============================================================================

print("=" * 60)
print("Entity-Capabilities Example Complete!")
print("=" * 60)
print("""
Key Features Demonstrated:
1. Action-level capability requirements (a_fly requires 'fly')
2. Entity-level capability assignment (drone_1 has 'fly')
3. Automatic capability filtering during planning
4. Multi-agent planning with heterogeneous capabilities
5. Capability violation detection and failure

The planner automatically selects actions that match each agent's
capabilities, enabling flexible multi-agent coordination without
hardcoding agent-specific logic.
""")
