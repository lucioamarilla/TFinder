import os


APP_NAME = "notif-api"


def get_config():
    return {
        "app_name": APP_NAME,
        "port": int(os.getenv("PORT", "8004")),
        "debug": os.getenv("DEBUG", "true").lower() in ("1", "true"),
    }