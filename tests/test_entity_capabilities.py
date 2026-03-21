#!/usr/bin/env python
"""
Unit Tests for Entity-Capabilities System in IPyHOP-temporal

These tests validate:
1. EntityCapabilities class functionality
2. Integration with Actions class
3. Integration with Methods class
4. Capability-based filtering in IPyHOP planner
5. Multi-agent planning with heterogeneous capabilities

Author: Ernest Lee
Date: 2024-03-20
"""

import os
import sys
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from modules to avoid matplotlib dependency
import importlib.util

# Load State module
state_spec = importlib.util.spec_from_file_location("state", "ipyhop/state.py")
state_module = importlib.util.module_from_spec(state_spec)
state_spec.loader.exec_module(state_module)
State = state_module.State

# Load Methods module
methods_spec = importlib.util.spec_from_file_location("methods", "ipyhop/methods.py")
methods_module = importlib.util.module_from_spec(methods_spec)
methods_spec.loader.exec_module(methods_module)
Methods = methods_module.Methods

# Load Actions module
actions_spec = importlib.util.spec_from_file_location("actions", "ipyhop/actions.py")
actions_module = importlib.util.module_from_spec(actions_spec)
actions_spec.loader.exec_module(actions_module)
Actions = actions_module.Actions

# Load Capabilities module (ReBAC-based)
caps_spec = importlib.util.spec_from_file_location("capabilities", "ipyhop/capabilities.py")
caps_module = importlib.util.module_from_spec(caps_spec)
caps_spec.loader.exec_module(caps_module)
ReBACEngine = caps_module.ReBACEngine
EntityCapabilities = caps_module.EntityCapabilities
RelationshipType = caps_module.RelationshipType
Condition = caps_module.Condition

# Load Planner module (this one has more dependencies)
try:
    from ipyhop.planner import IPyHOP

    PLANNER_AVAILABLE = True
except ImportError as e:
    IPyHOP = None
    PLANNER_AVAILABLE = False
    print(f"Warning: IPyHOP not available for testing: {e}")


# ============================================================================
# Test EntityCapabilities Class
# ============================================================================


