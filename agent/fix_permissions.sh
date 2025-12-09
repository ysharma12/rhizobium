#!/bin/bash
# Fix Google Drive permission issues

echo "============================================"
echo "Fix Google Drive Permissions"
echo "============================================"
echo ""
echo "This script will re-authenticate with Google Drive"
echo "to get both read and write permissions."
echo ""
echo "What will happen:"
echo "  1. Delete old authentication token"
echo "  2. Re-authenticate (browser will open)"
echo "  3. Grant both read and write access"
echo ""

read -p "Continue? (y/n) [y]: " confirm
confirm=${confirm:-y}

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Step 1: Removing old token..."
if [ -f "token.pickle" ]; then
    rm token.pickle
    echo "✅ Removed token.pickle"
else
    echo "ℹ️  No token.pickle found (this is OK)"
fi

echo ""
echo "Step 2: Re-authenticating..."
echo ""

# Activate venv
source venv/bin/activate

# Use account-aware authentication script
python auth_with_account.py

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "✅ Permissions fixed!"
    echo "============================================"
    echo ""
    echo "You can now:"
    echo "  • Download files: python download_from_gdrive.py"
    echo "  • Upload files: ./upload.sh"
    echo "  • Run complete analysis: ./run_complete_analysis.sh"
else
    echo ""
    echo "❌ Authentication failed"
    echo ""
    echo "Make sure you have credentials.json in this directory."
    echo "See TROUBLESHOOTING_GDRIVE.md for help."
    exit 1
fi

