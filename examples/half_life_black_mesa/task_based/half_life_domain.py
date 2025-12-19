#!/usr/bin/env python
"""
File Description: Half-Life Black Mesa domain - Multi-faction temporal planning puzzle.
Characters: Scientists, Guards, Aliens, Military
Goals: 
  - Military: Kill humans and aliens
  - Aliens: Kill all humans
  - Scientists/Guards: Survive and defend Black Mesa
Actions: Move between zones, control zones, combat actions
"""

from ipyhop import Actions, Methods


# ============================================================================
# ACTIONS - Movement and Zone Control
# ============================================================================

def a_move_to_zone(state, character, from_zone, to_zone):
    """Move character from one zone to another."""
    if (state.character_location[character] == from_zone and
        from_zone in state.zone_accessible and
        to_zone in state.zone_accessible[from_zone] and
        state.zone_accessible[from_zone][to_zone] and
        state.character_alive[character]):
        state.character_location[character] = to_zone
        return state


def a_control_zone(state, character, zone):
    """Character takes control of a zone."""
    if (state.character_location[character] == zone and
        state.character_alive[character] and
        state.zone_controller[zone] != character):
        # Only military and guards can control zones
        if state.character_faction[character] in ['military', 'guard']:
            state.zone_controller[zone] = character
            state.zone_controlled[zone] = True
            return state


def a_secure_area(state, character, area):
    """Secure an area (guards/scientists can do this)."""
    if (state.character_location[character] == area and
        state.character_alive[character] and
        state.character_faction[character] in ['guard', 'scientist'] and
        not state.area_secured.get(area, False)):
        if not hasattr(state, 'area_secured'):
            state.area_secured = {}
        state.area_secured[area] = True
        return state


# ============================================================================
# ACTIONS - Combat
# ============================================================================

def a_attack_character(state, attacker, target, zone):
    """Attack another character in the same zone."""
    if (state.character_location[attacker] == zone and
        state.character_location[target] == zone and
        state.character_alive[attacker] and
        state.character_alive[target] and
        attacker != target):
        # Check if attack is valid based on faction goals
        attacker_faction = state.character_faction[attacker]
        target_faction = state.character_faction[target]
        
        # Military attacks everyone
        if attacker_faction == 'military':
            state.character_alive[target] = False
            state.character_location[target] = 'deceased'
            return state
        # Aliens attack humans (scientists, guards)
        elif attacker_faction == 'alien' and target_faction in ['scientist', 'guard']:
            state.character_alive[target] = False
            state.character_location[target] = 'deceased'
            return state
        # Guards can defend against aliens and military
        elif attacker_faction == 'guard' and target_faction in ['alien', 'military']:
            state.character_alive[target] = False
            state.character_location[target] = 'deceased'
            return state


def a_defend_zone(state, defender, zone):
    """Defend a zone (guards/scientists can defend)."""
    if (state.character_location[defender] == zone and
        state.character_alive[defender] and
        state.character_faction[defender] in ['guard', 'scientist']):
        # Mark zone as defended
        state.zone_defended[zone] = True
        return state


# ============================================================================
# ACTIONS - Special Operations
# ============================================================================

def a_evacuate_scientist(state, scientist, from_zone, to_zone):
    """Evacuate scientist to safety."""
    if (state.character_location[scientist] == from_zone and
        state.character_faction[scientist] == 'scientist' and
        state.character_alive[scientist] and
        state.zone_safe[to_zone]):
        # Check zone accessibility (allow if already at safe zone or if accessible)
        zone_accessible = False
        if from_zone == to_zone and from_zone == 'safe_zone':
            # Already at safe zone, just mark as evacuated
            zone_accessible = True
        elif from_zone in state.zone_accessible:
            zone_accessible = (to_zone in state.zone_accessible[from_zone] and
                             state.zone_accessible[from_zone][to_zone])
        
        if zone_accessible:
            state.character_location[scientist] = to_zone
            state.scientist_evacuated[scientist] = True
            return state


def a_establish_perimeter(state, guard, zone):
    """Guard establishes defensive perimeter."""
    if (state.character_location[guard] == zone and
        state.character_faction[guard] == 'guard' and
        state.character_alive[guard]):
        state.zone_defended[zone] = True
        state.perimeter_established[zone] = True
        return state


# ============================================================================
# ACTIONS - Temporal Actions Declaration
# ============================================================================

