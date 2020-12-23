from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from ..models import TransactionJournalEntry, Transaction
from ..utilities import set_message_and_redirect
from ..forms import TransactionForm


@login_required
def add_edit(request, transaction_uuid=None):
    initial_data = {}
    transaction = Transaction()

    if transaction_uuid is not None:
        transaction = Transaction.objects.select_related("journal_entry").select_related("account__account_type").get(uuid=transaction_uuid)

        if transaction.journal_entry.user != request.user:
            return set_message_and_redirect(
                request,
                "f|You don't have access to this transaction.",
                reverse(
                    "blackbook:accounts", kwargs={"account_type": transaction.account.account_type.slug, "account_name": transacion.account.slug}
                ),
            )

        initial_data = {
            "amount": transaction.journal_entry.amount,
            "description": transaction.journal_entry.description,
            "transaction_type": transaction.journal_entry.transaction_type,
            "date": transaction.journal_entry.date,
            "category": transaction.journal_entry.category,
            "budget": transaction.journal_entry.budget.budget,
            "tags": ", ".join([tag.name for tag in transaction.journal_entry.tags.all()]),
            "from_account": transaction.journal_entry.from_account,
            "to_account": transaction.journal_entry.to_account,
        }

        print(initial_data)

    transaction_form = TransactionForm(request.user, request.POST or None, initial=initial_data)

    if request.POST and transaction_form.is_valid():
        if transaction_uuid is not None:
            transaction.journal_entry.update(
                amount=transaction_form.cleaned_data["amount"],
                description=transaction_form.cleaned_data["description"],
                transaction_type=transaction_form.cleaned_data["transaction_type"],
                date=transaction_form.cleaned_data["date"],
                category=transaction_form.cleaned_data["category"],
                budget=transaction_form.cleaned_data["budget"].get_period_for_date(transaction_form.cleaned_data["date"])
                if transaction_form.cleaned_data["budget"] is not None
                else None,
                tags=transaction_form.cleaned_data["tags"],
                from_account=transaction_form.cleaned_data["from_account"],
                to_account=transaction_form.cleaned_data["to_account"],
            )

            return set_message_and_redirect(
                request,
                's|Transaction "{description}" saved succesfully.'.format(description=transaction_form.cleaned_data["description"]),
                reverse("blackbook:transactions_edit", kwargs={"transaction_uuid": transaction.uuid}),
            )

        else:
            TransactionJournalEntry.create_transaction(
                amount=transaction_form.cleaned_data["amount"],
                description=transaction_form.cleaned_data["description"],
                transaction_type=transaction_form.cleaned_data["transaction_type"],
                user=request.user,
                date=transaction_form.cleaned_data["date"],
                category=transaction_form.cleaned_data["category"],
                budget=transaction_form.cleaned_data["budget"].get_period_for_date(transaction_form.cleaned_data["date"])
                if transaction_form.cleaned_data["budget"] is not None
                else None,
                tags=transaction_form.cleaned_data["tags"],
                from_account=transaction_form.cleaned_data["from_account"],
                to_account=transaction_form.cleaned_data["to_account"],
            )

            return set_message_and_redirect(
                request,
                's|Transaction "{description}" saved succesfully.'.format(description=transaction_form.cleaned_data["description"]),
                reverse("blackbook:transactions_add"),
            )

    return render(request, "blackbook/transactions/form.html", {"transaction_form": transaction_form, "transaction": transaction})


@login_required
def delete(request):
    if request.method == "POST":
        transaction = (
            Transaction.objects.select_related("journal_entry").select_related("account__account_type").get(uuid=request.POST.get("transaction_uuid"))
        )

        if transaction.journal_entry.user != request.user:
            return set_message_and_redirect(
                request,
                "f|You don't have access to delete this transaction.",
                reverse(
                    "blackbook:accounts", kwargs={"account_type": transaction.account.account_type.slug, "account_name": transacion.account.slug}
                ),
            )

        transaction.journal_entry.delete()
        return set_message_and_redirect(
            request,
            's|Transaction "{transaction.journal_entry.description}" was succesfully deleted.'.format(transaction=transaction),
            reverse("blackbook:accounts", kwargs={"account_type": transaction.account.account_type.slug, "account_name": transaction.account.slug}),
        )

    else:
        return set_message_and_redirect(
            request,
            "w|You are not allowed to access this page like this.",
            reverse("blackbook:accounts", kwargs={"account_type": transaction.account.account_type.slug, "account_name": transaction.account.slug}),
        )
