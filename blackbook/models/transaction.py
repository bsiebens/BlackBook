from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from djmoney.models.fields import MoneyField
from djmoney.money import Money

from .base import get_default_currency
from .account import Account
from .category import Category
from .budget import BudgetPeriod

import uuid


class TransactionJournal(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        START = "start", "Opening balance"
        RECONCILIATION = "reconciliation", "Reconciliation"
        TRANSFER = "transfer", "Transfer"
        WITHDRAWAL = "withdrawal", "Withdrawal"

    type = models.CharField(max_length=50, choices=TransactionType.choices, default=TransactionType.WITHDRAWAL)
    date = models.DateField(default=timezone.localdate)
    short_description = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, db_index=True, unique=True)
    budget = models.ForeignKey(BudgetPeriod, on_delete=models.SET_NULL, blank=True, null=True, related_name="transactions")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="transactions")
    source_accounts = models.JSONField(null=True)
    destination_accounts = models.JSONField(null=True)
    amount = MoneyField("amount", max_digits=15, decimal_places=2, default_currency=get_default_currency(), default=0)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "created"]
        get_latest_by = "date"

    def __str__(self):
        return self.short_description

    def _verify_transaction_type(self, type, transactions):
        if type in [self.TransactionType.START, self.TransactionType.RECONCILIATION]:
            return type

        owned_accounts = [Account.AccountType.ASSET_ACCOUNT, Account.AccountType.LIABILITIES_ACCOUNT]

        source_accounts = []
        destination_accounts = []

        for transaction in transactions:
            if transaction["amount"].amount > 0:
                destination_accounts.append(transaction["account"])
            else:
                source_accounts.append(transaction["account"])

        source_accounts = list(set(source_accounts))
        destination_accounts = list(set(destination_accounts))

        source_accounts_owned = True
        destination_accounts_owned = True

        if len(source_accounts) > 0:
            for account in source_accounts:
                if account.type not in owned_accounts:
                    source_accounts_owned = False

        if len(destination_accounts) > 0:
            for account in destination_accounts:
                if account.type not in owned_accounts:
                    destination_accounts_owned = False

        if len(source_accounts) > 0:
            if source_accounts_owned:
                if len(destination_accounts) > 0 and destination_accounts_owned:
                    return self.TransactionType.TRANSFER

                return self.TransactionType.WITHDRAWAL

            else:
                if len(destination_accounts) > 0 and destination_accounts_owned:
                    return self.TransactionType.DEPOSIT

                return self.TransactionType.WITHDRAWAL

        return self.TransactionType.DEPOSIT

    def _create_transactions(self, transactions):
        source_accounts = []
        destination_accounts = []

        for transaction in transactions:
            if transaction["amount"].amount > 0:
                destination_accounts.append(transaction["account"])
            else:
                source_accounts.append(transaction["account"])

        if self.type in [self.TransactionType.DEPOSIT, self.TransactionType.RECONCILIATION]:
            if len(destination_accounts) == 0:
                raise AttributeError("There should be at least one receiving transaction for this transaction type %s" % self.type)

        elif self.type == self.TransactionType.WITHDRAWAL:
            if len(source_accounts) == 0:
                raise AttributeError("There should be at least one spending transaction for this transaction type %s" % self.type)

        for transaction in transactions:
            if str(transaction["amount"].currency) != str(transaction["account"].currency):
                raise AttributeError("Amount should be in the same currency as the account it relates to (%s)" % transaction)

            self.transactions.create(
                account=transaction["account"], amount=transaction["amount"], foreign_amount=transaction.get("foreign_amount", None)
            )

    @classmethod
    def create(cls, transactions):
        """Transactions should be in a fixed format
        {
            "short_description", "description", "date", "type", "category", "budget", "transactions" [{
                "account", "amount", "foreign_amount"
            }]
        }"""
        journal = cls.objects.create(
            date=transactions["date"],
            short_description=transactions["short_description"],
            type=transactions["type"],
            description=transactions.get("description", None),
            category=transactions.get("category", None),
            budget=transactions.get("budget", None),
        )

        journal.type = journal._verify_transaction_type(type=transactions["type"], transactions=transactions["transactions"])
        journal._create_transactions(transactions=transactions["transactions"])
        journal.update_accounts()

        return journal

    def update(self, transactions):
        self.short_description = transactions["short_description"]
        self.description = transactions["description"]
        self.date = transactions["date"]
        self.type = transactions["type"]
        self.category = transactions.get("category", None)
        self.budget = transactions.get("budget", None)

        self.save()

        self.transactions.all().delete()
        self._create_transactions(transactions=transactions["transactions"])
        self.update_accounts()

    def update_accounts(self):
        source_accounts = self.get_source_accounts()
        destination_accounts = self.get_destination_accounts()

        self.source_accounts = [
            {"account": account.name, "slug": account.slug, "type": account.get_type_display(), "link_type": account.type, "icon": account.icon}
            for account in source_accounts
        ]
        self.destination_accounts = [
            {"account": account.name, "slug": account.slug, "type": account.get_type_display(), "link_type": account.type, "icon": account.icon}
            for account in destination_accounts
        ]

        self.amount = self.transactions.first().amount
        if self.type == self.TransactionType.WITHDRAWAL:
            self.amount = self.transactions.get(amount__lte=0).amount
        if self.type == self.TransactionType.DEPOSIT or type == self.TransactionType.TRANSFER:
            self.amount = self.transactions.get(amount__gte=0).amount

        if self.type == self.TransactionType.TRANSFER:
            self.amount = abs(self.amount)

        self.save()

    def get_source_accounts(self):
        accounts = Account.objects.filter(transactions__journal=self, transactions__amount__lte=0).distinct()

        return [account for account in accounts]

    def get_destination_accounts(self):
        accounts = Account.objects.filter(transactions__journal=self, transactions__amount__gte=0).distinct()

        return [account for account in accounts]


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True, related_name="transactions")
    amount = MoneyField("amount", max_digits=15, decimal_places=2, default_currency=get_default_currency(), default=0)
    foreign_amount = MoneyField(
        "foreign amount", max_digits=15, decimal_places=2, default_currency=get_default_currency(), default=0, blank=True, null=True
    )
    uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, db_index=True, unique=True)
    journal = models.ForeignKey(TransactionJournal, on_delete=models.CASCADE, related_name="transactions")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.journal.short_description
