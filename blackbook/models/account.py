from django.db import models
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError

from localflavor.generic.models import IBANField
from djmoney.money import Money
from decimal import Decimal
from mptt.models import MPTTModel, TreeForeignKey

from .currency import Currency
from ..utilities import unique_slugify

import uuid


class Account(MPTTModel):
    class AccountType(models.TextChoices):
        ASSET_ACCOUNT = "assets", "Asset Account"
        INCOME_ACCOUNT = "income", "Income Account"
        EXPENSE_ACCOUNT = "expenses", "Expense Account"
        LIABILITIES_ACCOUNT = "liabilities", "Liabilities"
        CASH_ACCOUNT = "cash", "Cash Account"

    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    name = models.CharField(max_length=250)
    slug = models.SlugField(editable=False, db_index=True, unique=True)
    uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, db_index=True, unique=True)
    active = models.BooleanField("active?", default=True)
    net_worth = models.BooleanField("include in net worth?", default=True, help_text="Include this account when calculating total net worth?")
    dashboard = models.BooleanField("show on dashboard?", default=True, help_text="Show this transaction on the dashboard?")
    currencies = models.ManyToManyField(Currency, blank=True)
    type = models.CharField(max_length=50, choices=AccountType.choices)
    icon = models.CharField(max_length=50)
    iban = IBANField("IBAN", null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["parent", "name"], name="unique_account_name_for_parent")]

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent is not None:
            if self.type != self.parent.type:
                raise ValidationError(
                    {"type": "Account type must be the same as the account type of the parent account (%s)" % self.parent.get_type_display()}
                )

    def save(self, *args, **kwargs):
        type_to_icon = {
            "assets": "fa-landmark",
            "income": "fa-donate",
            "expenses": "fa-file-invoice-dollar",
            "liabilities": "fa-home",
            "cash": "fa-coins",
        }

        self.clean()

        unique_slugify(self, self.name)
        self.icon = type_to_icon[self.type]

        super(Account, self).save(*args, **kwargs)

    @classmethod
    def get_or_create(cls, account_string, return_last=True):
        account_tree = account_string.split(":")
        accounts = []
        parent_account = None
        account_type = None

        for index, account_name in enumerate(account_tree):
            if index == 0:
                # If index == 0, we don't create an account but verify if the type of account is correct and set that accordingly
                if account_name.lower() not in cls.AccountType.values:
                    raise ValidationError("Incorrect account type set as first value.")

                account_type = account_name.lower()

            else:
                account, created = cls.objects.get_or_create(name=account_name, parent=parent_account, type=account_type)
                accounts.append((account, created))
                parent_account = account

        if return_last:
            return accounts[-1][0]

        return accounts

    @cached_property
    def starting_balance(self):
        # from .transaction import TransactionJournal

        # try:
        #     opening_balance = (
        #         self.transactions.filter(journal__type=TransactionJournal.TransactionType.START).get(journal__date=self.created.date()).amount
        #     )

        #     return opening_balance

        # except:
        #     return Money(0, self.currency)
        return Money(0, "EUR")

    @cached_property
    def balance(self):
        return self.balance_until_date()

    def balance_until_date(self, date=timezone.localdate()):
        # try:
        #     total_amount = self.transactions.filter(journal__date__lte=date).aggregate(total=Coalesce(Sum("amount"), Decimal(0)))["total"]
        #     total = Money(total_amount, self.currency)

        #     return total - Money(self.virtual_balance, self.currency)

        # except:
        #     return Money(0, self.currency) - Money(self.virtual_balance, self.currency)
        return Money(0, "EUR")
