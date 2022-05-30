import os
import logging
from typing import List
from datetime import datetime
from dataclasses import dataclass

import httpx
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


# Logging setup
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Model setup
@dataclass
class Game:
    title: str
    store_link: str
    image_url: str


# Epic functionality
def get_free_epic_games() -> List[Game]:
    """Uses an API from Epic to parse a list of free games to find this week's free games."""
    # HTTP params for the US free games
    free_games_params = {
        "locale": "en-US",
        "country": "US",
        "allowCountries": "US",
    }

    # Epic's backend API URL for the free games promotion
    epic_api_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    # backend API request
    response = httpx.get(epic_api_url, params=free_games_params)
    logger.info("## HTTP response code")
    logger.info(response)
    logger.info("## HTTP response body")
    logger.info(response.json())

    # list of dictionaries containing information about the free games
    free_games: List[Game] = []

    # create Game objects for each entry found
    for game in response.json()["data"]["Catalog"]["searchStore"]["elements"]:
        if len(game["promotions"]["promotionalOffers"]) == 0:
            continue
        else:
            discount_price = game["price"]["totalPrice"]["discountPrice"]

            promo_start_date = datetime.strptime(
                game["promotions"]["promotionalOffers"][0][
                    "promotionalOffers"
                ][0]["startDate"],
                "%Y-%m-%dT%H:%M:%S.000%z",
            ).replace(tzinfo=None)

            promo_end_date = datetime.strptime(
                game["promotions"]["promotionalOffers"][0][
                    "promotionalOffers"
                ][0]["endDate"],
                "%Y-%m-%dT%H:%M:%S.000%z",
            ).replace(tzinfo=None)

            if (
                discount_price == 0
                and promo_start_date <= datetime.now() <= promo_end_date
            ):
                free_games.append(
                    Game(
                        title=game["title"],
                        store_link=f"https://www.epicgames.com/store/en-US/p/{game['productSlug']}"
                        if game["productSlug"]
                        else "https://www.epicgames.com/store/en-US/p/",
                        image_url=[
                            image["url"]
                            for image in game["keyImages"]
                            if image["type"] == "OfferImageWide"
                        ][0],
                    )
                )

    logger.info("## Free game(s)")
    logger.info(free_games)

    return free_games


# Slack setup
def lambda_handler(event, context):
    slack_client = WebClient(token=os.getenv("SLACK_TOKEN"))
    free_epic_games = get_free_epic_games()

    for entry in free_epic_games:
        game_blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{entry.title}"},
            },
            {
                "type": "image",
                "title": {"type": "plain_text", "text": f"{entry.title}"},
                "image_url": f"{entry.image_url}",
                "alt_text": f"{entry.title}",
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click Me"},
                        "value": "click_me_123",
                        "url": f"{entry.store_link}",
                        "action_id": "button-action",
                    }
                ],
            },
            {"type": "divider"},
        ]

        print(game_blocks)

        try:
            slack_client.chat_postMessage(
                channel=str(
                    os.getenv("SLACK_CHANNEL_ID")
                ),  # get this from an env variable
                blocks=game_blocks,
            )
            logger.info("## Slack message")
            logger.info("Slack message successfully sent")
        except SlackApiError as e:
            logger.error("## Slack message ERROR")
            logger.error(e.response["error"])
            assert e.response["error"]


if __name__ == "__main__":
    lambda_handler("", "")
