"""
QA Progress Visualizer
Creates charts and graphs to visualize testing progress over time.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys
import os


class ProgressVisualizer:
    """Creates visualizations for QA testing progress."""
    
    def __init__(self, csv_directory: str = "."):
        """Initialize the visualizer with a directory containing CSV files."""
        self.csv_directory = Path(csv_directory)
        self.csv_files = []
        self.combined_data = None
        self.output_dir = Path("visualizations")
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        
    def load_csv_files(self, pattern: str = "qa_results_*.csv") -> bool:
        """Load all timestamped CSV files matching the pattern."""
        csv_pattern = str(self.csv_directory / pattern)
        self.csv_files = sorted(glob.glob(csv_pattern))
        
        if not self.csv_files:
            print(f"⚠ No CSV files found matching pattern: {pattern}")
            return False
        
        print(f"✓ Found {len(self.csv_files)} CSV files")
        
        # Load and combine all CSV files
        dfs = []
        for csv_file in self.csv_files:
            df = pd.read_csv(csv_file)
            dfs.append(df)
        
        self.combined_data = pd.concat(dfs, ignore_index=True)
        
        # Convert timestamp to datetime
        self.combined_data['timestamp'] = pd.to_datetime(self.combined_data['timestamp'])
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"✓ Loaded data from {self.combined_data['timestamp'].min()} to {self.combined_data['timestamp'].max()}")
        print(f"✓ Visualizations will be saved to: {self.output_dir}/")
        print()
        return True
    
    def create_latest_pie_chart(self) -> str:
        """Create a pie chart for the latest test results."""
        if self.combined_data is None:
            return None
        
        # Get latest data
        latest_timestamp = self.combined_data['timestamp'].max()
        latest_data = self.combined_data[
            (self.combined_data['timestamp'] == latest_timestamp) & 
            (self.combined_data['has_results'] == True)
        ]
        
        # Calculate totals
        total_pass = int(latest_data['pass_count'].sum())
        total_fail = int(latest_data['fail_count'].sum())
        total_not_available = int(latest_data['not_available_count'].sum())
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sizes = [total_pass, total_fail, total_not_available]
        labels = [f'Passed\n{total_pass}', f'Failed\n{total_fail}', f'Not Available\n{total_not_available}']
        colors = ['#2ecc71', '#e74c3c', '#95a5a6']
        explode = (0.05, 0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            explode=explode, 
            labels=labels, 
            colors=colors,
            autopct='%1.1f%%',
            shadow=True, 
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'}
        )
        
        # Make percentage text white for better visibility
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
        
        ax.axis('equal')
        
        title = f'Current Test Results Distribution\n{latest_timestamp.strftime("%Y-%m-%d %H:%M")}'
        plt.title(title, fontsize=16, weight='bold', pad=20)
        
        # Add total count
        total = total_pass + total_fail + total_not_available
        plt.figtext(0.5, 0.02, f'Total Tests: {total}', ha='center', fontsize=12, style='italic')
        
        # Save
        output_path = self.output_dir / "current_distribution_pie.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created pie chart: {output_path}")
        return str(output_path)
    
    def create_trend_line_chart(self) -> str:
        """Create a line chart showing pass/fail trends over time."""
        if self.combined_data is None:
            return None
        
        # Group by timestamp
        trends = self.combined_data[self.combined_data['has_results'] == True].groupby('timestamp').agg({
            'pass_count': 'sum',
            'fail_count': 'sum',
            'not_available_count': 'sum',
            'total_tests': 'sum'
        }).reset_index()
        
        if len(trends) < 1:
            print("⚠ Not enough data for trend chart")
            return None
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Raw counts
        ax1.plot(trends['timestamp'], trends['pass_count'], 
                marker='o', linewidth=2, markersize=8, label='Passed', color='#2ecc71')
        ax1.plot(trends['timestamp'], trends['fail_count'], 
                marker='s', linewidth=2, markersize=8, label='Failed', color='#e74c3c')
        ax1.plot(trends['timestamp'], trends['not_available_count'], 
                marker='^', linewidth=2, markersize=8, label='Not Available', color='#95a5a6')
        
        ax1.set_xlabel('Date', fontsize=12, weight='bold')
        ax1.set_ylabel('Number of Tests', fontsize=12, weight='bold')
        ax1.set_title('Test Results Trend Over Time', fontsize=14, weight='bold', pad=15)
        ax1.legend(loc='best', fontsize=11, framealpha=0.9)
        ax1.grid(True, alpha=0.3)
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Add value labels on points
        for idx, row in trends.iterrows():
            ax1.annotate(f"{int(row['pass_count'])}", 
                        (row['timestamp'], row['pass_count']),
                        textcoords="offset points", xytext=(0,10), 
                        ha='center', fontsize=9, color='#27ae60')
            ax1.annotate(f"{int(row['fail_count'])}", 
                        (row['timestamp'], row['fail_count']),
                        textcoords="offset points", xytext=(0,-15), 
                        ha='center', fontsize=9, color='#c0392b')
        
        # Plot 2: Pass percentage
        trends['pass_percentage'] = (trends['pass_count'] / trends['total_tests'] * 100).round(2)
        
        ax2.plot(trends['timestamp'], trends['pass_percentage'], 
                marker='o', linewidth=3, markersize=10, label='Pass Rate %', 
                color='#3498db', markerfacecolor='#2ecc71', markeredgewidth=2, markeredgecolor='#27ae60')
        ax2.fill_between(trends['timestamp'], trends['pass_percentage'], alpha=0.3, color='#3498db')
        
        ax2.set_xlabel('Date', fontsize=12, weight='bold')
        ax2.set_ylabel('Pass Rate (%)', fontsize=12, weight='bold')
        ax2.set_title('Pass Rate Trend', fontsize=14, weight='bold', pad=15)
        ax2.legend(loc='best', fontsize=11, framealpha=0.9)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 100)
        
        # Format x-axis
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Add value labels
        for idx, row in trends.iterrows():
            ax2.annotate(f"{row['pass_percentage']:.1f}%", 
                        (row['timestamp'], row['pass_percentage']),
                        textcoords="offset points", xytext=(0,10), 
                        ha='center', fontsize=10, weight='bold', color='#2c3e50')
        
        # Save
        output_path = self.output_dir / "trend_line_chart.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created trend line chart: {output_path}")
        return str(output_path)
    
    def create_stacked_bar_chart(self) -> str:
        """Create a stacked bar chart showing pass/fail distribution over time."""
        if self.combined_data is None:
            return None
        
        # Group by timestamp
        trends = self.combined_data[self.combined_data['has_results'] == True].groupby('timestamp').agg({
            'pass_count': 'sum',
            'fail_count': 'sum',
            'not_available_count': 'sum'
        }).reset_index()
        
        if len(trends) < 1:
            print("⚠ Not enough data for stacked bar chart")
            return None
        
        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Format timestamps for x-axis labels
        x_labels = [ts.strftime('%Y-%m-%d\n%H:%M') for ts in trends['timestamp']]
        x_pos = range(len(trends))
        
        # Create stacked bars
        p1 = ax.bar(x_pos, trends['pass_count'], label='Passed', color='#2ecc71', edgecolor='white', linewidth=2)
        p2 = ax.bar(x_pos, trends['fail_count'], bottom=trends['pass_count'], 
                   label='Failed', color='#e74c3c', edgecolor='white', linewidth=2)
        p3 = ax.bar(x_pos, trends['not_available_count'], 
                   bottom=trends['pass_count'] + trends['fail_count'],
                   label='Not Available', color='#95a5a6', edgecolor='white', linewidth=2)
        
        # Add value labels on bars
        for i, (p, f, u) in enumerate(zip(trends['pass_count'], trends['fail_count'], trends['not_available_count'])):
            total = p + f + u
            # Pass count
            if p > 0:
                ax.text(i, p/2, f'{int(p)}', ha='center', va='center', 
                       fontsize=11, weight='bold', color='white')
            # Fail count
            if f > 0:
                ax.text(i, p + f/2, f'{int(f)}', ha='center', va='center', 
                       fontsize=11, weight='bold', color='white')
            # Unknown count
            if u > 0:
                ax.text(i, p + f + u/2, f'{int(u)}', ha='center', va='center', 
                       fontsize=10, weight='bold', color='white')
            # Total on top
            ax.text(i, total, f'{int(total)}', ha='center', va='bottom', 
                   fontsize=12, weight='bold', color='#2c3e50')
        
        ax.set_xlabel('Date', fontsize=12, weight='bold')
        ax.set_ylabel('Number of Tests', fontsize=12, weight='bold')
        ax.set_title('Test Results Distribution Over Time (Stacked)', fontsize=14, weight='bold', pad=15)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels)
        ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Save
        output_path = self.output_dir / "stacked_bar_chart.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created stacked bar chart: {output_path}")
        return str(output_path)
    
    def create_daily_comparison_bars(self) -> str:
        """Create grouped bar chart comparing pass/fail counts day by day."""
        if self.combined_data is None:
            return None
        
        # Group by timestamp
        trends = self.combined_data[self.combined_data['has_results'] == True].groupby('timestamp').agg({
            'pass_count': 'sum',
            'fail_count': 'sum',
            'not_available_count': 'sum'
        }).reset_index()
        
        if len(trends) < 1:
            print("⚠ Not enough data for comparison chart")
            return None
        
        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x_labels = [ts.strftime('%Y-%m-%d\n%H:%M') for ts in trends['timestamp']]
        x = range(len(trends))
        width = 0.25
        
        # Create bars
        bars1 = ax.bar([i - width for i in x], trends['pass_count'], width, 
                       label='Passed', color='#2ecc71', edgecolor='#27ae60', linewidth=1.5)
        bars2 = ax.bar(x, trends['fail_count'], width, 
                       label='Failed', color='#e74c3c', edgecolor='#c0392b', linewidth=1.5)
        bars3 = ax.bar([i + width for i in x], trends['not_available_count'], width, 
                       label='Not Available', color='#95a5a6', edgecolor='#7f8c8d', linewidth=1.5)
        
        # Add value labels on bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=10, weight='bold')
        
        add_value_labels(bars1)
        add_value_labels(bars2)
        add_value_labels(bars3)
        
        ax.set_xlabel('Date', fontsize=12, weight='bold')
        ax.set_ylabel('Number of Tests', fontsize=12, weight='bold')
        ax.set_title('Daily Test Results Comparison', fontsize=14, weight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels)
        ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Save
        output_path = self.output_dir / "daily_comparison_bars.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created daily comparison chart: {output_path}")
        return str(output_path)
    
    def create_sheet_heatmap(self) -> str:
        """Create a heatmap showing pass rates by sheet over time."""
        if self.combined_data is None:
            return None
        
        # Get data with results
        data_with_results = self.combined_data[self.combined_data['has_results'] == True].copy()
        
        if len(data_with_results) < 1:
            print("⚠ Not enough data for heatmap")
            return None
        
        # Create pivot table
        pivot = data_with_results.pivot_table(
            values='pass_percentage',
            index='sheet_name',
            columns='timestamp',
            aggfunc='first'
        )
        
        if pivot.empty or len(pivot.columns) < 2:
            print("⚠ Not enough data points for heatmap")
            return None
        
        # Sort by latest pass rate (descending) - highest pass rates at top
        # Use the last column (most recent timestamp) for sorting
        latest_col = pivot.columns[-1]
        pivot = pivot.sort_values(by=latest_col, ascending=False)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(max(12, len(pivot.columns) * 2), max(8, len(pivot.index) * 0.5)))
        
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', center=50,
                   vmin=0, vmax=100, linewidths=1, linecolor='white',
                   cbar_kws={'label': 'Pass Rate (%)'}, ax=ax)
        
        # Format column labels (timestamps)
        col_labels = [ts.strftime('%Y-%m-%d\n%H:%M') for ts in pivot.columns]
        ax.set_xticklabels(col_labels, rotation=45, ha='right')
        
        ax.set_xlabel('Date', fontsize=12, weight='bold')
        ax.set_ylabel('Sheet Name', fontsize=12, weight='bold')
        ax.set_title('Pass Rate by Sheet Over Time (%)', fontsize=14, weight='bold', pad=15)
        
        # Save
        output_path = self.output_dir / "sheet_heatmap.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created sheet heatmap: {output_path}")
        return str(output_path)
    
    def create_sheet_details_chart(self) -> str:
        """Create a detailed chart showing pass/fail/unknown counts and percentages for each sheet."""
        if self.combined_data is None:
            return None
        
        # Get latest data
        latest_timestamp = self.combined_data['timestamp'].max()
        latest_data = self.combined_data[
            (self.combined_data['timestamp'] == latest_timestamp) & 
            (self.combined_data['has_results'] == True)
        ].copy()
        
        if len(latest_data) < 1:
            print("⚠ No data for sheet details chart")
            return None
        
        # Sort by pass percentage descending
        latest_data = latest_data.sort_values('pass_percentage', ascending=True)
        
        # Create figure with two subplots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, max(10, len(latest_data) * 0.4)))
        
        sheet_names = latest_data['sheet_name'].tolist()
        y_pos = range(len(sheet_names))
        
        # LEFT CHART: Stacked horizontal bar with raw numbers
        pass_counts = latest_data['pass_count'].tolist()
        fail_counts = latest_data['fail_count'].tolist()
        not_available_counts = latest_data['not_available_count'].tolist()
        
        p1 = ax1.barh(y_pos, pass_counts, label='Passed', color='#2ecc71', edgecolor='white', linewidth=1)
        p2 = ax1.barh(y_pos, fail_counts, left=pass_counts, label='Failed', color='#e74c3c', edgecolor='white', linewidth=1)
        
        # Calculate left position for unknown bars
        left_unknown = [p + f for p, f in zip(pass_counts, fail_counts)]
        p3 = ax1.barh(y_pos, not_available_counts, left=left_unknown, label='Not Available', color='#95a5a6', edgecolor='white', linewidth=1)
        
        # Add value labels on bars
        for i, (p, f, u) in enumerate(zip(pass_counts, fail_counts, not_available_counts)):
            total = p + f + u
            # Pass count
            if p > 0:
                ax1.text(p/2, i, f'{int(p)}', ha='center', va='center', 
                        fontsize=9, weight='bold', color='white')
            # Fail count
            if f > 0:
                ax1.text(p + f/2, i, f'{int(f)}', ha='center', va='center', 
                        fontsize=9, weight='bold', color='white')
            # Unknown count
            if u > 0:
                ax1.text(p + f + u/2, i, f'{int(u)}', ha='center', va='center', 
                        fontsize=8, weight='bold', color='white')
            # Total at the end
            ax1.text(total + 2, i, f'Total: {int(total)}', ha='left', va='center', 
                    fontsize=9, weight='bold', color='#2c3e50')
        
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(sheet_names, fontsize=10)
        ax1.set_xlabel('Number of Tests', fontsize=12, weight='bold')
        ax1.set_title('Raw Test Counts by Sheet', fontsize=14, weight='bold', pad=15)
        ax1.legend(loc='lower right', fontsize=10, framealpha=0.9)
        ax1.grid(True, alpha=0.3, axis='x')
        
        # RIGHT CHART: Horizontal bar chart showing pass rate percentage
        pass_percentages = latest_data['pass_percentage'].tolist()
        
        # Color bars based on pass rate (green > 80%, yellow 50-80%, red < 50%)
        bar_colors = []
        for pct in pass_percentages:
            if pct >= 80:
                bar_colors.append('#2ecc71')
            elif pct >= 50:
                bar_colors.append('#f39c12')
            else:
                bar_colors.append('#e74c3c')
        
        bars = ax2.barh(y_pos, pass_percentages, color=bar_colors, edgecolor='#2c3e50', linewidth=1)
        
        # Add percentage labels
        for i, (bar, pct, p, f, u) in enumerate(zip(bars, pass_percentages, pass_counts, fail_counts, not_available_counts)):
            total = p + f + u
            # Percentage on the bar
            ax2.text(pct/2, bar.get_y() + bar.get_height()/2, 
                    f'{pct:.1f}%', ha='center', va='center', 
                    fontsize=10, weight='bold', color='white')
            # Detailed breakdown at the end
            ax2.text(pct + 2, bar.get_y() + bar.get_height()/2, 
                    f'P:{int(p)} F:{int(f)} U:{int(u)}', ha='left', va='center', 
                    fontsize=8, color='#2c3e50')
        
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(sheet_names, fontsize=10)
        ax2.set_xlabel('Pass Rate (%)', fontsize=12, weight='bold')
        ax2.set_title('Pass Rate by Sheet (with P/F/U counts)', fontsize=14, weight='bold', pad=15)
        ax2.set_xlim(0, 110)  # Extra space for labels
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add reference lines
        ax2.axvline(x=50, color='red', linestyle='--', alpha=0.3, linewidth=1)
        ax2.axvline(x=80, color='green', linestyle='--', alpha=0.3, linewidth=1)
        
        # Add legend for color coding
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ecc71', label='≥80% (Good)'),
            Patch(facecolor='#f39c12', label='50-80% (Fair)'),
            Patch(facecolor='#e74c3c', label='<50% (Needs Attention)')
        ]
        ax2.legend(handles=legend_elements, loc='lower right', fontsize=9, framealpha=0.9)
        
        # Overall title
        fig.suptitle(f'Detailed Sheet-by-Sheet Analysis\n{latest_timestamp.strftime("%Y-%m-%d %H:%M")}', 
                    fontsize=16, weight='bold', y=0.98)
        
        # Save
        output_path = self.output_dir / "sheet_details_chart.png"
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created sheet details chart: {output_path}")
        return str(output_path)
    
    def create_improvement_chart(self) -> str:
        """Create a chart showing improvement from first to last run."""
        if self.combined_data is None:
            return None
        
        # Get first and last timestamps
        timestamps = sorted(self.combined_data['timestamp'].unique())
        
        if len(timestamps) < 2:
            print("⚠ Need at least 2 runs to show improvement")
            return None
        
        first_ts = timestamps[0]
        last_ts = timestamps[-1]
        
        # Get data for both timestamps
        first_data = self.combined_data[
            (self.combined_data['timestamp'] == first_ts) & 
            (self.combined_data['has_results'] == True)
        ]
        last_data = self.combined_data[
            (self.combined_data['timestamp'] == last_ts) & 
            (self.combined_data['has_results'] == True)
        ]
        
        # Calculate totals
        first_totals = {
            'pass': int(first_data['pass_count'].sum()),
            'fail': int(first_data['fail_count'].sum()),
            'not_available': int(first_data['not_available_count'].sum())
        }
        last_totals = {
            'pass': int(last_data['pass_count'].sum()),
            'fail': int(last_data['fail_count'].sum()),
            'not_available': int(last_data['not_available_count'].sum())
        }
        
        # Create comparison chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        categories = ['Passed', 'Failed', 'Not Available']
        first_values = [first_totals['pass'], first_totals['fail'], first_totals['not_available']]
        last_values = [last_totals['pass'], last_totals['fail'], last_totals['not_available']]
        colors = ['#2ecc71', '#e74c3c', '#95a5a6']
        
        x = range(len(categories))
        width = 0.35
        
        # Bar chart comparison
        bars1 = ax1.bar([i - width/2 for i in x], first_values, width, 
                       label=f'First Run\n{first_ts.strftime("%Y-%m-%d")}', 
                       color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        bars2 = ax1.bar([i + width/2 for i in x], last_values, width, 
                       label=f'Latest Run\n{last_ts.strftime("%Y-%m-%d")}', 
                       color=colors, alpha=1.0, edgecolor='black', linewidth=1.5)
        
        # Add value labels
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=11, weight='bold')
        
        add_labels(bars1)
        add_labels(bars2)
        
        ax1.set_ylabel('Number of Tests', fontsize=12, weight='bold')
        ax1.set_title('First vs. Latest Run Comparison', fontsize=14, weight='bold', pad=15)
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.legend(fontsize=10, framealpha=0.9)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Change arrows
        changes = {
            'Pass': last_totals['pass'] - first_totals['pass'],
            'Fail': last_totals['fail'] - first_totals['fail'],
            'Not Available': last_totals['not_available'] - first_totals['not_available']
        }
        
        change_labels = list(changes.keys())
        change_values = list(changes.values())
        change_colors = ['#2ecc71' if v >= 0 else '#e74c3c' for v in change_values]
        
        bars = ax2.barh(change_labels, change_values, color=change_colors, 
                       edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, change_values)):
            x_pos = val + (5 if val >= 0 else -5)
            ha = 'left' if val >= 0 else 'right'
            sign = '+' if val >= 0 else ''
            ax2.text(x_pos, bar.get_y() + bar.get_height()/2, f'{sign}{int(val)}',
                    ha=ha, va='center', fontsize=12, weight='bold')
        
        ax2.set_xlabel('Change in Number of Tests', fontsize=12, weight='bold')
        ax2.set_title('Changes from First to Latest Run', fontsize=14, weight='bold', pad=15)
        ax2.axvline(x=0, color='black', linewidth=1.5)
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Save
        output_path = self.output_dir / "improvement_chart.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created improvement chart: {output_path}")
        return str(output_path)
    
    def create_all_visualizations(self) -> List[str]:
        """Create all available visualizations."""
        print("\n" + "=" * 70)
        print("CREATING VISUALIZATIONS")
        print("=" * 70)
        print()
        
        output_files = []
        
        # Create each visualization
        charts = [
            ("Current distribution pie chart", self.create_latest_pie_chart),
            ("Trend line chart", self.create_trend_line_chart),
            ("Stacked bar chart", self.create_stacked_bar_chart),
            ("Daily comparison bars", self.create_daily_comparison_bars),
            ("Sheet details chart", self.create_sheet_details_chart),
            ("Sheet heatmap", self.create_sheet_heatmap),
            ("Improvement chart", self.create_improvement_chart)
        ]
        
        for name, func in charts:
            try:
                result = func()
                if result:
                    output_files.append(result)
            except Exception as e:
                print(f"⚠ Error creating {name}: {e}")
        
        print()
        print("=" * 70)
        print(f"✅ CREATED {len(output_files)} VISUALIZATIONS")
        print("=" * 70)
        print()
        print(f"All visualizations saved to: {self.output_dir}/")
        print()
        
        return output_files
    
    def create_html_report(self, image_files: List[str]) -> str:
        """Create an HTML report with all visualizations."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>QA Testing Progress Visualizations</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .info {{
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .chart {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chart h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        .chart img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>QA Testing Progress Visualizations</h1>
    
    <div class="info">
        <strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        <strong>Data Source:</strong> {len(self.csv_files)} CSV files<br>
        <strong>Time Period:</strong> {self.combined_data['timestamp'].min()} to {self.combined_data['timestamp'].max()}
    </div>
"""
        
        # Add each chart
        chart_titles = {
            'current_distribution_pie.png': 'Current Test Results Distribution',
            'trend_line_chart.png': 'Test Results Trend Over Time',
            'stacked_bar_chart.png': 'Test Results Distribution Over Time (Stacked)',
            'daily_comparison_bars.png': 'Daily Test Results Comparison',
            'sheet_details_chart.png': 'Detailed Sheet-by-Sheet Analysis (Raw Counts & Percentages)',
            'sheet_heatmap.png': 'Pass Rate by Sheet Over Time',
            'improvement_chart.png': 'Improvement from First to Latest Run'
        }
        
        for img_file in image_files:
            img_name = Path(img_file).name
            title = chart_titles.get(img_name, img_name)
            html_content += f"""
    <div class="chart">
        <h2>{title}</h2>
        <img src="{img_name}" alt="{title}">
    </div>
"""
        
        html_content += """
    <div class="footer">
        Generated by QA Progress Visualizer<br>
        For more information, see the documentation
    </div>
</body>
</html>
"""
        
        output_path = self.output_dir / "visualizations_report.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Created HTML report: {output_path}")
        print(f"  Open this file in your web browser to view all charts")
        return str(output_path)


def main():
    """Main function to create visualizations."""
    # Allow specifying directory as argument
    if len(sys.argv) > 1:
        csv_directory = sys.argv[1]
    else:
        csv_directory = "."
    
    # Create visualizer
    visualizer = ProgressVisualizer(csv_directory)
    
    # Load CSV files
    if not visualizer.load_csv_files():
        print("No CSV files to visualize. Run qa_analyzer.py first to generate data.")
        return
    
    # Create all visualizations
    image_files = visualizer.create_all_visualizations()
    
    # Create HTML report
    if image_files:
        visualizer.create_html_report(image_files)
        
        print("\n" + "=" * 70)
        print("🎨 VISUALIZATION COMPLETE!")
        print("=" * 70)
        print()
        print(f"View your charts:")
        print(f"  1. Open: {visualizer.output_dir}/visualizations_report.html")
        print(f"  2. Or check individual PNG files in: {visualizer.output_dir}/")
        print()


if __name__ == "__main__":
    main()