actions = Actions()
actions.declare_temporal_actions([
    ('a_move_to_zone', a_move_to_zone, 'PT5M'),           # 5 minutes to move between zones
    ('a_control_zone', a_control_zone, 'PT10M'),         # 10 minutes to control a zone
    ('a_secure_area', a_secure_area, 'PT15M'),           # 15 minutes to secure area
    ('a_attack_character', a_attack_character, 'PT2M'),  # 2 minutes for combat
    ('a_defend_zone', a_defend_zone, 'PT8M'),            # 8 minutes to set up defense
    ('a_evacuate_scientist', a_evacuate_scientist, 'PT12M'),  # 12 minutes to evacuate
    ('a_establish_perimeter', a_establish_perimeter, 'PT20M'),  # 20 minutes to establish perimeter
])


# ============================================================================
# METHODS - Task Decomposition
# ============================================================================

methods = Methods()


# Method: Control a zone
def m_control_zone_direct(state, character, zone):
    """Directly control a zone if already there."""
    if state.character_location[character] == zone:
        return [('a_control_zone', character, zone)]


def m_control_zone_move_then_control(state, character, zone):
    """Move to zone then control it."""
    current_zone = state.character_location[character]
    if current_zone == zone:
        return None  # Already there, use direct method
    
    # Check for direct connection
    if (current_zone in state.zone_accessible and
        zone in state.zone_accessible[current_zone] and
        state.zone_accessible[current_zone][zone]):
        return [
            ('a_move_to_zone', character, current_zone, zone),
            ('a_control_zone', character, zone)
        ]
    
    # Try to find a 1-hop path
    if current_zone in state.zone_accessible:
        for intermediate in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][intermediate] and
                intermediate in state.zone_accessible and
                zone in state.zone_accessible[intermediate] and
                state.zone_accessible[intermediate][zone]):
                return [
                    ('a_move_to_zone', character, current_zone, intermediate),
                    ('a_move_to_zone', character, intermediate, zone),
                    ('a_control_zone', character, zone)
                ]
    
    # Try to find a 2-hop path
    if current_zone in state.zone_accessible:
        for hop1 in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][hop1] and
                hop1 in state.zone_accessible):
                for hop2 in state.zone_accessible[hop1]:
                    if (state.zone_accessible[hop1][hop2] and
                        hop2 in state.zone_accessible and
                        zone in state.zone_accessible[hop2] and
                        state.zone_accessible[hop2][zone]):
                        return [
                            ('a_move_to_zone', character, current_zone, hop1),
                            ('a_move_to_zone', character, hop1, hop2),
                            ('a_move_to_zone', character, hop2, zone),
                            ('a_control_zone', character, zone)
                        ]
    
    return None


methods.declare_task_methods('control_zone', [m_control_zone_direct, m_control_zone_move_then_control])


# Method: Secure area
def m_secure_area_direct(state, character, area):
    """Directly secure area if already there."""
    if state.character_location[character] == area:
        return [('a_secure_area', character, area)]


def m_secure_area_move_then_secure(state, character, area):
    """Move to area then secure it."""
    current_zone = state.character_location[character]
    if current_zone == area:
        return None  # Already there, use direct method
    
    # Check for direct connection
    if (current_zone in state.zone_accessible and
        area in state.zone_accessible[current_zone] and
        state.zone_accessible[current_zone][area]):
        return [
            ('a_move_to_zone', character, current_zone, area),
            ('a_secure_area', character, area)
        ]
    
    # Try to find a 1-hop path
    if current_zone in state.zone_accessible:
        for intermediate in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][intermediate] and
                intermediate in state.zone_accessible and
                area in state.zone_accessible[intermediate] and
                state.zone_accessible[intermediate][area]):
                return [
                    ('a_move_to_zone', character, current_zone, intermediate),
                    ('a_move_to_zone', character, intermediate, area),
                    ('a_secure_area', character, area)
                ]
    
    # Try to find a 2-hop path
    if current_zone in state.zone_accessible:
        for hop1 in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][hop1] and
                hop1 in state.zone_accessible):
                for hop2 in state.zone_accessible[hop1]:
                    if (state.zone_accessible[hop1][hop2] and
                        hop2 in state.zone_accessible and
                        area in state.zone_accessible[hop2] and
                        state.zone_accessible[hop2][area]):
                        return [
                            ('a_move_to_zone', character, current_zone, hop1),
                            ('a_move_to_zone', character, hop1, hop2),
                            ('a_move_to_zone', character, hop2, area),
                            ('a_secure_area', character, area)
                        ]
    
    return None


