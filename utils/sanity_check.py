def safe_to_post():
    """Sanity check to verify that these games haven't already been posted."""
    with open("posted_games.txt") as log_file:
        lines = log_file.readlines()
        last_two_lines = lines[-2:]
        last_two_lines = [line.strip() for line in last_two_lines]
    return last_two_lines
