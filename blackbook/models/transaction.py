from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, base
from django.utils import timezone
from django.utils.functional import cached_property

from djmoney.models.fields import MoneyField
from djmoney.money import Money

from .base import get_default_currency
from .account import Account
from .currency import Currency, CurrencyConversion
from .category import Category
from .budget import BudgetPeriod

import uuid


class Transaction(models.Model):
    date = models.DateField(default=timezone.localdate)
    short_description = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    payee = models.CharField(max_length=250, blank=True, null=True)
    uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, db_index=True, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "created"]
        get_latest_by = "date"

    def __str__(self):
        return self.short_description

    def save(self, *args, **kwargs):
        self.clean()

        super(Transaction, self).save(*args, **kwargs)

    @classmethod
    def create(cls, short_description, transactions, date=timezone.localdate(), description=None, payee=None, category=None):
        """Transactions should be in a fixed format
        {
            "account", "amount", "currency"
        }"""

        # In order to proceed we will first convert all values in the transactions dictionary to proper objects
        for transaction in transactions:
            if type(transaction["currency"]) == str:
                transaction["currency"], created = Currency.objects.get_or_create(code=transaction["currency"])

            if type(transaction["account"]) == str:
                # Here the format should be with a ":" separting the different accounts, the first level should always specify the account type
                account_tree = Account.get_or_create(transaction["account"])
                transaction["account"] = account_tree[-1][0]

        # Now we run a check on the different transaction legs to verify if the sum of all legs equals to zero.
        # One leg is allowed to be "empty", in case it has a currency set we will use that currency to fill up the leg, otherwise it will default to
        # a random base currency that's used on the transaction.
        total_amount_per_currency = {}
        total_baseline_amount = 0
        empty_transaction_index = -1

        for index, transaction in enumerate(transactions):
            





    @classmethod
    def create2(cls, short_description, transactions, date=timezone.localdate(), description=None, payee=None, category=None):
        # For each transaction we attempt to convert string values into proper objects
        for transaction in transactions:
            if type(transaction["currency"]) == str:
                pass

        # First run a check on the different transactions to confirm if they equal to zero
        total_amount_per_currency = {}
        total_baseline_amount = 0
        empty_transaction_index = -1

        for index, transaction in enumerate(transactions):
            if transaction["amount"] is None or transaction["amount"] == "":
                if empty_transaction_index != -1:
                    raise ValidationError("Only 1 transaction leg can have an empty amount specificed.")

                empty_transaction_index = index

            if transaction["amount"] != "" and transaction["amount"] is not None:
                total_amount_per_currency[transaction["currency"]] = total_amount_per_currency.get(transaction["currency"], 0) + transaction["amount"]

        if len(total_amount_per_currency.keys()) >= 1:
            baseline_currency = None

            for currency, amount in total_amount_per_currency.items():
                if baseline_currency is None:
                    baseline_currency = currency

                if amount == "" or amount is None:
                    continue

                total_baseline_amount += CurrencyConversion.convert(base=currency, target=baseline_currency, amount=amount)

            if empty_transaction_index != -1:
                currency = transactions[empty_transaction_index]["currency"]

                if currency is None or currency == "":
                    currency = baseline_currency

                transactions[empty_transaction_index]["amount"] = (
                    CurrencyConversion.convert(base=baseline_currency, target=currency, amount=total_baseline_amount) * -1
                )
                transactions[empty_transaction_index]["currency"] = currency

                total_baseline_amount = 0

            if total_baseline_amount != 0:
                raise ValidationError(
                    "Total sum of all transaction legs should be 0 (now {total_sum} {base_currency}).".format(
                        total_sum=total_baseline_amount, base_currency=baseline_currency
                    )
                )

        transaction_object = cls.objects.create(
            short_description=short_description, date=date, description=description, payee=payee, category=category
        )

        transactionlegs = []
        for transaction in transactions:
            account, created = Account.objects.get_or_create(name=transaction["name"])
            currency, created = Currency.objects.get_or_create(code=transaction["currency"])

            transactionlegs.append(TransactionLeg(transaction=transaction_object, account=account, amount=transaction["amount"], currency=currency))

        TransactionLeg.objects.bulk_create(transactionlegs)


class TransactionLeg(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="transaction_legs")
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    currency = models.ForeignKey(Currency, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "{i.account} {i.amount} {i.currency.code}".format(i=self)


# class TransactionJournal(models.Model):
#     class TransactionType(models.TextChoices):
#         DEPOSIT = "deposit", "Deposit"
#         START = "start", "Opening balance"
#         RECONCILIATION = "reconciliation", "Reconciliation"
#         TRANSFER = "transfer", "Transfer"
#         WITHDRAWAL = "withdrawal", "Withdrawal"

#     type = models.CharField(max_length=50, choices=TransactionType.choices, default=TransactionType.WITHDRAWAL)
#     date = models.DateField(default=timezone.localdate)
#     short_description = models.CharField(max_length=150)
#     description = models.TextField(blank=True, null=True)
#     uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, db_index=True, unique=True)
#     budget = models.ForeignKey(BudgetPeriod, on_delete=models.SET_NULL, blank=True, null=True, related_name="transactions")
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="transactions")
#     source_accounts = models.JSONField(null=True)
#     destination_accounts = models.JSONField(null=True)
#     amount = MoneyField("amount", max_digits=15, decimal_places=2, default_currency=get_default_currency(), default=0)

#     created = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["date", "created"]
#         get_latest_by = "date"

#     def __str__(self):
#         return self.short_description

