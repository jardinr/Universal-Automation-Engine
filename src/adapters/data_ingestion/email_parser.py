
import re

class EmailParser:
    def __init__(self, config=None):
        self.config = config if config is not None else {}

    def parse_email(self, raw_email_content):
        # Simple regex to extract Subject and Body
        subject_match = re.search(r"Subject: (.*)\n", raw_email_content, re.IGNORECASE)
        body_match = re.search(r"\n\n(.*)", raw_email_content, re.DOTALL)

        subject = subject_match.group(1).strip() if subject_match else "No Subject"
        body = body_match.group(1).strip() if body_match else raw_email_content.strip()

        # Extract client name from body (very basic, can be improved with more advanced NLP)
        client_name_match = re.search(r"Best regards,\n(.*)", body, re.IGNORECASE)
        extracted_client_name = client_name_match.group(1).strip() if client_name_match else "Unknown Client"

        return {
            "subject": subject,
            "body": body,
            "extracted_client_name": extracted_client_name
        }
