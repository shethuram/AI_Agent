import os
import json
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        print("Please copy config.json.template to config.json and fill in your details.")
        sys.exit(1)
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    # Check if user has updated the placeholder values
    placeholders = ["YOUR_GROQ_API_KEY", "your_email@gmail.com", "your_gmail_app_password", "recipient_email@gmail.com"]
    for key, val in config.items():
        if val in placeholders:
            print(f"Warning: {key} still has a default placeholder value ({val}). Please update config.json.")
            
    return config

def read_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def call_groq_api(config, prompt_content, requirements_text):
    api_key = config.get("GROQ_API_KEY")
    model = config.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    if not api_key or api_key == "YOUR_GROQ_API_KEY":
        # Check environment variable as fallback
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Error: GROQ_API_KEY not found in config.json or environment variables.")
            sys.exit(1)

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = prompt_content.replace("{requirements_text}", requirements_text)
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": system_prompt
            }
        ],
        "temperature": 0.2
    }
    
    print(f"Calling Groq API with model '{model}'...")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"API Error (Status {response.status_code}): {response.text}")
        sys.exit(1)
        
    result = response.json()
    return result["choices"][0]["message"]["content"]

def parse_groq_response(response_text):
    # Standard format expected:
    # Subject: [Subject]
    # [HTML Body]
    lines = response_text.strip().split("\n")
    subject = "Requirements Analysis and Response Plan"
    body_lines = []
    
    subject_found = False
    for line in lines:
        if line.lower().startswith("subject:") and not subject_found:
            subject = line[len("subject:"):].strip()
            subject_found = True
        else:
            body_lines.append(line)
            
    body_content = "\n".join(body_lines).strip()
    
    # Strip leading markdown indicators if any
    if body_content.startswith("```html"):
        body_content = body_content[7:]
    if body_content.endswith("```"):
        body_content = body_content[:-3]
        
    return subject, body_content.strip()

def send_email(config, subject, html_content):
    sender_email = config.get("SENDER_EMAIL")
    sender_password = config.get("SENDER_PASSWORD")
    recipient_email = config.get("RECIPIENT_EMAIL")
    smtp_server = config.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = config.get("SMTP_PORT", 587)
    
    if not sender_email or not sender_password or not recipient_email:
        print("SMTP config incomplete in config.json. Skipping email dispatch.")
        return False
        
    print(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
    try:
        # Create MIMEMultipart message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # Plain text fallback
        text_fallback = "Please use an HTML-compatible email client to view this analysis."
        part1 = MIMEText(text_fallback, "plain")
        part2 = MIMEText(html_content, "html")
        
        message.attach(part1)
        message.attach(part2)
        
        # Connect & login
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade connection to secure
        server.login(sender_email, sender_password)
        
        print(f"Sending email to {recipient_email}...")
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def main():
    config = load_config()
    
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    prompt_file = os.path.join(os.path.dirname(__file__), "prompt.txt")
    
    requirements_text = read_file(requirements_file)
    prompt_content = read_file(prompt_file)
    
    print("Analyzing requirements...")
    raw_response = call_groq_api(config, prompt_content, requirements_text)
    
    # Save raw response for debug/deliverables reference
    output_raw_path = os.path.join(os.path.dirname(__file__), "output_raw_response.txt")
    with open(output_raw_path, "w", encoding="utf-8") as f:
        f.write(raw_response)
    print(f"Raw response saved to {output_raw_path}")
    
    subject, html_content = parse_groq_response(raw_response)
    
    # Save the parsed HTML file
    output_html_path = os.path.join(os.path.dirname(__file__), "output_analysis.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML analysis saved to {output_html_path}")
    
    # Send email
    send_email(config, subject, html_content)
    
if __name__ == "__main__":
    main()
