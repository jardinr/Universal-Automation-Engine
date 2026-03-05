#!/bin/bash

# This script sets up environment variables and runs the Universal Automation Engine polling agent.
# It is designed to be run autonomously, for example, via a cron job or a systemd service.

# --- Set Environment Variables (Replace with your actual keys) ---
# For production, consider using a secure secrets management system (e.g., AWS Secrets Manager, Azure Key Vault).
# These environment variables MUST be set in the environment where this script is executed.
# Example:
# export HUBSPOT_API_KEY="your_hubspot_api_key_here"
# export OPENAI_API_KEY="your_openai_api_key_here"
# export PARSEUR_API_KEY="your_parseur_api_key_here"

# --- Optional: Configure paths and polling interval ---
# export COMPANY_PROFILE_PATH="/home/ubuntu/universal_automation_engine/config/beluga_hospitality/company_profile.json"
# export WORKFLOW_CONFIG_PATH="/home/ubuntu/universal_automation_engine/config/beluga_hospitality/workflow_config.json"
# export POLLING_INTERVAL_SECONDS=300 # Poll every 5 minutes

# --- Run the Autonomous Polling Agent ---
# This script will continuously check for new documents and process them.
echo "Starting Universal Automation Engine polling agent..."
python3 /home/ubuntu/universal_automation_engine/polling_agent.py

echo "Universal Automation Engine polling agent stopped."
