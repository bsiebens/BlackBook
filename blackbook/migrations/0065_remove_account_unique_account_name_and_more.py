# Generated by Django 4.0b1 on 2021-11-07 12:07

from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blackbook', '0064_currency_currencyconversion'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='account',
            name='unique_account_name',
        ),
        migrations.RemoveField(
            model_name='account',
            name='virtual_balance',
        ),
        migrations.AddField(
            model_name='account',
            name='level',
            field=models.PositiveIntegerField(default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='account',
            name='lft',
            field=models.PositiveIntegerField(default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='account',
            name='parent',
            field=mptt.fields.TreeForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='blackbook.account'),
        ),
        migrations.AddField(
            model_name='account',
            name='rght',
            field=models.PositiveIntegerField(default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='account',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='account',
            name='currency',
        ),
        migrations.AddField(
            model_name='account',
            name='currency',
            field=models.ManyToManyField(blank=True, to='blackbook.Currency'),
        ),
        migrations.AlterField(
            model_name='bonus',
            name='gross_amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='bonus',
            name='net_amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='bonus',
            name='taxes_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='budget',
            name='amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='budgetperiod',
            name='amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='paycheck',
            name='gross_amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='paycheck',
            name='net_amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='paycheckitem',
            name='amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='paycheckitem',
            name='real_amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='paycheckitemcategory',
            name='default_amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='foreign_amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='transactionjournal',
            name='amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('ALL', 'Albanian Lek'), ('AMD', 'Armenian Dram'), ('AZN', 'Azerbaijani Manat'), ('BYN', 'Belarusian Ruble'), ('BAM', 'Bosnia-Herzegovina Convertible Mark'), ('GBP', 'British Pound'), ('BGN', 'Bulgarian Lev'), ('HRK', 'Croatian Kuna'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GEL', 'Georgian Lari'), ('HUF', 'Hungarian Forint'), ('ISK', 'Icelandic Króna'), ('MKD', 'Macedonian Denar'), ('MDL', 'Moldovan Leu'), ('NOK', 'Norwegian Krone'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('RSD', 'Serbian Dinar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('TRY', 'Turkish Lira'), ('UAH', 'Ukrainian Hryvnia')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AddConstraint(
            model_name='account',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='unique_account_name_for_parent'),
        ),
    ]
