# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 15:20:19 2025

@author: mjustus
"""

def simple_marker_strategy(lamp_state, memory):
    """
    Strategy algorithm:
    1. Turn OFF lamp in start wagon.
    2. Move forward until finding a lamp that is OFF.
    3. Turn it ON.
    4. Move backward until back at start.
    5. If start lamp is ON → done.
    6. Otherwise repeat.
    """
    # Initialize memory
    if memory == {}:
        memory["phase"] = "init_off"
        memory["direction"] = +1
        memory["steps_from_start"] = 0
    
    toggle = False
    done = False
    estimated_n = None
    
    # PHASE 1: At start → turn lamp OFF
    if memory["phase"] == "init_off":
        if lamp_state == 1:
            toggle = True
        memory["phase"] = "search_off"
        memory["direction"] = +1
        memory["steps_from_start"] = 0
        return toggle, memory["direction"], memory, done, estimated_n
    
    # PHASE 2: Move forward until OFF lamp found
    if memory["phase"] == "search_off":
        memory["steps_from_start"] += 1
        if lamp_state == 0:
            toggle = True
            memory["phase"] = "go_back"
            memory["direction"] = -1
            memory["last_cycle_length"] = memory["steps_from_start"]
            return toggle, memory["direction"], memory, done, estimated_n
        else:
            return toggle, +1, memory, done, estimated_n
    
    # PHASE 3: Go back to start
    if memory["phase"] == "go_back":
        memory["steps_from_start"] -= 1
        if memory["steps_from_start"] == 0:
            if lamp_state == 1:
                done = True
                estimated_n = memory["last_cycle_length"]
                return toggle, 0, memory, done, estimated_n
            memory["phase"] = "search_off"
            memory["direction"] = +1
            return toggle, +1, memory, done, estimated_n
        else:
            return toggle, -1, memory, done, estimated_n
        
        
heimkehr_marker = simple_marker_strategy