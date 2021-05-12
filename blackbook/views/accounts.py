from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Sum, Prefetch, Count
from django.db.models.functions import Coalesce
from django.utils import timezone

from djmoney.money import Money
from decimal import Decimal

from ..models import get_default_value, Account, Transaction, TransactionJournal
from ..utilities import set_message_and_redirect, calculate_period
from ..forms import AccountForm
from ..charts import AccountChart, TransactionChart


@login_required
def accounts(request, account_type=None, account_slug=None):
    if account_slug is not None:
        period = get_default_value(key="default_period", default_value="month", user=request.user)
        period = calculate_period(periodicity=period, start_date=timezone.localdate())

        account = get_object_or_404(Account, slug=account_slug)
        transactions = (
            Transaction.objects.filter(account=account)
            .filter(journal__date__range=(period["start_date"], period["end_date"]))
            .select_related("journal", "account")
            .order_by("-journal__date")
        )

        period_in = Money(transactions.filter(amount__gte=0).aggregate(total=Coalesce(Sum("amount"), Decimal(0)))["total"], account.currency)
        period_out = Money(transactions.filter(amount__lte=0).aggregate(total=Coalesce(Sum("amount"), Decimal(0)))["total"], account.currency)
        period_balance = period_in + period_out

        charts = {
            "account_chart": AccountChart(
                data=transactions, accounts=[account], start_date=period["start_date"], end_date=period["end_date"], user=request.user
            ).generate_json(),
            "income_chart": TransactionChart(data=transactions, user=request.user, income=True).generate_json(),
            "income_chart_count": len([item for item in transactions if not item.amount.amount < 0]),
            "expense_budget_chart": TransactionChart(data=transactions, expenses_budget=True, user=request.user).generate_json(),
            "expense_budget_chart_count": len([item for item in transactions if item.amount.amount < 0 and item.journal.budget is not None]),
            "expense_category_chart": TransactionChart(data=transactions, expenses_category=True, user=request.user).generate_json(),
            "expense_category_chart_count": len([item for item in transactions if item.amount.amount < 0 and item.journal.category is not None]),
        }

        return render(
            request,
            "blackbook/accounts/detail.html",
            {
                "transactions": transactions,
                "account": account,
                "in_for_period": period_in,
                "out_for_period": period_out,
                "balance_for_period": period_balance,
                "period": period,
                "charts": charts,
            },
        )

    else:
        account_types = {
            "assetaccount": {"name": "asset accounts", "icon": "fa-landmark", "total": {}},
            "revenueaccount": {"name": "revenue accounts", "icon": "fa-donate", "total": {}},
            "expenseaccount": {"name": "expense accounts", "icon": "fa-file-invoice-dollar", "total": {}},
            "liabilities": {"name": "liabilities", "icon": "fa-home", "total": {}},
            "cashaccount": {"name": "cash accounts", "icon": "fa-coins", "total": {}},
        }

        accounts = (
            Account.objects.filter(type=account_type)
            .annotate(
                total=Coalesce(Sum("transactions__amount"), Decimal(0)),
            )
            .order_by("name")
        )

        account_type = account_types[account_type]

        for account in accounts:
            account.total_amount = Money(account.total, account.currency) - Money(account.virtual_balance, account.currency)
            account_type["total"][account.currency] = account_type["total"].get(account.currency, Money(0, account.currency)) + account.total_amount

        return render(request, "blackbook/accounts/list.html", {"account_type": account_type, "accounts": accounts})


@login_required
def add_edit_account(request, account_slug=None):
    account = Account()

    if account_slug is not None:
        account = get_object_or_404(Account, slug=account_slug)

    account_form = AccountForm(request.POST or None, instance=account, initial={"starting_balance": account.starting_balance.amount})

    if request.POST and account_form.is_valid():
        account = account_form.save()

        if account_form.cleaned_data["starting_balance"] != 0:
            opening_balance = Money(account_form.cleaned_data["starting_balance"], account.currency)

            try:
                opening_balance_transaction = account.transactions.filter(journal__type=TransactionJournal.TransactionType.START).get(
                    journal__date=account.created.date()
                )

                if opening_balance_transaction.amount != opening_balance:
                    opening_balance_transaction.amount = opening_balance
                    opening_balance_transaction.save()

            except Transaction.DoesNotExist:
                transaction = {
                    "short_description": "Starting balance",
                    "description": "Starting balance",
                    "date": account.created.date(),
                    "type": TransactionJournal.TransactionType.START,
                    "transactions": [{"account": account, "amount": opening_balance}],
                }

                TransactionJournal.create(transactions=transaction)

        return set_message_and_redirect(
            request,
            "s|Account '{account_name}' ({account_type}) was saved succesfully.".format(
                account_name=account.name, account_type=account.get_type_display()
            ),
            reverse("blackbook:dashboard"),
        )

    return render(request, "blackbook/accounts/form.html", {"account_form": account_form, "account": account})


@login_required
def delete(request):
    if request.method == "POST":
        account = Account.objects.get(uuid=request.POST.get("account_uuid"))
        account.delete()

        hanging_transactions = Transaction.objects.filter(source_account=None, destination_account=None)
        hanging_transactions.delete()
        hanging_journals = TransactionJournal.objects.filter(transactions=None)
        hanging_journals.delete()

        return set_message_and_redirect(
            request,
            's|Account "{account.name}" was succesfully deleted.'.format(account=account),
            reverse("blackbook:accounts_list", kwargs={"account_type": account.type}),
        )
    else:
        return set_message_and_redirect(request, "w|You are not allowed to access this page like this.", reverse("blackbook:dashboard"))
