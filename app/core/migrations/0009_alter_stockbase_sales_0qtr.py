# Generated by Django 4.0.7 on 2022-10-07 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_stockbase_base_failure_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockbase',
            name='sales_0qtr',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
