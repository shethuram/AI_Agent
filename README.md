# Client Requirements Analyzer & Email Automation

This utility automates the analysis of software requirement requests from clients. It leverages the Groq API (e.g., Llama-3.3) to dissect client emails into structured functional/non-functional requirements, risks, assumptions, and client questions, formats the output as a premium HTML email, and sends it directly to a recipient Gmail account.

## System Architecture

```mermaid
graph TD
    A[requirements.txt] --> B(analyze_and_email.py)
    C[prompt.txt] --> B
    D[config.json] --> B
    B --> E[Groq API completions]
    E -->|JSON Response| B
    B -->|Parse HTML & Subject| F[SMTP Gmail Server]
    F -->|SSL/TLS Mail| G[Recipient Inbox]
```

## Setup Instructions

1. **Prerequisites**:
   Ensure you have Python 3 installed. You will need the `requests` library:
   ```bash
   pip install requests
   ```

2. **Configure Credentials**:
   Create a file named `config.json` (you can copy `config.json.template`) and update it with:
   - `GROQ_API_KEY`: Your API key from Groq Console.
   - `SENDER_EMAIL`: The Gmail address that will send the email.
   - `SENDER_PASSWORD`: Your Gmail **App Password** (Not your regular password. Go to Google Account -> Security -> 2-Step Verification -> App Passwords).
   - `RECIPIENT_EMAIL`: The destination email address.

3. **Run the Script**:
   ```bash
   python analyze_and_email.py
   ```

## Deliverables Reference

This project is structured to directly map to the participants' deliverables:

- **Prompt used**: Located in [prompt.txt](file:///e:/AI%20Agent/prompt.txt)
- **Python Script**: Located in [analyze_and_email.py](file:///e:/AI%20Agent/analyze_and_email.py)
- **Sample Input**: Located in [requirements.txt](file:///e:/AI%20Agent/requirements.txt)
- **Sample Output**: Generated at `output_analysis.html` and `output_raw_response.txt` after running the script.
- **Architecture Diagram**: Rendered above in this README.
