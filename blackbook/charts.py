from django.db.models import Sum

from djmoney.money import Money
from datetime import timedelta, date

import json
import re

from .models import get_default_currency, TransactionJournal, Transaction, Account
from .utilities import get_currency


def get_color_code(i):
    color_codes = ["98, 181, 229", "134, 188, 37", "152, 38, 73", "124, 132, 131", "213, 216, 135", "247, 174, 248"]
    color = (i - 1) % len(color_codes)

    return color_codes[color]


class Chart:
    def __init__(self, data):
        self.data = data

    def generate_json(self):
        chart_data = self._generate_chart_data()
        chart_options = self._generate_chart_options()
        chart_data["options"] = chart_options

        return json.dumps(chart_data).replace('"<<', "").replace('>>"', "")

    def _generate_chart_data(self):
        raise NotImplementedError

    def _generate_chart_options(self):
        return self._get_default_options()

    def _get_default_options(self):
        return {
            "maintainAspectRatio": False,
            "legend": {
                "display": False,
            },
            "animation": {"duration": 0},
            "responsive": True,
            "tooltips": {
                "backgroundColor": "#f5f5f5",
                "titleFontColor": "#333",
                "bodyFontColor": "#666",
                "bodySpacing": 4,
                "xPadding": 12,
                "mode": "nearest",
                "intersect": 0,
                "position": "nearest",
            },
            "scales": {
                "yAxes": [
                    {
                        "barPercentage": 1.6,
                        "gridLines": {"drawBorder": False, "color": "rgba(225,78,202,0.1)", "zeroLineColor": "transparent"},
                        "ticks": {"padding": 20, "fontColor": "#9a9a9a"},
                    }
                ],
                "xAxes": [
                    {
                        "type": "time",
                        "time": {"unit": "day"},
                        "barPercentage": 1.6,
                        "gridLines": {"drawBorder": False, "color": "rgba(225,78,202,0.1)", "zeroLineColor": "transparent"},
                        "ticks": {"padding": 20, "fontColor": "#9a9a9a"},
                    }
                ],
            },
        }


class PayCheckChart(Chart):
    def _generate_chart_options(self):
        options = self._get_default_options()

        options["scales"]["xAxes"][0]["time"]["unit"] = "quarter"

        return options

    def _generate_chart_data(self):
        data = {
            "type": "line",
            "data": {
                "labels": [],
                "datasets": [
                    {
                        "label": "Paychecks (net amount)",
                        "fill": "!1",
                        "borderColor": "rgba({color}, 1.0)".format(color=get_color_code(1)),
                        "borderWidth": 2,
                        "borderDash": [],
                        "borderDash0ffset": 0,
                        "pointBackgroundColor": "rgba({color}, 1.0)".format(color=get_color_code(1)),
                        "pointBorderColor": "rgba(255,255,255,0)",
                        "pointHoverBackgroundColor": "rgba({color}, 1.0)".format(color=get_color_code(1)),
                        "pointBorderWidth": 20,
                        "pointHoverRadius": 4,
                        "pointHoverBorderWidth": 15,
                        "pointRadius": 4,
                        "data": [],
                    },
                    {
                        "label": "Paychecks (gross amount)",
                        "fill": "!1",
                        "borderColor": "rgba({color}, 1.0)".format(color=get_color_code(2)),
                        "borderWidth": 2,
                        "borderDash": [],
                        "borderDash0ffset": 0,
                        "pointBackgroundColor": "rgba({color}, 1.0)".format(color=get_color_code(2)),
                        "pointBorderColor": "rgba(255,255,255,0)",
                        "pointHoverBackgroundColor": "rgba({color}, 1.0)".format(color=get_color_code(2)),
                        "pointBorderWidth": 20,
                        "pointHoverRadius": 4,
                        "pointHoverBorderWidth": 15,
                        "pointRadius": 4,
                        "data": [],
                    },
                ],
            },
        }

        for paycheck in self.data:
            if not paycheck.hidden:
                paycheck_date = date(paycheck.date.year, paycheck.date.month, 15).strftime("%d %b %Y")

                if paycheck_date not in data["data"]["labels"]:
                    data["data"]["labels"].append(paycheck_date)
                    data["data"]["datasets"][0]["data"].append(float(paycheck.net_amount.amount))
                    data["data"]["datasets"][1]["data"].append(float(paycheck.gross_amount.amount))
                else:
                    index = data["data"]["labels"].index(paycheck_date)
                    data["data"]["datasets"][0]["data"][index] += float(paycheck.net_amount.amount)
                    data["data"]["datasets"][1]["data"][index] += float(paycheck.gross_amount.amount)

        if len(data) > 150:
            data["data"]["datasets"][0]["pointRadius"] = 0
            data["data"]["datasets"][1]["pointRadius"] = 0

        return data


