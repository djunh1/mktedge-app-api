# Generated by Django 4.0.8 on 2022-10-11 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_stockbase_vol_20_alter_stockbase_vol_bo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockbase',
            name='price_percent_range',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]