methods.declare_task_methods('secure_area', [m_secure_area_direct, m_secure_area_move_then_secure])


# Method: Attack target
def m_attack_target_same_zone(state, attacker, target):
    """Attack target if in same zone."""
    attacker_zone = state.character_location[attacker]
    target_zone = state.character_location[target]
    if attacker_zone == target_zone:
        return [('a_attack_character', attacker, target, attacker_zone)]


def m_attack_target_move_then_attack(state, attacker, target):
    """Move to target's zone then attack."""
    attacker_zone = state.character_location[attacker]
    target_zone = state.character_location[target]
    if attacker_zone == target_zone:
        return None  # Already there, use same-zone method
    
    # Check for direct connection
    if (attacker_zone in state.zone_accessible and
        target_zone in state.zone_accessible[attacker_zone] and
        state.zone_accessible[attacker_zone][target_zone]):
        return [
            ('a_move_to_zone', attacker, attacker_zone, target_zone),
            ('a_attack_character', attacker, target, target_zone)
        ]
    
    # Try to find a 1-hop path
    if attacker_zone in state.zone_accessible:
        for intermediate in state.zone_accessible[attacker_zone]:
            if (state.zone_accessible[attacker_zone][intermediate] and
                intermediate in state.zone_accessible and
                target_zone in state.zone_accessible[intermediate] and
                state.zone_accessible[intermediate][target_zone]):
                return [
                    ('a_move_to_zone', attacker, attacker_zone, intermediate),
                    ('a_move_to_zone', attacker, intermediate, target_zone),
                    ('a_attack_character', attacker, target, target_zone)
                ]
    
    # Try to find a 2-hop path
    if attacker_zone in state.zone_accessible:
        for hop1 in state.zone_accessible[attacker_zone]:
            if (state.zone_accessible[attacker_zone][hop1] and
                hop1 in state.zone_accessible):
                for hop2 in state.zone_accessible[hop1]:
                    if (state.zone_accessible[hop1][hop2] and
                        hop2 in state.zone_accessible and
                        target_zone in state.zone_accessible[hop2] and
                        state.zone_accessible[hop2][target_zone]):
                        return [
                            ('a_move_to_zone', attacker, attacker_zone, hop1),
                            ('a_move_to_zone', attacker, hop1, hop2),
                            ('a_move_to_zone', attacker, hop2, target_zone),
                            ('a_attack_character', attacker, target, target_zone)
                        ]
    
    return None


methods.declare_task_methods('attack_target', [m_attack_target_same_zone, m_attack_target_move_then_attack])


# Method: Defend zone
def m_defend_zone_direct(state, defender, zone):
    """Directly defend zone if already there."""
    if state.character_location[defender] == zone:
        return [('a_defend_zone', defender, zone)]


def m_defend_zone_move_then_defend(state, defender, zone):
    """Move to zone then defend it."""
    current_zone = state.character_location[defender]
    if current_zone == zone:
        return None  # Already there, use direct method
    
    # Check for direct connection
    if (current_zone in state.zone_accessible and
        zone in state.zone_accessible[current_zone] and
        state.zone_accessible[current_zone][zone]):
        return [
            ('a_move_to_zone', defender, current_zone, zone),
            ('a_defend_zone', defender, zone)
        ]
    
    # Try to find a 1-hop path
    if current_zone in state.zone_accessible:
        for intermediate in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][intermediate] and
                intermediate in state.zone_accessible and
                zone in state.zone_accessible[intermediate] and
                state.zone_accessible[intermediate][zone]):
                return [
                    ('a_move_to_zone', defender, current_zone, intermediate),
                    ('a_move_to_zone', defender, intermediate, zone),
                    ('a_defend_zone', defender, zone)
                ]
    
    return None


methods.declare_task_methods('defend_zone', [m_defend_zone_direct, m_defend_zone_move_then_defend])


# Method: Evacuate scientist
def m_evacuate_scientist_direct(state, scientist, safe_zone):
    """Evacuate scientist if already at safe zone."""
    if state.character_location[scientist] == safe_zone:
        return [('a_evacuate_scientist', scientist, safe_zone, safe_zone)]


