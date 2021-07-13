import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logging.info("patch all import")
from aws_xray_sdk.core import patch_all

logging.info("bootstrap import")
from stravabot.bootstrap import bootstrap

logging.info("starting patch all")
patch_all()
logging.info("ending patch all")

logging.info("calling bootstrap")
api = bootstrap()
logging.info("returned from bootstrap")


def handler(event, context):
    logging.info("handler")
    return api.handle(event, context)
