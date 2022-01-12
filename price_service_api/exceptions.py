class PriceServiceError(Exception):
    """Base Exception that all others are subclassing."""


class PriceError(PriceServiceError):
    """Error when fetching prices."""
