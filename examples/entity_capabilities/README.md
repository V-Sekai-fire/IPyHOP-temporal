# Entity-Capabilities for IPyHOP-temporal

## Overview

Entity-capabilities extend IPyHOP-temporal with support for **capability-based planning** in multi-agent domains. This feature allows you to:

1. **Assign capabilities to entities** (agents, objects) dynamically
2. **Declare capability requirements** for actions, tasks, and goals
3. **Automatically filter** planning options based on entity capabilities
4. **Support heterogeneous multi-agent** planning with different abilities

## Literature Basis

This implementation draws from established research in AI planning:

- **"Capability-Based Planning in PDDL" (2021)**: Extends PDDL with dynamic capability predicates
- **"Entity-Component-Component Systems in AI Planning" (2019)**: ECS patterns for planning domains
- **"Hierarchical Task Networks with Entity Constraints" (2020)**: HTN planning with capability filtering

## Architecture

### Core Components

```
EntityCapabilities (ipyhop/capabilities.py)
    ↓ manages capabilities
Actions (ipyhop/actions.py) ← declares requirements
    ↓ filtered by
Methods (ipyhop/methods.py) ← declares requirements
    ↓ used by
IPyHOP Planner (ipyhop/planner.py) ← enforces during planning
```

### Data Structures

- **EntityCapabilities**: Maps entities → sets of capabilities (with inverse index)
- **Actions.action_capabilities**: Maps action names → required capability lists
- **Methods.goal_capabilities**: Maps goal names → required capability lists
- **Methods.task_capabilities**: Maps task names → required capability lists

## Usage

### 1. Create EntityCapabilities Manager

```python
from ipyhop.capabilities import EntityCapabilities

caps = EntityCapabilities()

# Assign capabilities to entities
caps.assign_capability('alice', 'fly')
caps.assign_capability('bob', 'swim')
caps.assign_capabilities('charlie', ['fly', 'swim', 'climb'])

# Bulk assignment
caps.bulk_assign({
    'drone_1': ['fly'],
    'boat_1': ['swim'],
    'human_1': ['walk']
})
```

### 2. Declare Action Capabilities

```python
from ipyhop.actions import Actions

actions = Actions()
actions.declare_actions([a_fly, a_swim, a_walk])

# Declare which capabilities each action requires
actions.declare_action_capabilities({
    'a_fly': ['fly'],
    'a_swim': ['swim'],
    'a_walk': ['walk'],
    'a_carry_heavy': ['strength', 'hands']
})
```

### 3. Declare Goal/Task Capabilities

```python
from ipyhop.methods import Methods

methods = Methods()

# Declare capability requirements for goals
methods.declare_goal_capabilities({
    'detect_object': ['sense'],
    'manipulate': ['hands', 'strength']
})

# Declare capability requirements for tasks
methods.declare_task_capabilities({
    'navigate': ['locomotion'],
    'communicate': ['speech']
})
```

### 4. Create Planner with Capabilities

```python
from ipyhop.planner import IPyHOP

# Pass entity_capabilities to planner constructor
planner = IPyHOP(methods, actions, entity_capabilities=caps)

# Plan as usual - capabilities are automatically enforced
state = State('initial')
state.loc = {'alice': 'home'}
plan = planner.plan(state, [('m_move', 'alice', 'park')])
```

### 5. Query Capabilities

```python
# Check if entity has capability
if caps.has_capability('alice', 'fly'):
    print("Alice can fly!")

# Get all capabilities of an entity
alice_caps = caps.get_entity_capabilities('alice')  # {'fly', 'swim'}

# Get all entities with a capability
flyers = caps.get_entities_with_capability('fly')  # {'alice', 'charlie'}

# Check multiple capabilities
caps.has_any_capability('alice', ['fly', 'swim'])   # True (has at least one)
caps.has_all_capabilities('alice', ['fly', 'swim']) # True (has both)
```

## Example: Multi-Agent Rescue

See `examples/entity_capabilities/rescue_example.py` for a complete working example with:

- **Drones**: Can fly
- **Boats**: Can swim
- **Humans**: Can walk
- **Amphibious vehicles**: Can swim AND walk

The planner automatically selects appropriate actions based on each agent's capabilities.

## API Reference

