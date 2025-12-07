# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 15:24:27 2025

@author: mjustus
"""

def counter_strategy(lamp_state, memory):
    """
    Alternative strategy using a counter:
    1. Always move forward
    2. When lamp is OFF, toggle it ON and increment counter
    3. When counter reaches threshold, assume we've seen all wagons
    """
    if memory == {}:
        memory["counter"] = 0
        memory["direction"] = +1
        memory["last_seen"] = 0
        memory["steps"] = 0
        memory["threshold"] = 5  # Initial threshold
    
    toggle = False
    done = False
    estimated_n = None
    
    # Always move in first step
    if memory["steps"] == 0:
        memory["steps"] = 1
        if lamp_state == 1:
            toggle = True
        return toggle, 1, memory, done, estimated_n
    
    # Process current lamp
    if lamp_state == 0:
        toggle = True
        memory["counter"] += 1
        memory["last_seen"] = 0
    else:
        memory["last_seen"] += 1
    
    # Heuristic: if we've seen many consecutive ON lamps after counting many OFF lamps
    if memory["counter"] > 0 and memory["last_seen"] > memory["counter"] * 3:
        done = True
        estimated_n = memory["counter"]
        return toggle, 0, memory, done, estimated_n
    
    # If counter reached threshold, increase threshold
    if memory["counter"] >= memory["threshold"]:
        memory["threshold"] *= 2
    
    # Always move forward
    memory["steps"] += 1
    
    return toggle, +1, memory, done, estimated_n
    
counter = counter_strategy