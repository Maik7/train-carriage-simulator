# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 15:32:57 2025

@author: mjustus
"""

def hypothesis_testing_strategy(lamp_state, memory):
    """
    Hypothesis Testing Strategy:
    1. Turn OFF light in first car (0)
    2. Go forward until finding a car with light OFF (car k) → initial hypothesis k
    3. Turn this light ON
    4. Go forward to car 2k:
       - If find light OFF before 2k → update hypothesis to current position, turn it ON
       - If reach 2k and it's ON → turn it OFF (strong hypothesis)
    5. Go back k cars to check if light in car k changed
       - If changed → done, n = k
       - If not changed → continue with new search
    """
    # Initialize memory
    if memory == {}:
        memory["step"] = 0
        memory["state"] = 0  # 0=start, 1=find_k, 2=to_2k, 3=back_check
        memory["k"] = 0
        memory["counter"] = 0
        memory["k_light"] = 0
        memory["strong"] = False
    
    toggle = False
    done = False
    estimated_n = None
    
    # STATE 0: Start - turn off car 0
    if memory["state"] == 0:
        if lamp_state == 1:
            toggle = True
        memory["state"] = 1
        memory["step"] = 0
        return toggle, 1, memory, done, estimated_n
    
    # STATE 1: Find first OFF light (k)
    elif memory["state"] == 1:
        memory["step"] += 1
        
        if lamp_state == 0:
            # Found k!
            toggle = True  # Turn ON
            memory["k"] = memory["step"] - 0  # Current position
            memory["k_light"] = 1  # Now it's ON
            memory["state"] = 2
            memory["counter"] = memory["k"] - 0  # Steps to reach 2k
            return toggle, 1, memory, done, estimated_n
        
        return toggle, +1, memory, done, estimated_n
    
    # STATE 2: Go to 2k
    elif memory["state"] == 2:
        memory["step"] += 1
        memory["counter"] -= 1
        if memory["counter"] > 0:
            
            
            
            if lamp_state == 0:
                # Found OFF before 2k → new k
                toggle = True  # Turn ON
                memory["k"] = memory["step"] - 0
                memory["k_light"] = 1
                memory["counter"] = memory["k"] - 0 # Reset counter
                memory["strong"] = False
                return toggle, 1, memory, done, estimated_n
            
            return toggle, +1, memory, done, estimated_n
        else:
            # Reached 2k position
            if lamp_state == 1:
                # 2k is ON → turn OFF (strong hypothesis)
                toggle = True
                memory["strong"] = True
                memory["state"] = 3
                memory["counter"] = memory["k"] - 0  # Steps back to k
                return toggle, -1, memory, done, estimated_n
            else:
                # 2k is OFF → new k
                toggle = True  # Turn ON
                memory["k"] = memory["step"] - 0
                memory["k_light"] = 1
                memory["counter"] = memory["k"] - 1
                memory["strong"] = False
                return toggle, 1, memory, done, estimated_n
    
    # STATE 3: Return to k and check
    elif memory["state"] == 3:
        memory["step"] -= 1
        memory["counter"] -= 1
        if memory["counter"] > 0:
            #memory["counter"] -= 1
            return toggle, -1, memory, done, estimated_n
        else:
            # Back at k
            if memory["strong"]:
                if lamp_state != memory["k_light"]:
                    # Light changed - success!
                    done = True
                    estimated_n = memory["k"]
                    return toggle, 0, memory, done, estimated_n
                else:
                    # Light unchanged - restart from here
                    memory["state"] = 1
                    memory["k"] =  memory["step"] - 0
                    memory["strong"] = False
                    return toggle, 1, memory, done, estimated_n
            else:
                # Shouldn't happen
                memory["state"] = 1
                memory["step"] += 1
                return toggle, 1, memory, done, estimated_n
    
    return toggle, +1, memory, done, estimated_n   

hypothesis_testing = hypothesis_testing_strategy