import imaplib
import email
import os

class OutlookIMAP:
    def __init__(self, imap_server, imap_port, imap_username, imap_password, imap_mailbox='INBOX', imap_folder='UAE-Processing'):
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.imap_username = imap_username
        self.imap_password = imap_password
        self.imap_mailbox = imap_mailbox
        self.imap_folder = imap_folder
        self.mail = None

    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.imap_username, self.imap_password)
            print(f"Successfully connected to IMAP server: {self.imap_server}")
            return True
        except Exception as e:
            print(f"Error connecting to IMAP server: {e}")
            self.mail = None
            return False

    def disconnect(self):
        if self.mail:
            try:
                self.mail.logout()
                print("Disconnected from IMAP server.")
            except Exception as e:
                print(f"Error disconnecting from IMAP server: {e}")

    def fetch_new_emails(self):
        if not self.mail:
            if not self.connect():
                return []

        emails = []
        try:
            # Select the specified folder
            status, messages = self.mail.select(self.imap_folder, readonly=False)
            if status != 'OK':
                print(f"Error selecting IMAP folder '{self.imap_folder}': {messages}")
                # Attempt to create the folder if it doesn't exist
                if b'[TRYCREATE]' in messages[0]:
                    print(f"Attempting to create IMAP folder '{self.imap_folder}'...")
                    self.mail.create(self.imap_folder)
                    status, messages = self.mail.select(self.imap_folder, readonly=False)
                    if status != 'OK':
                        print(f"Failed to create and select IMAP folder '{self.imap_folder}': {messages}")
                        return []
                else:
                    return []

            # Search for unread emails
            status, email_ids = self.mail.search(None, 'UNSEEN')
            if status != 'OK':
                print(f"Error searching for unread emails: {email_ids}")
                return []

            for email_id in email_ids[0].split():
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    print(f"Error fetching email {email_id}: {msg_data}")
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                emails.append(msg.as_string())
                
                # Mark email as read after fetching
                self.mail.store(email_id, '+FLAGS', '\Seen')
                print(f"Fetched and marked email {email_id} as seen.")

        except Exception as e:
            print(f"Error fetching emails: {e}")
        finally:
            self.disconnect() # Disconnect after each fetch to avoid stale connections
        return emails

if __name__ == '__main__':
    # Example usage (for testing the adapter directly)
    # Ensure these environment variables are set for local testing
    IMAP_SERVER = os.getenv("IMAP_SERVER", "outlook.office365.com") # Example for Outlook
    IMAP_PORT = os.getenv("IMAP_PORT", "993")
    IMAP_USERNAME = os.getenv("IMAP_USERNAME")
    IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")
    IMAP_FOLDER = os.getenv("IMAP_FOLDER", "UAE-Processing")

    if not all([IMAP_USERNAME, IMAP_PASSWORD]):
        print("Please set IMAP_USERNAME and IMAP_PASSWORD environment variables for testing.")
    else:
        imap_client = OutlookIMAP(IMAP_SERVER, IMAP_PORT, IMAP_USERNAME, IMAP_PASSWORD, imap_folder=IMAP_FOLDER)
        new_emails = imap_client.fetch_new_emails()
        if new_emails:
            print(f"Found {len(new_emails)} new emails.")
            for i, mail_content in enumerate(new_emails):
                print(f"--- Email {i+1} ---")
                print(mail_content[:500]) # Print first 500 chars
        else:
            print("No new emails found.")
