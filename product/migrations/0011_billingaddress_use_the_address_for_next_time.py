# Generated by Django 5.0.6 on 2024-06-17 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_rename_billing_address_billingaddress_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingaddress',
            name='use_the_address_for_next_time',
            field=models.BooleanField(default=False),
        ),
    ]