class TestEntityCapabilities(unittest.TestCase):
    """Test suite for EntityCapabilities class."""

    def setUp(self):
        """Set up test fixtures."""
        self.caps = EntityCapabilities()

    def test_initialization(self):
        """Test that EntityCapabilities initializes correctly."""
        self.assertEqual(self.caps.get_all_entities(), set())
        self.assertEqual(self.caps.get_all_capabilities(), set())

    def test_assign_capability(self):
        """Test assigning a single capability to an entity."""
        self.caps.assign_capability("alice", "fly")

        self.assertTrue(self.caps.has_capability("alice", "fly"))
        self.assertFalse(self.caps.has_capability("alice", "swim"))
        self.assertIn("alice", self.caps.get_all_entities())
        self.assertIn("fly", self.caps.get_all_capabilities())

    def test_assign_multiple_capabilities(self):
        """Test assigning multiple capabilities to an entity."""
        self.caps.assign_capabilities("alice", ["fly", "swim", "climb"])

        self.assertTrue(self.caps.has_capability("alice", "fly"))
        self.assertTrue(self.caps.has_capability("alice", "swim"))
        self.assertTrue(self.caps.has_capability("alice", "climb"))
        self.assertEqual(len(self.caps.get_entity_capabilities("alice")), 3)

    def test_revoke_capability(self):
        """Test revoking a capability from an entity."""
        self.caps.assign_capability("alice", "fly")
        self.assertTrue(self.caps.has_capability("alice", "fly"))

        result = self.caps.revoke_capability("alice", "fly")
        self.assertTrue(result)
        self.assertFalse(self.caps.has_capability("alice", "fly"))

    def test_revoke_nonexistent_capability(self):
        """Test revoking a capability that doesn't exist."""
        result = self.caps.revoke_capability("alice", "fly")
        self.assertFalse(result)

    def test_get_entities_with_capability(self):
        """Test getting all entities with a specific capability."""
        self.caps.assign_capability("alice", "fly")
        self.caps.assign_capability("bob", "fly")
        self.caps.assign_capability("charlie", "swim")

        flyers = self.caps.get_entities_with_capability("fly")
        self.assertEqual(flyers, {"alice", "bob"})

        swimmers = self.caps.get_entities_with_capability("swim")
        self.assertEqual(swimmers, {"charlie"})

    def test_get_entity_capabilities(self):
        """Test getting all capabilities of an entity."""
        self.caps.assign_capabilities("alice", ["fly", "swim"])
        self.caps.assign_capability("bob", "climb")

        alice_caps = self.caps.get_entity_capabilities("alice")
        self.assertEqual(alice_caps, {"fly", "swim"})

        bob_caps = self.caps.get_entity_capabilities("bob")
        self.assertEqual(bob_caps, {"climb"})

    def test_count_entities_with_capability(self):
        """Test counting entities with a capability."""
        self.caps.assign_capability("alice", "fly")
        self.caps.assign_capability("bob", "fly")
        self.caps.assign_capability("charlie", "fly")

        count = self.caps.count_entities_with_capability("fly")
        self.assertEqual(count, 3)

    def test_count_capabilities_of_entity(self):
        """Test counting capabilities of an entity."""
        self.caps.assign_capabilities("alice", ["fly", "swim", "climb"])

        count = self.caps.count_capabilities_of_entity("alice")
        self.assertEqual(count, 3)

    def test_has_any_capability(self):
        """Test checking if entity has any of multiple capabilities."""
        self.caps.assign_capability("alice", "fly")

        self.assertTrue(self.caps.has_any_capability("alice", ["swim", "fly", "climb"]))
        self.assertTrue(self.caps.has_any_capability("alice", ["fly"]))
        self.assertFalse(self.caps.has_any_capability("alice", ["swim", "climb"]))

    def test_has_all_capabilities(self):
        """Test checking if entity has all of multiple capabilities."""
        self.caps.assign_capabilities("alice", ["fly", "swim"])

        self.assertTrue(self.caps.has_all_capabilities("alice", ["fly", "swim"]))
        self.assertTrue(self.caps.has_all_capabilities("alice", ["fly"]))
        self.assertFalse(self.caps.has_all_capabilities("alice", ["fly", "climb"]))

    def test_bulk_assign(self):
        """Test bulk assignment of capabilities."""
        self.caps.bulk_assign({"alice": ["fly", "swim"], "bob": ["swim", "climb"], "charlie": ["fly", "climb"]})

        self.assertTrue(self.caps.has_capability("alice", "fly"))
        self.assertTrue(self.caps.has_capability("alice", "swim"))
        self.assertTrue(self.caps.has_capability("bob", "swim"))
        self.assertTrue(self.caps.has_capability("bob", "climb"))
        self.assertTrue(self.caps.has_capability("charlie", "fly"))
        self.assertTrue(self.caps.has_capability("charlie", "climb"))

    def test_copy(self):
        """Test copying EntityCapabilities."""
        self.caps.assign_capability("alice", "fly")
        self.caps.assign_capability("bob", "swim")

        caps_copy = self.caps.copy()

        self.assertTrue(caps_copy.has_capability("alice", "fly"))
        self.assertTrue(caps_copy.has_capability("bob", "swim"))

        # Modify copy
        caps_copy.revoke_capability("alice", "fly")

        # Original should be unchanged
        self.assertTrue(self.caps.has_capability("alice", "fly"))
        self.assertFalse(caps_copy.has_capability("alice", "fly"))

    def test_clear(self):
        """Test clearing all capabilities."""
        self.caps.assign_capability("alice", "fly")
        self.caps.assign_capability("bob", "swim")

        self.caps.clear()

        self.assertEqual(self.caps.get_all_entities(), set())
        self.assertEqual(self.caps.get_all_capabilities(), set())

    def test_string_representation(self):
        """Test string representation of EntityCapabilities."""
        self.caps.assign_capability("alice", "fly")
        self.caps.assign_capability("bob", "swim")

        str_repr = str(self.caps)

        self.assertIn("ENTITY-CAPABILITIES:", str_repr)
        self.assertIn("alice", str_repr)
        self.assertIn("bob", str_repr)
        self.assertIn("fly", str_repr)
        self.assertIn("swim", str_repr)


# ============================================================================
# Test Actions Integration
# ============================================================================


