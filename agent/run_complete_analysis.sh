#!/bin/bash
# Complete QA Analysis Workflow
# Downloads from Google Drive → Analyzes → Creates Visualizations

echo "============================================"
echo "🚀 Complete QA Analysis Workflow"
echo "============================================"
echo ""
echo "This script will:"
echo "  1. 📥 Download latest file from Google Drive"
echo "  2. 🔍 Analyze QA test results (30 configured sheets)"
echo "  3. 📊 Create visualizations"
echo "  4. 📄 Generate all reports"
echo ""
echo "📋 Configuration: Using QA team's specified sheets & columns"
echo ""
echo "============================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Step 1: Download from Google Drive
echo "Step 1/3: Downloading from Google Drive..."
echo "--------------------------------------------"
python download_from_gdrive.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Download failed. Aborting."
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check your internet connection"
    echo "  2. Verify Google Drive file is shared"
    echo "  3. See GDRIVE_SETUP.md for help"
    exit 1
fi

echo ""
echo "✅ Download complete!"
echo ""

# Step 2: Run QA Analysis
echo "============================================"
echo "Step 2/3: Running QA Analysis..."
echo "--------------------------------------------"
echo "Analyzing 30 configured sheets with specific column mappings..."
python qa_analyzer.py "../data/Testing master_Welcome Call 2026.xlsx"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Analysis failed. Aborting."
    exit 1
fi

echo ""
echo "✅ Analysis complete!"
echo ""

# Step 3: Create Visualizations
echo "============================================"
echo "Step 3/3: Creating Visualizations..."
echo "--------------------------------------------"
python visualize_progress.py

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Visualization failed (this is OK if it's your first run)"
    echo "    You need at least 2 analysis runs to create visualizations."
    echo ""
    echo "✅ Analysis completed successfully!"
    echo ""
    echo "Generated files:"
    echo "  📄 qa_summary_*.txt"
    echo "  📊 qa_results_*.csv"
    echo "  📋 qa_analysis_*.json"
    echo ""
    echo "Run this script again tomorrow to create visualizations!"
    exit 0
fi

echo ""
echo "✅ Visualizations created!"
echo ""

# Step 3.5: Convert HTML Report to PDF
echo "============================================"
echo "Step 3.5/4: Converting Report to PDF..."
echo "--------------------------------------------"
python html_to_pdf.py visualizations/visualizations_report.html

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ PDF report created!"
else
    echo ""
    echo "⚠️  PDF conversion failed (HTML report is still available)"
    echo "    To enable PDF generation, install weasyprint:"
    echo "    pip install weasyprint"
fi
echo ""

# Step 4: Upload to Google Drive (Optional)
echo "============================================"
echo "Step 4/4: Upload to Google Drive (Optional)"
echo "--------------------------------------------"
echo ""

# Check if auto-upload is enabled via environment variable
if [ -n "$AUTO_UPLOAD" ] || [ -f ".auto_upload" ]; then
    upload_choice="y"
    echo "🔄 Auto-upload enabled"
else
    echo "Would you like to upload the reports to Google Drive?"
    read -p "Upload now? (y/n) [n]: " upload_choice
    upload_choice=${upload_choice:-n}
fi

if [ "$upload_choice" = "y" ] || [ "$upload_choice" = "Y" ]; then
    echo ""
    echo "Uploading reports to Google Drive..."
    python upload_to_gdrive.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Upload complete!"
    else
        echo ""
        echo "⚠️  Upload failed (this is OK - you can upload manually later)"
        echo "    Run: ./upload.sh"
    fi
else
    echo ""
    echo "⏭️  Skipping upload. You can upload later with: ./upload.sh"
fi

echo ""

# Final Summary
echo "============================================"
echo "🎉 COMPLETE ANALYSIS FINISHED!"
echo "============================================"
echo ""
echo "📊 Generated Reports:"
echo "  • qa_summary_*.txt       (Human-readable summary)"
echo "  • qa_results_*.csv       (Progress tracking data)"
echo "  • qa_analysis_*.json     (Detailed JSON data)"
echo ""
echo "📈 Visualizations:"
echo "  • visualizations/*.png   (7 chart types)"
echo "  • visualizations/visualizations_report.html ⭐"
echo "  • visualizations/visualizations_report.pdf 📄 (Daily report)"
echo ""
echo "👀 View Your Results:"
echo "  Text report:"
echo "    cat \$(ls -t qa_summary_*.txt | head -1)"
echo ""
echo "  Open visualization report in browser:"
echo "    visualizations/visualizations_report.html"
echo ""
echo "============================================"
echo "💡 Tips:"
echo "  • Run this daily to track progress!"
echo "  • For automatic upload, set SKIP_UPLOAD_PROMPT=y"
echo "============================================"

