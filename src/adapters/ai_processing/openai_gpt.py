
import openai
import os

class OpenAIGPTAdapter:
    def __init__(self, config):
        self.config = config
        openai.api_key = os.getenv(config.get("api_key_env_var", "OPENAI_API_KEY"))

    def process_text(self, text_data, prompt_template_file):
        with open(prompt_template_file, 'r') as f:
            prompt_template = f.read()

        prompt = prompt_template.format(**text_data)

        response = openai.chat.completions.create(
            model=self.config.get("model_id", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content
