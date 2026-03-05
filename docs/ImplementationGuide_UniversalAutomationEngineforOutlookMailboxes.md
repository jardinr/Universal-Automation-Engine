# Implementation Guide: Universal Automation Engine for Outlook Mailboxes

This guide provides a step-by-step process for integrating your Outlook mailboxes with the Universal Automation Engine. The goal is to automate the extraction, categorization, and actioning of emails, significantly reducing manual effort and improving response times.

## Prerequisites

Before you begin, ensure you have:

*   An active **Outlook** email account (or Microsoft 365 account).
*   Accounts with the chosen tools: **Parseur** (or similar email parser), **Zapier** (or Make.com), **OpenAI** (for API access), and your preferred **Action Platform** (e.g., HubSpot CRM, Trello).
*   Access to the `Universal Automation Engine` repository and its configuration files.

## Step 1: Prepare Your Outlook Mailbox

This step ensures that relevant emails are automatically directed to the automation pipeline.

1.  **Create a Dedicated Folder/Label:** In your Outlook client, create a new folder (e.g., "`Automation Inbox`" or "`To Process by AI`"). This will be the designated folder for emails that need to be processed by the engine.
2.  **Set Up an Inbox Rule for Forwarding:**
    *   Go to **File > Manage Rules & Alerts > New Rule...**
    *   Select "`Apply rule on messages I receive`" and click **Next**.
    *   **Conditions:** Define criteria for emails you want to automate. For example:
        *   "`with specific words in the subject or body`" (e.g., "Inquiry", "Booking Request")
        *   "`sent to specific people or public group`" (e.g., your general inquiry email address like `info@yourcompany.com`)
        *   "`from people or public group`" (e.g., if you only want to process emails from external clients).
    *   Click **Next**.
    *   **Actions:** Select "`forward it to people or public group`". In the lower box, click on "`people or public group`" and enter the unique email address provided by your **Parseur mailbox** (e.g., `your-mailbox-id@parseur.com`).
    *   **(Optional) Move to Folder:** You can also add an action to "`move it to the specified folder`" (e.g., the "`Automation Inbox`" folder you created) to keep your main inbox clean.
    *   Click **Next**, add any exceptions, and then **Finish** to activate the rule.

    > **Note:** This rule ensures that a copy of every relevant email is sent to Parseur for processing, while the original remains in your Outlook for archiving or manual review if needed.

## Step 2: Configure Your Email Parser (e.g., Parseur)

This step teaches the engine how to extract specific data points from your emails.

1.  **Create a Parseur Mailbox:** Log in to your Parseur account and create a new mailbox. Give it a descriptive name (e.g., "`[Your Company Name] Outlook Inquiries`"). Parseur will provide a unique email address for this mailbox.
2.  **Forward Sample Emails:** Send 5-10 representative emails from your Outlook (emails that match your forwarding rule) to this new Parseur email address. Include a variety of inquiry types.
3.  **Train the Parseur Template:**
    *   In Parseur, open one of the forwarded emails.
    *   Use the point-and-click interface to **highlight the data you want to extract** (e.g., client name, company, event date, specific questions, contact number). For each highlighted piece of text, assign it a meaningful field name (e.g., `client_name`, `event_interest`, `inquiry_details`).
    *   Repeat this process for a few more emails. Parseur's AI will learn from your selections. Review and correct any auto-extracted fields until the accuracy is high.
    *   **Save** your parsing template.

## Step 3: Set Up the Automation Workflow (e.g., Zapier)

Zapier will act as the orchestrator, connecting Outlook (via Parseur), OpenAI, and your action platform.

1.  **Create a New Zap:** Log in to Zapier and click "`Create Zap`."
2.  **Trigger: New Parsed Email in Parseur**
    *   **App:** Search for and select "`Parseur`."
    *   **Event:** Choose "`New Document Processed`."
    *   **Account:** Connect your Parseur account.
    *   **Mailbox:** Select the Parseur mailbox you configured in Step 2.
    *   **Test Trigger:** Run a test to ensure Zapier can pull data from Parseur.
3.  **Action: Send Data to OpenAI for AI Processing**
    *   **App:** Search for and select "`OpenAI`."
    *   **Event:** Choose "`Send Prompt`" or "`Conversation`" (depending on the OpenAI Zapier integration version).
    *   **Account:** Connect your OpenAI API account (ensure your API key is configured).
    *   **Action Setup:**
        *   **Model:** Select `gpt-4o-mini` or `gpt-4o`.
        *   **User Message/Prompt:** Construct a prompt using the extracted fields from Parseur. This prompt will instruct the AI to categorize the inquiry, summarize it, determine urgency, and draft a suggested response. Refer to the `ai_prompts/categorization_prompt.txt` in your Universal Automation Engine repository for a template. Ensure the output format is JSON.
        *   **Example Prompt Structure:**
            ```
            You are an expert assistant for [Your Company Name]. Based on the following client inquiry, categorize it, summarize it, determine urgency, and draft a concise response.

            Client Name: {{client_name_from_parseur}}
            Inquiry Details: {{inquiry_details_from_parseur}}
            Event Interest: {{event_interest_from_parseur}}

            Categorize as: New Booking, Existing Booking Update, Bespoke Request, General Inquiry.
            Urgency: High, Medium, Low.
            Summary: [One sentence summary].
            Suggested Response: [Draft a polite, relevant response].

            Provide output in JSON format only.
            ```
    *   **Test Action:** Run a test to ensure OpenAI processes the data and returns a structured JSON response.
4.  **Action: Create/Update Record in Your Action Platform (e.g., HubSpot CRM)**
    *   **App:** Search for and select your chosen action platform (e.g., "`HubSpot`").
    *   **Event:** Choose the appropriate action (e.g., "`Create Deal`", "`Create Ticket`", "`Create Contact`").
    *   **Account:** Connect your HubSpot account.
    *   **Action Setup:** Map the fields from Parseur and OpenAI to the corresponding fields in HubSpot.
        *   **Deal Name:** Use the AI-generated `summary`.
        *   **Deal Stage/Ticket Status:** Use the AI-generated `category`.
        *   **Contact Email:** Use the `client_email` from Parseur.
        *   **Notes/Description:** Include the full original email body, the AI-generated `summary`, `category`, `urgency`, and `suggested_response`.
        *   **(Optional) Assign Owner:** Based on the AI-generated `category`, you can use Zapier's "`Paths`" or "`Filter`" steps to assign the deal/ticket to a specific team member (e.g., `Bespoke Request` to Dudley Horn, `New Booking` to Sales).
    *   **Test Action:** Run a test to ensure a new deal/ticket is created correctly in HubSpot.

## Step 4: Activate Your Workflow

Once all steps in your Zap are configured and tested successfully, turn the Zap "`On`." From this point forward, any email that matches your Outlook forwarding rule will automatically trigger this workflow, leading to:

1.  **Automatic forwarding** from Outlook to Parseur.
2.  **Data extraction** by Parseur.
3.  **AI categorization and response drafting** by OpenAI.
4.  **Creation of a new, pre-filled task** in your action platform (e.g., HubSpot), ready for your team to review and act upon.

This fully automates the initial triage and data entry, allowing your team to focus on personalized client engagement and strategic tasks.