class TestActionsCapabilitiesIntegration(unittest.TestCase):
    """Test suite for Actions class capability integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.actions = Actions()

    def test_declare_action_capabilities(self):
        """Test declaring capabilities for actions."""

        def dummy_action():
            return False

        self.actions.declare_actions([dummy_action])
        self.actions.declare_action_capabilities({"dummy_action": ["fly", "strength"]})

        caps = self.actions.get_action_capabilities("dummy_action")
        self.assertEqual(caps, ["fly", "strength"])

    def test_get_action_capabilities_nonexistent(self):
        """Test getting capabilities for non-existent action."""
        caps = self.actions.get_action_capabilities("nonexistent")
        self.assertEqual(caps, [])

    def test_requires_capabilities(self):
        """Test checking if action requires capabilities."""

        def action_with_caps():
            return False

        def action_without_caps():
            return False

        self.actions.declare_actions([action_with_caps, action_without_caps])
        self.actions.declare_action_capabilities({"action_with_caps": ["fly"]})

        self.assertTrue(self.actions.requires_capabilities("action_with_caps"))
        self.assertFalse(self.actions.requires_capabilities("action_without_caps"))


# ============================================================================
# Test Methods Integration
# ============================================================================


class TestMethodsCapabilitiesIntegration(unittest.TestCase):
    """Test suite for Methods class capability integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.methods = Methods()

    def test_declare_goal_capabilities(self):
        """Test declaring capabilities for goals."""
        self.methods.declare_goal_capabilities({"detect_object": ["sense"], "manipulate": ["hands", "strength"]})

        caps = self.methods.get_goal_capabilities("detect_object")
        self.assertEqual(caps, ["sense"])

        caps = self.methods.get_goal_capabilities("manipulate")
        self.assertEqual(caps, ["hands", "strength"])

    def test_get_goal_capabilities_nonexistent(self):
        """Test getting capabilities for non-existent goal."""
        caps = self.methods.get_goal_capabilities("nonexistent")
        self.assertEqual(caps, [])

    def test_declare_task_capabilities(self):
        """Test declaring capabilities for tasks."""
        self.methods.declare_task_capabilities({"navigate": ["locomotion"], "communicate": ["speech"]})

        caps = self.methods.get_task_capabilities("navigate")
        self.assertEqual(caps, ["locomotion"])

        caps = self.methods.get_task_capabilities("communicate")
        self.assertEqual(caps, ["speech"])

    def test_get_task_capabilities_nonexistent(self):
        """Test getting capabilities for non-existent task."""
        caps = self.methods.get_task_capabilities("nonexistent")
        self.assertEqual(caps, [])


# ============================================================================
# Test Planner Integration
# ============================================================================


class TestPlannerCapabilitiesIntegration(unittest.TestCase):
    """Test suite for IPyHOP planner capability integration."""

    def setUp(self):
        """Set up test fixtures."""
        if not PLANNER_AVAILABLE:
            self.skipTest("IPyHOP planner not available (missing dependencies)")
        self.methods = Methods()
        self.actions = Actions()
        self.caps = EntityCapabilities()

    def test_planner_accepts_entity_capabilities(self):
        """Test that planner accepts entity_capabilities parameter."""
        planner = IPyHOP(self.methods, self.actions, entity_capabilities=self.caps)

        self.assertIsNotNone(planner._entity_capabilities)
        self.assertIs(planner._entity_capabilities, self.caps)

    def test_planner_without_entity_capabilities(self):
        """Test that planner works without entity_capabilities."""
        planner = IPyHOP(self.methods, self.actions)

        self.assertIsNone(planner._entity_capabilities)

    def test_capability_checking_logic(self):
        """Test that capability checking logic works correctly."""
        # Set up capabilities
        self.caps.assign_capability("alice", "fly")
        self.caps.assign_capability("bob", "swim")

        # Test has_all_capabilities
        self.assertTrue(self.caps.has_all_capabilities("alice", ["fly"]))
        self.assertFalse(self.caps.has_all_capabilities("alice", ["swim"]))
        self.assertFalse(self.caps.has_all_capabilities("bob", ["fly"]))

        # Test capability retrieval from actions
        def dummy_action(state, agent, dest):
            return None

        self.actions.declare_actions([dummy_action])
        self.actions.declare_action_capabilities({"dummy_action": ["fly"]})

        caps = self.actions.get_action_capabilities("dummy_action")
        self.assertEqual(caps, ["fly"])

        # Verify capability check would fail for bob
        self.assertFalse(self.caps.has_all_capabilities("bob", caps))

    def test_capability_violation_detection(self):
        """Test that capability violations are properly detected."""

        # Set up an action requiring a capability
        def a_fly(state, agent, dest):
            return None

        self.actions.declare_actions([a_fly])
        self.actions.declare_action_capabilities({"a_fly": ["fly"]})

        # Entity without the capability
        self.caps.assign_capability("bob", "swim")  # bob can swim, not fly

        # Verify the violation would be detected
        required_caps = self.actions.get_action_capabilities("a_fly")
        self.assertFalse(self.caps.has_all_capabilities("bob", required_caps))

        # Entity with the capability
        self.caps.assign_capability("alice", "fly")
        self.assertTrue(self.caps.has_all_capabilities("alice", required_caps))


