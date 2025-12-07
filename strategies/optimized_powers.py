# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 15:30:57 2025

@author: mjustus
"""

def optimized_powers_strategy(lamp_state, memory):

    """
    Optimized version that "ignores" carts with light OFF:
    1. For step n, try to switch OFF 2**n lights
    2. If you encounter 2**n carts with light OFF in a row → return early
    3. This means all lights might already be OFF
    """
    # Initialize memory
    if memory == {}:
        memory["phase"] = "init_on"
        memory["power"] = 0
        memory["steps_forward"] = 0
        memory["lights_turned_off"] = 0
        memory["consecutive_off"] = 0
        memory["direction"] = +1
        memory["checking_all_off"] = False
    
    toggle = False
    done = False
    estimated_n = None
    # PHASE 0: Ensure cart 0 light is ON and move
    if memory["phase"] == "init_on":
        if lamp_state == 0:
            toggle = True
        memory["phase"] = "forward_phase"
        memory["direction"] = +1
        memory["target_lights"] = 2 ** memory["power"]
        memory["steps_forward"] = 0  # Start moving
        memory["lights_turned_off"] = 0
        memory["consecutive_off"] = 0
        return toggle, 1, memory, done, estimated_n  # Always move
    
    # PHASE 1: Moving forward with optimization
    if memory["phase"] == "forward_phase":
        target = 2 ** memory["power"]
        memory["steps_forward"] += 1
        # Process current lamp
        if lamp_state == 1:
            # Turn OFF and count
            toggle = True
            memory["lights_turned_off"] += 1
            memory["consecutive_off"] = 0  # Reset consecutive OFF counter
        else:
            # Lamp already OFF
            memory["consecutive_off"] += 1
        
        # Check termination conditions AFTER processing current lamp
        if memory["lights_turned_off"] >= target:
            # Successfully turned off enough lights
            memory["phase"] = "return_phase"
            memory["direction"] = -1
            return toggle, -1, memory, done, estimated_n
        
        if memory["consecutive_off"] >= target:
            # Found target consecutive OFF lights - all might be OFF!
            memory["phase"] = "verify_all_off"
            memory["checking_all_off"] = True
            return toggle, -1, memory, done, estimated_n
        
        # Normal forward movement
        
        return toggle, +1, memory, done, estimated_n
    
    # PHASE 2: Verify if all lights are OFF
    if memory["phase"] == "verify_all_off":
        memory["steps_forward"] -= 1
        # We think all lights might be OFF
        # Need to check cart 0
        if memory["steps_forward"] > 0:
            # Still returning to cart 0
            
            return toggle, -1, memory, done, estimated_n
        else:
            # At cart 0
            if lamp_state == 0:
                # All lights are OFF!
                memory["phase"] = "count_prep"
            else:
                # Not all OFF yet, continue with next power
                memory["power"] += 1
                memory["phase"] = "forward_phase"
                memory["direction"] = +1
                memory["target_lights"] = 2 ** memory["power"]
                memory["lights_turned_off"] = 0
                memory["consecutive_off"] = 0
                memory["steps_forward"] = 0  # Start moving
            
            return toggle, 1, memory, done, estimated_n
    
    # PHASE 3: Returning to cart 0 (normal return)
    if memory["phase"] == "return_phase":
        memory["steps_forward"] -= 1
        if memory["steps_forward"] == 0:
            # Back at cart 0
            if lamp_state == 0:
                # All lights OFF!
                memory["phase"] = "count_prep"
            else:
                # Continue with next power
                memory["power"] += 1
                memory["phase"] = "forward_phase"
                memory["direction"] = +1
                memory["target_lights"] = 2 ** memory["power"]
                memory["lights_turned_off"] = 0
                memory["consecutive_off"] = 0
                memory["steps_forward"] = 0  # Start moving
            
            return toggle, 1, memory, done, estimated_n
        else:
            
            return toggle, -1, memory, done, estimated_n
    
    # PHASE 4: Prepare for counting (all lights confirmed OFF)
    if memory["phase"] == "count_prep":
        # Turn ON light in cart 0 and move
        if lamp_state == 0:
            toggle = True
        memory["phase"] = "counting"
        memory["direction"] = +1
        memory["count"] = 1  # Start counting from 1 (we're moving)
        return toggle, 1, memory, done, estimated_n
    
    # PHASE 5: Counting - find the ON light
    if memory["phase"] == "counting":
        # If we found the ON light
        if lamp_state == 1:
            done = True
            estimated_n = memory["count"]
            return toggle, 0, memory, done, estimated_n
        
        # Keep moving forward and counting
        memory["count"] += 1
        return toggle, +1, memory, done, estimated_n


optimized_powers = optimized_powers_strategy