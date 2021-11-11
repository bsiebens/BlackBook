from django.db import models
from django.db.models import Q
from django.utils import timezone

from decimal import Decimal


class Currency(models.Model):
    code = models.CharField(max_length=10)

    class Meta:
        ordering = ["code"]
        verbose_name_plural = "currencies"

    def __str__(self):
        return self.code


class CurrencyConversion(models.Model):
    base = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="base_currency")
    target = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="target_currency")
    multiplier = models.DecimalField(max_digits=20, decimal_places=10)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return "1 {i.base} = {i.multiplier} {i.target} ({timestamp})".format(i=self, timestamp=self.timestamp.strftime("%d %b %Y %H:%m"))

    def convert_to(self, target, amount=1):
        return self.__class__.convert(base=self.base.code, target=target, amount=amount)

    @classmethod
    def convert(cls, base, target, amount):
        conversion_object = None
        multiplier = 1

        if type(base) == str:
            base = base.upper()

        if type(target) == str:
            target = target.upper()

        if base == target:
            return amount

        try:
            conversion_object = (
                cls.objects.filter(Q(base__code=base, target__code=target) | Q(base__code=target, target__code=base))
                .select_related()
                .latest("timestamp")
            )

            if conversion_object.base.code == str(base):
                multiplier = conversion_object.multiplier
            else:
                multiplier = 1 / conversion_object.multiplier

        except cls.DoesNotExist:
            pass

        return Decimal(amount) * multiplier
