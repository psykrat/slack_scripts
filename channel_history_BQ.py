import os
from google.cloud import bigquery
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack setup
slack_token = 'your-slack-token'
client = WebClient(token=slack_token)
channel_id = 'channel-id'

# Set environment variable for google cloud authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_your_service_account_file.json"

# BigQuery setup
client_bq = bigquery.Client()
table_id = "your_project.your_dataset.your_table"

try:
    result = client.conversations_history(channel=channel_id)

    rows_to_insert = []

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

        # Prepare data to be inserted into BigQuery
        row = (user_name, text, ts, reactions, thread_text)
        rows_to_insert.append(row)

    errors = client_bq.insert_rows(client_bq.get_table(table_id), rows_to_insert)

    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))

except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
