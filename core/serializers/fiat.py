from django.conf import settings
from rest_framework import serializers

from core.currency import CurrencySerialField
from core.models.fiat import UserFiatWallet


class UserFaitCurrencySerializer(serializers.Serializer):
    """
    Used when create new user wallet and requesting wallets list
    """
    currency = CurrencySerialField(required=False)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )


class UserFiatWalletSerializer(serializers.ModelSerializer):
    currency = CurrencySerialField()

    class Meta:
        model = UserFiatWallet
        fields = (
            'currency',
            'merchant',
            'block_type',
        )
