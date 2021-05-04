# Generated by Django 3.1.4 on 2021-01-23 15:00

from django.db import migrations, models
import django.db.models.deletion
import localflavor.generic.models


class Migration(migrations.Migration):

    dependencies = [
        ('blackbook', '0024_add_account_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetAccount',
            fields=[
                ('account_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blackbook.account')),
                ('iban', localflavor.generic.models.IBANField(blank=True, include_countries=None, max_length=34, null=True, use_nordea_extensions=False, verbose_name='IBAN')),
            ],
            bases=('blackbook.account',),
        ),
        migrations.CreateModel(
            name='CashAccount',
            fields=[
                ('account_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blackbook.account')),
            ],
            bases=('blackbook.account',),
        ),
        migrations.CreateModel(
            name='ExpenseAccount',
            fields=[
                ('account_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blackbook.account')),
                ('iban', localflavor.generic.models.IBANField(blank=True, include_countries=None, max_length=34, null=True, use_nordea_extensions=False, verbose_name='IBAN')),
            ],
            bases=('blackbook.account',),
        ),
        migrations.CreateModel(
            name='LiabilitiesAccount',
            fields=[
                ('account_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blackbook.account')),
                ('account_number', models.CharField(blank=True, max_length=100, null=True)),
            ],
            bases=('blackbook.account',),
        ),
        migrations.CreateModel(
            name='RevenueAccount',
            fields=[
                ('account_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blackbook.account')),
                ('iban', localflavor.generic.models.IBANField(blank=True, include_countries=None, max_length=34, null=True, use_nordea_extensions=False, verbose_name='IBAN')),
            ],
            bases=('blackbook.account',),
        ),
    ]
