#!/bin/bash
# Cleanup Old Analysis Results
# Use this when you change the configuration to avoid mixing old and new data

echo "============================================"
echo "🗑️  Clean Up Old Analysis Results"
echo "============================================"
echo ""
echo "This will archive old analysis files that used different"
echo "sheet/column configurations."
echo ""

# Create archive directory with timestamp
ARCHIVE_DIR="archived_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

echo "Moving old results to: $ARCHIVE_DIR"
echo ""

# Count files to move
OLD_SUMMARY_COUNT=$(ls qa_summary_*.txt 2>/dev/null | wc -l)
OLD_CSV_COUNT=$(ls qa_results_*.csv 2>/dev/null | wc -l)
OLD_JSON_COUNT=$(ls qa_analysis_*.json 2>/dev/null | wc -l)

if [ "$OLD_SUMMARY_COUNT" -eq 0 ] && [ "$OLD_CSV_COUNT" -eq 0 ] && [ "$OLD_JSON_COUNT" -eq 0 ]; then
    echo "✓ No old analysis files found. Nothing to clean up."
    rmdir "$ARCHIVE_DIR"
    exit 0
fi

echo "Found files to archive:"
echo "  • $OLD_SUMMARY_COUNT summary reports (qa_summary_*.txt)"
echo "  • $OLD_CSV_COUNT CSV files (qa_results_*.csv)"
echo "  • $OLD_JSON_COUNT JSON files (qa_analysis_*.json)"
echo ""

read -p "Archive these files? (y/n) [y]: " confirm
confirm=${confirm:-y}

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    rmdir "$ARCHIVE_DIR"
    exit 0
fi

# Move files
echo ""
echo "Archiving files..."

if [ "$OLD_SUMMARY_COUNT" -gt 0 ]; then
    mv qa_summary_*.txt "$ARCHIVE_DIR/" 2>/dev/null
    echo "  ✓ Moved $OLD_SUMMARY_COUNT summary files"
fi

if [ "$OLD_CSV_COUNT" -gt 0 ]; then
    mv qa_results_*.csv "$ARCHIVE_DIR/" 2>/dev/null
    echo "  ✓ Moved $OLD_CSV_COUNT CSV files"
fi

if [ "$OLD_JSON_COUNT" -gt 0 ]; then
    mv qa_analysis_*.json "$ARCHIVE_DIR/" 2>/dev/null
    echo "  ✓ Moved $OLD_JSON_COUNT JSON files"
fi

# Also archive old combined history if it exists
if [ -f "combined_history_*.csv" ]; then
    mv combined_history_*.csv "$ARCHIVE_DIR/" 2>/dev/null
    echo "  ✓ Moved combined history files"
fi

# Archive old progress reports if they exist
if [ -f "progress_report_*.txt" ]; then
    mv progress_report_*.txt "$ARCHIVE_DIR/" 2>/dev/null
    echo "  ✓ Moved progress reports"
fi

echo ""
echo "============================================"
echo "✅ Cleanup Complete!"
echo "============================================"
echo ""
echo "Old results archived to: $ARCHIVE_DIR"
echo ""
echo "You can now run a fresh analysis with the new configuration:"
echo "  ./run_analysis.sh"
echo ""
echo "To restore old files if needed:"
echo "  mv $ARCHIVE_DIR/* ."
echo "============================================"