def m_evacuate_scientist_move_then_evacuate(state, scientist, safe_zone):
    """Move scientist to safe zone."""
    current_zone = state.character_location[scientist]
    if current_zone == safe_zone:
        return None  # Already there, use direct method
    
    # Check for direct connection
    if (current_zone in state.zone_accessible and
        safe_zone in state.zone_accessible[current_zone] and
        state.zone_accessible[current_zone][safe_zone]):
        return [
            ('a_move_to_zone', scientist, current_zone, safe_zone),
            ('a_evacuate_scientist', scientist, safe_zone, safe_zone)
        ]
    
    # Try to find a 1-hop path
    if current_zone in state.zone_accessible:
        for intermediate in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][intermediate] and
                intermediate in state.zone_accessible and
                safe_zone in state.zone_accessible[intermediate] and
                state.zone_accessible[intermediate][safe_zone]):
                return [
                    ('a_move_to_zone', scientist, current_zone, intermediate),
                    ('a_move_to_zone', scientist, intermediate, safe_zone),
                    ('a_evacuate_scientist', scientist, safe_zone, safe_zone)
                ]
    
    # Try to find a 2-hop path
    if current_zone in state.zone_accessible:
        for hop1 in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][hop1] and
                hop1 in state.zone_accessible):
                for hop2 in state.zone_accessible[hop1]:
                    if (state.zone_accessible[hop1][hop2] and
                        hop2 in state.zone_accessible and
                        safe_zone in state.zone_accessible[hop2] and
                        state.zone_accessible[hop2][safe_zone]):
                        return [
                            ('a_move_to_zone', scientist, current_zone, hop1),
                            ('a_move_to_zone', scientist, hop1, hop2),
                            ('a_move_to_zone', scientist, hop2, safe_zone),
                            ('a_evacuate_scientist', scientist, safe_zone, safe_zone)
                        ]
    
    # Try to find a 3-hop path (for routes like corridor_1 -> corridor_2 -> corridor_3 -> safe_zone)
    if current_zone in state.zone_accessible:
        for hop1 in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][hop1] and
                hop1 in state.zone_accessible):
                for hop2 in state.zone_accessible[hop1]:
                    if (state.zone_accessible[hop1][hop2] and
                        hop2 in state.zone_accessible):
                        for hop3 in state.zone_accessible[hop2]:
                            if (state.zone_accessible[hop2][hop3] and
                                hop3 in state.zone_accessible and
                                safe_zone in state.zone_accessible[hop3] and
                                state.zone_accessible[hop3][safe_zone]):
                                return [
                                    ('a_move_to_zone', scientist, current_zone, hop1),
                                    ('a_move_to_zone', scientist, hop1, hop2),
                                    ('a_move_to_zone', scientist, hop2, hop3),
                                    ('a_move_to_zone', scientist, hop3, safe_zone),
                                    ('a_evacuate_scientist', scientist, safe_zone, safe_zone)
                                ]
    
    # Try to find a 4-hop path (for routes like lab_a -> corridor_1 -> corridor_2 -> corridor_3 -> safe_zone)
    if current_zone in state.zone_accessible:
        for hop1 in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][hop1] and
                hop1 in state.zone_accessible):
                for hop2 in state.zone_accessible[hop1]:
                    if (state.zone_accessible[hop1][hop2] and
                        hop2 in state.zone_accessible):
                        for hop3 in state.zone_accessible[hop2]:
                            if (state.zone_accessible[hop2][hop3] and
                                hop3 in state.zone_accessible):
                                for hop4 in state.zone_accessible[hop3]:
                                    if (state.zone_accessible[hop3][hop4] and
                                        hop4 in state.zone_accessible and
                                        safe_zone in state.zone_accessible[hop4] and
                                        state.zone_accessible[hop4][safe_zone]):
                                        return [
                                            ('a_move_to_zone', scientist, current_zone, hop1),
                                            ('a_move_to_zone', scientist, hop1, hop2),
                                            ('a_move_to_zone', scientist, hop2, hop3),
                                            ('a_move_to_zone', scientist, hop3, hop4),
                                            ('a_move_to_zone', scientist, hop4, safe_zone),
                                            ('a_evacuate_scientist', scientist, safe_zone, safe_zone)
                                        ]
    
    return None


