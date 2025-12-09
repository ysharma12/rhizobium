"""
QA Progress Tracker
Analyzes multiple timestamped CSV files to track testing progress over time.
"""

import pandas as pd
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys


class ProgressTracker:
    """Tracks QA testing progress across multiple timestamped CSV files."""
    
    def __init__(self, csv_directory: str = "."):
        """Initialize the progress tracker with a directory containing CSV files."""
        self.csv_directory = Path(csv_directory)
        self.csv_files = []
        self.combined_data = None
        
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
        
        print(f"✓ Loaded data from {self.combined_data['timestamp'].min()} to {self.combined_data['timestamp'].max()}")
        print()
        return True
    
    def get_overall_progress(self) -> pd.DataFrame:
        """Get overall progress across all sheets over time."""
        if self.combined_data is None:
            return None
        
        # Group by timestamp and calculate totals
        progress = self.combined_data[self.combined_data['has_results'] == True].groupby('timestamp').agg({
            'pass_count': 'sum',
            'fail_count': 'sum',
            'unknown_count': 'sum',
            'total_tests': 'sum'
        }).reset_index()
        
        # Calculate percentages
        progress['pass_percentage'] = (progress['pass_count'] / progress['total_tests'] * 100).round(2)
        progress['fail_percentage'] = (progress['fail_count'] / progress['total_tests'] * 100).round(2)
        progress['unknown_percentage'] = (progress['unknown_count'] / progress['total_tests'] * 100).round(2)
        
        return progress
    
    def get_sheet_progress(self, sheet_name: str) -> pd.DataFrame:
        """Get progress for a specific sheet over time."""
        if self.combined_data is None:
            return None
        
        sheet_data = self.combined_data[self.combined_data['sheet_name'] == sheet_name].copy()
        sheet_data = sheet_data.sort_values('timestamp')
        
        return sheet_data
    
    def get_latest_snapshot(self) -> pd.DataFrame:
        """Get the most recent snapshot of all sheets."""
        if self.combined_data is None:
            return None
        
        latest_timestamp = self.combined_data['timestamp'].max()
        return self.combined_data[self.combined_data['timestamp'] == latest_timestamp]
    
    def compare_first_and_last(self) -> Dict:
        """Compare the first and last snapshots to show overall progress."""
        if self.combined_data is None or len(self.combined_data['timestamp'].unique()) < 2:
            return None
        
        first_timestamp = self.combined_data['timestamp'].min()
        last_timestamp = self.combined_data['timestamp'].max()
        
        first_data = self.combined_data[self.combined_data['timestamp'] == first_timestamp]
        last_data = self.combined_data[self.combined_data['timestamp'] == last_timestamp]
        
        # Calculate totals for sheets with results
        first_totals = first_data[first_data['has_results'] == True].agg({
            'pass_count': 'sum',
            'fail_count': 'sum',
            'unknown_count': 'sum',
            'total_tests': 'sum'
        })
        
        last_totals = last_data[last_data['has_results'] == True].agg({
            'pass_count': 'sum',
            'fail_count': 'sum',
            'unknown_count': 'sum',
            'total_tests': 'sum'
        })
        
        return {
            'first_timestamp': first_timestamp,
            'last_timestamp': last_timestamp,
            'first': first_totals.to_dict(),
            'last': last_totals.to_dict(),
            'changes': {
                'pass_change': int(last_totals['pass_count'] - first_totals['pass_count']),
                'fail_change': int(last_totals['fail_count'] - first_totals['fail_count']),
                'unknown_change': int(last_totals['unknown_count'] - first_totals['unknown_count']),
                'total_change': int(last_totals['total_tests'] - first_totals['total_tests'])
            }
        }
    
    def generate_progress_report(self) -> str:
        """Generate a comprehensive progress report."""
        if self.combined_data is None:
            return "No data loaded"
        
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("QA TESTING PROGRESS REPORT")
        report_lines.append("=" * 70)
        report_lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"CSV Files Analyzed: {len(self.csv_files)}")
        report_lines.append("")
        
        # Time range
        time_range = f"{self.combined_data['timestamp'].min()} to {self.combined_data['timestamp'].max()}"
        report_lines.append(f"Time Period: {time_range}")
        report_lines.append("")
        
        # Latest snapshot
        latest = self.get_latest_snapshot()
        latest_timestamp = latest['timestamp'].iloc[0]
        report_lines.append("CURRENT STATUS (Latest Run)")
        report_lines.append("-" * 70)
        report_lines.append(f"As of: {latest_timestamp}")
        
        latest_with_results = latest[latest['has_results'] == True]
        total_pass = int(latest_with_results['pass_count'].sum())
        total_fail = int(latest_with_results['fail_count'].sum())
        total_unknown = int(latest_with_results['unknown_count'].sum())
        total_tests = int(latest_with_results['total_tests'].sum())
        
        report_lines.append(f"Total Test Cases: {total_tests}")
        report_lines.append(f"  ✓ Passed: {total_pass} ({total_pass/total_tests*100:.1f}%)" if total_tests > 0 else "  ✓ Passed: 0")
        report_lines.append(f"  ✗ Failed: {total_fail} ({total_fail/total_tests*100:.1f}%)" if total_tests > 0 else "  ✗ Failed: 0")
        report_lines.append(f"  ? Unknown/Pending: {total_unknown} ({total_unknown/total_tests*100:.1f}%)" if total_tests > 0 else "  ? Unknown/Pending: 0")
        report_lines.append("")
        
        # Progress over time (if multiple snapshots)
        if len(self.combined_data['timestamp'].unique()) > 1:
            comparison = self.compare_first_and_last()
            if comparison:
                report_lines.append("PROGRESS OVER TIME")
                report_lines.append("-" * 70)
                report_lines.append(f"From: {comparison['first_timestamp']}")
                report_lines.append(f"To:   {comparison['last_timestamp']}")
                report_lines.append("")
                
                changes = comparison['changes']
                report_lines.append("Changes:")
                report_lines.append(f"  Total Tests: {changes['total_change']:+d}")
                report_lines.append(f"  Passed: {changes['pass_change']:+d}")
                report_lines.append(f"  Failed: {changes['fail_change']:+d}")
                report_lines.append(f"  Unknown/Pending: {changes['unknown_change']:+d}")
                report_lines.append("")
                
                # Trend analysis
                overall_progress = self.get_overall_progress()
                if len(overall_progress) > 1:
                    report_lines.append("TREND ANALYSIS")
                    report_lines.append("-" * 70)
                    report_lines.append("")
                    report_lines.append("Date                    | Total | Pass | Fail | Unknown | Pass%")
                    report_lines.append("-" * 70)
                    
                    for _, row in overall_progress.iterrows():
                        ts = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                        report_lines.append(
                            f"{ts} | {int(row['total_tests']):5d} | "
                            f"{int(row['pass_count']):4d} | {int(row['fail_count']):4d} | "
                            f"{int(row['unknown_count']):7d} | {row['pass_percentage']:5.1f}%"
                        )
                    report_lines.append("")
        
        # Per-sheet summary
        report_lines.append("SHEET-BY-SHEET CURRENT STATUS")
        report_lines.append("-" * 70)
        
        for _, row in latest.iterrows():
            report_lines.append(f"\n📄 {row['sheet_name']}")
            if row['has_results']:
                report_lines.append(f"   Total Tests: {int(row['total_tests'])}")
                report_lines.append(f"   ✓ Pass: {int(row['pass_count'])} ({row['pass_percentage']:.1f}%)")
                report_lines.append(f"   ✗ Fail: {int(row['fail_count'])} ({row['fail_percentage']:.1f}%)")
                report_lines.append(f"   ? Unknown: {int(row['unknown_count'])} ({row['unknown_percentage']:.1f}%)")
            else:
                report_lines.append(f"   Status: {row['status']}")
        
        report_lines.append("")
        report_lines.append("=" * 70)
        report_lines.append("END OF PROGRESS REPORT")
        report_lines.append("=" * 70)
        
        return "\n".join(report_lines)
    
    def save_progress_report(self, output_path: str = None) -> str:
        """Save the progress report to a file."""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"progress_report_{timestamp}.txt"
        
        report = self.generate_progress_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✓ Progress report saved to: {output_path}")
        return output_path
    
    def export_combined_csv(self, output_path: str = None) -> str:
        """Export all combined data to a single CSV for further analysis."""
        if self.combined_data is None:
            return None
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"combined_history_{timestamp}.csv"
        
        self.combined_data.to_csv(output_path, index=False)
        print(f"✓ Combined history saved to: {output_path}")
        return output_path


def main():
    """Main function to run the progress tracker."""
    # Allow specifying directory as argument
    if len(sys.argv) > 1:
        csv_directory = sys.argv[1]
    else:
        csv_directory = "."
    
    # Create tracker
    tracker = ProgressTracker(csv_directory)
    
    # Load CSV files
    if not tracker.load_csv_files():
        print("No CSV files to analyze. Run qa_analyzer.py first to generate data.")
        return
    
    # Generate and print report
    report = tracker.generate_progress_report()
    print(report)
    
    # Save report
    tracker.save_progress_report()
    tracker.export_combined_csv()


if __name__ == "__main__":
    main()

