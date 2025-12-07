# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 15:29:12 2025

@author: mjustus
"""

def state_machine_strategy(lamp_state, memory):
    """
    State machine based strategy:
    States: 0=looking for OFF, 1=found OFF, returning to start
    """
    if memory == {}:
        memory["state"] = 0
        memory["count"] = 0
        memory["direction"] = +1
        memory["steps"] = 0
    
    toggle = False
    done = False
    estimated_n = None
    
    # Initial state: need to move first
    if memory["steps"] == 0 and memory["state"] == 0:
        if lamp_state == 1:
            toggle = True
        memory["steps"] = 1
        return toggle, 1, memory, done, estimated_n
    
    if memory["state"] == 0:  # Looking for OFF
        if lamp_state == 0:
            toggle = True
            memory["state"] = 1
            memory["direction"] = -1
            memory["found_at"] = memory["steps"]
            memory["steps"] -= 1
            return toggle, -1, memory, done, estimated_n
        else:
            memory["steps"] += 1
            return toggle, +1, memory, done, estimated_n
    else:  # Returning to start (state == 1)
        if memory["steps"] == 0:
            if lamp_state == 1:
                done = True
                estimated_n = memory["found_at"]
                return toggle, 0, memory, done, estimated_n
            else:
                memory["state"] = 0
                memory["direction"] = +1
                memory["count"] = memory.get("count", 0) + 1
                memory["steps"] = 1  # Start moving
                return toggle, 1, memory, done, estimated_n
        else:
            memory["steps"] -= 1
            return toggle, -1, memory, done, estimated_n   



state_machine = state_machine_strategy