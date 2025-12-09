"""
QA Testing Results Analyzer
Reads Excel sheets, identifies pass/fail results, and generates comprehensive summaries.
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
from datetime import datetime


# QA Team Configuration - Specific sheets and columns to analyze
# Maps sheet names to their result columns (using Excel column letters)
# Note: Column letters are 1-indexed as in Excel (A=1, B=2, ..., I=9, J=10, etc.)
QA_SHEET_CONFIG = {
    'SMS template': ['I'],                                    # Column I (index 8)
    'GreetingOpening': ['J'],                       # Column J (index 9)
    'WrapUp': ['J'],                                 # Column J (index 9)
    'Auth New OP': ['K'],                            # Column K (index 10)
    'Auth New Non-OP': ['J'],                       # Column J (index 9) - note: 2 spaces in sheet name
    'Conversation Flow_main menu': ['K', 'L'],       # Columns K & L (indices 10, 11)
    'CF1_ID card': ['J'],                            # Column J (index 9)
    'RegistrationSuppression': ['J'],               # Column J (index 9)
    'Email content sections': ['W'],                 # Column W (index 22)
    'CF3_Digital experience': ['J'],                 # Column J (index 9)
    'CF4_Pharmacy': ['J'],                           # Column J (index 9)
    'CF5_Extra benefits': ['M'],                     # Column M (index 12)
    'CF6_Flu': ['J'],                                # Column J (index 9)
    'CF7_AWV': ['J'],                                # Column J (index 9)
    'CF8_HRA+Cntact+DEAC': ['I'],                    # Column I (index 8)
    'CF9_Plan Satisfaction Survey': ['J'],           # Column J (index 9)
    'CF10_Communication preference': ['J'],          # Column J (index 9)
    'CF12_Help&Support': ['J'],                      # Column J (index 9)
    'Email Input': ['J'],                            # Column J (index 9)
    'Dedicated landing page': ['G'],                 # Column G (index 6)
    'LAP': ['G'],                                    # Column G (index 6)
    'Reschedule': ['H'],                             # Column H (index 7)
    'Terminate Resume conversation': ['G'],          # Column G (index 6)
    'Benefit info': ['H'],                           # Column H (index 7)
    'Browser adaptiveness': ['G'],                   # Column G (index 6)
    'Accessibility': ['H'],                          # Column H (index 7)
    'Holiday checking': ['G'],                       # Column H (index 7)
    'Report': ['AD']                                 # Column AD (index 29)
}


class QAAnalyzer:
    """Analyzes QA testing results from Excel spreadsheets with ad hoc formats."""
    
    # Keywords to identify pass/fail columns
    RESULT_KEYWORDS = ['result', 'status', 'outcome', 'pass', 'fail', 'test result', 
                       'qa result', 'test status', 'qa status', 'verdict', 'n/a']
    
    # Patterns to identify pass/fail/not available values
    PASS_PATTERNS = [
        r'\bpass(ed)?\b',
        r'\bsuccess(ful)?\b',
        r'\bok\b',
        r'\baccepted?\b',
        r'\bapproved?\b',
        r'\bcompleted?\b',
        r'\bvalid\b',
        r'\b✓\b',
        r'\b✔\b'
    ]
    
    FAIL_PATTERNS = [
        r'\bfail(ed|ure)?\b',
        r'\berror\b',
        r'\brejected?\b',
        r'\bblocked?\b',
        r'\binvalid\b',
        r'\bincomplete\b',
        r'\bpending\b',
        r'\bin progress\b',
        r'\b✗\b',
        r'\b✘\b',
        r'\bto ?do\b',
        r'\bnot (started|done|completed)\b'
    ]
    
    NOT_AVAILABLE_PATTERNS = [
        r'\bn[/\-\s]?a\b',  # Matches: n/a, n-a, n a, na
        r'\bnot[\s\-_]?available\b',
        r'\bnot[\s\-_]?applicable\b',
        r'\bN/A\b',
        r'\bNA\b',
        r'\bn/a\b'
    ]
    
    def __init__(self, excel_path: str, sheet_config: Dict[str, List[str]] = None):
        """Initialize the analyzer with an Excel file path and optional sheet configuration.
        
        Args:
            excel_path: Path to the Excel file
            sheet_config: Dictionary mapping sheet names to list of column letters (e.g., {'SMS': ['I'], 'CF1': ['J', 'K']})
                         If None, will auto-detect columns (legacy behavior)
        """
        self.excel_path = Path(excel_path)
        self.workbook = None
        self.sheet_names = []
        self.analysis_results = {}
        self.sheet_config = sheet_config
        
    @staticmethod
    def column_letter_to_index(letter: str) -> int:
        """Convert Excel column letter(s) to zero-based index.
        
        Examples: A->0, B->1, Z->25, AA->26, AB->27, AD->29
        """
        result = 0
        for char in letter.upper():
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1
        
    def load_workbook(self) -> bool:
        """Load the Excel workbook and get sheet names."""
        try:
            # Get all sheet names
            self.workbook = pd.ExcelFile(self.excel_path)
            self.sheet_names = self.workbook.sheet_names
            print(f"✓ Loaded workbook: {self.excel_path.name}")
            print(f"  Found {len(self.sheet_names)} sheets: {', '.join(self.sheet_names)}\n")
            return True
        except Exception as e:
            print(f"✗ Error loading workbook: {e}")
            return False
    
    def identify_result_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify columns that likely contain pass/fail results."""
        result_columns = []
        
        # Check column names
        for col in df.columns:
            col_lower = str(col).lower().strip()
            # Check if column name contains result keywords
            if any(keyword in col_lower for keyword in self.RESULT_KEYWORDS):
                result_columns.append(col)
                continue
                
            # Check if column contains pass/fail patterns
            if self._column_has_pass_fail_values(df[col]):
                result_columns.append(col)
        
        return result_columns
    
    def _column_has_pass_fail_values(self, series: pd.Series) -> bool:
        """Check if a column contains pass/fail/not available values."""
        # Sample non-null values
        sample = series.dropna().astype(str).str.lower().head(100)
        if len(sample) == 0:
            return False
        
        # Count how many values match pass/fail/not available patterns
        matches = 0
        for value in sample:
            if self._classify_value(value) in ['pass', 'fail', 'not_available']:
                matches += 1
        
        # If more than 30% of sampled values are pass/fail/not available, consider it a result column
        return (matches / len(sample)) > 0.3
    
    def _classify_value(self, value: str) -> str:
        """Classify a value as pass, fail, not_available, or unknown."""
        if pd.isna(value) or value == '':
            return 'not_available'
        
        value_str = str(value).lower().strip()
        
        # Check pass patterns
        for pattern in self.PASS_PATTERNS:
            if re.search(pattern, value_str, re.IGNORECASE):
                return 'pass'
        
        # Check fail patterns
        for pattern in self.FAIL_PATTERNS:
            if re.search(pattern, value_str, re.IGNORECASE):
                return 'fail'
        
        # Check not available patterns
        for pattern in self.NOT_AVAILABLE_PATTERNS:
            if re.search(pattern, value_str, re.IGNORECASE):
                return 'not_available'
        
        return 'not_available'
    
    def analyze_sheet(self, sheet_name: str) -> Dict[str, Any]:
        """Analyze a single sheet for pass/fail results."""
        print(f"Analyzing sheet: {sheet_name}")
        
        try:
            # Read the sheet
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            
            # Basic info
            total_rows = len(df)
            total_columns = len(df.columns)
            
            print(f"  Rows: {total_rows}, Columns: {total_columns}")
            
            # Identify result columns based on config or auto-detection
            if self.sheet_config and sheet_name in self.sheet_config:
                # Use configured columns
                column_letters = self.sheet_config[sheet_name]
                result_columns = []
                column_mapping = []  # Track letter -> actual column name mapping
                for letter in column_letters:
                    col_idx = self.column_letter_to_index(letter)
                    if col_idx < len(df.columns):
                        actual_col_name = df.columns[col_idx]
                        result_columns.append(actual_col_name)
                        column_mapping.append(f"Column {letter} (index {col_idx}) -> '{actual_col_name}'")
                    else:
                        print(f"  ⚠ Column {letter} (index {col_idx}) out of range - sheet only has {len(df.columns)} columns")
                
                if result_columns:
                    print(f"  ✓ Using configured columns:")
                    for mapping in column_mapping:
                        print(f"    {mapping}")
            else:
                # Auto-detect result columns (legacy behavior)
                result_columns = self.identify_result_columns(df)
                if result_columns:
                    print(f"  ✓ Auto-detected result columns: {', '.join(result_columns)}")
            
            if not result_columns:
                print(f"  ⚠ No pass/fail columns detected\n")
                return {
                    'sheet_name': sheet_name,
                    'total_rows': total_rows,
                    'total_columns': total_columns,
                    'has_results': False,
                    'result_columns': [],
                    'summary': {}
                }
            
            # Analyze each result column
            column_summaries = {}
            for col in result_columns:
                summary = self._analyze_result_column(df, col)
                column_summaries[col] = summary
            
            # Calculate overall summary (use the first/primary result column)
            primary_col = result_columns[0]
            primary_summary = column_summaries[primary_col]
            
            # Track configured column letter if available
            configured_column_letter = None
            if self.sheet_config and sheet_name in self.sheet_config:
                configured_column_letter = self.sheet_config[sheet_name][0]
            
            print(f"  📊 Results from '{primary_col}':")
            print(f"     Pass: {primary_summary['pass_count']}")
            print(f"     Fail: {primary_summary['fail_count']}")
            print(f"     Not Available: {primary_summary['not_available_count']}")
            print()
            
            return {
                'sheet_name': sheet_name,
                'total_rows': total_rows,
                'total_columns': total_columns,
                'has_results': True,
                'result_columns': result_columns,
                'primary_column': primary_col,
                'configured_column_letter': configured_column_letter,
                'column_summaries': column_summaries,
                'summary': primary_summary
            }
            
        except Exception as e:
            print(f"  ✗ Error analyzing sheet: {e}\n")
            return {
                'sheet_name': sheet_name,
                'error': str(e),
                'has_results': False
            }
    
    def _analyze_result_column(self, df: pd.DataFrame, column: str) -> Dict[str, int]:
        """Analyze a specific result column for pass/fail/not available counts."""
        pass_count = 0
        fail_count = 0
        not_available_count = 0
        
        for value in df[column]:
            classification = self._classify_value(value)
            if classification == 'pass':
                pass_count += 1
            elif classification == 'fail':
                fail_count += 1
            else:
                not_available_count += 1
        
        return {
            'pass_count': pass_count,
            'fail_count': fail_count,
            'not_available_count': not_available_count,
            'total': len(df)
        }
    
    def analyze_all_sheets(self) -> Dict[str, Any]:
        """Analyze all sheets in the workbook (or only configured sheets if config is provided)."""
        print("=" * 70)
        print("QA TESTING RESULTS ANALYSIS")
        print("=" * 70)
        
        if self.sheet_config:
            print(f"Using sheet configuration - will analyze {len(self.sheet_config)} configured sheets")
            sheets_to_analyze = [s for s in self.sheet_config.keys() if s in self.sheet_names]
            if len(sheets_to_analyze) < len(self.sheet_config):
                missing_sheets = set(self.sheet_config.keys()) - set(self.sheet_names)
                print(f"⚠ Warning: {len(missing_sheets)} configured sheets not found in workbook: {', '.join(missing_sheets)}")
        else:
            print(f"No configuration provided - will auto-detect columns in all {len(self.sheet_names)} sheets")
            sheets_to_analyze = self.sheet_names
        
        print()
        
        for sheet_name in sheets_to_analyze:
            result = self.analyze_sheet(sheet_name)
            self.analysis_results[sheet_name] = result
        
        return self.analysis_results
    
    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report."""
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("QA TESTING SUMMARY REPORT")
        report_lines.append("=" * 70)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"File: {self.excel_path.name}")
        report_lines.append(f"Total Sheets in Workbook: {len(self.sheet_names)}")
        if self.sheet_config:
            report_lines.append(f"Configuration: Using QA team's specified sheets and columns")
            report_lines.append(f"Configured Sheets: {len(self.sheet_config)}")
        else:
            report_lines.append(f"Configuration: Auto-detection mode (all sheets)")
        report_lines.append("")
        
        # Overall statistics
        sheets_with_results = [s for s in self.analysis_results.values() if s.get('has_results', False)]
        total_pass = sum(s['summary']['pass_count'] for s in sheets_with_results)
        total_fail = sum(s['summary']['fail_count'] for s in sheets_with_results)
        total_not_available = sum(s['summary']['not_available_count'] for s in sheets_with_results)
        total_tests = total_pass + total_fail + total_not_available
        
        report_lines.append("OVERALL SUMMARY")
        report_lines.append("-" * 70)
        report_lines.append(f"Sheets with QA Results: {len(sheets_with_results)}/{len(self.sheet_names)}")
        report_lines.append(f"Total Test Cases: {total_tests}")
        report_lines.append(f"  ✓ Passed: {total_pass} ({total_pass/total_tests*100:.1f}%)" if total_tests > 0 else "  ✓ Passed: 0")
        report_lines.append(f"  ✗ Failed: {total_fail} ({total_fail/total_tests*100:.1f}%)" if total_tests > 0 else "  ✗ Failed: 0")
        report_lines.append(f"  ⊘ Not Available: {total_not_available} ({total_not_available/total_tests*100:.1f}%)" if total_tests > 0 else "  ⊘ Not Available: 0")
        report_lines.append("")
        
        # Per-sheet details
        report_lines.append("SHEET-BY-SHEET BREAKDOWN")
        report_lines.append("-" * 70)
        
        for sheet_name, result in self.analysis_results.items():
            report_lines.append(f"\n📄 {sheet_name}")
            report_lines.append(f"   Total Rows: {result.get('total_rows', 0)}")
            
            if result.get('has_results', False):
                summary = result['summary']
                primary_col = result.get('primary_column', 'Unknown')
                configured_letter = result.get('configured_column_letter', None)
                
                if configured_letter:
                    report_lines.append(f"   Configured Column: {configured_letter}")
                    report_lines.append(f"   Actual Column Name: {primary_col}")
                else:
                    report_lines.append(f"   Result Column: {primary_col}")
                
                report_lines.append(f"   ✓ Pass: {summary['pass_count']}")
                report_lines.append(f"   ✗ Fail: {summary['fail_count']}")
                report_lines.append(f"   ⊘ Not Available: {summary['not_available_count']}")
                
                # Additional result columns if any
                if len(result['result_columns']) > 1:
                    report_lines.append(f"   Other result columns: {', '.join(result['result_columns'][1:])}")
            else:
                if 'error' in result:
                    report_lines.append(f"   ⚠ Error: {result['error']}")
                else:
                    report_lines.append(f"   ⚠ No QA result columns detected")
        
        report_lines.append("")
        report_lines.append("=" * 70)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 70)
        
        return "\n".join(report_lines)
    
    def save_summary_to_file(self, output_path: str = None) -> str:
        """Save the summary report to a file."""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"qa_summary_{timestamp}.txt"
        
        summary = self.generate_summary_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n✓ Summary report saved to: {output_path}")
        return output_path
    
    def save_detailed_json(self, output_path: str = None) -> str:
        """Save detailed analysis results to JSON."""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"qa_analysis_{timestamp}.json"
        
        # Convert any datetime objects to strings for JSON serialization
        json_safe_results = self._make_json_serializable(self.analysis_results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_safe_results, f, indent=2)
        
        print(f"✓ Detailed analysis saved to: {output_path}")
        return output_path
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format, including datetime keys."""
        if isinstance(obj, dict):
            # Convert both keys and values - keys might be datetime objects too
            new_dict = {}
            for k, v in obj.items():
                # Convert key if it's a datetime
                if isinstance(k, (pd.Timestamp, datetime)):
                    new_key = k.strftime('%Y-%m-%d %H:%M:%S')
                elif pd.isna(k):
                    new_key = 'null'
                else:
                    new_key = str(k)  # Ensure all keys are strings
                new_dict[new_key] = self._make_json_serializable(v)
            return new_dict
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    def save_to_csv(self, output_path: str = None) -> str:
        """Save analysis results to CSV format for easy tracking over time."""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"qa_results_{timestamp}.csv"
        
        # Prepare data for CSV
        csv_data = []
        run_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for sheet_name, result in self.analysis_results.items():
            row = {
                'timestamp': run_timestamp,
                'sheet_name': sheet_name,
                'total_rows': result.get('total_rows', 0),
                'total_columns': result.get('total_columns', 0),
                'has_results': result.get('has_results', False),
            }
            
            if result.get('has_results', False):
                summary = result['summary']
                total_tests = summary['total']
                pass_count = summary['pass_count']
                fail_count = summary['fail_count']
                not_available_count = summary['not_available_count']
                
                # Convert result columns to strings (they might be datetime objects)
                result_columns = result.get('result_columns', [])
                result_columns_str = []
                for col in result_columns:
                    if isinstance(col, (pd.Timestamp, datetime)):
                        result_columns_str.append(col.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        result_columns_str.append(str(col))
                
                # Same for primary column
                primary_col = result.get('primary_column', '')
                if isinstance(primary_col, (pd.Timestamp, datetime)):
                    primary_col = primary_col.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    primary_col = str(primary_col)
                
                row.update({
                    'pass_count': pass_count,
                    'fail_count': fail_count,
                    'not_available_count': not_available_count,
                    'total_tests': total_tests,
                    'pass_percentage': round(pass_count / total_tests * 100, 2) if total_tests > 0 else 0,
                    'fail_percentage': round(fail_count / total_tests * 100, 2) if total_tests > 0 else 0,
                    'not_available_percentage': round(not_available_count / total_tests * 100, 2) if total_tests > 0 else 0,
                    'configured_column_letter': result.get('configured_column_letter', ''),
                    'primary_result_column': primary_col,
                    'all_result_columns': '|'.join(result_columns_str),
                    'status': 'analyzed'
                })
            else:
                row.update({
                    'pass_count': 0,
                    'fail_count': 0,
                    'not_available_count': 0,
                    'total_tests': 0,
                    'pass_percentage': 0,
                    'fail_percentage': 0,
                    'not_available_percentage': 0,
                    'configured_column_letter': result.get('configured_column_letter', ''),
                    'primary_result_column': '',
                    'all_result_columns': '',
                    'status': 'no_results' if 'error' not in result else 'error'
                })
            
            csv_data.append(row)
        
        # Write to CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(output_path, index=False)
        
        print(f"✓ CSV results saved to: {output_path}")
        return output_path


def main():
    """Main function to run the QA analyzer."""
    import sys
    
    # Default to the data file if no argument provided
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        excel_path = "data/Testing master_Welcome Call 2026.xlsx"
    
    # Create analyzer with QA team's sheet configuration
    analyzer = QAAnalyzer(excel_path, sheet_config=QA_SHEET_CONFIG)
    
    # Load workbook
    if not analyzer.load_workbook():
        return
    
    # Analyze configured sheets
    analyzer.analyze_all_sheets()
    
    # Generate and print summary
    summary = analyzer.generate_summary_report()
    print("\n" + summary)
    
    # Save reports
    analyzer.save_summary_to_file()
    analyzer.save_detailed_json()
    analyzer.save_to_csv()


if __name__ == "__main__":
    main()

