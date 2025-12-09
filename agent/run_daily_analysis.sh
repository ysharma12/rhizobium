#!/bin/bash
# Daily QA Analysis with Google Drive Download
# This script downloads the latest file from Google Drive and runs the analysis

echo "============================================"
echo "Daily QA Analysis"
echo "============================================"
echo "📋 Using QA team's configured sheets & columns"
echo ""

# Activate virtual environment
source venv/bin/activate

# Step 1: Download latest file from Google Drive
echo "Step 1: Downloading latest file from Google Drive..."
python download_from_gdrive.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Download failed. Aborting analysis."
    echo "Check GDRIVE_SETUP.md for troubleshooting help."
    exit 1
fi

echo ""
echo "============================================"

# Step 2: Run QA Analysis
echo ""
echo "Step 2: Running QA Analysis..."
python qa_analyzer.py "../data/Testing master_Welcome Call 2026.xlsx"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Analysis failed."
    exit 1
fi

echo ""
echo "============================================"
echo "✅ Daily analysis complete!"
echo "============================================"
echo ""
echo "Generated files:"
echo "  📄 qa_summary_TIMESTAMP.txt - Human-readable report"
echo "  📊 qa_results_TIMESTAMP.csv - For progress tracking"
echo "  📋 qa_analysis_TIMESTAMP.json - Detailed data"
echo ""
echo "Next steps:"
echo "  • Track progress over time: ./track_progress.sh"
echo "  • Create visualizations: ./visualize.sh"
echo ""
echo "============================================"

