# test slack
# listen to channel
# wait for msg
# app management dashboard: https://api.slack.com/apps

import os, time #, logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# store as environment variable
slack_token = os.environ["MONITOR_BOT_TOKEN"]
#print(slack_token)
client = WebClient(token=slack_token)

# all-evs C07DD7KH5HR
# all-arbs C079MMZQ1GU
channel_name = 'all-evs' 
#print('channel_name: ' + channel_name)
send_text = 'test slack. please show notification of new msg'
# if posting new msg does not show notice
# then click general channel
# so that we see ev-arb channels highlighted when new msg
# bc if inside channel, menu item does not highlight for new msg


# Post to Channel
# client.chat_postMessage(
#     channel=channel_name,
#     text=send_text,
#     username='Ball'
# )



# Listen to Channel
channel_name = "needle"
conversation_id = None
try:
    # Call the conversations.list method using the WebClient
    for result in client.conversations_list(types="private_channel"):
        if conversation_id is not None:
            break
        for channel in result["channels"]:
            print('channel: ' + channel["name"] + channel["id"])
            # if channel["name"] == channel_name:
            #     conversation_id = channel["id"]
            #     #Print result
            #     print(f"Found conversation ID: {conversation_id}")
            #     break

except SlackApiError as e:
    print(f"Error: {e}")
    


def read_channel(channel_name):
    # Store conversation history
    conversation_history = []
    # ID of the channel you want to send the message to
    # use fcn read_channel_id(channel_name)
    channel_ids = {'all-evs':'C07DD7KH5HR', 
                    'all-arbs':'C079MMZQ1GU'}
    channel_id = channel_ids[channel_name]

    try:
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        result = client.conversations_history(channel=channel_id)

        conversation_history = result["messages"]

        # Print results
        #logger.info("{} messages found in {}".format(len(conversation_history), channel_id))
        print("{} messages found in {}, {}".format(len(conversation_history), channel_id, channel_name))

    except SlackApiError as e:
        #logger.error("Error creating conversation: {}".format(e))
        print("Error creating conversation: {}".format(e))

    return conversation_history


# try:
#     # Call the conversations.history method using the WebClient
#     # The client passes the token you included in initialization    
#     result = client.conversations_history(
#         channel=channel_id,
#         inclusive=True,
#         oldest="1610144875.000600",
#         limit=1
#     )

#     message = result["messages"][0]
#     # Print message text
#     print(message["text"])

# except SlackApiError as e:
#     print(f"Error: {e}")

# sorted from recent to distant
# print('\n===All Messages===\n')
# for message in conversation_history:
#     print(message["text"])

# check if diff last msg to see if update
# prev_last_msg = None
# # saved msgs is evs or arbs json file
# saved_msgs = []

# while True:

#     # read channel
#     conversation_history = read_channel(channel_name)

#     # Monitor New Msgs
#     # get last msg
#     last_msg = conversation_history[0]

#     if last_msg != prev_last_msg:
#         # check num new msgs
#         new_msgs = []
#         for message in conversation_history:
#             print(message["text"])
#             if message not in saved_msgs:
#                 new_msgs.append(message)

#         saved_msgs.extend(new_msgs)

#         prev_last_msg = last_msg


#     time.sleep(5) # check every 5 seconds

