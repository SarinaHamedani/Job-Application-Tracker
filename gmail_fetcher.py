from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import email
from datetime import datetime
from google.auth.transport.requests import AuthorizedSession

import httplib2
import pickle

from requests import Request 
import os

http = httplib2.Http(timeout=60)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    token_path = 'token.pickle'
    credentials_path = 'credentials.json'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    # Use AuthorizedSession to apply a longer timeout
    session = AuthorizedSession(creds)
    session.timeout = 60  # seconds

    return build('gmail', 'v1', credentials=creds)

# def search_emails(service, query):
#     result = service.users().messages().list(userId="me", q=query).execute()
#     messages = result.get("messages", [])
#     emails = []
    
    
    
#     for msg in messages:
#         text = service.users().messages().get(userId="me", id=msg['id'], format='full').execute()
#         payload = text['payload']
#         headers = payload['headers']
        
#         parts = payload.get('parts', [])   
#         body = "" 
        
#         if "data" in payload.get('body', {}):
#             body = base64.urlsafe_b64decode(payload['body']['data']).decode()
#         elif parts:
#             for part in parts:
#                 if part['mimeType'] == 'text/plain':
#                     body = base64.urlsafe_b64decode(part['body']['data']).decode()
#                     break
#         subject = next((h['value'] for h in headers if h['name']=='Subject'), '')
#         date = next((h['value'] for h in headers if h['name']=='Date'), '')
#         emails.append({ 'subject': subject, 'date': date, 'body': body })
    
#     print(f"Found {len(emails)}, {query}")
#     return emails

def parse_message(text):
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
    return { 'subject': subject, 'date': date, 'body': body }

def search_emails(service, query, user_id='me'):
    all_messages = []
    response = service.users().messages().list(userId=user_id, q=query, maxResults=500).execute()
    if 'messages' in response:
        all_messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(
            userId=user_id,
            q=query,
            pageToken=page_token,
            maxResults=100
        ).execute()
        if 'messages' in response:
            all_messages.extend(response['messages'])

    # Then fetch full email bodies (assumes you already do this in gmail_fetcher)
    full_emails = []
    print(len(all_messages))
    for msg in all_messages:
        message = service.users().messages().get(userId=user_id, id=msg['id'], format='full').execute()
        # parse message and append to full_emails
        full_emails.append(parse_message(message))  # <-- your custom logic

    print(f"Found {len(full_emails)} emails, {query}")
    return full_emails
