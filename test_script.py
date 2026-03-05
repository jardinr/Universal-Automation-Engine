
import os
import json
from src.core.orchestrator import Orchestrator

def run_test(company_profile_path, workflow_config_path, test_email_content):
    print(f"\n--- Running Test for: {company_profile_path.split('/')[-2]} ---")
    print("Simulating incoming email:")
    print(test_email_content)

    # Set dummy environment variables for testing purposes
    os.environ["HUBSPOT_API_KEY"] = "dummy_hubspot_api_key"
    os.environ["OPENAI_API_KEY"] = "dummy_openai_api_key"

    # Create dummy prompt file for testing if it doesn't exist
    # This ensures the orchestrator can find the prompt template during local testing
    company_config_dir = os.path.dirname(company_profile_path)
    ai_prompts_dir = os.path.join(company_config_dir, "ai_prompts")
    os.makedirs(ai_prompts_dir, exist_ok=True)
    prompt_template_file = os.path.join(ai_prompts_dir, "categorization_prompt.txt")
    if not os.path.exists(prompt_template_file):
        with open(prompt_template_file, "w") as f:
            f.write("""
            You are an expert assistant. Based on the following email content, categorize the inquiry and extract key details.
            Client Name: {extracted_client_name}
            Email Body: {body}

            Your Task:
            1. Categorize the inquiry into one of the following types: `New Booking Inquiry`, `Existing Booking Update`, `Bespoke/Custom Request`, or `General/Support Question`.
            2. Summarize the client's request in one sentence.
            3. Determine the urgency as `High`, `Medium`, or `Low`.

            Provide your output in JSON format only.
            """)

    # Create dummy mapping files for testing if they don't exist
    if not os.path.exists(os.path.join(company_config_dir, "hubspot_mappings.json")):
        with open(os.path.join(company_config_dir, "hubspot_mappings.json"), "w") as f:
            f.write("{}")
    if not os.path.exists(os.path.join(company_config_dir, "trello_list_mappings.json")):
        with open(os.path.join(company_config_dir, "trello_list_mappings.json"), "w") as f:
            f.write("{}")

    try:
        orchestrator = Orchestrator(company_profile_path, workflow_config_path)
        result_context = orchestrator.execute_workflow(test_email_content)
        print("\nWorkflow executed successfully. Result context:")
        print(json.dumps(result_context, indent=2))
    except Exception as e:
        print(f"\nError during workflow execution: {e}")

if __name__ == "__main__":
    # Example for Beluga Hospitality
    beluga_company_profile = "/home/ubuntu/universal_automation_engine/config/beluga_hospitality/company_profile.json"
    beluga_workflow_config = "/home/ubuntu/universal_automation_engine/config/beluga_hospitality/workflow_config.json"

    test_email_1 = """
Subject: Inquiry about F1 VIP Package

Dear Beluga Team,

I am interested in booking the F1 VIP package for the upcoming season. Could you please provide details on pricing and availability for 10 guests?

Best regards,
John Doe
"""

    test_email_2 = """
Subject: Urgent - Change of Date for Wedding Event

Hi team,

My wedding event, currently booked for June 15th, needs to be moved to July 20th due to unforeseen circumstances. Please let me know if this is possible.

Thanks,
Jane Smith
"""

    run_test(beluga_company_profile, beluga_workflow_config, test_email_1)
    run_test(beluga_company_profile, beluga_workflow_config, test_email_2)

    # You can add more test cases or company profiles here