#     def _verify_transaction_type(self, type, transactions):
#         if type in [self.TransactionType.START, self.TransactionType.RECONCILIATION]:
#             return type

#         owned_accounts = [Account.AccountType.ASSET_ACCOUNT, Account.AccountType.LIABILITIES_ACCOUNT]

#         source_accounts = []
#         destination_accounts = []

#         for transaction in transactions:
#             if transaction["amount"].amount > 0:
#                 destination_accounts.append(transaction["account"])
#             else:
#                 source_accounts.append(transaction["account"])

#         source_accounts = list(set(source_accounts))
#         destination_accounts = list(set(destination_accounts))

#         source_accounts_owned = True
#         destination_accounts_owned = True

#         if len(source_accounts) > 0:
#             for account in source_accounts:
#                 if account.type not in owned_accounts:
#                     source_accounts_owned = False

#         if len(destination_accounts) > 0:
#             for account in destination_accounts:
#                 if account.type not in owned_accounts:
#                     destination_accounts_owned = False

#         if len(source_accounts) > 0:
#             if source_accounts_owned:
#                 if len(destination_accounts) > 0 and destination_accounts_owned:
#                     return self.TransactionType.TRANSFER

#                 return self.TransactionType.WITHDRAWAL

#             else:
#                 if len(destination_accounts) > 0 and destination_accounts_owned:
#                     return self.TransactionType.DEPOSIT

#                 return self.TransactionType.WITHDRAWAL

#         return self.TransactionType.DEPOSIT

#     def _create_transactions(self, transactions):
#         source_accounts = []
#         destination_accounts = []

#         for transaction in transactions:
#             if transaction["amount"].amount > 0:
#                 destination_accounts.append(transaction["account"])
#             else:
#                 source_accounts.append(transaction["account"])

#         if self.type in [self.TransactionType.DEPOSIT, self.TransactionType.RECONCILIATION]:
#             if len(destination_accounts) == 0:
#                 raise AttributeError("There should be at least one receiving transaction for this transaction type %s" % self.type)

#         elif self.type == self.TransactionType.WITHDRAWAL:
#             if len(source_accounts) == 0:
#                 raise AttributeError("There should be at least one spending transaction for this transaction type %s" % self.type)

#         for transaction in transactions:
#             if str(transaction["amount"].currency) != str(transaction["account"].currency):
#                 raise AttributeError("Amount should be in the same currency as the account it relates to (%s)" % transaction)

#             self.transactions.create(
#                 account=transaction["account"], amount=transaction["amount"], foreign_amount=transaction.get("foreign_amount", None)
#             )

#     @classmethod
#     def create(cls, transactions):
#         """Transactions should be in a fixed format
#         {
#             "short_description", "description", "date", "type", "category", "budget", "transactions" [{
#                 "account", "amount", "foreign_amount"
#             }]
#         }"""
#         journal = cls.objects.create(
#             date=transactions["date"],
#             short_description=transactions["short_description"],
#             type=transactions["type"],
#             description=transactions.get("description", None),
#             category=transactions.get("category", None),
#             budget=transactions.get("budget", None),
#         )

#         journal.type = journal._verify_transaction_type(type=transactions["type"], transactions=transactions["transactions"])
#         journal._create_transactions(transactions=transactions["transactions"])
#         journal.update_accounts()

#         return journal

#     def update(self, transactions):
#         self.short_description = transactions["short_description"]
#         self.description = transactions["description"]
#         self.date = transactions["date"]
#         self.type = transactions["type"]
#         self.category = transactions.get("category", None)
#         self.budget = transactions.get("budget", None)

#         self.save()

#         self.transactions.all().delete()
#         self._create_transactions(transactions=transactions["transactions"])
#         self.update_accounts()

#     def update_accounts(self):
#         source_accounts = self.get_source_accounts()
#         destination_accounts = self.get_destination_accounts()

#         self.source_accounts = [
#             {"account": account.name, "slug": account.slug, "type": account.get_type_display(), "link_type": account.type, "icon": account.icon}
#             for account in source_accounts
#         ]
#         self.destination_accounts = [
#             {"account": account.name, "slug": account.slug, "type": account.get_type_display(), "link_type": account.type, "icon": account.icon}
#             for account in destination_accounts
#         ]

#         self.amount = self.transactions.first().amount
#         if self.type == self.TransactionType.WITHDRAWAL:
#             self.amount = self.transactions.get(amount__lte=0).amount
#         if self.type == self.TransactionType.DEPOSIT or type == self.TransactionType.TRANSFER:
#             self.amount = self.transactions.get(amount__gte=0).amount

#         if self.type == self.TransactionType.TRANSFER:
#             self.amount = abs(self.amount)

#         self.save()

#     def get_source_accounts(self):
#         accounts = Account.objects.filter(transactions__journal=self, transactions__amount__lte=0).distinct()

#         return [account for account in accounts]

#     def get_destination_accounts(self):
#         accounts = Account.objects.filter(transactions__journal=self, transactions__amount__gte=0).distinct()

#         return [account for account in accounts]


# class Transaction(models.Model):
#     account = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True, related_name="transactions")
#     amount = MoneyField("amount", max_digits=15, decimal_places=2, default_currency=get_default_currency(), default=0)
#     foreign_amount = MoneyField(
#         "foreign amount", max_digits=15, decimal_places=2, default_currency=get_default_currency(), default=0, blank=True, null=True
#     )
#     uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, db_index=True, unique=True)
#     journal = models.ForeignKey(TransactionJournal, on_delete=models.CASCADE, related_name="transactions")

#     created = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.journal.short_description
