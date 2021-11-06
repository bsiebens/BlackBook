from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from djmoney.money import Money
from decimal import Decimal

from ..models import Transaction, TransactionJournal, Account, Category, Budget, get_default_currency, get_default_value
from ..utilities import set_message_and_redirect, calculate_period, set_message
from ..charts import TransactionChart
from ..forms import TransactionForm, TransactionFilterForm

import datetime
import re

ACCOUNT_REGEX = re.compile(r"(.*)\s-\s(.*)")


@login_required
def transactions(request):
    transaction_journals = TransactionJournal.objects.all()

    period = get_default_value(key="default_period", default_value="month", user=request.user)
    period = calculate_period(periodicity=period, start_date=timezone.localdate())

    filter_form = TransactionFilterForm(request.GET or None, initial={"start_date": period["start_date"], "end_date": period["end_date"]})
    if filter_form.is_valid():
        period["start_date"] = filter_form.cleaned_data["start_date"]
        period["end_date"] = filter_form.cleaned_data["end_date"]

        if filter_form.cleaned_data["description"] != "":
            transaction_journals = transaction_journals.filter(
                Q(short_description__icontains=filter_form.cleaned_data["description"])
                | Q(description__icontains=filter_form.cleaned_data["description"])
            )

        if filter_form.cleaned_data["account"] != "":
            account_type = Account.AccountType.INCOME_ACCOUNT
            account_name = filter_form.cleaned_data["account"]

            for type in Account.AccountType:
                if type.label == ACCOUNT_REGEX.match(account_name)[1]:
                    account_type = type

            if ACCOUNT_REGEX.match(account_name) is not None:
                account_name = ACCOUNT_REGEX.match(account_name)[2]

            account = Account.objects.get(name=account_name, type=account_type)
            transaction_journals = transaction_journals.filter(transactions__account=account)

        if filter_form.cleaned_data["category"] != "":
            transaction_journals = transaction_journals.filter(category__name__icontains=filter_form.cleaned_data["category"])

        if filter_form.cleaned_data["budget"] != "":
            transaction_journals = transaction_journals.filter(budget__budget__name__icontains=filter_form.cleaned_data["budget"])

    transaction_journals = (
        transaction_journals.filter(date__range=(period["start_date"], period["end_date"]))
        .prefetch_related("transactions")
        .select_related("category")
        .order_by("-date")
    )
    transactions = Transaction.objects.filter(journal__in=transaction_journals).annotate(total=Coalesce(Sum("amount"), Decimal(0)))

    charts = {
        "income_chart": TransactionChart(
            data=transactions.exclude(journal__type=TransactionJournal.TransactionType.TRANSFER), user=request.user, income=True
        ).generate_json(),
        "income_chart_count": len([item for item in transactions if not item.amount.amount < 0]),
        "expense_budget_chart": TransactionChart(data=transactions, expenses_budget=True, user=request.user).generate_json(),
        "expense_budget_chart_count": len([item for item in transactions if item.amount.amount < 0 and item.journal.budget is not None]),
        "expense_category_chart": TransactionChart(data=transactions, expenses_category=True, user=request.user).generate_json(),
        "expense_category_chart_count": len([item for item in transactions if item.amount.amount < 0 and item.journal.category is not None]),
    }

    return render(
        request,
        "blackbook/transactions/list.html",
        {"filter_form": filter_form, "charts": charts, "period": period, "transaction_journals": transaction_journals},
    )