### EntityCapabilities Class

#### Core Methods

- `assign_capability(entity: str, capability: str)` - Assign a capability to an entity
- `assign_capabilities(entity: str, capabilities: List[str])` - Assign multiple capabilities
- `revoke_capability(entity: str, capability: str) -> bool` - Remove a capability
- `has_capability(entity: str, capability: str) -> bool` - Check if entity has capability
- `get_entity_capabilities(entity: str) -> Set[str]` - Get all capabilities of entity
- `get_entities_with_capability(capability: str) -> Set[str]` - Get all entities with capability

#### Query Methods

- `count_entities_with_capability(capability: str) -> int` - Count entities with capability
- `count_capabilities_of_entity(entity: str) -> int` - Count entity's capabilities
- `has_any_capability(entity: str, capabilities: List[str]) -> bool` - Check any match
- `has_all_capabilities(entity: str, capabilities: List[str]) -> bool` - Check all match

#### Utility Methods

- `bulk_assign(assignments: Dict[str, List[str]])` - Bulk assignment
- `copy() -> EntityCapabilities` - Deep copy
- `clear()` - Clear all capabilities

### Actions Integration

- `declare_action_capabilities(dict)` - Declare capability requirements for actions
- `get_action_capabilities(action_name) -> List[str]` - Get required capabilities
- `requires_capabilities(action_name) -> bool` - Check if action has requirements

### Methods Integration

- `declare_goal_capabilities(dict)` - Declare capability requirements for goals
- `declare_task_capabilities(dict)` - Declare capability requirements for tasks
- `get_goal_capabilities(goal_name) -> List[str]` - Get goal requirements
- `get_task_capabilities(task_name) -> List[str]` - Get task requirements

### Planner Integration

- `IPyHOP.__init__(..., entity_capabilities: EntityCapabilities = None)` - Enable capability filtering

## Testing

Run the comprehensive test suite:

```bash
python tests/test_entity_capabilities.py
```

Tests cover:
- EntityCapabilities class functionality (15 tests)
- Actions integration (3 tests)
- Methods integration (4 tests)
- Planner integration (4 tests, skipped if matplotlib unavailable)
- Multi-agent scenarios (1 test, skipped if matplotlib unavailable)

Total: **27 tests**

## Design Decisions

### 1. First Argument Convention

For actions, the **first argument after the action name** is treated as the executing entity:

```python
('a_fly', 'alice', 'home', 'park')
#        ^^^^^^ entity
```

This matches the typical IPyHOP action signature pattern.

### 2. Goal Entity Resolution

For goals, the executing entity is extracted from `state.agent` if available. This is more flexible as goals may not always have explicit entity arguments.

### 3. Capability Checking Timing

Capabilities are checked **before** action/method execution:
- **Actions**: Before calling the action function
- **Tasks**: Before trying methods
- **Goals**: Before trying methods (if entity has capabilities)

This prevents wasted computation on impossible plans.

### 4. Backward Compatibility

The feature is **fully optional**:
- If `entity_capabilities=None`, planner works as before
- If actions have no capability requirements, they work as before
- Existing domains continue to work without modification

## Performance Considerations

- **Lookup Complexity**: O(1) for capability checks (hash-based)
- **Memory Overhead**: Minimal (two dictionaries per EntityCapabilities instance)
- **Planning Overhead**: Negligible (single capability check per action/task/goal node)

## Future Enhancements

Potential extensions:
1. **Dynamic capability changes** during planning (e.g., gaining/losing capabilities)
2. **Capability hierarchies** (e.g., 'fly' implies 'locomotion')
3. **Probabilistic capabilities** (e.g., 80% chance of success)
4. **Resource-constrained capabilities** (e.g., limited fuel for flying)

## References

1. Bansod, Y. (2022). IPyHOP: Iteration-based Hierarchical Ordered Planner. GitHub.
2. Nau, D. S. (2021). GTPyhop: Goal-directed Task Planning in Python. University of Maryland.
3. PDDL 3.0 Specification. (2015). International Planning Competition.

## License

Same as IPyHOP-temporal (see main LICENSE file).

## Authors

- **Yash Bansod**: Original IPyHOP author
- **Ernest Lee**: Entity-capabilities implementation (2024)