methods.declare_task_methods('evacuate_scientist', [m_evacuate_scientist_direct, m_evacuate_scientist_move_then_evacuate])


# Method: Establish perimeter
def m_establish_perimeter_direct(state, guard, zone):
    """Establish perimeter if already at zone."""
    if state.character_location[guard] == zone:
        return [('a_establish_perimeter', guard, zone)]


def m_establish_perimeter_move_then_establish(state, guard, zone):
    """Move to zone then establish perimeter."""
    current_zone = state.character_location[guard]
    if current_zone == zone:
        return None  # Already there, use direct method
    
    # Check for direct connection
    if (current_zone in state.zone_accessible and
        zone in state.zone_accessible[current_zone] and
        state.zone_accessible[current_zone][zone]):
        return [
            ('a_move_to_zone', guard, current_zone, zone),
            ('a_establish_perimeter', guard, zone)
        ]
    
    # Try to find a 1-hop path
    if current_zone in state.zone_accessible:
        for intermediate in state.zone_accessible[current_zone]:
            if (state.zone_accessible[current_zone][intermediate] and
                intermediate in state.zone_accessible and
                zone in state.zone_accessible[intermediate] and
                state.zone_accessible[intermediate][zone]):
                return [
                    ('a_move_to_zone', guard, current_zone, intermediate),
                    ('a_move_to_zone', guard, intermediate, zone),
                    ('a_establish_perimeter', guard, zone)
                ]
    
    return None


methods.declare_task_methods('establish_perimeter', [m_establish_perimeter_direct, m_establish_perimeter_move_then_establish])


# Method: Multi-goal methods for faction objectives

def m_military_objective_control_zones(state, military_char, zones):
    """Military objective: Control multiple zones."""
    tasks = []
    for zone in zones:
        if state.zone_controller.get(zone) != military_char:
            tasks.append(('control_zone', military_char, zone))
    return tasks if tasks else None


def m_military_objective_eliminate_targets(state, military_char, targets):
    """Military objective: Eliminate targets."""
    tasks = []
    for target in targets:
        if state.character_alive.get(target, True):
            tasks.append(('attack_target', military_char, target))
    return tasks if tasks else None


methods.declare_task_methods('military_control_zones', [m_military_objective_control_zones])
methods.declare_task_methods('military_eliminate_targets', [m_military_objective_eliminate_targets])


def m_alien_objective_eliminate_humans(state, alien_char, humans):
    """Alien objective: Eliminate all humans."""
    tasks = []
    for human in humans:
        if state.character_alive.get(human, True):
            tasks.append(('attack_target', alien_char, human))
    return tasks if tasks else None


methods.declare_task_methods('alien_eliminate_humans', [m_alien_objective_eliminate_humans])


def m_defend_black_mesa_secure_areas(state, defenders, areas):
    """Defend Black Mesa by securing areas."""
    tasks = []
    secured_areas = set()
    for defender in defenders:
        for area in areas:
            if not state.area_secured.get(area, False) and area not in secured_areas:
                tasks.append(('secure_area', defender, area))
                secured_areas.add(area)  # Mark as assigned to avoid duplicates
    return tasks if tasks else None


def m_defend_black_mesa_evacuate_scientists(state, scientists, safe_zone):
    """Evacuate scientists to safety."""
    tasks = []
    for scientist in scientists:
        if not state.scientist_evacuated.get(scientist, False):
            tasks.append(('evacuate_scientist', scientist, safe_zone))
    return tasks if tasks else None


def m_defend_black_mesa_establish_perimeters(state, guards, zones):
    """Establish defensive perimeters."""
    tasks = []
    for guard in guards:
        for zone in zones:
            if not state.perimeter_established.get(zone, False):
                tasks.append(('establish_perimeter', guard, zone))
    return tasks if tasks else None


methods.declare_task_methods('defend_secure_areas', [m_defend_black_mesa_secure_areas])
methods.declare_task_methods('defend_evacuate_scientists', [m_defend_black_mesa_evacuate_scientists])
methods.declare_task_methods('defend_establish_perimeters', [m_defend_black_mesa_establish_perimeters])


"""
Author(s): K. S. Ernest (iFire) Lee
Half-Life Black Mesa Planning Domain - 2025
Inspired by MiniZinc aircraft disassembly puzzle structure
"""