class AccountChart(Chart):
    def __init__(self, data, accounts, start_date, end_date, user=None, *args, **kwargs):
        self.start_date = start_date
        self.end_date = end_date
        self.accounts = accounts
        self.user = user
        self.currency = get_default_currency(user=self.user)

        super().__init__(data=data, *args, **kwargs)

    def _generate_chart_options(self):
        options = self._get_default_options()

        options["tooltips"]["callbacks"] = {
            "label": "<<function(tooltipItems, data) { return data.datasets[tooltipItems.datasetIndex].label + ': ' + tooltipItems.yLabel + ' (%s)'; }>>"
            % get_currency(self.currency, self.user)
        }

        if abs((self.end_date - self.start_date).days) > 150:
            options["scales"]["xAxes"][0]["time"]["unit"] = "week"

        return options

    def _generate_chart_data(self):
        dates = []

        for days_to_add in range(abs((self.end_date - self.start_date).days) + 1):
            day = self.start_date + timedelta(days=days_to_add)
            dates.append(day)

        data = {"type": "line", "data": {"labels": [date.strftime("%d %b %Y") for date in dates], "datasets": []}}

        accounts = {}
        accounts_virtual_balance = {}

        for item in self.data:
            if str(item.amount.currency) == str(self.currency) and item.account is not None:
                account_key = "{type} - {account}".format(type=item.account.get_type_display(), account=item.account.name)

                if account_key in accounts.keys():
                    date_entry = accounts[account_key].get(item.journal.date, Money(0, self.currency))
                    date_entry += item.amount

                    accounts[account_key][item.journal.date] = date_entry

                else:
                    accounts[account_key] = {item.journal.date: item.amount}
                    accounts_virtual_balance[account_key] = item.account.virtual_balance

        for account in self.accounts:
            account_key = "{type} - {account}".format(type=account.get_type_display(), account=account.name)

            if account_key not in accounts.keys():
                accounts[account_key] = {}

        counter = 1
        for account, date_entries in accounts.items():
            color = get_color_code(counter)

            account_data = {
                "label": account,
                "fill": "!1",
                "borderColor": "rgba({color}, 1.0)".format(color=color),
                "borderWidth": 2,
                "borderDash": [],
                "borderDash0ffset": 0,
                "pointBackgroundColor": "rgba({color}, 1.0)".format(color=color),
                "pointBorderColor": "rgba(255,255,255,0)",
                "pointHoverBackgroundColor": "rgba({color}, 1.0)".format(color=color),
                "pointBorderWidth": 20,
                "pointHoverRadius": 4,
                "pointHoverBorderWidth": 15,
                "pointRadius": 4,
                "data": [],
            }

            if abs((self.end_date - self.start_date).days) > 150:
                account_data["pointRadius"] = 0

            counter += 1

            for date_index in range(len(dates)):
                date = dates[date_index]

                value = 0

                if date_index == 0:
                    ACCOUNT_REGEX = re.compile(r"(.*)\s-\s(.*)")

                    account_name = ACCOUNT_REGEX.match(account)[2]
                    account_type = Account.AccountType.ASSET_ACCOUNT

                    for type in Account.AccountType:
                        if type.label == ACCOUNT_REGEX.match(account)[1]:
                            account_type = type

                    account_object = Account.objects.get(name=account_name, type=account_type)
                    value = float(account_object.balance_until_date(date - timedelta(days=1)).amount) - float(account_object.virtual_balance)
                else:
                    value = account_data["data"][date_index - 1]

                if date in date_entries.keys():
                    value += float(date_entries[date].amount)

                account_data["data"].append(round(value, 2))
            data["data"]["datasets"].append(account_data)

        return data


class TransactionChart(Chart):
    def __init__(self, data, user=None, income=False, expenses_budget=False, expenses_category=False, *args, **kwargs):
        self.income = income
        self.expenses_budget = expenses_budget
        self.expenses_category = expenses_category
        self.user = user
        self.currency = get_default_currency(user=self.user)

        super().__init__(data=data, *args, **kwargs)

    def _generate_chart_options(self):
        options = self._get_default_options()

        options["scales"] = {}
        options["legend"] = {"position": "right"}

        return options

    def _generate_chart_data(self):
        data = {"type": "pie", "data": {"labels": [], "datasets": [{"data": [], "borderWidth": [], "backgroundColor": [], "borderColor": []}]}}

        amounts = {}
        account_names = {}

        if self.income:
            self.data = [item for item in self.data if not item.amount.amount < 0]
        else:
            self.data = [item for item in self.data if item.amount.amount < 0]

        for transaction in self.data:
            account_name = "External account (untracked)"

            if self.income:
                if transaction.journal.type == TransactionJournal.TransactionType.START:
                    account_name = "Starting balance"

                else:
                    if len(transaction.journal.source_accounts) > 0:
                        account_name = ", ".join([account["account"] for account in transaction.journal.source_accounts])

            else:
                if self.expenses_budget and transaction.journal.budget is not None:
                    account_name = transaction.journal.budget.budget.name

                if self.expenses_category and transaction.journal.category is not None:
                    account_name = transaction.journal.category.name

            amount = amounts.get(account_name, 0.0)
            amount += float(transaction.amount.amount)
            amounts[account_name] = amount

        if not self.income:
            amounts.pop("External account (untracked)", None)

        counter = 1
        for account, amount in amounts.items():
            color = get_color_code(counter)
            counter += 1

            data["data"]["labels"].append("{account} ({currency})".format(account=account, currency=get_currency(self.currency, self.user)))
            data["data"]["datasets"][0]["data"].append(round(amount, 2))
            data["data"]["datasets"][0]["borderWidth"].append(2)
            data["data"]["datasets"][0]["backgroundColor"].append("rgba({color}, 1.0)".format(color=color))
            data["data"]["datasets"][0]["borderColor"].append("rgba(255, 255, 255, 1.0)".format(color=color))

        return data
