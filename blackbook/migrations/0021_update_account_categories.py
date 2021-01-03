# Generated by Django 3.1.4 on 2021-01-03 21:43

from django.db import migrations


def create_default_values(apps, schema_editor):
    AccountType = apps.get_model("blackbook", "AccountType")

    initial_data = [
        ("Asset account", "assets"),
        ("Cash account", "assets"),
        ("Credit card account", "liabilities"),
        ("Expense account", "expenses"),
        ("Loan", "liabilities"),
        ("Mortgage", "liabilities"),
        ("Revenue account", "income"),
        ("Savings account", "assets"),
    ]

    for account_type in initial_data:
        at_object = AccountType.objects.get(name=account_type[0])

        at_object.category = account_type[1]
        at_object.save()


class Migration(migrations.Migration):

    dependencies = [
        ("blackbook", "0020_add_account_type_category"),
    ]

    operations = [migrations.RunPython(create_default_values)]
