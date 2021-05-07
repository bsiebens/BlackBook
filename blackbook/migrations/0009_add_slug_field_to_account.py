# Generated by Django 3.1.4 on 2020-12-20 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blackbook', '0008_add_slug_field_to_account_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='slug',
            field=models.SlugField(default='blank'),
            preserve_default=False,
        ),
    ]
