import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from utils.epic import get_free_epic_games


slack_client = WebClient(token=os.getenv("SLACK_TOKEN"))
free_epic_games = get_free_epic_games()

epic_games_list = [game.title for game in free_epic_games]

for entry in free_epic_games:
    game_blocks = [
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"*{entry.title}*"
			},
			"accessory": {
				"type": "image",
				"image_url": f"{entry.image_url}",
				"alt_text": f"{entry.title}"
			}
		},
		{
			"type": "section",
            "text": {
                "type": "plain_text",
                "text": f"{entry.store_link}"
            },
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Epic store link"
				},
				"value": "click_me_123",
				"url": f"{entry.store_link}",
				"action_id": "button-action"
			}
		},
		{
			"type": "divider"
		}
    ]

    try:
        slack_client.chat_postMessage(
            channel = str(os.getenv("SLACK_CHANNEL_TOKEN")),  # get this from an env variable
            blocks = game_blocks
        )
    except SlackApiError as e:
        assert e.response["error"]

