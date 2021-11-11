import django

django.setup()


from django.test import TestCase
from django.utils import timezone

from blackbook.models import Currency, CurrencyConversion

from datetime import timedelta
from decimal import Decimal


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
        date_yesterday = timezone.localdate() - timedelta(days=1)
        CurrencyConversion.objects.create(base=self.EUR, target=self.USD, multiplier=2, timestamp=date_yesterday)
        CurrencyConversion.objects.create(base=self.USD, target=self.EUR, multiplier=3)

        eur_to_usd = CurrencyConversion.convert(base="EUR", target="USD", amount=1)

        self.assertAlmostEqual(eur_to_usd, Decimal(0.33), places=2)
