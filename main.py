import os
import sys

from dhooks import Webhook, Embed

from utils.epic import get_free_epic_games
from utils.sanity_check import safe_to_post


hook = Webhook(os.environ['free_games_discord_webhook'])
free_epic_games = get_free_epic_games()

if safe_to_post() == False:
    sys.exit("Not good to post")
else:
    last_games_posted = safe_to_post()
    epic_list = [game.title for game in free_epic_games]
    if sorted(last_games_posted) == sorted(epic_list):
        sys.exit("These games have already been posted. Exiting")
    else:
        for entry in free_epic_games:
            data = Embed(
                title=entry.title,
                description=entry.store_link,
                image_url=entry.image_url
            )
            data.set_author(name="FreeGamesBot", icon_url="https://img.icons8.com/fluency/96/000000/xbox-controller.png")
            hook.send(embed=data)
            with open("posted_games.txt", "a") as log_file:
                log_file.write(entry.title + "\n")
