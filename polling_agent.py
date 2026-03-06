import os
import time
import json
from src.core.orchestrator import Orchestrator

# --- Configuration from Environment Variables ---
# These should be set securely in your deployment environment.
# For local testing, you can set them in autonomous_commands.sh

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PARSEUR_API_KEY = os.getenv("PARSEUR_API_KEY") # Still needed for Parseur if not using IMAP

# IMAP Listener Configuration (for custom email ingestion)
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = os.getenv("IMAP_PORT", "993")
IMAP_USERNAME = os.getenv("IMAP_USERNAME")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")
IMAP_MAILBOX = os.getenv("IMAP_MAILBOX", "INBOX")
IMAP_FOLDER = os.getenv("IMAP_FOLDER", "UAE-Processing") # Folder to monitor for new emails

COMPANY_PROFILE_PATH = os.getenv("COMPANY_PROFILE_PATH", "config/beluga_hospitality/company_profile.json")
WORKFLOW_CONFIG_PATH = os.getenv("WORKFLOW_CONFIG_PATH", "config/beluga_hospitality/workflow_config.json")
POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL_SECONDS", "300")) # Default to 5 minutes

def main():
    print("Starting Universal Automation Engine Polling Agent...")

    # Initialize Orchestrator with API keys and configuration paths
    orchestrator = Orchestrator(
        company_profile_path=COMPANY_PROFILE_PATH,
        workflow_config_path=WORKFLOW_CONFIG_PATH,
        openai_api_key=OPENAI_API_KEY,
        hubspot_api_key=HUBSPOT_API_KEY,
        parseur_api_key=PARSEUR_API_KEY # Pass if Parseur is still used
    )

    while True:
        print(f"Polling for new emails... (Next poll in {POLLING_INTERVAL_SECONDS} seconds)")
        try:
            # --- Simulate Email Ingestion (Replace with actual IMAP listener or Parseur API call) ---
            # For now, this is a placeholder. The IMAP listener development is the next step.
            # In a real scenario, this would fetch new emails from IMAP or Parseur.
            # For testing, we can simulate an email by reading from a test file or a mock source.
            
            # Example of a simulated email (for testing the full pipeline without IMAP/Parseur yet)
            # In a real scenario, this would come from the IMAP listener or Parseur webhook
            simulated_email_content = """
            Subject: New Event Inquiry - Corporate Gala
            From: client@example.com
            To: events@belugahospitality.co.za

            Dear Beluga Hospitality Team,

            We are interested in booking a corporate gala for approximately 150 guests on October 26, 2026.
            Our budget is around R50,000. Please let us know your availability and package options.

            Best regards,
            John Doe
            Client Solutions
            """
            
            # Process the simulated email
            print("Simulating new email for processing...")
            orchestrator.process_email(simulated_email_content)
            print("Simulated email processed.")

        except Exception as e:
            print(f"An error occurred during polling: {e}")

        time.sleep(POLLING_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