# ============================================================================
# Test Multi-Agent Scenarios
# ============================================================================


class TestMultiAgentCapabilities(unittest.TestCase):
    """Test suite for multi-agent planning with heterogeneous capabilities."""

    def setUp(self):
        """Set up test fixtures."""
        if not PLANNER_AVAILABLE:
            self.skipTest("IPyHOP planner not available (missing dependencies)")
        self.methods = Methods()
        self.actions = Actions()
        self.caps = EntityCapabilities()

    def test_heterogeneous_capabilities(self):
        """Test planning with agents having different capabilities."""

        # Define actions
        def a_fly(state, agent, dest):
            new_state = State("s")
            new_state.loc = state.loc.copy()
            new_state.loc[agent] = dest
            return new_state

        def a_swim(state, agent, dest):
            new_state = State("s")
            new_state.loc = state.loc.copy()
            new_state.loc[agent] = dest
            return new_state

        def a_walk(state, agent, dest):
            new_state = State("s")
            new_state.loc = state.loc.copy()
            new_state.loc[agent] = dest
            return new_state

        self.actions.declare_actions([a_fly, a_swim, a_walk])
        self.actions.declare_action_capabilities({"a_fly": ["fly"], "a_swim": ["swim"], "a_walk": ["legs"]})

        # Define method
        def m_move(state, agent, dest):
            return [("a_fly", agent, dest), ("a_swim", agent, dest), ("a_walk", agent, dest)]

        self.methods.declare_task_methods("m_move", [m_move])

        # Set up heterogeneous capabilities
        self.caps.assign_capability("bird", "fly")
        self.caps.assign_capability("fish", "swim")
        self.caps.assign_capability("human", "legs")
        self.caps.assign_capabilities("mermaid", ["swim", "legs"])  # mermaid can do both

        planner = IPyHOP(self.methods, self.actions, entity_capabilities=self.caps)

        # Test bird
        state1 = State("s1")
        state1.loc = {"bird": "nest"}
        plan1 = planner.plan(state1, [("m_move", "bird", "sky")])
        self.assertIsInstance(plan1, list)

        # Test fish
        state2 = State("s2")
        state2.loc = {"fish": "pond"}
        plan2 = planner.plan(state2, [("m_move", "fish", "ocean")])
        self.assertIsInstance(plan2, list)

        # Test human
        state3 = State("s3")
        state3.loc = {"human": "home"}
        plan3 = planner.plan(state3, [("m_move", "human", "work")])
        self.assertIsInstance(plan3, list)

        # Test mermaid (has multiple options)
        state4 = State("s4")
        state4.loc = {"mermaid": "beach"}
        plan4 = planner.plan(state4, [("m_move", "mermaid", "ocean")])
        self.assertIsInstance(plan4, list)


# ============================================================================
# Test ReBAC Engine
# ============================================================================


