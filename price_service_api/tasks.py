import logging

from price_service.celery import app
from .exchange import update_price


logger = logging.getLogger(__name__)


@app.task(bind=True)
def price_check(self):
    """Scheduled task."""
    logger.debug("Request: {0!r}".format(self.request))
    logger.info("Automatically getting new price for BTC/USD.")

    update_price()