@login_required
def add_edit(request, transaction_uuid=None):
    initial_data = {}
    transaction_journal = TransactionJournal()

    initial_data["amount"] = Money(0, get_default_currency(user=request.user))

    if transaction_uuid is not None:
        transaction_journal = (
            TransactionJournal.objects.prefetch_related("transactions", "transactions__account").select_related("category").get(uuid=transaction_uuid)
        )

        initial_data = {
            "amount": abs(transaction_journal.amount),
            "short_description": transaction_journal.short_description,
            "description": transaction_journal.description,
            "type": transaction_journal.type,
            "date": transaction_journal.date,
            "category": transaction_journal.category.name if transaction_journal.category is not None else None,
            "budget": transaction_journal.budget.budget.name if transaction_journal.budget is not None else None,
            "source_account": None,
            "destination_account": None,
        }

        if len(transaction_journal.source_accounts) > 0:
            initial_data["source_account"] = "{type} - {name}".format(
                type=transaction_journal.source_accounts[0]["type"], name=transaction_journal.source_accounts[0]["account"]
            )

        if len(transaction_journal.destination_accounts) > 0:
            initial_data["destination_account"] = "{type} - {name}".format(
                type=transaction_journal.destination_accounts[0]["type"], name=transaction_journal.destination_accounts[0]["account"]
            )

    transaction_form = TransactionForm(request.user, request.POST or None, initial=initial_data)

    if request.POST and transaction_form.is_valid():
        return_url = reverse("blackbook:dashboard")

        if transaction_form.cleaned_data["add_new"]:
            return_url = reverse("blackbook:transactions_add")

        transaction = {
            "short_description": transaction_form.cleaned_data["short_description"],
            "description": transaction_form.cleaned_data["description"],
            "date": transaction_form.cleaned_data["date"],
            "type": transaction_form.cleaned_data["type"],
            "category": None,
            "budget": None,
            "transactions": [],
        }

        for account_type_key in ["source_account", "destination_account"]:
            if transaction_form.cleaned_data[account_type_key] != "":
                account_name = transaction_form.cleaned_data[account_type_key]

                account_type = Account.AccountType.INCOME_ACCOUNT
                if account_type_key == "destination_account":
                    account_type = Account.AccountType.EXPENSE_ACCOUNT

                if ACCOUNT_REGEX.match(transaction_form.cleaned_data[account_type_key]) is not None:
                    account_name = ACCOUNT_REGEX.match(transaction_form.cleaned_data[account_type_key])[2]

                    for type in Account.AccountType:
                        if type.label == ACCOUNT_REGEX.match(transaction_form.cleaned_data[account_type_key])[1]:
                            account_type = type

                account, account_created = Account.objects.get_or_create(
                    name=account_name, type=account_type, defaults={"type": account_type, "net_worth": False, "dashboard": False}
                )

                if account_created:
                    set_message(request, 's|Account "{account.name}" was saved succesfully.'.format(account=account))

                amount = transaction_form.cleaned_data["amount"]
                if account_type_key == "source_account":
                    amount *= -1

                transaction["transactions"].append({"account": account, "amount": amount})

        if transaction_form.cleaned_data["category"] != "":
            category, created = Category.objects.get_or_create(name=transaction_form.cleaned_data["category"])
            transaction["category"] = category

            if created:
                set_message(request, 's|Category "{category.name}" was saved succesfully.'.format(category=category))

        if transaction_form.cleaned_data["budget"] != "":
            budget, created = Budget.objects.get_or_create(name=transaction_form.cleaned_data["budget"])
            transaction["budget"] = budget.current_period

            if created:
                set_message(request, 's|Budget "{budget.name}" was saved succesfully.'.format(budget=budget))

        if transaction_uuid is None:
            transaction_journal = TransactionJournal.create(transactions=transaction)
        else:
            transaction_journal.update(transactions=transaction)

        if transaction_form.cleaned_data["display"]:
            return_url = reverse("blackbook:transactions_edit", kwargs={"transaction_uuid": transaction_journal.uuid})

        return set_message_and_redirect(
            request,
            's|Transaction "{short_description}" was saved succesfully.'.format(short_description=transaction_form.cleaned_data["short_description"]),
            return_url,
        )

    return render(
        request,
        "blackbook/transactions/form.html",
        {"transaction_form": transaction_form, "transaction_journal": transaction_journal, "amount": initial_data["amount"]},
    )


@login_required
def delete(request):
    if request.method == "POST":
        journal_entry = TransactionJournal.objects.get(uuid=request.POST.get("transaction_uuid"))
        journal_entry.delete()

        return set_message_and_redirect(
            request,
            's|Transaction "{journal_entry.short_description}" was succesfully deleted.'.format(journal_entry=journal_entry),
            reverse("blackbook:dashboard"),
        )
    else:
        return set_message_and_redirect(request, "w|You are not allowed to access this page like this.", reverse("blackbook:dashboard"))
