#!/bin/bash
###############################################################################
# setup_automation.sh - Automated Setup Script for Monthly Reporting
#
# This script helps you set up the automated monthly reporting system on your
# Raspberry Pi. It will:
# 1. Install required Python packages
# 2. Configure environment variables for email
# 3. Set up the cron job for automatic monthly reports
#
# Usage:
#   chmod +x setup_automation.sh
#   ./setup_automation.sh
###############################################################################

echo "========================================================================"
echo "  YOLOv8 Inventory System - Automated Reporting Setup"
echo "========================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Installation directory: $SCRIPT_DIR"
echo ""

# Step 1: Install Python dependencies
echo "========================================================================"
echo "Step 1: Installing Python dependencies"
echo "========================================================================"
echo ""

pip3 install python-dateutil

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install Python dependencies${NC}"
    exit 1
fi

echo ""

# Step 2: Configure email settings
echo "========================================================================"
echo "Step 2: Configure Email Settings"
echo "========================================================================"
echo ""
echo "The system needs email credentials to send monthly reports."
echo "These will be stored in your ~/.bashrc file as environment variables."
echo ""

read -p "Enter your email address (SMTP_USER): " smtp_user
read -sp "Enter your email password or app password (SMTP_PASS): " smtp_pass
echo ""
read -p "Enter recipient email address (NOTIFY_TO): " notify_to

# Add environment variables to ~/.bashrc if not already present
if ! grep -q "SMTP_USER" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# YOLOv8 Inventory System - Email Configuration" >> ~/.bashrc
    echo "export SMTP_HOST=\"smtp.gmail.com\"" >> ~/.bashrc
    echo "export SMTP_PORT=\"465\"" >> ~/.bashrc
    echo "export SMTP_USER=\"$smtp_user\"" >> ~/.bashrc
    echo "export SMTP_PASS=\"$smtp_pass\"" >> ~/.bashrc
    echo "export NOTIFY_FROM=\"$smtp_user\"" >> ~/.bashrc
    echo "export NOTIFY_TO=\"$notify_to\"" >> ~/.bashrc
    
    echo -e "${GREEN}✓ Email configuration added to ~/.bashrc${NC}"
else
    echo -e "${YELLOW}⚠ Email configuration already exists in ~/.bashrc${NC}"
    echo "Please update it manually if needed."
fi

# Source the bashrc to load the new variables
source ~/.bashrc

echo ""

# Step 3: Set up cron job
echo "========================================================================"
echo "Step 3: Configure Automatic Monthly Reports"
echo "========================================================================"
echo ""
echo "The system will generate and email a report at 2:00 AM on the 1st of"
echo "each month."
echo ""

# Create the cron command
CRON_CMD="0 2 1 * * cd $SCRIPT_DIR && /usr/bin/python3 $SCRIPT_DIR/report_generator.py >> $SCRIPT_DIR/report_cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "report_generator.py"; then
    echo -e "${YELLOW}⚠ Cron job already exists${NC}"
    echo "Existing cron jobs for report_generator.py:"
    crontab -l | grep "report_generator.py"
    echo ""
    read -p "Do you want to replace it? (y/n): " replace_cron
    
    if [ "$replace_cron" = "y" ]; then
        # Remove old cron job and add new one
        (crontab -l 2>/dev/null | grep -v "report_generator.py"; echo "$CRON_CMD") | crontab -
        echo -e "${GREEN}✓ Cron job updated${NC}"
    else
        echo "Keeping existing cron job"
    fi
else
    # Add new cron job
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo -e "${GREEN}✓ Cron job added successfully${NC}"
fi

echo ""
echo "Current cron schedule:"
crontab -l | grep "report_generator.py"

echo ""

# Step 4: Test the setup
echo "========================================================================"
echo "Step 4: Test the Setup"
echo "========================================================================"
echo ""
read -p "Do you want to run a test report now? (y/n): " run_test

if [ "$run_test" = "y" ]; then
    echo ""
    echo "Running test report..."
    echo ""
    
    cd "$SCRIPT_DIR"
    python3 report_generator.py --month $(date +%Y-%m)
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Test report completed${NC}"
    else
        echo ""
        echo -e "${RED}✗ Test report failed${NC}"
        echo "Please check the logs for errors."
    fi
fi

echo ""
echo "========================================================================"
echo "  Setup Complete!"
echo "========================================================================"
echo ""
echo "Summary:"
echo "  • Python dependencies installed"
echo "  • Email configuration saved to ~/.bashrc"
echo "  • Cron job scheduled for monthly reports"
echo ""
echo "Monthly reports will be generated at 2:00 AM on the 1st of each month."
echo ""
echo "To manually generate a report:"
echo "  cd $SCRIPT_DIR"
echo "  python3 report_generator.py"
echo ""
echo "To view scheduled cron jobs:"
echo "  crontab -l"
echo ""
echo "To view report generation logs:"
echo "  cat $SCRIPT_DIR/report_cron.log"
echo "  cat $SCRIPT_DIR/report_generator.log"
echo ""
echo "========================================================================"

