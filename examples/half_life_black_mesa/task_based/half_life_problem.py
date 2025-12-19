#!/usr/bin/env python
"""
File Description: Half-Life Black Mesa problem - Initial state and task lists.
Multi-faction scenario with scientists, guards, aliens, and military.
"""

from ipyhop import State

# Initialize state with temporal planning
init_state = State('black_mesa', initial_time='2025-01-15T08:00:00Z')

# ============================================================================
# CHARACTERS AND FACTIONS
# ============================================================================

# Scientists (including named Half-Life characters)
init_state.character_faction = {
    'gordon_freeman': 'scientist',  # The protagonist!
    'dr_kleiner': 'scientist',
    'dr_vance': 'scientist',
    'scientist1': 'scientist',
    'scientist2': 'scientist',
    'scientist3': 'scientist',
}

# Guards (including Barney Calhoun)
init_state.character_faction.update({
    'barney_calhoun': 'guard',  # Security guard who helps Gordon
    'guard1': 'guard',
    'guard2': 'guard',
    'guard3': 'guard',
})

# Aliens (Half-Life specific types)
init_state.character_faction.update({
    'headcrab1': 'alien',  # Basic headcrab
    'headcrab2': 'alien',
    'vortigaunt1': 'alien',  # Intelligent alien species
    'vortigaunt2': 'alien',
    'barnacle1': 'alien',  # Ceiling-dwelling alien
    'houndeye1': 'alien',  # Pack-hunting alien
    'bullsquid1': 'alien',  # Aggressive alien
})

# Military (HECU - Hazardous Environment Combat Unit)
init_state.character_faction.update({
    'hecu_soldier1': 'military',
    'hecu_soldier2': 'military',
    'hecu_soldier3': 'military',
    'hecu_commander': 'military',  # HECU commander
})

# ============================================================================
# CHARACTER LOCATIONS AND STATUS
# ============================================================================

# Initial locations (Half-Life iconic locations)
init_state.character_location = {
    # Gordon Freeman starts in Sector C Test Labs
    'gordon_freeman': 'sector_c_test_labs',
    'dr_kleiner': 'sector_c_test_labs',
    'dr_vance': 'anomalous_materials',
    'scientist1': 'sector_c_test_labs',
    'scientist2': 'anomalous_materials',
    'scientist3': 'sector_c',
    # Barney and guards
    'barney_calhoun': 'sector_c',
    'guard1': 'sector_c',
    'guard2': 'lambda_complex',
    'guard3': 'surface_tension',
    # Aliens spawn after Resonance Cascade
    'headcrab1': 'sector_c',
    'headcrab2': 'anomalous_materials',
    'vortigaunt1': 'sector_c',
    'vortigaunt2': 'lambda_complex',
    'barnacle1': 'sector_c_test_labs',  # On ceiling
    'houndeye1': 'sector_c',
    'bullsquid1': 'anomalous_materials',
    # HECU arrives after the incident
    'hecu_soldier1': 'surface_tension',
    'hecu_soldier2': 'surface_tension',
    'hecu_soldier3': 'lambda_complex',
    'hecu_commander': 'surface_tension',
}

# All characters start alive
init_state.character_alive = {
    'gordon_freeman': True,
    'dr_kleiner': True,
    'dr_vance': True,
    'scientist1': True,
    'scientist2': True,
    'scientist3': True,
    'barney_calhoun': True,
    'guard1': True,
    'guard2': True,
    'guard3': True,
    'headcrab1': True,
    'headcrab2': True,
    'vortigaunt1': True,
    'vortigaunt2': True,
    'barnacle1': True,
    'houndeye1': True,
    'bullsquid1': True,
    'hecu_soldier1': True,
    'hecu_soldier2': True,
    'hecu_soldier3': True,
    'hecu_commander': True,
}

# ============================================================================
# ZONES AND CORRIDORS
# ============================================================================

# Zone accessibility (Half-Life iconic locations)
init_state.zone_accessible = {
    # Sector C Test Labs - Where Gordon starts
    'sector_c_test_labs': {'sector_c': True, 'anomalous_materials': True},
    # Anomalous Materials - Where the experiment goes wrong
    'anomalous_materials': {'sector_c_test_labs': True, 'sector_c': True, 'xen_portal': True},
    # Sector C - Main facility area
    'sector_c': {'sector_c_test_labs': True, 'anomalous_materials': True, 'lambda_complex': True, 'surface_tension': True},
    # Lambda Complex - Advanced research facility
    'lambda_complex': {'sector_c': True, 'xen_portal': True, 'surface_tension': True},
    # Surface Tension - Where HECU arrives
    'surface_tension': {'sector_c': True, 'lambda_complex': True, 'safe_zone': True},
    # Xen Portal - Gateway to alien dimension
    'xen_portal': {'anomalous_materials': True, 'lambda_complex': True, 'xen': True},
    # Xen - Alien dimension
    'xen': {'xen_portal': True},
    # Safe Zone - Evacuation point
    'safe_zone': {'surface_tension': True},
}

