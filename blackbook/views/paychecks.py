from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from djmoney.money import Money
from decimal import Decimal
from collections import defaultdict

from ..models import Paycheck, PayCheckItem, get_default_currency
from ..utilities import set_message_and_redirect


@login_required
def paychecks(request):
    paychecks = Paycheck.objects.all().order_by("date").prefetch_related("items").prefetch_related("items__category").order_by("-date")
    currency = get_default_currency(user=request.user)

    data = {}

    for paycheck in paychecks:
        if paycheck.date.year not in data.keys():
            data[paycheck.date.year] = {
                "Gross amount": {},
                "Taxable amount": {},
                "Net amount": {},
                "Sum": [[Money(0, currency)] * 12, [Money(0, currency)] * 12],
            }

        for item in paycheck.items.all():
            if item.category.name not in data[paycheck.date.year][item.category.type].keys():
                data[paycheck.date.year][item.category.type][item.category.name] = {
                    "amount": [Money(0, currency)] * 12,
                    "real_amount": [Money(0, currency)] * 12,
                }

            data[paycheck.date.year][item.category.type][item.category.name]["amount"][paycheck.date.month - 1] = item.amount
            data[paycheck.date.year][item.category.type][item.category.name]["real_amount"][paycheck.date.month - 1] = item.real_amount

        data[paycheck.date.year]["Sum"][paycheck.date.month - 1][0] = paycheck.amount

        if paycheck.date.month >= 1:
            data[paycheck.date.year]["Sum"][paycheck.date.month - 1][1] = (
                paycheck.amount - data[paycheck.date.year]["Sum"][paycheck.date.month - 2][0]
            )
        else:
            if (paycheck.date.year - 1) in data.keys():
                data[paycheck.date.year]["Sum"][paycheck.date.month - 1][1] = paycheck.amount - data[paycheck.date.year - 1]["Sum"][11][0]
            else:
                data[paycheck.date.year]["Sum"][paycheck.date.month - 1][1] = paycheck.amount - Money(0, currency)

    for year in data.keys():
        for key in ["Gross amount", "Taxable amount", "Net amount"]:
            month_sum = [Money(0, currency)] * 12

            for category in data[year][key].keys():
                for i in range(12):
                    if data[year][key][category]["real_amount"][i] != Money(0, currency):
                        if month_sum[i] == Money(0, currency):
                            month_sum[i] = data[year][key][category]["real_amount"][i]
                        else:
                            month_sum[i] += data[year][key][category]["real_amount"][i]

            data[year][key]["Sum"] = month_sum

    return render(request, "blackbook/paychecks/list.html", {"data": data, "range": range(12)})