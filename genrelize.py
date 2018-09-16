import os
import time
import re
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "!themify"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

genre_counter = {
    "fantasy": 0,
    "horror": 0,
    "adventure": 0,
    "sci-fi": 0,
    "mystery": 6,
    "action": 0,
    "crime": 0,
    "romance": 0,
    "comedy": 0,
    "thriller": 0,
    "drama": 0
}

genre_colors = {
    "horror": [0xAC813D, 0xAC813D,0x6F6F6F, 0xFFFFFF, 0x6F6F6F, 0xFFFFFF, 0x6F6F6F, 0x6F6F6F],
    "adventure": [0x705116, 0x379114,0x1b480a, 0xFFFFFF, 0x1b480a, 0xFFFFFF, 0x1b480a, 0x1b480a],
    "comedy": [0xe6e600,0x999999,0x999999,0x000000,0x4da6ff,0x000000,0xb3b3b3,0xb3b3b3],
    "fantasy": [0x379114, 0xAC813D,0x1b480a, 0xFFFFFF, 0x1b480a, 0xFFFFFF, 0x1b480a, 0x1b480a],
    "drama": [0x8000ff,0x4d0099,0xFF4DC4,0xffffff,0x4d0099,0xFFFFFF,0x00FFB7,0xFF4DC4],
    "sci-fi": [0x1a1aff,0xe60000,0x7300e6,0xFFFFFF,0xb30000,0xFFFFFF,0xff1a1a,0xff1a1a],
    "mystery": [0x4D5250,0x444A47,0xD39B46,0xFFFFFF,0x434745,0xFFFFFF,0x99D04A,0xDB6668],
    "crime": [0xcc6600,0x994d00,0x994d00,0xFFFFFF,0xb36b00,0xFFFFFF,0x994d00,0x994d00],
    "action": [0xff0000,0x1a1aff,0x000099,0xFFFFFF,0x1a1aff,0xFFFFFF,0x1a1aff,0x9999ff],
    "thriller": [0x101010, 0x101010, 0x5df322, 0xFFFFFF, 0x5df322, 0xFFFFFF, 0x5df322, 0x5df322],
    "romance": [0xFF847C,0xBB76E7,0xbb76e7,0xFFFFFF,0xbb76e7,0xFFFFFF,0xbb76e7,0xbb76e7],
    "default": [0xF8F8FA,0xF8F8FA,0x2D9EE0,0xFFFFFF,0xFFFFFF,0x383F45,0x60D156,0xDC5960]
}


def find_dominant_genre():
    maxVal = 0
    diff = 0
    cur_genre = ''
    for key in genre_counter:
        if genre_counter[key] - maxVal > diff:
            diff = genre_counter[key] - maxVal
            maxVal = genre_counter[key]
            cur_genre = key
    return (diff, cur_genre)

    #(genre_1, val_1), (genre_2, val_2) = sorted(d.items(), key=lambda x: x[1], reverse=True)[:2]

def find_cur_hex_code():
    diff, cur_genre = find_dominant_genre()
    if not cur_genre:
        return genre_colors["default"]
    ans = []
    print(diff, cur_genre)
    for i in range(8):
        default_val = (10-diff)* int(genre_colors["default"][i])
        genre_val = diff * int(genre_colors[cur_genre][i])
        print(genre_colors["default"][i], genre_colors[cur_genre][i])
        print(default_val, genre_val)
        ans.append(hex(int((default_val + genre_val)/10)))
    #return [hex((10-diff)/10 * genre_colors["default"][i] + diff/10 * genre_colors[cur_genre][i]) for i in range(8)]
    return ans

def hex_code_as_string():
    hex_code = find_cur_hex_code()
    ans = ""
    for i in range(7):
        ans += '#' + str(hex_code[i])[2:] + ', '
    ans += '#' + str(hex_code[7])[2:]
    return ans

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event and event["channel"] == "GCUAGSGTU":
            print(event["text"])
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = hex_code_as_string()

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Genrelize Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
