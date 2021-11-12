from typing import Dict, List
import django
from django.core.exceptions import ValidationError

from blackbook import models

django.setup()


from django.test import TestCase
from django.utils import timezone

from blackbook.models import Currency, CurrencyConversion, Account, Transaction, TransactionLeg

from datetime import timedelta
from decimal import Decimal


class TransactionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.EUR = Currency.objects.create(code="EUR")
        cls.CHF = Currency.objects.create(code="CHF")

        cls.EUR_TO_CHF = CurrencyConversion.objects.create(base=cls.EUR, target=cls.CHF, multiplier=2)

    def testTransactionCreationNoMissingLegsSameCurrency(self):
        transactions = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": 7, "currency": "EUR"},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 3, "currency": "EUR"},
        ]

        transaction = Transaction.create(short_description="testTransactionCreationNoMissingLegsSameCurrency", transactions=transactions)
        transaction_legs = transaction.transaction_legs.all().select_related("account", "currency")

        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(len(transaction_legs), 3)

        for transaction_leg in transaction_legs:
            if transaction_leg.account.name == "Account Naam 1":
                self.assertEqual(transaction_leg.amount, -10)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.ASSET_ACCOUNT)
            elif transaction_leg.account.name == "Expense Type 1":
                self.assertEqual(transaction_leg.amount, 7)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)
            else:
                self.assertEqual(transaction_leg.amount, 3)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)

    def testTransactionCreationNoMissingLegsMultipleCurrencies(self):
        transactions = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": 14, "currency": "CHF"},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 3, "currency": "EUR"},
        ]

        transaction = Transaction.create(short_description="testTransactionCreationNoMissingLegsMultipleCurrencies", transactions=transactions)
        transaction_legs = transaction.transaction_legs.all().select_related("account", "currency")

        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(len(transaction_legs), 3)

        for transaction_leg in transaction_legs:
            if transaction_leg.account.name == "Account Naam 1":
                self.assertEqual(transaction_leg.amount, -10)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.ASSET_ACCOUNT)
            elif transaction_leg.account.name == "Expense Type 1":
                self.assertEqual(transaction_leg.amount, 14)
                self.assertEqual(transaction_leg.currency.code, "CHF")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)
            else:
                self.assertEqual(transaction_leg.amount, 3)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)

    def testTransactionCreationInbalanceLegs(self):
        transactions_same_currencies = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": 5, "currency": "EUR"},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 3, "currency": "EUR"},
        ]
        transactions_different_currencies = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": 5, "currency": "CHF"},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 3, "currency": "EUR"},
        ]

        with self.assertRaises(ValidationError):
            Transaction.create(short_description="testTransactionCreationInbalanceLegs", transactions=transactions_same_currencies)

        with self.assertRaises(ValidationError):
            Transaction.create(short_description="testTransactionCreationInbalanceLegs", transactions=transactions_different_currencies)

    def testTransactionCreationEmptyTransactionSameCurrency(self):
        transactions = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": "", "currency": "EUR"},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 3, "currency": "EUR"},
        ]

        transaction = Transaction.create(short_description="testTransactionCreationEmptyTransactionSameCurrency", transactions=transactions)
        transaction_legs = transaction.transaction_legs.all().select_related("account", "currency")

        for transaction_leg in transaction_legs:
            if transaction_leg.account.name == "Account Naam 1":
                self.assertEqual(transaction_leg.amount, -10)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.ASSET_ACCOUNT)
            elif transaction_leg.account.name == "Expense Type 1":
                self.assertEqual(transaction_leg.amount, 7)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)
            else:
                self.assertEqual(transaction_leg.amount, 3)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)

        transactions = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": "", "currency": ""},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 3, "currency": "EUR"},
        ]

        transaction = Transaction.create(short_description="testTransactionCreationEmptyTransactionSameCurrency", transactions=transactions)
        transaction_legs = transaction.transaction_legs.all().select_related("account", "currency")

        for transaction_leg in transaction_legs:
            if transaction_leg.account.name == "Account Naam 1":
                self.assertEqual(transaction_leg.amount, -10)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.ASSET_ACCOUNT)
            elif transaction_leg.account.name == "Expense Type 1":
                self.assertEqual(transaction_leg.amount, 7)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)
            else:
                self.assertEqual(transaction_leg.amount, 3)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)

    def testTransactionCreationEmptyTransactionDifferentCurrency(self):
        transactions = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": "", "currency": "CHF"},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 3, "currency": "EUR"},
        ]

        transaction = Transaction.create(short_description="testTransactionCreationEmptyTransactionDifferentCurrency", transactions=transactions)
        transaction_legs = transaction.transaction_legs.all().select_related("account", "currency")

        for transaction_leg in transaction_legs:
            if transaction_leg.account.name == "Account Naam 1":
                self.assertEqual(transaction_leg.amount, -10)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.ASSET_ACCOUNT)
            elif transaction_leg.account.name == "Expense Type 1":
                self.assertEqual(transaction_leg.amount, 14)
                self.assertEqual(transaction_leg.currency.code, "CHF")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)
            else:
                self.assertEqual(transaction_leg.amount, 3)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)

        transactions = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": "", "currency": ""},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 6, "currency": "CHF"},
        ]

        transaction = Transaction.create(short_description="testTransactionCreationEmptyTransactionDifferentCurrency", transactions=transactions)
        transaction_legs = transaction.transaction_legs.all().select_related("account", "currency")

        for transaction_leg in transaction_legs:
            if transaction_leg.account.name == "Account Naam 1":
                self.assertEqual(transaction_leg.amount, -10)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.ASSET_ACCOUNT)
            elif transaction_leg.account.name == "Expense Type 1":
                self.assertEqual(transaction_leg.amount, 7)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)
            else:
                self.assertEqual(transaction_leg.amount, 6)
                self.assertEqual(transaction_leg.currency.code, "CHF")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)

    def testTransactionCreationMultipleEmpty(self):
        transactions = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": "", "currency": ""},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": "", "currency": "CHF"},
        ]

        with self.assertRaises(ValidationError):
            Transaction.create(short_description="testTransactionCreationMultipleEmpty", transactions=transactions)

    def testUpdateTransactions(self):
        transactions = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -10, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": 7, "currency": "EUR"},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 3, "currency": "EUR"},
        ]
        transactions_updated = [
            {"account": "Assets:Bank:Account Type:Account Naam 1", "amount": -20, "currency": "EUR"},
            {"account": "Expenses:Expense Type 1", "amount": "", "currency": ""},
            {"account": "Expenses:Expense Type 2:Expense Subtype 1", "amount": 10, "currency": "CHF"},
        ]

        transaction = Transaction.create(short_description="testUpdateTransactions", transactions=transactions)
        transaction.update_transactions(transactions=transactions_updated)
        transaction_legs = transaction.transaction_legs.all().select_related("account", "currency")

        self.assertEqual(len(transaction_legs), 3)
        for transaction_leg in transaction_legs:
            if transaction_leg.account.name == "Account Naam 1":
                self.assertEqual(transaction_leg.amount, -20)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.ASSET_ACCOUNT)
            elif transaction_leg.account.name == "Expense Type 1":
                self.assertEqual(transaction_leg.amount, 15)
                self.assertEqual(transaction_leg.currency.code, "EUR")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)
            else:
                self.assertEqual(transaction_leg.amount, 10)
                self.assertEqual(transaction_leg.currency.code, "CHF")
                self.assertEqual(transaction_leg.account.type, Account.AccountType.EXPENSE_ACCOUNT)


