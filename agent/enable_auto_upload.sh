#!/bin/bash
# Enable automatic upload to Google Drive

echo "============================================"
echo "Enable Auto-Upload to Google Drive"
echo "============================================"
echo ""
echo "This will create a .auto_upload file that tells"
echo "run_complete_analysis.sh to automatically upload"
echo "reports to Google Drive without prompting."
echo ""

read -p "Enable auto-upload? (y/n) [y]: " confirm
confirm=${confirm:-y}

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    touch .auto_upload
    echo ""
    echo "✅ Auto-upload enabled!"
    echo ""
    echo "From now on, run_complete_analysis.sh will automatically"
    echo "upload reports to Google Drive."
    echo ""
    echo "To disable: rm .auto_upload"
else
    echo ""
    echo "⏭️  Auto-upload not enabled"
fi


