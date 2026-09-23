import os


APP_NAME = "feed-api"


def get_config():
    return {
        "app_name": APP_NAME,
        "port": int(os.getenv("PORT", "8003")),
        "debug": os.getenv("DEBUG", "true").lower() in ("1", "true"),
    }