# Zone controllers (who controls each zone)
init_state.zone_controller = {
    'sector_c_test_labs': None,
    'anomalous_materials': None,
    'sector_c': None,
    'lambda_complex': None,
    'surface_tension': None,
    'xen_portal': None,
    'xen': None,
    'safe_zone': None,
}

# Zone control status
init_state.zone_controlled = {
    'sector_c_test_labs': False,
    'anomalous_materials': False,
    'sector_c': False,
    'lambda_complex': False,
    'surface_tension': False,
    'xen_portal': False,
    'xen': False,
    'safe_zone': False,
}

# Zone defense status
init_state.zone_defended = {
    'sector_c_test_labs': False,
    'anomalous_materials': False,
    'sector_c': False,
    'lambda_complex': False,
    'surface_tension': False,
    'xen_portal': False,
    'xen': False,
    'safe_zone': False,
}

# Area security status (Half-Life locations)
init_state.area_secured = {
    'sector_c_test_labs': False,
    'sector_c': False,
    'lambda_complex': False,
}

# Perimeter establishment
init_state.perimeter_established = {
    'sector_c': False,
    'lambda_complex': False,
    'surface_tension': False,
}

# Safe zones for evacuation
init_state.zone_safe = {
    'sector_c_test_labs': False,
    'anomalous_materials': False,
    'sector_c': False,
    'lambda_complex': False,
    'surface_tension': False,
    'xen_portal': False,
    'xen': False,
    'safe_zone': True,  # Only safe_zone is safe
}

# Scientist evacuation status
init_state.scientist_evacuated = {
    'gordon_freeman': False,  # Gordon's goal is to escape
    'dr_kleiner': False,
    'dr_vance': False,
    'scientist1': False,
    'scientist2': False,
    'scientist3': False,
}

# ============================================================================
# TASK LISTS - Different Faction Objectives
# ============================================================================

# Task List 1: HECU Objective - Control key zones and eliminate threats
task_list_military = [
    ('military_control_zones', 'hecu_commander', ['sector_c', 'lambda_complex', 'surface_tension']),
    ('military_eliminate_targets', 'hecu_soldier1', ['headcrab1', 'headcrab2', 'vortigaunt1', 'vortigaunt2', 'bullsquid1']),
]

# Task List 2: Alien Objective - Eliminate all humans
task_list_alien = [
    ('alien_eliminate_humans', 'vortigaunt1', ['gordon_freeman', 'dr_kleiner', 'dr_vance', 'scientist1', 'scientist2', 'scientist3', 'barney_calhoun', 'guard1', 'guard2', 'guard3']),
]

# Task List 3: Defend Black Mesa - Secure areas, evacuate scientists, establish perimeters
task_list_defend = [
    ('defend_secure_areas', ['barney_calhoun', 'guard1'], ['sector_c', 'lambda_complex', 'sector_c_test_labs']),
    ('defend_evacuate_scientists', ['gordon_freeman', 'dr_kleiner', 'dr_vance', 'scientist1', 'scientist2', 'scientist3'], 'safe_zone'),
    ('defend_establish_perimeters', ['guard2', 'guard3'], ['sector_c', 'lambda_complex', 'surface_tension']),
]

# Task List 4: Mixed scenario - Guards defend while scientists evacuate
task_list_mixed = [
    ('secure_area', 'barney_calhoun', 'sector_c'),
    ('evacuate_scientist', 'gordon_freeman', 'safe_zone'),
    ('defend_zone', 'guard1', 'lambda_complex'),
]

# Task List 5: Simple movement and control
task_list_simple = [
    ('control_zone', 'hecu_soldier1', 'sector_c'),
]

# Task List 6: Gordon Freeman's escape mission
task_list_gordon_escape = [
    ('evacuate_scientist', 'gordon_freeman', 'safe_zone'),
]

"""
Author(s): K. S. Ernest (iFire) Lee
Half-Life Black Mesa Planning Problem - 2025
"""

