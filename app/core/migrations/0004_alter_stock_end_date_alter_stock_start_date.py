# Generated by Django 4.0.7 on 2022-10-03 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_stock_stock_run_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='stock',
            name='start_date',
            field=models.DateField(),
        ),
    ]
