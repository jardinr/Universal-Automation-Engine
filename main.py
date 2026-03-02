
import os
from src.core.orchestrator import Orchestrator

def main():
    # --- Setup for demonstration ---
    # Create dummy prompt file for testing
    os.makedirs("/home/ubuntu/universal_automation_engine/config/beluga_hospitality/ai_prompts", exist_ok=True)
    with open("/home/ubuntu/universal_automation_engine/config/beluga_hospitality/ai_prompts/categorization_prompt.txt", "w") as f:
        f.write("""
        You are an expert hospitality assistant for Beluga Hospitality. Based on the following email content, categorize the inquiry and extract key details.
        Client Name: {extracted_client_name}
        Email Body: {body}

        Your Task:
        1. Categorize the inquiry into one of the following types: `New Booking Inquiry`, `Existing Booking Update`, `Bespoke/Custom Request`, or `General/Support Question`.
        2. Summarize the client's request in one sentence.
        3. Determine the urgency as `High`, `Medium`, or `Low`.

        Provide your output in JSON format only.
        """)

    # Create dummy mapping files for testing
    with open("/home/ubuntu/universal_automation_engine/config/beluga_hospitality/hubspot_mappings.json", "w") as f:
        f.write("{}")
    with open("/home/ubuntu/universal_automation_engine/config/beluga_hospitality/trello_list_mappings.json", "w") as f:
        f.write("{}")

    # Set dummy environment variable for HubSpot API key for testing
    os.environ["HUBSPOT_API_KEY"] = "dummy_hubspot_api_key"
    # --- End Setup ---

    print("Initializing Orchestrator for Beluga Hospitality...")
    orchestrator = Orchestrator(
        "/home/ubuntu/universal_automation_engine/config/beluga_hospitality/company_profile.json",
        "/home/ubuntu/universal_automation_engine/config/beluga_hospitality/workflow_config.json"
    )
    print("Orchestrator initialized.")
    
    # Simulate an incoming email
    test_email_content = "Subject: Inquiry about F1 VIP Package\n\nDear Beluga Team,\n\nI am interested in booking the F1 VIP package for the upcoming season. Could you please provide details on pricing and availability for 10 guests?\n\nBest regards,\nJohn Doe"

    print("Executing workflow with simulated email...")
    result_context = orchestrator.execute_workflow(test_email_content)
    print("Workflow execution complete. Result context:")
    print(result_context)

if __name__ == "__main__":
    main()
