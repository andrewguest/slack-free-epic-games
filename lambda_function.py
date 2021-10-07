import os
from typing import List

import httpx
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


# Model setup
class Game:
    def __init__(self, title, store_link, image_url) -> None:
        self.title = title
        self.store_link = store_link
        self.image_url = image_url


# Epic functionality
def get_free_epic_games() -> List[Game]:
    """Uses an API from Epic to parse a list of free games to find this week's free games."""
    # HTTP params for the US free games
    free_games_params = {"locale": "en-US", "country": "US", "allowCountries": "US"}

    # Epic's backend API URL for the free games promotion
    epic_api_url = (
        "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    )

    # backend API request
    response = httpx.get(epic_api_url, params=free_games_params)

    # list of dictionaries containing information about the free games
    free_games: List[Game] = []

    # find the free games in the response
    for game in response.json()["data"]["Catalog"]["searchStore"]["elements"]:
        # for some reason, Epic returns some games that aren't actually free. This is to filter those out.
        if (
            game["price"]["totalPrice"]["originalPrice"]
            - game["price"]["totalPrice"]["discount"]
        ) == 0 and (
            game["price"]["totalPrice"]["originalPrice"] != 0
            and game["price"]["totalPrice"]["discount"] != 0
        ):
            game = Game(
                title=game["title"],
                store_link="https://www.epicgames.com/store/en-US/p/"
                + game["productSlug"],
                image_url=[
                    image["url"]
                    for image in game["keyImages"]
                    if image["type"] == "OfferImageWide"
                ][0],
            )
            free_games.append(game)

    return free_games


# Slack setup
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

