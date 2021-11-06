from django.db import models
from django.utils import timezone


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

    def convert(self, target, amount=1):
        return self.__class__.convert(base=self.base.code, target=target, amount=amount)

    @classmethod
    def convert(cls, base, target, amount):
        conversion = None
        multiplier = 1

        # Let's first try to see if we can find a conversion rate from base to target
        try:
            conversion = cls.objects.filter(base__code=base, target__code=target).latest("timestamp")
            multiplier = conversion.multiplier

        except cls.DoesNotExist:
            pass

        # Let's try to see if there is maybe a newer or reverse conversion rate?
        try:
            reverse_conversion = cls.objects.filter(base__code=target, target__code=base).latest("timestamp")

            if conversion is None or conversion.timestamp < reverse_conversion.timestamp:
                multiplier = 1 / reverse_conversion.multiplier

        except cls.DoesNotExist:
            pass

        return amount * multiplier
