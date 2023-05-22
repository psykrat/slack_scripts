import os
import slack
from google.cloud import bigquery

def slack_to_bigquery(request):
    slack_token = os.environ["SLACK_TOKEN"]
    channel_id = os.environ["SLACK_CHANNEL_ID"]
    client = slack.WebClient(token=slack_token)
    client_bq = bigquery.Client()

    # BigQuery table info
    dataset_id = 'dataset'
    table_id = f'project.dataset.channel'

    # Slack API cursor-based pagination parameters
    cursor = None
    total_messages_processed = 0

    while True:
        try:
            # Pass cursor to conversations_history
            result = client.conversations_history(channel=channel_id, cursor=cursor, limit=200)
            messages = result["messages"]
            messages.sort(key=lambda message: message["ts"])

            rows_to_insert = []

            for message in messages:
                user_id = message.get("user", message.get("bot_id", message.get("username", "Unknown")))
                text = message.get("text", "")
                ts = message.get("ts", "")

                # Get user info if user_id is not 'Unknown'
                user_name = "Unknown"
                if user_id != "Unknown":
                    try:
                        user_info = client.users_info(user=user_id)
                        user_name = user_info["user"]["name"]
                    except:
                        user_name = user_id  # If it fails (like for a bot_id), use the id as the name

                # Handle reactions
                reactions = ""
                if "reactions" in message:
                    reactions = ', '.join([f'{reaction["name"]} ({reaction["count"]})' for reaction in message["reactions"]])

                # Check if message is part of a thread
                thread_text = ""
                if "thread_ts" in message:
                    thread = client.conversations_replies(channel=channel_id, ts=message["thread_ts"])
                    thread_messages = thread["messages"]
                    for thread_message in thread_messages[1:]:
                        thread_user = thread_message.get("user", thread_message.get("parent_user_id", "Unknown"))
                        thread_text += f'[{thread_user}]: {thread_message.get("text", "")}\n'

                # Prepare data to be inserted into BigQuery
                row = (user_name, text, ts, reactions, thread_text)
                rows_to_insert.append(row)

            # Insert rows into BigQuery
            errors = client_bq.insert_rows(client_bq.get_table(table_id), rows_to_insert)

            if errors == []:
                print(f"New rows have been added.")
            else:
                print(f"Encountered errors while inserting rows: {errors}")

            # Update cursor and processed messages count
            cursor = result["response_metadata"]["next_cursor"]
            total_messages_processed += len(messages)

            # If there is no more data to be fetched, break the loop
            if not result["has_more"]:
                break
        except Exception as e:
            print(f"Error: {str(e)}")
            break

    return f"Finished processing. Total messages processed: {total_messages_processed}.", 200
