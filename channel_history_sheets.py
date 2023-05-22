import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack setup
slack_token = 'your-slack-token'
client = WebClient(token=slack_token)
channel_id = 'channel-id'

# Google sheets setup
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(creds)
sh = gc.create('Slack Channel Messages')  # creates a new google spreadsheet
worksheet = sh.get_worksheet(0)  # get the first sheet

# Define the headers
headers = ["User", "Message", "Timestamp", "Reactions", "Thread"]
worksheet.append_row(headers)

try:
    result = client.conversations_history(channel=channel_id)

    for message in result["messages"]:
        user_id = message["user"]
        text = message["text"]
        ts = message["ts"]

        # Get user info
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["name"]

        # Handle reactions
        reactions = ""
        if "reactions" in message:
            reactions = ', '.join([f'{reaction["name"]} ({reaction["count"]})' for reaction in message["reactions"]])

        # Check if message is part of a thread
        thread_text = ""
        if "thread_ts" in message:
            thread = client.conversations_replies(channel=channel_id, ts=message["thread_ts"])
            thread_messages = thread["messages"]
            # Skip the first message, since it's the same as the parent
            for thread_message in thread_messages[1:]:
                thread_text += f'[{thread_message["user"]}]: {thread_message["text"]}\n'

        # Write to Google Sheets
        row = [user_name, text, ts, reactions, thread_text]
        worksheet.append_row(row)

except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
