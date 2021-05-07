# Generated by Django 3.2rc1 on 2021-05-03 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blackbook', '0046_auto_20210429_2039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='destination_accounts',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='source_accounts',
        ),
        migrations.AddField(
            model_name='transactionjournal',
            name='source_accounts',
            field=models.JSONField(null=True),
        ),
    ]
