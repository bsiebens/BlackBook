from django.db import models
from django.db.models import Sum
from django.utils import timezone

from djmoney.models.fields import MoneyField
from djmoney.money import Money

from .base import get_default_currency

import uuid


class PayCheck(models.Model):
    date = models.DateField("date", default=timezone.localdate)
    net_amount = MoneyField("net amount", max_digits=15, decimal_places=2, default_currency=get_default_currency(), default=0)
    gross_amount = MoneyField("gross amount", max_digits=15, decimal_places=2, default_currency=get_default_currency(), default=0)
    uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, db_index=True, unique=True)
    hidden = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "PayCheck {date}".format(date=self.date.strftime("%b %Y"))

    def update_amount(self, currency=get_default_currency()):
        self.net_amount = Money(self.items.aggregate(amount=models.Sum("real_amount"))["amount"], currency)
        self.gross_amount = Money(
            self.items.filter(category__type=PayCheckItemCategory.ItemType.GROSS).aggregate(amount=models.Sum("real_amount"))["amount"], currency
        )
        self.save()


class PayCheckItemCategory(models.Model):
    class ItemType(models.TextChoices):
        GROSS = "Gross amount"
        TAXABLE = "Taxable amount"
        NET = "Net amount"

    name = models.CharField("name", max_length=250, unique=True, db_index=True)
    type = models.CharField("type", max_length=50, choices=ItemType.choices, default=ItemType.GROSS)
    counterbalance = models.BooleanField(default=False)
    counterbalance_percentage = models.DecimalField(
        help_text="100% means the entire amount will be counterbalanced.", max_digits=5, decimal_places=2, default=0
    )
    default_amount = MoneyField(max_digits=10, decimal_places=2, default_currency=get_default_currency(), default=0)
    default = models.BooleanField(default=False, help_text="Show this category as a default field on a new paycheck?")

    class Meta:
        verbose_name_plural = "paycheck item categories"

    def __str__(self):
        return self.name


class PayCheckItem(models.Model):
    paycheck = models.ForeignKey(PayCheck, on_delete=models.CASCADE, related_name="items")
    category = models.ForeignKey(PayCheckItemCategory, on_delete=models.CASCADE, related_name="items")
    amount = MoneyField("amount", max_digits=10, decimal_places=2, default_currency=get_default_currency(), default=0)
    real_amount = MoneyField(max_digits=10, decimal_places=2, default_currency=get_default_currency(), default=0)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{i.category.name}: {i.amount}".format(i=self)

    def save(self, *args, **kwargs):
        self.real_amount = self.amount

        if self.category.counterbalance:
            self.real_amount = self.amount - (self.amount / 100) * self.category.counterbalance_percentage

        super(PayCheckItem, self).save(*args, **kwargs)


class Bonus(models.Model):
    date = models.DateField(default=timezone.localdate)
    gross_amount = MoneyField(max_digits=10, decimal_places=2, default_currency=get_default_currency(), default=0)
    net_amount = MoneyField(max_digits=10, decimal_places=2, default_currency=get_default_currency(), default=0)
    taxes = MoneyField(max_digits=10, decimal_places=2, default_currency=get_default_currency(), default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "bonuses"

    def __str__(self):
        return "Bonus {date}".format(date=self.date.strftime("%b %Y"))

    def save(self, *args, **kwargs):
        self.taxes = self.gross_amount - self.net_amount
        self.tax_percentage = (self.taxes / self.gross_amount) * 100

        super(Bonus, self).save(*args, **kwargs)
