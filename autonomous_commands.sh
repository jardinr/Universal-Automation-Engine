#!/bin/bash

# This script sets up environment variables and runs the polling agent for the Universal Automation Engine.
# IMPORTANT: For production, manage these API keys securely (e.g., Kubernetes secrets, AWS Secrets Manager, etc.)

# API keys should be set as environment variables in the execution environment.
# Example: export OPENAI_API_KEY="your_openai_key"
# Example: export HUBSPOT_API_KEY="your_hubspot_key"

# IMAP credentials for Outlook email ingestion
# Example: export IMAP_SERVER="outlook.office365.com"
# Example: export IMAP_PORT="993"
# Example: export IMAP_USERNAME="your_outlook_email@example.com"
# Example: export IMAP_PASSWORD="your_outlook_password"
# Example: export IMAP_FOLDER="UAE-Processing" # Folder to monitor for new emails

# Navigate to the project directory
cd /home/ubuntu/universal_automation_engine

# Run the polling agent
python3 polling_agent.py
