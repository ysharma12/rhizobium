#!/bin/bash
# Quick script to run QA analysis

echo "🔍 Running QA Analysis (30 configured sheets)..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run the analyzer
python qa_analyzer.py "../data/Testing master_Welcome Call 2026.xlsx"

echo ""
echo "============================================"
echo "Analysis complete!"
echo "To track progress over time, run:"
echo "  ./track_progress.sh"
echo "============================================"