class TestReBACEngine(unittest.TestCase):
    """Test suite for ReBAC (Relationship-Based Access Control) engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.rebac = ReBACEngine()

    def test_direct_capability(self):
        """Test direct capability assignment."""
        self.rebac.add_relationship("alice", "fly", RelationshipType.HAS_CAPABILITY)

        authorized, path = self.rebac.can("alice", "fly")
        self.assertTrue(authorized)
        self.assertEqual(path, ["alice", "[has_capability]", "fly"])

    def test_transitive_capability_via_group(self):
        """Test transitive capability through group membership."""
        # alice is member of pilots group
        self.rebac.add_relationship("alice", "pilots", RelationshipType.IS_MEMBER_OF)
        # pilots group has fly capability
        self.rebac.add_relationship("pilots", "fly", RelationshipType.HAS_CAPABILITY)

        authorized, path = self.rebac.can("alice", "fly")
        self.assertTrue(authorized)
        # Path should be: alice -> [is_member_of] -> pilots -> [has_capability] -> fly
        self.assertIn("pilots", path)
        self.assertIn("[is_member_of]", path)

    def test_conditional_capability(self):
        """Test capability with conditions."""

        class MockState:
            def __init__(self):
                self.fuel = {"charlie": 50}

        def has_fuel(state, subject, obj):
            return state.fuel.get(subject, 0) > 100

        self.rebac.add_relationship(
            "charlie", "fly", RelationshipType.HAS_CAPABILITY, conditions=[Condition(has_fuel, "fuel > 100")]
        )

        state = MockState()

        # Charlie has insufficient fuel
        authorized, _ = self.rebac.can("charlie", "fly", state)
        self.assertFalse(authorized)

        # Charlie has sufficient fuel
        state.fuel["charlie"] = 150
        authorized, _ = self.rebac.can("charlie", "fly", state)
        self.assertTrue(authorized)

    def test_no_capability(self):
        """Test entity without capability."""
        self.rebac.add_relationship("bob", "swim", RelationshipType.HAS_CAPABILITY)

        authorized, path = self.rebac.can("bob", "fly")
        self.assertFalse(authorized)
        self.assertEqual(path, [])

    def test_multiple_relationship_types(self):
        """Test different relationship types."""
        self.rebac.add_relationship("alice", "drone_1", RelationshipType.CONTROLS)
        self.rebac.add_relationship("drone_1", "fly", RelationshipType.HAS_CAPABILITY)

        # alice controls drone_1 which can fly
        authorized, path = self.rebac.can("alice", "fly")
        self.assertTrue(authorized)
        self.assertIn("[controls]", path)

    def test_remove_relationship(self):
        """Test removing a relationship."""
        self.rebac.add_relationship("alice", "fly", RelationshipType.HAS_CAPABILITY)
        self.assertTrue(self.rebac.can("alice", "fly")[0])

        self.rebac.remove_relationship("alice", "fly", RelationshipType.HAS_CAPABILITY)
        self.assertFalse(self.rebac.can("alice", "fly")[0])

    def test_get_relationships(self):
        """Test getting relationships for a subject."""
        self.rebac.add_relationship("alice", "fly", RelationshipType.HAS_CAPABILITY)
        self.rebac.add_relationship("alice", "swim", RelationshipType.HAS_CAPABILITY)

        relationships = self.rebac.get_relationships("alice")
        self.assertEqual(len(relationships), 2)

    def test_get_all_subjects(self):
        """Test getting all subjects."""
        self.rebac.add_relationship("alice", "fly", RelationshipType.HAS_CAPABILITY)
        self.rebac.add_relationship("bob", "swim", RelationshipType.HAS_CAPABILITY)

        subjects = self.rebac.get_all_subjects()
        self.assertEqual(subjects, {"alice", "bob"})

    def test_get_all_objects(self):
        """Test getting all objects."""
        self.rebac.add_relationship("alice", "fly", RelationshipType.HAS_CAPABILITY)
        self.rebac.add_relationship("bob", "swim", RelationshipType.HAS_CAPABILITY)

        objects = self.rebac.get_all_objects()
        self.assertEqual(objects, {"fly", "swim"})

    def test_clear(self):
        """Test clearing all relationships."""
        self.rebac.add_relationship("alice", "fly", RelationshipType.HAS_CAPABILITY)
        self.rebac.clear()

        self.assertEqual(self.rebac.get_all_subjects(), set())
        self.assertEqual(self.rebac.get_all_objects(), set())

    def test_copy(self):
        """Test copying ReBAC engine."""
        self.rebac.add_relationship("alice", "fly", RelationshipType.HAS_CAPABILITY)

        rebac_copy = self.rebac.copy()
        self.assertTrue(rebac_copy.can("alice", "fly")[0])

        # Modify copy
        rebac_copy.remove_relationship("alice", "fly", RelationshipType.HAS_CAPABILITY)

        # Original should be unchanged
        self.assertTrue(self.rebac.can("alice", "fly")[0])
        self.assertFalse(rebac_copy.can("alice", "fly")[0])

    def test_max_depth_prevents_infinite_loop(self):
        """Test that max_depth prevents infinite loops in cyclic graphs."""
        # Create a cycle: alice -> bob -> charlie -> alice
        self.rebac.add_relationship("alice", "bob", RelationshipType.PARTNER_OF)
        self.rebac.add_relationship("bob", "charlie", RelationshipType.PARTNER_OF)
        self.rebac.add_relationship("charlie", "alice", RelationshipType.PARTNER_OF)
        self.rebac.add_relationship("charlie", "fly", RelationshipType.HAS_CAPABILITY)

        # Should not hang, should return empty path or find path within max_depth
        authorized, path = self.rebac.can("alice", "fly", max_depth=5)
        # Either finds path or returns empty, but doesn't hang
        self.assertIsInstance(authorized, bool)


# ============================================================================
# Test Backward Compatibility
# ============================================================================


class TestBackwardCompatibility(unittest.TestCase):
    """Test that EntityCapabilities wrapper maintains backward compatibility."""

    def setUp(self):
        """Set up test fixtures."""
        self.caps = EntityCapabilities()

    def test_assign_capability(self):
        """Test assign_capability (backward compatible)."""
        self.caps.assign_capability("alice", "fly")
        self.assertTrue(self.caps.has_capability("alice", "fly"))

    def test_assign_multiple_capabilities(self):
        """Test assign_capabilities (backward compatible)."""
        self.caps.assign_capabilities("alice", ["fly", "swim"])
        self.assertTrue(self.caps.has_capability("alice", "fly"))
        self.assertTrue(self.caps.has_capability("alice", "swim"))

    def test_revoke_capability(self):
        """Test revoke_capability (backward compatible)."""
        self.caps.assign_capability("alice", "fly")
        self.caps.revoke_capability("alice", "fly")
        self.assertFalse(self.caps.has_capability("alice", "fly"))

    def test_get_entity_capabilities(self):
        """Test get_entity_capabilities (backward compatible)."""
        self.caps.assign_capabilities("alice", ["fly", "swim"])
        caps = self.caps.get_entity_capabilities("alice")
        self.assertEqual(caps, {"fly", "swim"})

    def test_get_entities_with_capability(self):
        """Test get_entities_with_capability (backward compatible)."""
        self.caps.assign_capability("alice", "fly")
        self.caps.assign_capability("bob", "fly")
        flyers = self.caps.get_entities_with_capability("fly")
        self.assertEqual(flyers, {"alice", "bob"})

    def test_has_any_capability(self):
        """Test has_any_capability (backward compatible)."""
        self.caps.assign_capability("alice", "fly")
        self.assertTrue(self.caps.has_any_capability("alice", ["swim", "fly"]))
        self.assertFalse(self.caps.has_any_capability("alice", ["swim", "climb"]))

    def test_has_all_capabilities(self):
        """Test has_all_capabilities (backward compatible)."""
        self.caps.assign_capabilities("alice", ["fly", "swim"])
        self.assertTrue(self.caps.has_all_capabilities("alice", ["fly", "swim"]))
        self.assertFalse(self.caps.has_all_capabilities("alice", ["fly", "climb"]))

    def test_bulk_assign(self):
        """Test bulk_assign (backward compatible)."""
        self.caps.bulk_assign({"alice": ["fly"], "bob": ["swim"]})
        self.assertTrue(self.caps.has_capability("alice", "fly"))
        self.assertTrue(self.caps.has_capability("bob", "swim"))


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEntityCapabilities))
    suite.addTests(loader.loadTestsFromTestCase(TestActionsCapabilitiesIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestMethodsCapabilitiesIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPlannerCapabilitiesIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiAgentCapabilities))
    suite.addTests(loader.loadTestsFromTestCase(TestReBACEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
