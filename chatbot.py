import openai
import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load environment variables from .env file
load_dotenv()

# Set up API keys
openai.api_key = os.getenv("CHATGPT_API_KEY")
followup_boss_api_key = os.getenv("FOLLOWUP_BOSS_API_KEY")

# Set up FollowUp Boss API base URL
followup_boss_base_url = "https://api.followupboss.com/v1/"

def create_lead(first_name, last_name, email, phone=None):
    auth = HTTPBasicAuth(followup_boss_api_key, '')
    data = {
        "firstName": first_name,
        "lastName": last_name,
        "emails": [{"value": email}],
    }
    if phone:
        data["phones"] = [{"value": phone}]

    response = requests.post(f"{followup_boss_base_url}people", auth=auth, json=data)
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Error creating lead: {response.text}")

def generate_chatgpt_response(prompt, max_tokens=50):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].text.strip()
    return message

def get_lead_information(lead_id):
    auth = HTTPBasicAuth(followup_boss_api_key, '')
    response = requests.get(f"{followup_boss_base_url}people/{lead_id}", auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error getting lead information: {response.text}")

def send_text_message_to_lead(lead_id, text):
    auth = HTTPBasicAuth(followup_boss_api_key, '')
    data = {
        "leadId": lead_id,
        "text": text,
    }
    response = requests.post(f"{followup_boss_base_url}texts", auth=auth, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error sending text message: {response.text}")

def send_chatgpt_response_to_lead(lead_id, prompt):
    try:
        lead_info = get_lead_information(lead_id)
        chatgpt_response = generate_chatgpt_response(prompt)
        response = send_text_message_to_lead(lead_id, chatgpt_response)
        print(f"Message sent to {lead_info['firstName']} {lead_info['lastName']}: {chatgpt_response}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Create a new lead for testing
first_name = "John"
last_name = "Doe"
email = "john.doe@example.com"
phone = "555-123-4567"

new_lead = create_lead(first_name, last_name, email, phone)

# Use the generated lead ID for testing
lead_id = new_lead["id"]
prompt = "Thank you for your interest in our properties. Do you have any questions or concerns?"

send_chatgpt_response_to_lead(lead_id, prompt)
