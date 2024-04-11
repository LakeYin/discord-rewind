import glob
import os
import json
import pandas as pd
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("messages_path", help="Path to the messages folder")
parser.add_argument("guild", help="Name of the Discord server")
parser.add_argument("-k", "--top-k", default=5, type=int, help="Number of top channels to return")
parser.add_argument("-s", "--since")

args = parser.parse_args()
messages_path = args.messages_path
guild = args.guild.lower()
top_k = args.top_k
since = args.since

if messages_path.endswith("messages"):
    messages_path += os.sep + "*" + os.sep
elif messages_path.endswith("messages" + os.sep):
    messages_path += "*" + os.sep
else:
    parser.error(f"messages_path string should end with 'messages' or 'messages{os.sep}'")

# parse all relevant messages
all_messages = []
for dir in glob.glob(messages_path, recursive=True):
    channel = os.path.join(dir, "channel.json")
    messages = os.path.join(dir, "messages.json")

    with open(channel, "r") as f:
        channel = json.load(f)

    with open(messages, "r") as f:
        messages = json.load(f)

    if channel["type"] == 0 and "guild" in channel.keys() and channel["guild"]["name"].lower() == guild:
        for m in messages:
            m["Channel"] = channel["name"]
            all_messages.append(m)

df = pd.DataFrame(all_messages)
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# filter for messages past date
if since is not None:
    since = pd.to_datetime(since)
    df = df[df["Timestamp"] >= since]

channel_count = df.value_counts("Channel")

print("Favorite channels")
for i in range(min(top_k, len(channel_count))):
    print(f"{i + 1}.) {channel_count.index[i]} ({channel_count.iloc[i]})")
