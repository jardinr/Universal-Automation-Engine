
import json
import importlib
import os
import requests
import time

class Orchestrator:
    def __init__(self, company_profile_path, workflow_config_path):
        self.company_profile_path = company_profile_path
        self.workflow_config_path = workflow_config_path
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
            if tool == "Parseur":
                self.adapters[adapter_id] = ParseurAdapter(source["parser_config"])
            elif tool == "AIEmailParser":
                self.adapters[adapter_id] = importlib.import_module("src.adapters.data_ingestion.ai_email_parser").AIEmailParser(source["parser_config"])
            elif tool == "SimulatedEmailParser":
                self.adapters[adapter_id] = importlib.import_module("src.adapters.data_ingestion.email_parser").EmailParser(source["parser_config"])

        # Initialize AI Processing Adapters
        for ai_model_config in self.company_profile.get("ai_models", []):
            adapter_id = ai_model_config["id"]
            provider = ai_model_config["provider"]
            if provider == "OpenAI":
                self.adapters[adapter_id] = importlib.import_module("src.adapters.ai_processing.openai_gpt").OpenAIGPTAdapter(ai_model_config)

        # Initialize Action Integration Adapters
        for platform_config in self.company_profile.get("action_platforms", []):
            adapter_id = platform_config["id"]
            provider = platform_config["provider"]
            if provider == "HubSpot":
                self.adapters[adapter_id] = importlib.import_module("src.adapters.action_integration.hubspot_crm").HubSpotCRM(platform_config)

    def execute_workflow(self, raw_input_data=None, document_id=None):
        context = {}

        trigger_config = self.workflow_config["trigger"]
        source_adapter_id = trigger_config["source_adapter"]
        source_adapter = self.adapters.get(source_adapter_id)

        if not source_adapter:
            raise ValueError(f"Source adapter {source_adapter_id} not found.")

        if trigger_config["event"] == "new_email":
            if isinstance(source_adapter, ParseurAdapter):
                if document_id:
                    parsed_data = source_adapter.get_document_data(document_id)
                    context.update(parsed_data)
                    context["raw_input"] = parsed_data.get("original_email_content", "")
                else:
                    raise ValueError("document_id must be provided for ParseurAdapter.")
            elif isinstance(source_adapter, importlib.import_module("src.adapters.data_ingestion.ai_email_parser").AIEmailParser):
                if raw_input_data:
                    company_profile_dir = os.path.dirname(self.company_profile_path)
                    parsed_data = source_adapter.parse_email(raw_input_data, company_profile_dir)
                    context.update(parsed_data)
                    context["raw_input"] = raw_input_data
                else:
                    raise ValueError("raw_input_data must be provided for AIEmailParser.")
            elif isinstance(source_adapter, importlib.import_module("src.adapters.data_ingestion.email_parser").EmailParser):
                if raw_input_data:
                    parsed_data = source_adapter.parse_email(raw_input_data)
                    context.update(parsed_data)
                    context["raw_input"] = raw_input_data
                else:
                    raise ValueError("raw_input_data must be provided for SimulatedEmailParser.")
            else:
                raise ValueError(f"Unsupported data source adapter type: {type(source_adapter)}")
        else:
            print(f"Unsupported trigger event: {trigger_config["event"]}")
            return

        for step in self.workflow_config["steps"]:
            step_type = step["type"]
            step_id = step["step_id"]

            if step_type == "data_extraction":
                pass # Handled by the initial parsing
            elif step_type == "ai_processing":
                ai_model_id = step["ai_model"]
                ai_adapter = self.adapters.get(ai_model_id)
                if not ai_adapter:
                    raise ValueError(f"AI adapter {ai_model_id} not found.")

                input_for_ai = {field: context.get(field) for field in step["input_fields"]}
                
                prompt_template_relative_path = step.get("prompt_template_file")
                if not prompt_template_relative_path:
                    raise ValueError(f"Prompt template file not specified for AI processing step {step_id}")
                
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
                    rendered_value = value_template
                    for k, v in context.items():
                        rendered_value = rendered_value.replace(f"{{{{{k}}}}", str(v))
                    action_data[key] = rendered_value

                if action_name == "create_deal":
                    action_adapter.create_deal(action_data)

        print("Workflow executed successfully.")
        return context

