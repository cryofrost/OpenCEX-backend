from django.conf import settings
from django.db import models
from django.db.transaction import atomic

# from core.consts.currencies import CRYPTO_WALLET_ACCOUNT_CREATORS
# from core.consts.currencies import BlockchainAccount
from core.currency import CurrencyModelField
from lib.cipher import AESCoderDecoder


class UserFiatWallet(models.Model):
    BLOCK_TYPE_NOT_BLOCKED = 0
    BLOCK_TYPE_DEPOSIT = 1
    BLOCK_TYPE_DEPOSIT_AND_ACCUMULATION = 2

    BLOCK_TYPES = (
        (BLOCK_TYPE_NOT_BLOCKED, 'Not blocked'),
        (BLOCK_TYPE_DEPOSIT, 'Deposits'),
        (BLOCK_TYPE_DEPOSIT_AND_ACCUMULATION, 'Deposits + Accumulations'),
    )

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    currency = CurrencyModelField(db_index=True)
    amount = models.DecimalField(max_digits=30, decimal_places=10)
    amount_in_orders = models.DecimalField(max_digits=30, decimal_places=10, default=0)
    # blockchain_currency = CurrencyModelField(default='BTC')
    # address = models.TextField(db_index=True)
    # private_key = models.TextField(null=True, blank=True)
    merchant = models.BooleanField(default=False)
    block_type = models.SmallIntegerField(choices=BLOCK_TYPES, default=BLOCK_TYPE_NOT_BLOCKED)
    is_old = models.BooleanField(default=False)

    class Meta:
        # unique_together = ('currency', 'address')
        unique_together = ('id', 'currency')

    @property
    def is_deposits_blocked(self):
        return self.block_type in [self.BLOCK_TYPE_DEPOSIT, self.BLOCK_TYPE_DEPOSIT_AND_ACCUMULATION]
    
    @classmethod
    def update_balance(cls, id, currency, amount):
        with atomic():
            balance, created = cls.objects.select_for_update().get_or_create(id=id, currency=currency)
            balance.amount += amount
            balance.save()

        return balance.amount

    @classmethod
    def get_balance(cls, id, currency):
        try:
            balance = cls.objects.get(id=id, currency=currency)
            return balance.amount
        except cls.DoesNotExist:
            return None

    def regenerate(self):
        """Marks current wallet as old. Creates new 'clean' wallet."""
        wallet_account: BlockchainAccount = CRYPTO_WALLET_ACCOUNT_CREATORS[self.blockchain_currency]()
        with atomic():
            new_user_wallet = UserFiatWallet.objects.create(
                user_id=self.user_id,
                currency=self.currency,
                blockchain_currency=self.blockchain_currency,
                address=wallet_account.address,
                private_key=AESCoderDecoder(settings.CRYPTO_KEY).encrypt(
                    wallet_account.private_key
                ),
            )
            self.is_old = True
            self.save()
            return new_user_wallet

    def unblock(self):
        self.block_type = self.BLOCK_TYPE_NOT_BLOCKED
        super(UserFiatWallet, self).save()

    def __str__(self):
        res = f'{self.currency}'
        if self.is_old:
            res += ' OLD'
        if self.block_type != self.BLOCK_TYPE_NOT_BLOCKED:
            res += ' Blocked'
        return res
