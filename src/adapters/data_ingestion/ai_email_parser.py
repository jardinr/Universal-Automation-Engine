
import os
import json
from openai import OpenAI

class AIEmailParser:
    def __init__(self, config=None):
        self.config = config if config is not None else {}
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set for AIEmailParser.")
        self.client = OpenAI(api_key=self.api_key)
        self.model_id = self.config.get("model_id", "gpt-4o-mini")
        self.prompt_template_file = self.config.get("prompt_template_file")

    def _load_prompt_template(self, prompt_template_file):
        if not prompt_template_file:
            raise ValueError("Prompt template file not specified for AIEmailParser.")
        if not os.path.exists(prompt_template_file):
            raise FileNotFoundError(f"Prompt template file not found: {prompt_template_file}")
        with open(prompt_template_file, "r") as f:
            return f.read()

    def parse_email(self, raw_email_content, company_profile_dir):
        if not self.prompt_template_file:
            raise ValueError("Prompt template file not configured for AIEmailParser.")

        # Construct absolute path for prompt template
        absolute_prompt_template_file = os.path.join(company_profile_dir, self.prompt_template_file)
        prompt_template = self._load_prompt_template(absolute_prompt_template_file)

        # Prepare input for the AI model
        input_for_ai = {"raw_email_content": raw_email_content}
        formatted_prompt = prompt_template.format(**input_for_ai)

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are an expert email parser. Extract structured data from the email content and output it as a JSON object. Ensure all extracted fields are present, using \'N/A\' if a field is not found."},
                    {"role": "user", "content": formatted_prompt}
                ],
                response_format={"type": "json_object"}
            )
            ai_output_str = response.choices[0].message.content
            return json.loads(ai_output_str)
        except Exception as e:
            print(f"Error calling OpenAI API for email parsing: {e}")
            return {"error": str(e), "raw_email_content": raw_email_content}