class ParseurAdapter:
    def __init__(self, config):
        self.config = config
        self.api_key = os.getenv("PARSEUR_API_KEY")
        if not self.api_key:
            raise ValueError("PARSEUR_API_KEY environment variable not set.")
        self.mailbox_id = config.get("mailbox_id")
        if not self.mailbox_id:
            raise ValueError("Parseur mailbox_id not specified in config.")
        self.base_url = "https://api.parseur.com/api/v1"

    def get_new_documents(self, limit=10):
        headers = {
            "Authorization": f"Token {self.api_key}"
        }
        params = {
            "mailbox_id": self.mailbox_id,
            "read": False,
            "limit": limit
        }
        try:
            response = requests.get(f"{self.base_url}/documents", headers=headers, params=params)
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching new documents from Parseur: {e}")
            return []

    def get_document_data(self, document_id):
        headers = {
            "Authorization": f"Token {self.api_key}"
        }
        try:
            response = requests.get(f"{self.base_url}/documents/{document_id}", headers=headers)
            response.raise_for_status()
            doc_data = response.json()["data"]
            
            self._mark_document_as_read(document_id)

            parsed_fields = {"original_email_content": doc_data.get("text_content", "")}
            for field in doc_data.get("fields", []):
                parsed_fields[field["name"]] = field["value"]
            return parsed_fields
        except requests.exceptions.RequestException as e:
            print(f"Error fetching document {document_id} from Parseur: {e}")
            return {}

    def _mark_document_as_read(self, document_id):
        headers = {
            "Authorization": f"Token {self.api_key}"
        }
        payload = {"read": True}
        try:
            requests.patch(f"{self.base_url}/documents/{document_id}", headers=headers, json=payload)
        except requests.exceptions.RequestException as e:
            print(f"Error marking document {document_id} as read: {e}")

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
        2. Summarize the client\'s request in one sentence.
        3. Determine the urgency as `High`, `Medium`, or `Low`.

        Provide your output in JSON format only.
        """)

    # Create dummy prompt for AI Email Parser
    with open("/home/ubuntu/universal_automation_engine/config/beluga_hospitality/ai_prompts/email_extraction_prompt.txt", "w") as f:
        f.write("""
        Extract the following information from the email below and return it as a JSON object. If a field is not found, use \"N/A\".
        Fields to extract: client_name, client_email, subject, event_type, guest_count, inquiry_details.

        Email Content: {raw_email_content}

        Example JSON output:
        {
            \"client_name\": \"John Doe\",
            \"client_email\": \"john.doe@example.com\",
            \"subject\": \"Inquiry about F1 VIP Package\",
            \"event_type\": \"F1 VIP Package\",
            \"guest_count\": \"10\",
            \"inquiry_details\": \"Details on pricing and availability.\"
        }
        """)

    # Create dummy mapping files for testing
    with open("/home/ubuntu/universal_automation_engine/config/beluga_hospitality/hubspot_mappings.json", "w") as f:
        f.write("{}")
    with open("/home/ubuntu/universal_automation_engine/config/beluga_hospitality/trello_list_mappings.json", "w") as f:
        f.write("{}")

    # Set dummy environment variables for testing
    os.environ["HUBSPOT_API_KEY"] = "dummy_hubspot_api_key"
    os.environ["OPENAI_API_KEY"] = "dummy_openai_api_key"
    os.environ["PARSEUR_API_KEY"] = "dummy_parseur_api_key"

    # --- Test with simulated email using AIEmailParser ---
    print("\n--- Testing with AIEmailParser (Simulated Email) ---")
    # Temporarily modify company_profile for AIEmailParser test
    temp_company_profile_path_ai = "/tmp/temp_company_profile_ai.json"
    with open("/home/ubuntu/universal_automation_engine/config/beluga_hospitality/company_profile.json", "r") as f:
        temp_profile_ai = json.load(f)
    temp_profile_ai["data_sources"][0]["provider"] = "AIEmailParser"
    temp_profile_ai["data_sources"][0]["parser_config"]["tool"] = "AIEmailParser"
    temp_profile_ai["data_sources"][0]["parser_config"]["prompt_template_file"] = "ai_prompts/email_extraction_prompt.txt"
    with open(temp_company_profile_path_ai, "w") as f:
        json.dump(temp_profile_ai, f, indent=2)

    orchestrator_ai_simulated = Orchestrator(
        temp_company_profile_path_ai,
        "/home/ubuntu/universal_automation_engine/config/beluga_hospitality/workflow_config.json"
    )
    test_email_content_ai = "Subject: Inquiry about F1 VIP Package\nFrom: john.doe@example.com\n\nDear Beluga Team,\n\nI am interested in booking the F1 VIP package for the upcoming season. Could you please provide details on pricing and availability for 10 guests?\n\nBest regards,\nJohn Doe"
    result_context_ai_simulated = orchestrator_ai_simulated.execute_workflow(raw_input_data=test_email_content_ai)
    print(json.dumps(result_context_ai_simulated, indent=2))
    if os.path.exists(temp_company_profile_path_ai):
        os.remove(temp_company_profile_path_ai)

    # --- Test with live Parseur (requires actual documents in Parseur mailbox) ---
    print("\n--- Testing with Live Parseur (Requires actual Parseur documents) ---")
    temp_company_profile_path_parseur = "/tmp/temp_company_profile_parseur.json"
    with open("/home/ubuntu/universal_automation_engine/config/beluga_hospitality/company_profile.json", "r") as f:
        temp_profile_parseur = json.load(f)
    temp_profile_parseur["data_sources"][0]["provider"] = "Parseur"
    temp_profile_parseur["data_sources"][0]["parser_config"]["tool"] = "Parseur"
    temp_profile_parseur["data_sources"][0]["parser_config"]["mailbox_id"] = "YOUR_PARSEUR_MAILBOX_ID" # <<< IMPORTANT: Replace with your actual Parseur Mailbox ID
    with open(temp_company_profile_path_parseur, "w") as f:
        json.dump(temp_profile_parseur, f, indent=2)

    try:
        orchestrator_live = Orchestrator(
            temp_company_profile_path_parseur,
            "/home/ubuntu/universal_automation_engine/config/beluga_hospitality/workflow_config.json"
        )
        print("Attempting to fetch new documents from Parseur...")
        new_documents = orchestrator_live.adapters["beluga_email_inbox"].get_new_documents(limit=1)
        if new_documents:
            print(f"Found {len(new_documents)} new document(s).")
            for doc in new_documents:
                print(f"Processing document ID: {doc["id"]}")
                result_context_live = orchestrator_live.execute_workflow(document_id=doc["id"])
                print(json.dumps(result_context_live, indent=2))
        else:
            print("No new documents found in Parseur mailbox.")
    except Exception as e:
        print(f"Error during live Parseur test: {e}")
    finally:
        if os.path.exists(temp_company_profile_path_parseur):
            os.remove(temp_company_profile_path_parseur)

