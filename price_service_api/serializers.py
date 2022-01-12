from decimal import Decimal

from rest_framework import serializers

from .models import Price


def remove_exponent(d):
    if d == d.to_integral_value():
        final_value = d.quantize(Decimal(1))
    else:
        final_value = d.normalize()
    return format(final_value, "f")


class PriceInputSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(max_length=20)
    price = serializers.DecimalField(
        max_digits=None,
        decimal_places=8,
        coerce_to_string=False,
    )

    class Meta:
        model = Price
        fields = (
            "symbol",
            "price",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["price"] = remove_exponent(representation["price"])

        return representation


class PriceOutputSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(max_length=20)
    price = serializers.DecimalField(
        max_digits=None,
        decimal_places=8,
        coerce_to_string=False,
    )
    created = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = Price
        fields = (
            "symbol",
            "price",
            "created",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["price"] = remove_exponent(representation["price"])

        return representation
