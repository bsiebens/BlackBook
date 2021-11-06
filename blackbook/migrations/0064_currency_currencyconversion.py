# Generated by Django 3.2.2 on 2021-11-06 11:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blackbook', '0063_alter_account_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name_plural': 'currencies',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='CurrencyConversion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('multiplier', models.DecimalField(decimal_places=10, max_digits=20)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='base_currency', to='blackbook.currency')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_currency', to='blackbook.currency')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]
