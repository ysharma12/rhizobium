#!/bin/bash
# Quick script to track QA progress over time

# Activate virtual environment
source venv/bin/activate

# Run the progress tracker
python progress_tracker.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Progress tracking failed."
    exit 1
fi

echo ""
echo "============================================"
echo "Progress tracking complete!"
echo "============================================"
echo ""
echo "Would you like to generate visualizations?"
read -p "Create charts and graphs? (y/n) [y]: " create_viz
create_viz=${create_viz:-y}

if [ "$create_viz" = "y" ] || [ "$create_viz" = "Y" ]; then
    echo ""
    python visualize_progress.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Visualizations created!"
        echo "   Open: visualizations/visualizations_report.html"
    fi
fi

echo ""
echo "============================================"

