"""Manages the configuration of logging operations across project."""

import logging


def setup_logging(output: str, filename="lmnh_plants.log", level=20):
    """Setup the basicConfig."""
    log_format = "{asctime} - {levelname} - {message}"
    log_datefmt = "%Y-%m-%d %H:%M"
    if output == "file":
        logging.basicConfig(
            filename=filename,
            encoding="utf-8",
            filemode="a",
            level=level,
            format=log_format,
            style="{",
            datefmt=log_datefmt
        )
        logging.info("Logging to file: %s", filename)
    else:
        logging.basicConfig(
            level=level,
            format=log_format,
            style="{",
            datefmt=log_datefmt
        )
        logging.info("Logging to console.")


if __name__ == '__main__':

    setup_logging("console")
    # Suggested use: Import setup_logging
    # call setup_logging("console" or "file")
    # then call logging.{levelname: (debug,info,warning,error)}("Message here")

    # DO NOT USE f-strings WHEN LOGGING!!!
    #   Use lazy-formatting i.e.:
    #       logging.info("Here is a variable: %s", my_variable)
    #   This ensures pylint doesn't shout at us

    # Use level=10 in setup_logging() when configuring (at the start of the file) to set to debug mode
    #   Debugging requires level=10 ; logging.debug("Message goes here.")
