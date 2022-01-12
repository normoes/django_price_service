import logging
from decimal import Decimal

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


logger = logging.getLogger(__name__)


class Price(models.Model):
    symbol = models.CharField(verbose_name="Symbol", max_length=20, db_index=True)
    price = models.DecimalField(
        verbose_name="Price", max_digits=18, decimal_places=8, default=Decimal("0"), null=False, editable=False
    )
    created = models.DateTimeField(verbose_name="Created at", auto_now_add=True)
    modified = models.DateTimeField(verbose_name="Modified at", auto_now=True)

    class Meta:
        db_table = "prices"

    def __str__(self):
        return f"Price for '{self.symbol}' is '{self.price}' at '{self.created}')."


# creating api token with every created user in admin panel
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
