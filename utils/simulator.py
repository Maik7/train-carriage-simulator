# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 18:14:05 2025

@author: mjustus
"""

"""
Simulation engine for the Train Carriage Problem
"""
import random
import pandas as pd
from typing import List, Tuple, Dict, Callable, Optional
import os
from .visualizer import render


def simulate(n: int, strategy: Callable, max_steps: int = 2000, 
             seed: Optional[int] = None, k: Optional[int] = None) -> Tuple:
    """
    Simulates the agent walking through a ring of n wagons.
    
    Args:
        n: Number of wagons
        strategy: Function(lamp_state, memory) → toggle, move, memory, done, estimate
        max_steps: Maximum steps before timeout
        seed: Random seed for reproducibility
        k: Initial lamp configuration mode:
           None: Random
           0: All lamps OFF
           1: All lamps ON
           2+: Use as random seed offset
    
    Returns:
        Tuple: (history, success, estimate, result_is_correct, steps_used)
    """
    # Set random seed if provided
    if seed is not None:
        random.seed(seed)
    
    # Initialize lamps based on k
    if k == 0:
        lamps = [0] * n  # All OFF
    elif k == 1:
        lamps = [1] * n  # All ON
    elif k is not None and k > 1:
        # Use k as seed offset
        random.seed(seed if seed is not None else 42 + k)
        lamps = [random.choice([0, 1]) for _ in range(n)]
    else:
        # Completely random
        lamps = [random.choice([0, 1]) for _ in range(n)]
    
    pos = 0
    memory = {}
    history = []
    
    for step in range(max_steps):
        lamp_state = lamps[pos]
        toggle, move, memory, done, estimate = strategy(lamp_state, memory)
        
        history.append((pos, lamps.copy(), toggle))
        if toggle:
            lamps[pos] ^= 1
        
        if done:
            return history, True, estimate, estimate == n, step + 1
        
        if move not in [-1, 0, +1]:
            raise ValueError("Strategy move must be -1, 0, or +1.")
        pos = (pos + move) % n
    
    return history, False, None, False, max_steps


def compare_strategies(configs: List[Tuple[int, int]], 
                      strategies: Dict[str, Callable],
                      max_steps: int = 5000,
                      save_images: bool = True,
                      output_dir: str = "simulation_results"):
    """
    Compare multiple strategies on different configurations.
    
    Args:
        configs: List of (n, k) tuples where n=wagon count, k=initial config
        strategies: Dictionary of strategy_name -> strategy_function
        max_steps: Maximum steps per simulation
        save_images: Whether to save visualization images
        output_dir: Directory to save results
    
    Returns:
        DataFrame with comparison results
    """
    # Create output directory
    if save_images and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []
    
    for n, k in configs:
        for strategy_name, strategy in strategies.items():
            # Create deterministic seed
            seed = n * 1000 + k if k not in [0, 1] else n * 1000
            
            print(f"Simulating: n={n}, k={k}, strategy={strategy_name}")
            
            history, success, estimate, correct, steps = simulate(
                n, strategy, max_steps, seed, k
            )
            
            # Save image if requested
            if save_images and len(history) > 0:
                filename = f"{output_dir}/n{n}_k{k}_{strategy_name}.png"
                render(history, filename)
            
            # Store results
            results.append({
                "n": n,
                "k": k,
                "strategy": strategy_name,
                "success": success,
                "correct": correct,
                "estimate": estimate,
                "steps": steps,
                "max_steps": max_steps,
                "efficiency": steps / n if n > 0 and success else None,
                "seed": seed
            })
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Print summary table
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)
    print(df.to_string())
    
    # Print aggregated statistics
    print("\n" + "="*80)
    print("AGGREGATED STATISTICS")
    print("="*80)
    
    stats = df.groupby('strategy').agg({
        'success': 'mean',
        'correct': 'mean',
        'steps': 'mean',
        'efficiency': 'mean'
    }).round(2)
    
    print(stats.to_string())
    
    # Save results to CSV
    csv_path = f"{output_dir}/simulation_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nDetailed results saved to: {csv_path}")
    
    return df