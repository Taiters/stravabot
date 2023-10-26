import os

from stravabot.config.base import *  # noqa

env = os.environ.get("STRAVABOT_ENV", "prod")
if env == "test":
    from stravabot.config.test import *  # noqa
elif env == "local":
    from stravabot.config.local import *  # noqa
else:
    from stravabot.config.prod import *  # noqa
