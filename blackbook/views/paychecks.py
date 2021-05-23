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
        year = paycheck.date.year
        month = paycheck.date.month

        if year not in data.keys():
            data[year] = {
                "gross amount": {},
                "taxable amount": {},
                "net amount": {},
                "sum": [],
            }

            for i in range(12):
                data[year]["sum"].append({"amount": Money(0, currency), "delta": Money(0, currency)})

        for item in paycheck.items.all():
            category_name = item.category.name
            category_type = item.category.type.lower()

            if category_name not in data[year][category_type].keys():
                data[year][category_type][category_name] = []
                for i in range(12):
                    data[year][category_type][category_name].append({"amount": Money(0, currency), "delta": Money(0, currency)})

            data[year][category_type][category_name][month - 1]["amount"] += item.amount
            data[year][category_type][category_name][month - 1]["delta"] += item.amount
        data[year]["sum"][month - 1]["amount"] += paycheck.net_amount
        data[year]["sum"][month - 1]["delta"] += paycheck.net_amount

    for year in data.keys():
        for category in ["gross amount", "taxable amount", "net amount"]:
            for item in data[year][category].keys():
                for i in range(12):
                    if i > 0 and data[year]["sum"][i]["amount"] != Money(0, currency):
                        data[year][category][item][i]["delta"] -= data[year][category][item][i - 1]["amount"]
                    else:
                        if (
                            (year - 1) in data.keys()
                            and item in data[(year - 1)][category].keys()
                            and data[year]["sum"][i]["amount"] != Money(0, currency)
                        ):
                            data[year][category][item][i]["delta"] -= data[year][category][item][11]["amount"]

        for i in range(12):
            if i > 0:
                data[year]["sum"][i]["delta"] -= data[year]["sum"][i - 1]["amount"]
            else:
                if (year - 1) in data.keys():
                    data[year]["sum"][i]["delta"] -= data[year]["sum"][11]["amount"]

    chart = PayCheckChart(paychecks.order_by("date")).generate_json()

    return render(request, "blackbook/paychecks/list.html", {"data": data, "chart": chart, "range": range(12)})
