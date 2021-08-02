from typing import List
import sys

import httpx

from models.games import Game


def get_free_epic_games() -> List[Game]:
    """Uses an API from Epic to parse a list of free games to find this week's free games.
    """
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
                    ][0]
            )
            free_games.append(game)

    return free_games
