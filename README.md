# gmail-read-history
Have you ever accidentally marked a message as read in Gmail? This script will list all of the last messages that have been marked as read so you can find it again.

There are a few steps to get started:
1. Go to the Google Cloud Console and enable the Gmail API
2. Create a new project
3. Go to Credentials and create a new OAuth 2.0 Client IDs with type Desktop
4. Click on the new Client, and under Client Secrets, click the download icon ("Download JSON")
5. Place this file in the same directory as this script and name it credentials.json
7. Run the script and OAuth to the account that you choose

You may need to modify START_HISTORY_OFFSET at the top of the file depending on how much email you get if you find that the initial messages returned are either too old or too recent. Larger values will start back further in time, and smaller values will start with more recent actions.

This is an unsupported script. Hopefully it helps but the author will not be providing any kind of help. Please ask ChatGPT if you have any questions.
