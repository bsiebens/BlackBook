from blackbook.models.paycheck import PayCheckItemCategory
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Sum, Q, Prefetch
from django.db.models.functions import Coalesce
from django.utils import timezone

from djmoney.money import Money
from decimal import Decimal
from collections import defaultdict

from ..models import PayCheck, PayCheckItem, get_default_currency
from ..utilities import set_message_and_redirect
from ..charts import PayCheckChart


@login_required
def paychecks(request):
    paychecks = (
        PayCheck.objects.all()
        .order_by("-date")
        .prefetch_related(Prefetch("items", queryset=PayCheckItem.objects.order_by("category__name")))
        .prefetch_related("items__category")
    )
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

        data[paycheck.date.year]["Sum"][0][paycheck.date.month - 1] = paycheck.net_amount

    for paycheck in paychecks:
        if paycheck.date.month >= 1:
            data[paycheck.date.year]["Sum"][1][paycheck.date.month - 1] = (
                paycheck.net_amount - data[paycheck.date.year]["Sum"][0][paycheck.date.month - 2]
            )
        else:
            if (paycheck.date.year - 1) in data.keys():
                data[paycheck.date.year]["Sum"][1][paycheck.date.month - 1] = paycheck.net_amount - data[paycheck.date.year - 1]["Sum"][0][11]
            else:
                data[paycheck.date.year]["Sum"][1][paycheck.date.month - 1] = paycheck.net_amount - Money(0, currency)

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

    chart = PayCheckChart(paychecks.order_by("date")).generate_json()

    return render(request, "blackbook/paychecks/list.html", {"data": data, "chart": chart, "range": range(12)})
