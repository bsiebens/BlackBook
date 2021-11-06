from django.db import models
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.functional import cached_property

from localflavor.generic.models import IBANField
from djmoney.money import Money
from djmoney.models.fields import CurrencyField
from decimal import Decimal

from .base import get_default_currency, get_currency_choices
from ..utilities import calculate_period, unique_slugify

import uuid


class Account(models.Model):
    class AccountType(models.TextChoices):
        ASSET_ACCOUNT = "assetaccount", "Asset Account"
        INCOME_ACCOUNT = "incomeaccount", "Income Account"
        EXPENSE_ACCOUNT = "expenseaccount", "Expense Account"
        LIABILITIES_ACCOUNT = "liabilitiesaccount", "Liabilities"
        CASH_ACCOUNT = "cashaccount", "Cash Account"

    name = models.CharField(max_length=250)
    slug = models.SlugField(editable=False, db_index=True, unique=True)
    uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, db_index=True, unique=True)
    active = models.BooleanField("active?", default=True)
    net_worth = models.BooleanField("include in net worth?", default=True, help_text="Include this account when calculating total net worth?")
    dashboard = models.BooleanField("show on dashboard?", default=True, help_text="Show this transaction on the dashboard?")
    currency = CurrencyField(default=get_default_currency(), choices=get_currency_choices())
    virtual_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        help_text="Enter a number here to have BlackBook treat this as the new zero point for this account. Default should always be 0.0",
    )
    type = models.CharField(max_length=50, choices=AccountType.choices)
    icon = models.CharField(max_length=50)
    iban = IBANField("IBAN", null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["type", "name"], name="unique_account_name")]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        type_to_icon = {
            "assetaccount": "fa-landmark",
            "incomeaccount": "fa-donate",
            "expenseaccount": "fa-file-invoice-dollar",
            "liabilitiesaccount": "fa-home",
            "cashaccount": "fa-coins",
        }

        unique_slugify(self, self.name)
        self.icon = type_to_icon[self.type]

        super(Account, self).save(*args, **kwargs)

    @cached_property
    def starting_balance(self):
        from .transaction import TransactionJournal

        try:
            opening_balance = (
                self.transactions.filter(journal__type=TransactionJournal.TransactionType.START).get(journal__date=self.created.date()).amount
            )

            return opening_balance

        except:
            return Money(0, self.currency)

    @cached_property
    def balance(self):
        return self.balance_until_date()

    def balance_until_date(self, date=timezone.localdate()):
        try:
            total_amount = self.transactions.filter(journal__date__lte=date).aggregate(total=Coalesce(Sum("amount"), Decimal(0)))["total"]
            total = Money(total_amount, self.currency)

            return total - Money(self.virtual_balance, self.currency)

        except:
            return Money(0, self.currency) - Money(self.virtual_balance, self.currency)
