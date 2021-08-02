from datetime import date, datetime


def safe_to_post():
    """Sanity check to verify a few constraints:
    1. That it's Thursday.
    2. That it's 3:15pm UTC or later.
    3. That these games haven't already been posted.
    """
    current_utc_time = datetime.utcnow()
    if date.today().weekday() == 3 and (current_utc_time.hour >= 15 and current_utc_time.minute >= 15):
        with open("posted_games.txt") as log_file:
            lines = log_file.readlines()
            last_two_lines = lines[-2:]
            last_two_lines = [line.strip() for line in last_two_lines]
        return last_two_lines
    else:
        return False
