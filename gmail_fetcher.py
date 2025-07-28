from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import email
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=creds)

def search_emails(service, query):
    result = service.users().messages().list(userId="me", q=query).execute()
    messages = result.get("messages", [])
    emails = []
    
    
    
    for msg in messages:
        text = service.users().messages().get(userId="me", id=msg['id'], format='full').execute()
        payload = text['payload']
        headers = payload['headers']
        
        parts = payload.get('parts', [])   
        body = "" 
        
        if "data" in payload.get('body', {}):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode()
        elif parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode()
                    break
        subject = next((h['value'] for h in headers if h['name']=='Subject'), '')
        date = next((h['value'] for h in headers if h['name']=='Date'), '')
        emails.append({ 'subject': subject, 'date': date, 'body': body })
    
    print(f"Found {len(emails)}, {query}")
    return emails