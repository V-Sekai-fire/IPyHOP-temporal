#!/usr/bin/env python3
"""
Adversarial test suite for plan plugin.
Tests all six domains with edge cases, precondition traps, and input validation.
"""

import sys
import copy
sys.path.insert(0, '/Users/ernest.lee/.hermes/plugins/plan')

from plan import plan_replan, plan_simulate

def test_simple_travel():
    """Test simple_travel domain adversarial cases."""
    print("=" * 60)
    print("SIMPLE_TRAVEL DOMAIN")
    print("=" * 60)
    
    # Test 1: Valid plan
    print("\n[1] Valid plan: alice home_a -> park")
    result = plan_replan('simple_travel', None, [[[ 'travel', 'alice', 'park' ]]])
    print(f"    steps={result.get('steps')} | session_id={result.get('session_id', 'N/A')[:8]}...")
    assert result.get('steps', 0) > 0, "Should have found a plan"
    
    # Test 2: No-op (already at destination)
    print("\n[2] No-op: alice already at park")
    state = {
        'rigid': {'dist': {('home_a', 'downtown'): 3, ('home_a', 'park'): 2}},
        'fluents': {'location': {'alice': 'park'}, 'cash': {'alice': 20}}
    }
    result = plan_replan('simple_travel', state, [[[ 'travel', 'alice', 'park' ]]])
    print(f"    steps={result.get('steps')} (expected: 0 for vacuous success)")
    assert result.get('steps') == 0, "Should return 0 steps for no-op"
    
    # Test 3: Impossible plan (no cash, distance too far)
    print("\n[3] Impossible: cash=0, dist=3 (can't walk or taxi)")
    state = {
        'rigid': {'dist': {('home_a', 'downtown'): 3}},
        'fluents': {'location': {'alice': 'home_a'}, 'cash': {'alice': 0}}
    }
    result = plan_replan('simple_travel', state, [[[ 'travel', 'alice', 'downtown' ]]])
    print(f"    steps={result.get('steps')} (expected: 0 for failure)")
    assert result.get('steps') == 0, "Should return 0 steps for failure"
    
    # Test 4: Invalid tasks type (string)
    print("\n[4] Invalid input: tasks as string")
    result = plan_replan('simple_travel', None, 'travel')
    print(f"    error={result.get('error', 'none')}")
    assert 'error' in result, "Should return error for non-list tasks"
    
    # Test 5: Invalid task (too short)
    print("\n[5] Invalid task: too short")
    result = plan_replan('simple_travel', None, [[[ 'travel' ]]])
    print(f"    error={result.get('error', 'none')}")
    assert 'error' in result, "Should return error for short task"
    
    # Test 6: Unknown task name
    print("\n[6] Unknown task: fly")
    result = plan_replan('simple_travel', None, [[[ 'fly', 'alice', 'mars' ]]])
    print(f"    steps={result.get('steps')} (expected: 0)")
    assert result.get('steps') == 0, "Should return 0 for unknown task"
    
    # Test 7: Unknown entity
    print("\n[7] Unknown person: carol")
    result = plan_replan('simple_travel', None, [[[ 'travel', 'carol', 'park' ]]])
    print(f"    steps={result.get('steps')} (expected: 0)")
    assert result.get('steps') == 0, "Should return 0 for unknown person"
    
    # Test 8: None tasks (should use default)
    print("\n[8] None tasks (should use default)")
    result = plan_replan('simple_travel', None, None)
    print(f"    steps={result.get('steps')} (expected: >0 from default)")
    assert result.get('steps', 0) > 0, "Should use default tasks"
    
    # Test 9: Empty tasks list
    print("\n[9] Empty tasks list")
    result = plan_replan('simple_travel', None, [[]])
    print(f"    steps={result.get('steps')} (expected: >0 from default fallback)")
    
    # Test 10: Invalid state type
    print("\n[10] Invalid state type: string")
    result = plan_replan('simple_travel', 'bad_state', [[[ 'travel', 'alice', 'park' ]]])
    print(f"    error={result.get('error', 'none')}")
    assert 'error' in result, "Should return error for invalid state"
    
    print("\n✓ simple_travel tests complete\n")


def test_healthcare():
    """Test healthcare_scheduling domain."""
    print("=" * 60)
    print("HEALTHCARE_SCHEDULING DOMAIN")
    print("=" * 60)
    
    # Test 1: Valid plan
    print("\n[1] Valid: patient1 OR1 cardiac surgery")
    result = plan_replan('healthcare_scheduling', None, [[[ 'perform_surgery', 'patient1', 'OR1', 'cardiac' ]]])
    print(f"    steps={result.get('steps')}")
    assert result.get('steps', 0) > 0, "Should find a valid plan"
    
    # Test 2: Precondition trap (patient3 not in OR1)
    print("\n[2] Precondition trap: patient3 in OR3, scheduling in OR1")
    result = plan_replan('healthcare_scheduling', None, [[[ 'perform_surgery', 'patient3', 'OR1', 'cardiac' ]]])
    print(f"    steps={result.get('steps')} (expected: 0, patient3 is in OR3)")
    assert result.get('steps') == 0, "Should fail due to patient_location precondition"
    
    # Test 3: simulate out-of-range step
    print("\n[3] simulate with out-of-range step")
    plan_result = plan_replan('healthcare_scheduling', None, [[[ 'perform_surgery', 'patient1', 'OR1', 'cardiac' ]]])
    session_id = plan_result.get('session_id')
    if session_id:
        sim_result = plan_simulate(session_id, 99999)
        print(f"    step={sim_result.get('step')}, actions={len(sim_result.get('plan', []))}")
        print(f"    (expected: step=99999, empty plan)")
    
    print("\n✓ healthcare_scheduling tests complete\n")


