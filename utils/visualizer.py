# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 18:14:35 2025

@author: mjustus
"""

"""
Visualization functions for simulation results
"""
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from matplotlib.lines import Line2D


def render(history, filename: str = None):
    """
    Produces an image where:
      - each wagon = 4 pixels wide
      - each step = 1 pixel high
    """
    n = len(history[0][1])
    h = len(history)
    width = n * 4
    height = h
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    for y, (pos, lamps, toggled) in enumerate(history):
        for i, lamp in enumerate(lamps):
            x = i * 4
            if lamp == 1:
                color = (200, 200, 200)
            else:
                color = (60, 60, 60)
            
            if i == pos:
                if toggled:
                    color = (255, 120, 120) if lamp else (180, 40, 40)
                else:
                    color = (140, 160, 255) if lamp else (50, 60, 150)
            
            draw.rectangle([x, y, x + 2, y], fill=color)
    
    if filename:
        img.save(filename)
    
    return img


def visualize_results(df: pd.DataFrame, output_dir: str = "simulation_results"):
    """
    Create improved visualizations of simulation results with better error handling.
    
    Args:
        df: DataFrame with simulation results
        output_dir: Directory to save plots
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get strategies in original order from dataframe
    strategy_list = []
    for s in df['strategy'].unique():
        if s not in strategy_list:
            strategy_list.append(s)
    
    # Prepare data for plotting
    df_plot = df.copy()
    
    # Find max steps for scaling error positions
    max_steps = df_plot['steps'].max() if df_plot['steps'].notna().any() else 100
    
    # Assign y-values with jitter for error cases
    def get_y_value(row, strategy_index, total_strategies):
        if not row['success']:
            # No solution - position based on strategy index with jitter
            base_y = -max_steps * 0.015
            jitter = -(strategy_index/total_strategies) * (max_steps * 0.005)
            return base_y + jitter
        elif not row['correct']:
            # Wrong result - different level
            base_y = -max_steps * 0.005
            jitter = -(strategy_index/total_strategies) * (max_steps * 0.005)
            return base_y + jitter
        else:
            # Success with correct result
            return row['steps']
    
    strategy_to_index = {s: i for i, s in enumerate(strategy_list)}
    
    # Apply y-value calculation
    df_plot['plot_y'] = df_plot.apply(
        lambda row: get_y_value(row, strategy_to_index[row['strategy']], len(strategy_list)), 
        axis=1
    )
    
    # Add result type for coloring
    def get_result_type(row):
        if not row['success']:
            return 'no_solution'
        elif not row['correct']:
            return 'wrong_result'
        else:
            return 'correct'
    
    df_plot['result_type'] = df_plot.apply(get_result_type, axis=1)
    
    # Create figure
    plt.figure(figsize=(14, 10))
    
    # Assign colors
    result_colors = {
        'correct': 'green',
        'wrong_result': 'orange',
        'no_solution': 'red'
    }
    
    strategy_colors = plt.cm.Set1(np.linspace(0, 1, len(strategy_list)))
    color_dict = dict(zip(strategy_list, strategy_colors))
    
    # Create subplot 1: Steps vs Wagon count with separated error points
    plt.subplot(2, 2, 1)
    
    # First plot successful runs
    for strategy in strategy_list:
        mask = (df_plot['strategy'] == strategy) & (df_plot['result_type'] == 'correct')
        subset = df_plot[mask]
        
        if len(subset) > 0:
            # Sort by n for better line connections
            subset = subset.sort_values('n')
            plt.plot(subset['n'], subset['plot_y'], 
                    marker='o', linestyle='-', linewidth=2,
                    label=f'{strategy} (korrekt)', 
                    color=color_dict[strategy], markersize=8, alpha=0.8)
    
    # Then plot error cases with different markers
    error_markers = {
        'wrong_result': 's',  # square
        'no_solution': 'X'    # x
    }
    
    error_labels_added = {'wrong_result': False, 'no_solution': False}
    
    for strategy in strategy_list:
        for error_type in ['wrong_result', 'no_solution']:
            mask = (df_plot['strategy'] == strategy) & (df_plot['result_type'] == error_type)
            subset = df_plot[mask]
            
            if len(subset) > 0:
                label = None
                if not error_labels_added[error_type]:
                    label = 'Falsches Ergebnis' if error_type == 'wrong_result' else 'Keine Lösung'
                    error_labels_added[error_type] = True
                
                plt.scatter(subset['n'], subset['plot_y'],
                           marker=error_markers[error_type],
                           color=color_dict[strategy],
                           s=100,  # marker size
                           edgecolors='black',
                           linewidths=1,
                           label=label,
                           zorder=5)  # Ensure errors are on top
    
    plt.xlabel('Zuglänge (n)', fontsize=12)
    plt.ylabel('Anzahl Schritte / Fehlerposition', fontsize=12)
    plt.title('Strategievergleich mit getrennten Fehlerdarstellungen', 
             fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Create custom legend handles
    legend_handles = []
    
    # Add strategy lines
    for strategy, color in color_dict.items():
        legend_handles.append(Line2D([0], [0], color=color, linewidth=2, 
                                    label=strategy))
    
    # Add error markers
    legend_handles.append(Line2D([0], [0], marker='o', color='w', 
                                markerfacecolor='gray', markersize=8,
                                label='Korrekt (Linie)'))
    legend_handles.append(Line2D([0], [0], marker='s', color='w', 
                                markerfacecolor='gray', markersize=8,
                                label='Falsches Ergebnis'))
    legend_handles.append(Line2D([0], [0], marker='X', color='w', 
                                markerfacecolor='gray', markersize=8,
                                label='Keine Lösung'))
    
    plt.legend(handles=legend_handles, loc='upper left', fontsize=9)
    
    # Add horizontal reference lines for error zones
    error_zone_y = -max_steps * 0.01
    plt.axhline(y=error_zone_y, color='gray', linestyle=':', alpha=0.5, linewidth=1)
    plt.text(plt.xlim()[1]*0.95, error_zone_y, 'Fehlerzone', 
             ha='right', va='bottom', color='gray', fontsize=9, alpha=0.7)
    
    # Subplot 2: Success rate by strategy
    plt.subplot(2, 2, 2)
    
    # Calculate success rates while preserving strategy order
    success_rates = []
    correct_rates = []
    for strategy in strategy_list:
        mask = df['strategy'] == strategy
        subset = df[mask]
        success_rates.append(subset['success'].mean() * 100)
        correct_rates.append(subset['correct'].mean() * 100)
    
    x = np.arange(len(strategy_list))
    width = 0.35
    
    plt.bar(x - width/2, success_rates, width, 
            label='Erfolg (beendet)', color='lightblue', alpha=0.8)
    plt.bar(x + width/2, correct_rates, width, 
            label='Korrekt', color='lightgreen', alpha=0.8)
    
    plt.xlabel('Strategie', fontsize=12)
    plt.ylabel('Prozent (%)', fontsize=12)
    plt.title('Erfolgs- und Korrektheitsraten', fontsize=14, fontweight='bold')
    plt.xticks(x, strategy_list, rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(success_rates):
        plt.text(i - width/2, v + 1, f'{v:.0f}%', 
                ha='center', va='bottom', fontsize=9)
    for i, v in enumerate(correct_rates):
        plt.text(i + width/2, v + 1, f'{v:.0f}%', 
                ha='center', va='bottom', fontsize=9)
    
    # Subplot 3: Detailed error analysis
    plt.subplot(2, 2, 3)
    
    # Count errors by type and strategy - preserve strategy order
    error_counts_data = []
    error_types = ['correct', 'wrong_result', 'no_solution']
    
    # Initialize counts for each strategy
    for strategy in strategy_list:
        counts = {'strategy': strategy}
        for error_type in error_types:
            counts[error_type] = 0
        error_counts_data.append(counts)
    
    # Fill counts from dataframe
    for _, row in df_plot.iterrows():
        strategy = row['strategy']
        result_type = row['result_type']
        
        # Find the index of this strategy in our list
        for counts in error_counts_data:
            if counts['strategy'] == strategy:
                counts[result_type] += 1
                break
    
    # Convert to arrays for plotting
    correct_counts = [c['correct'] for c in error_counts_data]
    wrong_counts = [c['wrong_result'] for c in error_counts_data]
    no_solution_counts = [c['no_solution'] for c in error_counts_data]
    
    # Create stacked bar chart
    x_pos = np.arange(len(strategy_list))
    bottom = np.zeros(len(strategy_list))
    
    # Plot each error type
    error_labels = ['Korrekt', 'Falsch', 'Keine Lösung']
    error_colors_plot = ['green', 'orange', 'red']
    
    for i, (counts, label, color) in enumerate(zip(
        [correct_counts, wrong_counts, no_solution_counts],
        error_labels,
        error_colors_plot
    )):
        plt.bar(x_pos, counts, bottom=bottom, label=label, 
               color=color, alpha=0.7, edgecolor='black')
        
        # Add labels in the middle of each segment
        for j, (val, bot) in enumerate(zip(counts, bottom)):
            if val > 0:
                plt.text(j, bot + val/2, str(val), 
                        ha='center', va='center', color='white',
                        fontweight='bold', fontsize=10)
        bottom += np.array(counts)
    
    plt.xlabel('Strategie', fontsize=12)
    plt.ylabel('Anzahl Simulationen', fontsize=12)
    plt.title('Detaillierte Fehleranalyse nach Strategie', 
             fontsize=14, fontweight='bold')
    plt.xticks(x_pos, strategy_list, rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    
    # Subplot 4: Scatter plot with jitter for all results
    plt.subplot(2, 2, 4)
    
    # Add small jitter to x-position to separate points
    np.random.seed(42)  # For reproducible jitter
    df_plot['n_jittered'] = df_plot['n'] + np.random.uniform(-0.2, 0.2, len(df_plot))
    
    # Plot different result types
    for result_type, color in result_colors.items():
        mask = df_plot['result_type'] == result_type
        if mask.any():
            subset = df_plot[mask]
            
            # Different markers for different result types
            marker = 'o' if result_type == 'correct' else 's' if result_type == 'wrong_result' else 'X'
            label_map = {'correct': 'Korrekt', 
                        'wrong_result': 'Falsches Ergebnis', 
                        'no_solution': 'Keine Lösung'}
            
            plt.scatter(subset['n_jittered'], subset['plot_y'],
                       c=[color_dict[s] for s in subset['strategy']],
                       marker=marker,
                       s=80,
                       edgecolors='black',
                       linewidths=0.5,
                       label=label_map[result_type],
                       alpha=0.8)
    
    plt.xlabel('Zuglänge (n) mit Jitter', fontsize=12)
    plt.ylabel('Ergebnis', fontsize=12)
    plt.title('Alle Ergebnisse mit Strategie-Farben und Jitter', 
             fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Create legend for result types
    result_legend_handles = []
    for result_type, color in result_colors.items():
        label_map = {'correct': 'Korrekt', 
                    'wrong_result': 'Falsches Ergebnis', 
                    'no_solution': 'Keine Lösung'}
        marker = 'o' if result_type == 'correct' else 's' if result_type == 'wrong_result' else 'X'
        result_legend_handles.append(Line2D([0], [0], marker=marker, color='w', 
                                           markerfacecolor=color, markersize=8,
                                           label=label_map[result_type]))
    
    plt.legend(handles=result_legend_handles, loc='upper left')
    
    plt.tight_layout()
    
    # Save the figure
    plot_path = f"{output_dir}/strategy_comparison_improved.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"\nVerbesserte Visualisierung gespeichert als: {plot_path}")
    
    # Show additional plot: Steps distribution with error indicators
    plt.figure(figsize=(12, 6))
    
    # Create violin plot for steps distribution
    successful_runs = df[df['success'] & df['correct']]
    
    if len(successful_runs) > 0:
        # Prepare data for violin plot in correct strategy order
        violin_data = []
        violin_labels = []
        
        for strategy in strategy_list:
            strategy_data = successful_runs[successful_runs['strategy'] == strategy]['steps']
            if len(strategy_data) > 0:
                violin_data.append(strategy_data.values)
                violin_labels.append(strategy)
        
        if violin_data:
            # Create violin plot
            parts = plt.violinplot(violin_data, showmeans=False, showmedians=True)
            
            # Color violins by strategy
            for i, pc in enumerate(parts['bodies']):
                pc.set_facecolor(color_dict[violin_labels[i]])
                pc.set_alpha(0.7)
            
            # Add error indicators as text
            for i, strategy in enumerate(violin_labels):
                # Count errors for this strategy
                total_simulations = len(df[df['strategy'] == strategy])
                successful = len(successful_runs[successful_runs['strategy'] == strategy])
                wrong = len(df[(df['strategy'] == strategy) & (df['success']) & (~df['correct'])])
                failed = len(df[(df['strategy'] == strategy) & (~df['success'])])
                
                if wrong > 0 or failed > 0:
                    # Position text above the violin
                    y_pos = max(violin_data[i]) * 1.1 if len(violin_data[i]) > 0 else 0
                    error_text = f"✗{wrong} ⚠{failed}" if failed > 0 else f"✗{wrong}"
                    plt.text(i + 1, y_pos, error_text, 
                            ha='center', va='bottom', fontsize=9,
                            bbox=dict(boxstyle="round,pad=0.3", 
                                     facecolor="yellow", alpha=0.7))
    
    plt.xlabel('Strategie', fontsize=12)
    plt.ylabel('Anzahl Schritte', fontsize=12)
    plt.title('Verteilung der Schritte mit Fehlerindikatoren', 
             fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    plt.xticks(range(1, len(violin_labels) + 1), violin_labels, rotation=45, ha='right')
    
    plt.tight_layout()
    plot_path2 = f"{output_dir}/steps_distribution_with_errors.png"
    plt.savefig(plot_path2, dpi=150, bbox_inches='tight')
    
    plt.show()
    
    print(f"Zusätzliche Verteilungsvisualisierung: {plot_path2}")