class AccountTest(TestCase):
    def testAccountCreation(self):
        output = Account.get_or_create("Assets:Bank:Account Type:Account Name")
        self.assertIsInstance(output, Account)
        self.assertEqual(output.parent.name, "Account Type")
        self.assertEqual(output.type, Account.AccountType.ASSET_ACCOUNT)

        output = Account.get_or_create("Assets:Bank:Account Type:Account Name", return_last=False)
        self.assertIsInstance(output, List)
        self.assertEqual(len(output), 3)

        self.assertEqual(output[0][0].name, "Bank")
        self.assertEqual(output[0][0].type, Account.AccountType.ASSET_ACCOUNT)
        self.assertEqual(output[1][0].name, "Account Type")
        self.assertEqual(output[1][0].type, Account.AccountType.ASSET_ACCOUNT)
        self.assertEqual(output[2][0].name, "Account Name")
        self.assertEqual(output[2][0].type, Account.AccountType.ASSET_ACCOUNT)

        self.assertFalse(output[0][1])
        self.assertFalse(output[1][1])
        self.assertFalse(output[2][1])


class CurrencyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.EUR = Currency.objects.create(code="EUR")
        cls.CHF = Currency.objects.create(code="CHF")
        cls.USD = Currency.objects.create(code="USD")

        cls.EUR_TO_CHF = CurrencyConversion.objects.create(base=cls.EUR, target=cls.CHF, multiplier=2)

    def testConversionWithString(self):
        eur_to_chf = CurrencyConversion.convert(base="EUR", target="CHF", amount=1)
        chf_to_eur = CurrencyConversion.convert(base="CHF", target="EUR", amount=1)

        self.assertEqual(eur_to_chf, 2)
        self.assertEqual(chf_to_eur, 0.5)

    def testConversionWithLowercaseString(self):
        eur_to_chf = CurrencyConversion.convert(base="eur", target="chf", amount=1)
        chf_to_eur = CurrencyConversion.convert(base="chf", target="eur", amount=1)

        self.assertEqual(eur_to_chf, 2)
        self.assertEqual(chf_to_eur, 0.5)

    def testConversionWithSameString(self):
        eur_to_eur = CurrencyConversion.convert(base="EUR", target="EUR", amount=1)

        self.assertEqual(eur_to_eur, 1)

    def testConversionWithStringUnknownCurrency(self):
        usd_to_eur = CurrencyConversion.convert(base="USD", target="EUR", amount=1)
        eur_to_usd = CurrencyConversion.convert(base="EUR", target="USD", amount=1)

        self.assertEqual(usd_to_eur, 1)
        self.assertEqual(eur_to_usd, 1)

    def testConversionWithObjects(self):
        eur_to_chf = CurrencyConversion.convert(base=self.EUR, target=self.CHF, amount=1)
        chf_to_eur = CurrencyConversion.convert(base=self.CHF, target=self.EUR, amount=1)

        self.assertEqual(eur_to_chf, 2)
        self.assertEqual(chf_to_eur, 0.5)

    def testConversionFromConversionObjectWithString(self):
        eur_to_chf = self.EUR_TO_CHF.convert_to(target="CHF", amount=1)

        self.assertEqual(eur_to_chf, 2)

    def testConversionFromConversionObjectWithObject(self):
        eur_to_chf = self.EUR_TO_CHF.convert_to(target=self.CHF, amount=1)

        self.assertEqual(eur_to_chf, 2)

    def testConversionWithNewerReverseConversionTimestamp(self):
        date_yesterday = timezone.now() - timedelta(days=1)

        CurrencyConversion.objects.create(base=self.EUR, target=self.USD, multiplier=2, timestamp=date_yesterday)
        CurrencyConversion.objects.create(base=self.USD, target=self.EUR, multiplier=3)

        eur_to_usd = CurrencyConversion.convert(base="EUR", target="USD", amount=1)

        self.assertAlmostEqual(eur_to_usd, Decimal(0.33), places=2)
