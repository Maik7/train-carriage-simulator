# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 18:13:05 2025

@author: mjustus
"""

# -*- coding: utf-8 -*-
"""
Train Carriage Problem Simulator - Main Program
Created on Sat Dec  6 11:03:27 2025
@author: mjustus
"""

import sys
import os

# Add strategies directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategies'))

# Import from modules
from strategies import strategies, list_strategies
from utils.simulator import simulate, compare_strategies
from utils.visualizer import render, visualize_results
from utils.analyzer import generate_report


def main():
    """Main execution function"""
    print("Verfügbare Strategien:")
    for i, name in enumerate(list_strategies(), 1):
        print(f"  {i}. {name}")
    
    # Define test configurations (n, k)
    test_configs = [
        (3, 0),   # Small train, all OFF
        (3, 1),   # Small train, all ON
        (3, 2),   # Small train, random
        #(5, 0),
        #(5, 1),
        #(5, 2),
        #(8, 0),
        #(8, 1),
        #(8, 2),
        (12, 0),
        (12, 1),
        (12, 2),
        #(24, 0),
        #(24, 1),
        #(24, 2),
        #(24, 3),
        #(24, 4),
        (48, 2),
        (48, 3),
        (48, 4),
        (80, 2),
        (80, 3),
        (80, 4),
        (90, 2),
        (100, 2),
        (120, 2),
        (160, 2),
        (200, 2),
        (250, 2),
        (300, 2),
        (350, 2),
        (400, 2),
        (450, 2),
        (500, 2),
        
    ]
    __test_configs = [
       
        (17, 1),
        
    ]
    print(f"\nTeste {len(test_configs)} Konfigurationen mit {len(strategies)} Strategien")
    print("="*80)
    
    print("Starting simulation comparison...")
    print(f"Testing {len(test_configs)} configurations with {len(strategies)} strategies")
    print("="*80)
    
    # Run comparison
    results_df = compare_strategies(
        configs=test_configs,
        strategies=strategies,
        max_steps=5000,
        save_images=True,
        output_dir="simulation_results",
        abort_incorrect_strategies = True
    )
    
    # Generate detailed report
    generate_report(results_df)
    
    # Generate visualizations
    visualize_results(results_df, "simulation_results")
    
    print("\nSimulation completed successfully!")


if __name__ == "__main__":
    main()