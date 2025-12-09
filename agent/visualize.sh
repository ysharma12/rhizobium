#!/bin/bash
# Generate visualizations from QA analysis results

echo "============================================"
echo "QA Progress Visualizer"
echo "============================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Run the visualizer
python visualize_progress.py

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "✅ Visualizations created successfully!"
    echo "============================================"
    echo ""
    echo "To view your charts:"
    echo "  1. Open: visualizations/visualizations_report.html"
    echo "  2. Or check PNG files in: visualizations/"
    echo ""
else
    echo ""
    echo "❌ Visualization failed."
    echo "Make sure you have run the analyzer at least once."
    exit 1
fi


