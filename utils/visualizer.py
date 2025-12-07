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
    
    # Create figure with 5 subplots (4 plots + 1 ranking)
    fig = plt.figure(figsize=(16, 14))
    
    # Assign colors
    result_colors = {
        'correct': 'green',
        'wrong_result': 'orange',
        'no_solution': 'red'
    }
    
    strategy_colors = plt.cm.Set1(np.linspace(0, 1, len(strategy_list)))
    color_dict = dict(zip(strategy_list, strategy_colors))
    
    # --------------------------------------------------------------------
    # SUBPLOT 1: Steps vs Wagon count - ONLY 100% CORRECT STRATEGIES
    # --------------------------------------------------------------------
    ax1 = plt.subplot(3, 2, 1)
    
    # Calculate which strategies are 100% correct
    strategy_success = df.groupby('strategy')['correct'].mean()
    perfect_strategies = strategy_success[strategy_success == 1.0].index.tolist()
    
    if perfect_strategies:
        # Plot only perfect strategies
        for strategy in perfect_strategies:
            mask = (df_plot['strategy'] == strategy) & (df_plot['result_type'] == 'correct')
            subset = df_plot[mask]
            
            if len(subset) > 0:
                # Sort by n for better line connections
                subset = subset.sort_values('n')
                ax1.plot(subset['n'], subset['plot_y'], 
                        marker='o', linestyle='-', linewidth=2,
                        label=f'{strategy}', 
                        color=color_dict[strategy], markersize=8, alpha=0.8)        
    
    ax1.set_xlabel('Train Length (n)', fontsize=12)
    ax1.set_ylabel('Number of Steps / Error Position', fontsize=12)
    ax1.set_title('Strategy Comparison - Perfect Strategies Only', 
                 fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Create custom legend handles
    legend_handles = []
    
    # Add perfect strategy lines
    for strategy in perfect_strategies:
        legend_handles.append(Line2D([0], [0], color=color_dict[strategy], linewidth=2, 
                                    label=strategy))
    

    
    ax1.legend(handles=legend_handles, loc='upper left', fontsize=9)
    
    
    
    # --------------------------------------------------------------------
    # SUBPLOT 2: Success rate by strategy
    # --------------------------------------------------------------------
    ax2 = plt.subplot(3, 2, 2)
    
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
    
    ax2.bar(x - width/2, success_rates, width, 
            label='Completed', color='lightblue', alpha=0.8)
    ax2.bar(x + width/2, correct_rates, width, 
            label='Correct', color='lightgreen', alpha=0.8)
    
    ax2.set_xlabel('Strategy', fontsize=12)
    ax2.set_ylabel('Percentage (%)', fontsize=12)
    ax2.set_title('Completion and Correctness Rates', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(strategy_list, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(success_rates):
        ax2.text(i - width/2, v + 1, f'{v:.0f}%', 
                ha='center', va='bottom', fontsize=9)
    for i, v in enumerate(correct_rates):
        ax2.text(i + width/2, v + 1, f'{v:.0f}%', 
                ha='center', va='bottom', fontsize=9)
    
    # --------------------------------------------------------------------
    # SUBPLOT 3: Detailed error analysis
    # --------------------------------------------------------------------
    ax3 = plt.subplot(3, 2, 3)
    
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
    error_labels = ['Correct', 'Wrong', 'No Solution']
    error_colors_plot = ['green', 'orange', 'red']
    
    for i, (counts, label, color) in enumerate(zip(
        [correct_counts, wrong_counts, no_solution_counts],
        error_labels,
        error_colors_plot
    )):
        ax3.bar(x_pos, counts, bottom=bottom, label=label, 
               color=color, alpha=0.7, edgecolor='black')
        
        # Add labels in the middle of each segment
        for j, (val, bot) in enumerate(zip(counts, bottom)):
            if val > 0:
                ax3.text(j, bot + val/2, str(val), 
                        ha='center', va='center', color='white',
                        fontweight='bold', fontsize=10)
        bottom += np.array(counts)
    
    ax3.set_xlabel('Strategy', fontsize=12)
    ax3.set_ylabel('Number of Simulations', fontsize=12)
    ax3.set_title('Detailed Error Analysis by Strategy', 
                 fontsize=14, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(strategy_list, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # --------------------------------------------------------------------
    # SUBPLOT 4: Scatter plot with jitter for all results
    # --------------------------------------------------------------------
    ax4 = plt.subplot(3, 2, 4)
    
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
            label_map = {'correct': 'Correct', 
                        'wrong_result': 'Wrong Result', 
                        'no_solution': 'No Solution'}
            
            ax4.scatter(subset['n_jittered'], subset['plot_y'],
                       c=[color_dict[s] for s in subset['strategy']],
                       marker=marker,
                       s=80,
                       edgecolors='black',
                       linewidths=0.5,
                       label=label_map[result_type],
                       alpha=0.8)
    
    ax4.set_xlabel('Train Length (n) with Jitter', fontsize=12)
    ax4.set_ylabel('Result', fontsize=12)
    ax4.set_title('All Results with Strategy Colors and Jitter', 
                 fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Create legend for result types
    result_legend_handles = []
    for result_type, color in result_colors.items():
        label_map = {'correct': 'Correct', 
                    'wrong_result': 'Wrong Result', 
                    'no_solution': 'No Solution'}
        marker = 'o' if result_type == 'correct' else 's' if result_type == 'wrong_result' else 'X'
        result_legend_handles.append(Line2D([0], [0], marker=marker, color='w', 
                                           markerfacecolor=color, markersize=8,
                                           label=label_map[result_type]))
    
    ax4.legend(handles=result_legend_handles, loc='upper left')
    
    # --------------------------------------------------------------------
    # SUBPLOT 5: Overall Ranking Table
    # --------------------------------------------------------------------
    ax5 = plt.subplot(3, 1, 3)
    ax5.axis('tight')
    ax5.axis('off')
    
    # Calculate ranking metrics
    ranking_data = []
    for strategy in strategy_list:
        mask = df['strategy'] == strategy
        subset = df[mask]
        
        # Basic metrics
        total_simulations = len(subset)
        success_rate = subset['success'].mean()
        correctness_rate = subset['correct'].mean()
        
        # Steps per wagon for successful correct runs
        successful_correct = subset[subset['success'] & subset['correct']]
        if len(successful_correct) > 0:
            avg_steps_per_wagon = successful_correct['efficiency'].mean()
        else:
            avg_steps_per_wagon = float('inf')
        
        # Total average steps (including failures)
        avg_total_steps = subset['steps'].mean()
        
        ranking_data.append({
            'Strategy': strategy,
            'Correctness': correctness_rate,
            'Avg Steps/Wagon': avg_steps_per_wagon if avg_steps_per_wagon != float('inf') else None,
            'Success Rate': success_rate,
            'Total Simulations': total_simulations,
            'Avg Total Steps': avg_total_steps
        })
    
    # Convert to DataFrame
    ranking_df = pd.DataFrame(ranking_data)
    
    # Sort by: 1. Correctness (descending), 2. Avg Steps/Wagon (ascending)
    ranking_df = ranking_df.sort_values(
        by=['Correctness', 'Avg Steps/Wagon'], 
        ascending=[False, True]
    ).reset_index(drop=True)
    
    # Add ranking position
    ranking_df['Rank'] = ranking_df.index + 1
    
    # Reorder columns
    ranking_df = ranking_df[['Rank', 'Strategy', 'Correctness', 'Avg Steps/Wagon', 
                            'Success Rate', 'Total Simulations', 'Avg Total Steps']]
    
    # Format values for display
    def format_correctness(val):
        return f"{val:.1%}" if pd.notnull(val) else "N/A"
    
    def format_steps(val):
        return f"{val:.1f}" if pd.notnull(val) and val != float('inf') else "N/A"
    
    def format_rate(val):
        return f"{val:.1%}" if pd.notnull(val) else "N/A"
    
    display_df = ranking_df.copy()
    display_df['Correctness'] = display_df['Correctness'].apply(format_correctness)
    display_df['Avg Steps/Wagon'] = display_df['Avg Steps/Wagon'].apply(format_steps)
    display_df['Success Rate'] = display_df['Success Rate'].apply(format_rate)
    display_df['Avg Total Steps'] = display_df['Avg Total Steps'].apply(lambda x: f"{x:.1f}" if pd.notnull(x) else "N/A")
    
    # Create table
    table_data = display_df.values.tolist()
    columns = list(display_df.columns)
    
    # Color rows based on correctness
    colors = []
    for _, row in ranking_df.iterrows():
        if row['Correctness'] == 1.0:
            colors.append(['lightgreen'] * len(columns))  # Perfect strategies
        elif row['Correctness'] >= 0.5:
            colors.append(['lightyellow'] * len(columns))  # Good strategies
        else:
            colors.append(['lightcoral'] * len(columns))  # Poor strategies
    
    table = ax5.table(cellText=table_data,
                     colLabels=columns,
                     cellLoc='center',
                     loc='center',
                     cellColours=colors)
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Make header row bold
    for i in range(len(columns)):
        table[(0, i)].set_text_props(weight='bold')
    
    ax5.set_title('Overall Strategy Ranking\n(Sorted by Correctness → Efficiency)', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Add legend for row colors
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='lightgreen', 
              markersize=15, label='Perfect (100% Correct)'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='lightyellow', 
              markersize=15, label='Good (≥50% Correct)'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='lightcoral', 
              markersize=15, label='Poor (<50% Correct)')
    ]
    
    ax5.legend(handles=legend_elements, loc='upper center', 
              bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=10)
    
    plt.tight_layout()
    
    # Save the figure
    plot_path = f"{output_dir}/strategy_comparison_improved.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"\nImproved visualization saved as: {plot_path}")
    
    # Save ranking as CSV
    ranking_csv_path = f"{output_dir}/strategy_ranking.csv"
    ranking_df.to_csv(ranking_csv_path, index=False)
    print(f"Strategy ranking saved as: {ranking_csv_path}")
    
    # Print ranking summary
    print("\n" + "="*80)
    print("OVERALL STRATEGY RANKING")
    print("="*80)
    print("\nTop 5 Strategies:")
    for i, (_, row) in enumerate(ranking_df.head(5).iterrows(), 1):
        steps = f"{row['Avg Steps/Wagon']:.1f}" if pd.notnull(row['Avg Steps/Wagon']) else "N/A"
        print(f"  {i}. {row['Strategy']:30s} - Correct: {row['Correctness']:.1%} - Steps/Wagon: {steps}")
    
    # Separate perfect and imperfect strategies
    perfect = ranking_df[ranking_df['Correctness'] == 1.0]
    imperfect = ranking_df[ranking_df['Correctness'] < 1.0]
    
    if len(perfect) > 0:
        print(f"\nPerfect Strategies ({len(perfect)} total):")
        for _, row in perfect.iterrows():
            steps = f"{row['Avg Steps/Wagon']:.1f}" if pd.notnull(row['Avg Steps/Wagon']) else "N/A"
            print(f"  ✓ {row['Strategy']:30s} - Steps/Wagon: {steps}")
    
    if len(imperfect) > 0:
        print(f"\nStrategies with Errors ({len(imperfect)} total):")
        for _, row in imperfect.iterrows():
            print(f"  ⚠ {row['Strategy']:30s} - Correct: {row['Correctness']:.1%}")
    
    # --------------------------------------------------------------------
    # Additional Plot: Steps distribution with error indicators
    # --------------------------------------------------------------------
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
    
    plt.xlabel('Strategy', fontsize=12)
    plt.ylabel('Number of Steps', fontsize=12)
    plt.title('Steps Distribution with Error Indicators (Correct Runs Only)', 
             fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    plt.xticks(range(1, len(violin_labels) + 1), violin_labels, rotation=45, ha='right')
    
    plt.tight_layout()
    plot_path2 = f"{output_dir}/steps_distribution_with_errors.png"
    plt.savefig(plot_path2, dpi=150, bbox_inches='tight')
    
    plt.show()
    
    print(f"\nAdditional distribution visualization: {plot_path2}")
    
    return ranking_df