# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 18:15:11 2025

@author: mjustus
"""

"""
Data analysis and reporting functions
"""
import pandas as pd


def generate_report(df: pd.DataFrame):
    """
    Generate a comprehensive report from simulation results.
    """
    print("\n" + "="*80)
    print("DETAILED REPORT")
    print("="*80)
    
    # Success rate by n
    print("\n1. Success Rate by Wagon Count:")
    success_by_n = df.groupby('n')['success'].mean().round(3)
    for n, rate in success_by_n.items():
        print(f"  n={n:3d}: {rate:.1%}")
    
    # Success rate by k
    print("\n2. Success Rate by Initial Configuration (k):")
    success_by_k = df.groupby('k')['success'].mean().round(3)
    for k, rate in success_by_k.items():
        k_desc = "All OFF" if k == 0 else "All ON" if k == 1 else f"Random (seed+{k})"
        print(f"  k={k}: {k_desc:20s} - {rate:.1%}")
    
    # Best strategy by efficiency
    print("\n3. Average Steps per Wagon (lower is better):")
    efficiency = df[df['success']].groupby('strategy')['efficiency'].mean().sort_values()
    for strategy, eff in efficiency.items():
        print(f"  {strategy:25s}: {eff:.1f} steps/wagon")
    
    # Find problematic configurations
    print("\n4. Failed Simulations:")
    failed = df[~df['success']]
    if len(failed) > 0:
        for _, row in failed.iterrows():
            print(f"  n={row['n']}, k={row['k']}, strategy={row['strategy']}")
    else:
        print("  None! All simulations succeeded.")