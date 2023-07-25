from django.db.models import CharField
from django.db.models.functions import Cast, Concat
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from core.consts.currencies import CRYPTO_WALLET_CREATORS, ALL_CURRENCIES
from core.filters.wallet import WalletHistoryFilter
from core.models.cryptocoins import UserWallet
from core.models.fiat import UserFiatWallet
from core.models.wallet_history import WalletHistoryItem
from core.serializers.cryptocoins import UserCurrencySerializer, UserWalletSerializer
from core.serializers.fiat import UserFaitCurrencySerializer, UserFiatWalletSerializer

from core.serializers.wallet_history import WalletHistoryItemSerializer


class CreateUserWallet(GenericAPIView):
    # TODO: review and rewrite!
    TIMEOUT = 30

    @extend_schema(
        description='Perform data',
        request=UserCurrencySerializer,
        responses={
            200: UserWalletSerializer
        },
    )
    def post(self, request):
        serializer = UserCurrencySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = data['user']
        currency = data['currency']
        blockchain_currency = data.get('blockchain_currency')

        wallet_creator_fn = CRYPTO_WALLET_CREATORS[currency]
        if isinstance(wallet_creator_fn, dict):
            wallet_creator_fn = wallet_creator_fn[blockchain_currency.code]
        
        if 'fiat' in wallet_creator_fn.__name__:
            self.wallet_serializer = UserFiatWalletSerializer
        else:
            self.wallet_serializer = UserWalletSerializer

        wallets = wallet_creator_fn(user_id=user.id, currency=currency)
        try:
            wallet_data = self.wallet_serializer(wallets, many=True).data
        except Exception as e:
            raise APIException(detail=str(e), code='server_error')
        return Response(status=status.HTTP_200_OK, data=wallet_data)


class UserWallets(GenericAPIView):
    pagination_class = None

    @extend_schema(
        description="Perform data",
        request=UserCurrencySerializer,
        responses={
            200: UserWalletSerializer(many=True),
        }
    )
    def post(self, request):
        serializer = UserCurrencySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = data['user']
        currency = data.get('currency')
        
        wallet_handler = UserFiatWallet if currency in ALL_CURRENCIES else UserWallet
        blocked_types = [UserWallet.BLOCK_TYPE_DEPOSIT, UserWallet.BLOCK_TYPE_DEPOSIT_AND_ACCUMULATION, UserFiatWallet.BLOCK_TYPE_DEPOSIT, UserFiatWallet.BLOCK_TYPE_DEPOSIT_AND_ACCUMULATION]

        # get only latest wallet for each currency
        token_wallets = UserWallet.objects.filter(
            user_id=user.id,
            merchant=False,
            is_old=False,
        ).annotate(
            currency_str=Cast('currency', output_field=CharField()),
            blockchain_currency_str=Cast('blockchain_currency', output_field=CharField()),
            uniq_cur=Concat('currency_str', 'blockchain_currency_str')
        ).order_by('uniq_cur', '-created').distinct('uniq_cur')
        
        fiat_wallets = UserFiatWallet.objects.filter(
            user_id=user.id,
            # merchant=False,
            is_old=False,
        # below annotation is required for further union
        ).annotate(
            currency_str=Cast('currency', output_field=CharField()),
            blockchain_currency_str=Cast('currency', output_field=CharField()),
            uniq_cur=Concat('currency_str', 'blockchain_currency_str')
        ).order_by('uniq_cur', '-created').distinct('uniq_cur')
        
        wallets = token_wallets.union(fiat_wallets)
        if currency:
            wallets = wallets.filter(currency=currency)

        token_wallet_data = UserWalletSerializer(token_wallets, many=True).data
        fiat_wallet_data = UserFiatWalletSerializer(fiat_wallets, many=True).data
        wallet_data = token_wallet_data  + fiat_wallet_data
        
        for w in wallet_data:
            w['is_blocked'] = False
            if w['block_type'] in blocked_types:
                w['address'] = f'Your deposit for {w["currency"]} is blocked'
                w['is_blocked'] = True
        return Response(status=status.HTTP_200_OK, data=wallet_data)


class WalletHistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = WalletHistoryItemSerializer
    queryset = WalletHistoryItem.objects.all().select_related(
        'transaction',
    )
    filter_class = WalletHistoryFilter

    def get_queryset(self):
        return super().get_queryset().filter(
            user_id=self.request.user.id,
        )
