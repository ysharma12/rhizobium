#!/bin/bash
# One-time setup script for QA Analyzer

echo "============================================"
echo "QA Analyzer - Setup"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "qa_analyzer.py" ]; then
    echo "❌ Error: Please run this script from the agent/ directory"
    exit 1
fi

# Step 1: Create virtual environment
echo "Step 1: Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "  ℹ Virtual environment already exists"
else
    python3 -m venv venv
    echo "  ✅ Virtual environment created"
fi

# Step 2: Activate virtual environment
echo ""
echo "Step 2: Activating virtual environment..."
source venv/bin/activate
echo "  ✅ Virtual environment activated"

# Step 3: Install dependencies
echo ""
echo "Step 3: Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "  ✅ Packages installed successfully"
else
    echo "  ❌ Package installation failed"
    exit 1
fi

# Step 4: Make scripts executable
echo ""
echo "Step 4: Making scripts executable..."
chmod +x run_analysis.sh
chmod +x run_daily_analysis.sh
chmod +x run_complete_analysis.sh
chmod +x track_progress.sh
chmod +x visualize.sh
chmod +x upload.sh
chmod +x enable_auto_upload.sh
chmod +x fix_permissions.sh
chmod +x setup.sh
echo "  ✅ Scripts are now executable"

# Step 5: Create logs directory
echo ""
echo "Step 5: Creating logs directory..."
mkdir -p logs
echo "  ✅ Logs directory created"

# Step 6: Configure Google Drive (optional)
echo ""
echo "============================================"
echo "Google Drive Configuration (Optional)"
echo "============================================"
echo ""
echo "Would you like to set up automatic downloading from Google Drive?"
echo "This allows the script to fetch the latest file before each analysis."
echo ""
read -p "Configure Google Drive now? (y/n) [y]: " configure_gdrive
configure_gdrive=${configure_gdrive:-y}

if [ "$configure_gdrive" = "y" ] || [ "$configure_gdrive" = "Y" ]; then
    python download_from_gdrive.py
    if [ $? -eq 0 ]; then
        echo ""
        echo "  ✅ Google Drive configured successfully"
    else
        echo ""
        echo "  ⚠ Google Drive configuration incomplete"
        echo "  You can configure it later by running:"
        echo "    python download_from_gdrive.py"
    fi
else
    echo "  ⏭ Skipping Google Drive configuration"
    echo "  You can configure it later by running:"
    echo "    python download_from_gdrive.py"
fi

# Done!
echo ""
echo "============================================"
echo "✅ Setup Complete!"
echo "============================================"
echo ""
echo "Quick Start:"
echo ""
echo "🌟 RECOMMENDED - Complete workflow (download + analyze + visualize):"
echo "   ./run_complete_analysis.sh"
echo ""
echo "Or run individual steps:"
echo "  1. Download + analyze: ./run_daily_analysis.sh"
echo "  2. Analyze local file: ./run_analysis.sh"
echo "  3. Track progress: ./track_progress.sh"
echo "  4. Create visualizations: ./visualize.sh"
echo ""
echo "For more help, see:"
echo "  - QUICKSTART.md - Quick start guide"
echo "  - README.md - Full documentation"
echo "  - GDRIVE_SETUP.md - Google Drive setup help"
echo ""
echo "============================================"