def test_blocks_world():
    """Test blocks_world domain."""
    print("=" * 60)
    print("BLOCKS_WORLD DOMAIN")
    print("=" * 60)
    
    # Test 1: Valid plan
    print("\n[1] Valid: stack a on b")
    result = plan_replan('blocks_world', None, [[[ 'stack', 'a', 'b' ]]])
    print(f"    steps={result.get('steps')}")
    assert result.get('steps', 0) > 0, "Should find a valid plan"
    
    # Test 2: Goal already satisfied
    print("\n[2] Goal already satisfied")
    # This is hard to test without knowing the exact init_state
    # Just verify it doesn't crash
    result = plan_replan('blocks_world', None, [[[ 'stack', 'a', 'b' ]]])
    print(f"    steps={result.get('steps')}")
    
    print("\n✓ blocks_world tests complete\n")


def test_temporal_travel():
    """Test temporal_travel domain."""
    print("=" * 60)
    print("TEMPORAL_TRAVEL DOMAIN")
    print("=" * 60)
    
    # Test 1: Valid plan
    print("\n[1] Valid: alice home_a -> downtown")
    result = plan_replan('temporal_travel', None, [[[ 'travel', 'alice', 'downtown' ]]])
    print(f"    steps={result.get('steps')}")
    assert result.get('steps', 0) > 0, "Should find a valid plan"
    
    # Test 2: None tasks
    print("\n[2] None tasks")
    result = plan_replan('temporal_travel', None, None)
    print(f"    steps={result.get('steps')}")
    
    print("\n✓ temporal_travel tests complete\n")


def test_rescue():
    """Test rescue domain."""
    print("=" * 60)
    print("RESCUE DOMAIN")
    print("=" * 60)
    
    # Test 1: Valid plan
    print("\n[1] Valid: move r1 + survey a1")
    result = plan_replan('rescue', None, [[[ 'move', 'r1', 'loc1', 'loc2' ], [ 'survey', 'a1', 'loc1' ]]])
    print(f"    steps={result.get('steps')}")
    
    print("\n✓ rescue tests complete\n")


def test_robosub():
    """Test robosub domain."""
    print("=" * 60)
    print("ROBOSUB DOMAIN")
    print("=" * 60)
    
    # Test 1: Valid plan
    print("\n[1] Valid: navigate sub1 to zone1")
    result = plan_replan('robosub', None, [[[ 'navigate', 'sub1', 'zone1' ]]])
    print(f"    steps={result.get('steps')}")
    
    print("\n✓ robosub tests complete\n")


def test_simulate():
    """Test plan_simulate function."""
    print("=" * 60)
    print("SIMULATE FUNCTION")
    print("=" * 60)
    
    # Get a valid plan first
    plan_result = plan_replan('simple_travel', None, [[[ 'travel', 'alice', 'park' ]]])
    session_id = plan_result.get('session_id')
    
    if not session_id:
        print("\n[SKIP] No session_id from plan_replan")
        return
    
    # Test 1: Valid step 0
    print("\n[1] simulate step 0")
    sim_result = plan_simulate(session_id, 0)
    print(f"    step={sim_result.get('step')}, actions_remaining={len(sim_result.get('plan', []))}")
    
    # Test 2: Valid step 1
    print("\n[2] simulate step 1")
    sim_result = plan_simulate(session_id, 1)
    print(f"    step={sim_result.get('step')}, actions_remaining={len(sim_result.get('plan', []))}")
    
    # Test 3: Out of range step
    print("\n[3] simulate out-of-range step 99999")
    sim_result = plan_simulate(session_id, 99999)
    print(f"    step={sim_result.get('step')}, actions_remaining={len(sim_result.get('plan', []))}")
    print(f"    (expected: step=99999, empty plan)")
    
    # Test 4: Invalid session_id
    print("\n[4] simulate with invalid session_id")
    sim_result = plan_simulate('invalid_session_12345', 0)
    print(f"    error={sim_result.get('error', 'none')}")
    
    print("\n✓ simulate tests complete\n")


def main():
    """Run all adversarial tests."""
    print("\n" + "=" * 60)
    print("PLAN PLUGIN ADVERSARIAL TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_simple_travel()
        test_healthcare()
        test_blocks_world()
        test_temporal_travel()
        test_rescue()
        test_robosub()
        test_simulate()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETE")
        print("=" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
