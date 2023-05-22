# Slack Channel to BigQuery Exporter

This script fetches message history including threads and emoji reactions from a specified Slack channel and exports the data to a Google BigQuery table.

## Setup

1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up the Google Cloud SDK if you haven't done so already. Follow the instructions here: https://cloud.google.com/sdk/docs/quickstart

4. Authenticate your account with Google Cloud:
    ```bash
    gcloud auth login
    ```

5. Set up your Google Cloud project:
    ```bash
    gcloud config set project PROJECT_ID
    ```

6. Create a BigQuery dataset and table with the following schema:
    ```markdown
    user_name: STRING
    text: STRING
    ts: TIMESTAMP
    reactions: STRING
    thread_text: STRING
    ```

7. Deploy the function:
    ```bash
    gcloud functions deploy slack_to_bigquery --runtime python39 --trigger-http --allow-unauthenticated
    ```

8. Set environment variables SLACK_TOKEN and CHANNEL_ID. SLACK_TOKEN is your Slack API token and CHANNEL_ID is the ID of the Slack channel from which you want to fetch message history.
    ```bash
    gcloud functions set-env-vars slack_to_bigquery --update-env-vars SLACK_TOKEN="xoxb-your-token",CHANNEL_ID="your-channel-id"
    ```

## Usage

After deploying the function and setting the environment variables, the function will be triggered with HTTP requests.

To see logs for your function, use:
```bash
gcloud functions logs read slack_to_bigquery
```

## Notes

Please be aware of rate limits imposed by the Slack API (https://api.slack.com/docs/rate-limits) as well as any costs associated with Google Cloud Functions and BigQuery usage.
