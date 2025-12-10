#!/bin/bash
# Upload reports to Google Drive

echo "============================================"
echo "Upload Reports to Google Drive"
echo "============================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Run the uploader
python upload_to_gdrive.py "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "✅ Upload complete!"
    echo "============================================"
else
    echo ""
    echo "❌ Upload failed."
    echo "See GDRIVE_SETUP.md for setup instructions."
    exit 1
fi




