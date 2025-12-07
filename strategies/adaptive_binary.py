# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 15:32:21 2025

@author: mjustus
"""
def adaptive_binary_strategy(lamp_state, memory):
    """
    Hybrid strategy that adapts based on what's found:
    - Uses binary search principles
    - Tracks both ON and OFF patterns
    """
    if memory == {}:
        memory["phase"] = "init"
        memory["min_bound"] = 0
        memory["max_bound"] = 1
        memory["current_test"] = 1
        memory["direction"] = +1
        memory["steps"] = 0
        memory["found_on"] = []
        memory["found_off"] = []
    
    toggle = False
    done = False
    estimated_n = None
    #print(lamp_state,memory)
    
    # Initial phase: explore and build understanding
    if memory["phase"] == "init":
        # Always move in first step
        if memory["steps"] == 0:
            memory["steps"] = 1
            return toggle, 1, memory, done, estimated_n
        
        # Record lamp state
        if lamp_state == 1:
            memory["found_on"].append(memory["steps"])
        else:
            memory["found_off"].append(memory["steps"])
        
        memory["steps"] += 1
        
        # After some exploration, switch to analysis
        if memory["steps"] >= min(10, memory["max_bound"] * 2):
            memory["phase"] = "analyze"
            memory["direction"] = 0  # Stop to think temporarily
        
        return toggle, +1, memory, done, estimated_n
    
    # Analysis phase: determine next move based on findings
    if memory["phase"] == "analyze":
        # Simple heuristic
        on_count = len(memory["found_on"])
        off_count = len(memory["found_off"])
        
        if on_count > off_count:
            memory["max_bound"] = max(memory["max_bound"], on_count * 2)
        else:
            memory["max_bound"] = max(memory["max_bound"], off_count * 3)
        
        # Move to testing phase and start moving
        memory["phase"] = "test_bound"
        memory["test_target"] = memory["max_bound"]
        memory["steps"] = 0  # Start moving
        return toggle, 1, memory, done, estimated_n
    
    # Test a specific bound
    if memory["phase"] == "test_bound":
        if memory["steps"] >= memory["test_target"]:
            # Reached the bound without finding anything special
            memory["phase"] = "return_and_decide"
            memory["direction"] = -1
            return toggle, -1, memory, done, estimated_n
        
        # Record lamp state
        if lamp_state == 1:
            memory["found_on"].append(memory["steps"])
        
        memory["steps"] += 1
        return toggle, +1, memory, done, estimated_n
    
    # Return and decide next action
    if memory["phase"] == "return_and_decide":
        if memory["steps"] == 0:
            # Back at start
            recent_on = len([x for x in memory["found_on"] if x >= memory["test_target"] // 2])
            
            if recent_on > 0:
                memory["max_bound"] *= 2
            else:
                memory["phase"] = "final_check"
            
            memory["test_target"] = memory["max_bound"]
            memory["steps"] = 0  # Start moving
            return toggle, 1, memory, done, estimated_n
        else:
            memory["steps"] -= 1
            return toggle, -1, memory, done, estimated_n
    
    # Final check phase
    if memory["phase"] == "final_check":
        memory["steps"] += 1
        
        if memory["steps"] > memory["max_bound"] * 1.5:
            # Went far beyond bound without issues
            done = True
            estimated_n = memory["max_bound"]
            return toggle, 0, memory, done, estimated_n
        
        return toggle, +1, memory, done, estimated_n
    
    # Fallback - always move
    return toggle, +1, memory, done, estimated_n


adaptive_binary = adaptive_binary_strategy