# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 15:30:19 2025

@author: mjustus
"""

def powers_of_two_strategy(lamp_state, memory):
    """
    Strategy based on powers of two:
    1. Start with light ON in cart 0
    2. For n = 1, 2, 4, 8, 16, ... (powers of 2):
        a. Move forward n carts, turning lights OFF
        b. Return to cart 0
        c. Check if light in cart 0 is still ON
    3. When light in cart 0 is OFF → all lights are OFF
    4. Turn ON light in cart 0, move forward until finding it to count carts
    """
    # Initialize memory
    if memory == {}:
        memory["phase"] = "init_on"
        memory["power"] = 0  # current power of two (2**power)
        memory["steps_forward"] = 0
        memory["direction"] = +1
        memory["all_off_verified"] = False
        memory["count_mode"] = False
        memory["count"] = 0
    
    toggle = False
    done = False
    estimated_n = None
    
    # PHASE 0: Initial setup - ensure cart 0 light is ON and move to right
    if memory["phase"] == "init_on":
        if lamp_state == 0:
            toggle = True  # Turn ON
        memory["phase"] = "forward_phase"
        memory["direction"] = +1
        memory["target_distance"] = 2 ** memory["power"]
        memory["steps_forward"] = 0
        return toggle, 1, memory, done, estimated_n
    
    # PHASE 1: Moving forward, turning lights OFF
    if memory["phase"] == "forward_phase":
        # If lamp is ON, turn it OFF
        if lamp_state == 1:
            toggle = True
        memory["steps_forward"] += 1
        
        # If we've reached our target distance
        if memory["steps_forward"] >= memory["target_distance"]:
            memory["phase"] = "return_phase"
            memory["direction"] = -1
            return toggle, -1, memory, done, estimated_n
        
        
        return toggle, +1, memory, done, estimated_n
    
    # PHASE 2: Returning to cart 0
    if memory["phase"] == "return_phase":
        # If we're back at start (cart 0)
        memory["steps_forward"] -= 1
        if memory["steps_forward"] == 0:
            # Check if cart 0 light is still ON
            if lamp_state == 0:
                # All lights are OFF!
                memory["phase"] = "count_prep"
                memory["all_off_verified"] = True
            else:
                # Increase power and try again
                memory["power"] += 1
                memory["phase"] = "forward_phase"
                memory["direction"] = +1
                memory["target_distance"] = 2 ** memory["power"]
                memory["steps_forward"] = 0
            
            return toggle, 1, memory, done, estimated_n
        else:
            # Keep moving back
            #memory["steps_forward"] -= 1
            return toggle, -1, memory, done, estimated_n
    
    # PHASE 3: Prepare for counting (all lights are OFF)
    if memory["phase"] == "count_prep":
        # Turn ON light in cart 0
        if lamp_state == 0:
            toggle = True
        memory["phase"] = "counting"
        memory["direction"] = +1
        memory["count"] = 0
        return toggle, 1, memory, done, estimated_n
    
    # PHASE 4: Counting mode - find the ON light
    if memory["phase"] == "counting":
        memory["count"] += 1
        
        # If we found the ON light (should be back at cart 0 after full loop)
        if lamp_state == 1:
            done = True
            estimated_n = memory["count"]
            return toggle, 0, memory, done, estimated_n
        
        # Keep moving forward
        return toggle, +1, memory, done, estimated_n
    
powers_of_two = powers_of_two_strategy