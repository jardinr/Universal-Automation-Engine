
import json
import importlib
import os

class Orchestrator:
    def __init__(self, company_profile_path, workflow_config_path):
        self.company_profile_path = company_profile_path # Store the path
        self.workflow_config_path = workflow_config_path # Store the path
        self.company_profile = self._load_config(company_profile_path)
        self.workflow_config = self._load_config(workflow_config_path)
        self.adapters = {}
        self._initialize_adapters(os.path.dirname(company_profile_path))

    def _load_config(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def _initialize_adapters(self, config_base_path):
        # Initialize Data Ingestion Adapters
        for source in self.company_profile.get("data_sources", []):
            adapter_id = source["id"]
            tool = source["parser_config"].get("tool")
            if tool == "Parseur" or tool == "SimulatedEmailParser": # Added SimulatedEmailParser
                self.adapters[adapter_id] = importlib.import_module("src.adapters.data_ingestion.email_parser").EmailParser(source["parser_config"])
            # Add other data ingestion tools here

        # Initialize AI Processing Adapters
        for ai_model_config in self.company_profile.get("ai_models", []):
            adapter_id = ai_model_config["id"]
            provider = ai_model_config["provider"]
            if provider == "OpenAI":
                self.adapters[adapter_id] = importlib.import_module("src.adapters.ai_processing.openai_gpt").OpenAIGPTAdapter(ai_model_config)
            # Add other AI providers here

        # Initialize Action Integration Adapters
        for platform_config in self.company_profile.get("action_platforms", []):
            adapter_id = platform_config["id"]
            provider = platform_config["provider"]
            if provider == "HubSpot":
                self.adapters[adapter_id] = importlib.import_module("src.adapters.action_integration.hubspot_crm").HubSpotCRM(platform_config)
            # Add other action platforms here

    def execute_workflow(self, raw_input_data):
        context = {"raw_input": raw_input_data}

        # Trigger step (e.g., receive email)
        trigger_config = self.workflow_config["trigger"]
        source_adapter_id = trigger_config["source_adapter"]
        source_adapter = self.adapters.get(source_adapter_id)

        if not source_adapter:
            raise ValueError(f"Source adapter {source_adapter_id} not found.")

        # Simulate data ingestion
        if trigger_config["event"] == "new_email":
            parsed_data = source_adapter.parse_email(raw_input_data)
            context.update(parsed_data)
        else:
            print(f"Unsupported trigger event: {trigger_config["event"]}")
            return

        for step in self.workflow_config["steps"]:
            step_type = step["type"]
            step_id = step["step_id"]

            if step_type == "data_extraction":
                # This step is already handled by the initial parse_email for now
                # In a real scenario, this might call a specific parser module
                pass
            elif step_type == "ai_processing":
                ai_model_id = step["ai_model"]
                ai_adapter = self.adapters.get(ai_model_id)
                if not ai_adapter:
                    raise ValueError(f"AI adapter {ai_model_id} not found.")

                input_for_ai = {field: context.get(field) for field in step["input_fields"]}
                
                # Get prompt template path from workflow config, relative to company_profile.json
                prompt_template_relative_path = step.get("prompt_template_file")
                if not prompt_template_relative_path:
                    raise ValueError(f"Prompt template file not specified for AI processing step {step_id}")
                
                # Construct absolute path for prompt template
                company_profile_dir = os.path.dirname(self.company_profile_path)
                prompt_template_file = os.path.join(company_profile_dir, prompt_template_relative_path)

                ai_output_str = ai_adapter.process_text(input_for_ai, prompt_template_file)
                
                try:
                    ai_output = json.loads(ai_output_str)
                    for out_field in step["output_fields"]:
                        if out_field in ai_output:
                            context[out_field] = ai_output[out_field]
                except json.JSONDecodeError:
                    print(f"AI output was not valid JSON: {ai_output_str}")
                    context["ai_raw_output"] = ai_output_str

            elif step_type == "action_integration":
                platform_adapter_id = step["platform_adapter"]
                action_adapter = self.adapters.get(platform_adapter_id)
                if not action_adapter:
                    raise ValueError(f"Action adapter {platform_adapter_id} not found.")

                action_name = step["action"]
                mapping = step["mapping"]
                action_data = {}
                for key, value_template in mapping.items():
                    # Simple template rendering for now
                    rendered_value = value_template
                    for k, v in context.items():
                        rendered_value = rendered_value.replace(f"{{{{{k}}}}", str(v))
                    action_data[key] = rendered_value

                if action_name == "create_deal":
                    action_adapter.create_deal(action_data)
                # Add other actions here

        print("Workflow executed successfully.")
        return context

# Example Usage (for testing within the sandbox)
if __name__ == "__main__":
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

    orchestrator = Orchestrator(
        "/home/ubuntu/universal_automation_engine/config/beluga_hospitality/company_profile.json",
        "/home/ubuntu/universal_automation_engine/config/beluga_hospitality/workflow_config.json"
    )
    
    # Simulate an incoming email
    test_email_content = "Subject: Inquiry about F1 VIP Package\n\nDear Beluga Team,\n\nI am interested in booking the F1 VIP package for the upcoming season. Could you please provide details on pricing and availability for 10 guests?\n\nBest regards,\nJohn Doe"

    # Set dummy environment variable for HubSpot API key for testing
    os.environ["HUBSPOT_API_KEY"] = "dummy_hubspot_api_key"

    orchestrator.execute_workflow(test_email_content)
