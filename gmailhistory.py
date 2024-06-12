import os
import json
import google.auth
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

# Start history ID offset
# Depending on how much email you get, you will need to adjust this up or down
#    the larger the number is, the further back it starts
#    emails marked read are displayed chronologically (oldest to newest)
START_HISTORY_OFFSET = 60000

# Path to the credentials.json file downloaded from Google Cloud Console
#    download the credentials files and place it in the same direction as this script
CREDENTIALS_FILE = 'credentials.json'

# >>> No need to modify anything after this line

# The file to store the token
TOKEN_FILE = 'token.json'

# Scopes required for the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def format_email(message):
    headers = {h['name']: h['value'] for h in message['payload']['headers']}
    from_name = headers.get('From', 'Unknown')
    subject = headers.get('Subject', 'No Subject')
    datetime_received = datetime.fromtimestamp(int(message['internalDate']) / 1000.0)
    
    # Truncate values to fit on one line
    from_name = (from_name[:20] + '...') if len(from_name) > 20 else from_name
    subject = (subject[:40] + '...') if len(subject) > 40 else subject
    
    return f"{datetime_received} - {from_name} - {subject}"

def get_message_details(service, message_id):
    message = service.users().messages().get(userId='me', id=message_id).execute()
    return format_email(message)

def list_history(service, start_history_id, next_page_token=None):

    history_response = service.users().history().list(
        userId='me', maxResults='500', historyTypes='labelRemoved', startHistoryId=start_history_id, pageToken=next_page_token
    ).execute()
    
    history_records = history_response.get('history', [])
    message_ids = []
    
    #print('history records returned')
    #print(json.dumps(history_records, indent=4))

    for record in history_records:
        #print("NEW RECORD")
        #print(json.dumps(record, indent=4))
        if 'labelsRemoved' in record:
            for label in record['labelsRemoved']:
                #print(json.dumps(label, indent=4))
                if 'UNREAD' in label['labelIds']:
                    #print("UNREAD label found")
                    message_ids.append(record['messages'][0]['id'])
    
    next_page_token = history_response.get('nextPageToken')

    #print("Next page token")
    #print(next_page_token)

    return message_ids, next_page_token

def main():
    creds = None

    # Load the token from file if it exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    
   # Get the initial history ID (could be stored from a previous run)
    initial_history_id = int(service.users().getProfile(userId='me').execute()['historyId']) - START_HISTORY_OFFSET
    
    #print(initial_history_id)

    next_page_token = None
    all_message_ids = []
    
    while True:
        message_ids, next_page_token = list_history(service, initial_history_id, next_page_token)

        for message_id in message_ids:
            print(get_message_details(service, message_id))

        if not next_page_token:
            break

        cont = input('Do you want to see more messages? (any key to continue, no to exit): ')
        if cont.lower() == 'no':
            break
    
if __name__ == '__main__':
    main()

